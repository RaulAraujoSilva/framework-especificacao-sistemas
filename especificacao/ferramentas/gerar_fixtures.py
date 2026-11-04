"""Gera os fixtures de aceitação do motor de cálculo a partir do levantamento da fase 5.

Entrada (só leitura, relativa à raiz do repositório):
- saida/levantamento/calculo/extracao_<processo>.json: fórmula, pesos e números de cada apuração, copiados das peças;
- saida/levantamento/calculo/recalculo.csv: o recálculo do oráculo (scripts/recalcular_reajuste.py);
- saida/levantamento/calculo/resumo.json: as contagens do levantamento, usadas como portão.

- insumos/mapeamento/casos_P01.json: linha do tempo de cada caso da coorte (atividades t1 a t16 com datas);
- insumos/mapeamento/conformidade_P01.csv: resultado de cada requisito legal R-P01 em cada caso (oráculo da conformidade);
- perfis/rj_agenersa.py: feriados que fecham o expediente (lidos do arquivo, sem importar o pacote de scripts).

Saídas:
- especificacao/fixtures/calculos_coorte.json: um caso por apuração completa (todos os componentes com número e IR
  escrito), com as entradas, o IR e o total esperados e a classificação ok/divergente com a causa;
- especificacao/fixtures/ciclos_coorte.json: os marcos reais de cada caso, a conformidade esperada de cada R-P01 e,
  para o ciclo-piloto de Paraty 2026, os vencimentos que as regras de prazo do TO-BE dariam com as datas reais;
- especificacao/fixtures/paraty_2026.json: o pleito real de Paraty 2026 no layout, o cadastro do contrato, o
  resultado esperado das regras V01 a V12 e as mutações do AT-05 (de saida/levantamento/pleito e saida/levantamento/contratos).

Regras:
- não acessa a rede nem a pasta dados/; usa só a biblioteca padrão;
- refaz a conta com a mesma regra do oráculo e para com erro se o resultado não bater com recalculo.csv
  (4 casas) ou se as contagens não baterem com resumo.json;
- ordena tudo e não grava data nem hora: duas rodadas com os mesmos arquivos dão o mesmo fixture.

Uso, da raiz do repositório: python especificacao/ferramentas/gerar_fixtures.py [--conferir]
Com --conferir, não grava: só compara o que geraria com o fixture existente e sai com código 1 se diferir.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CALCULO = RAIZ / "saida" / "levantamento" / "calculo"
COMUM = RAIZ / "scripts" / "comum.py"
SAIDA = RAIZ / "especificacao" / "fixtures" / "calculos_coorte.json"
CASOS = RAIZ / "insumos" / "mapeamento" / "casos_P01.json"
CONFORMIDADE = RAIZ / "insumos" / "mapeamento" / "conformidade_P01.csv"
PERFIL = RAIZ / "perfis" / "rj_agenersa.py"
SAIDA_CICLOS = RAIZ / "especificacao" / "fixtures" / "ciclos_coorte.json"
CICLO_PILOTO = "SEI-480002/009982/2025"  # Águas de Paraty, vigência 01/01/2026 (contrato-piloto)

# Causa de cada divergência: classificação do levantamento (docs/LEVANTAMENTO_MOTOR_CALCULO.md, seção 2).
# É julgamento registrado no levantamento, não conta; a conta vem do recálculo.
CAUSAS = {
    ("SEI-220007/004053/2022", "43014673"): {
        "tipo": "erro no texto",
        "descricao": ("As variações escritas da energia (-0,0085) e do IPC (0,0546) não batem com os números-índice "
                      "citados (-0,0840 e 0,0505). Foram deliberados 10,37% (cenário B). A confirmar com a CAPET "
                      "pela planilha anexa, que não foi extraída."),
        "teste_aceitacao": "AT-02",
    },
    ("SEI-480002/009058/2025", "118597733"): {
        "tipo": "erro no texto",
        "descricao": ("Os índices do próprio parecer dão 5,3195%, que foi o percentual deliberado. "
                      "O 4,1245% do texto é erro de digitação."),
        "teste_aceitacao": "AT-03",
    },
    ("SEI-480002/001912/2024", "69248862"): {
        "tipo": "arredondamento de insumo",
        "descricao": ("O preço da água da CEDAE foi escrito com 2 casas (2,23/2,09). A variação oficial é 6,75%; "
                      "com ela o IR fecha."),
        "componente_arredondado": "D",
        "teste_aceitacao": "AT-04",
    },
    ("SEI-480002/001913/2024", "69248357"): {
        "tipo": "arredondamento de insumo",
        "descricao": ("O preço da água da CEDAE foi escrito com 2 casas (2,23/2,09). A variação oficial é 6,75%; "
                      "com ela o IR fecha."),
        "componente_arredondado": "D",
        "teste_aceitacao": "AT-04",
    },
}
# Casos que, além do AT-01, sustentam outro teste de aceitação (12_TESTES.md).
OUTROS_TESTES = {
    "SEI-480002/009982/2025": ["AT-06"],  # Paraty 2026: o cálculo do parecer é o do pleito validado
    "SEI-480002/009822/2025": ["AT-07"],  # Águas da Imperatriz: generalização pelo cadastro
}


def tolerancia_pp() -> float:
    """Lê TOL_RECALCULO_PP de scripts/comum.py sem importar o módulo (que depende de caminhos locais)."""
    m = re.search(r"^TOL_RECALCULO_PP\s*=\s*([0-9.]+)", COMUM.read_text(encoding="utf-8"), re.M)
    if not m:
        raise SystemExit("TOL_RECALCULO_PP não encontrado em scripts/comum.py")
    return float(m.group(1))


def chave(sigla: str) -> str:
    """Mesma regra do oráculo: a sigla até o primeiro espaço ou parêntese, em maiúsculas."""
    return re.split(r"[\s(]", sigla.strip())[0].upper()


def var_escrita(v: dict) -> float | None:
    """Variação escrita como fração; uma razão i/o escrita (1,065231) vira 0,065231 (regra do oráculo)."""
    x = v.get("variacao")
    if x is None:
        return None
    return x - 1 if x > 0.5 else x


def termo(v: dict, modo: str) -> float | None:
    if modo == "indices":
        return v["i"] / v["o"] - 1 if v.get("i") is not None and v.get("o") else None
    return var_escrita(v)


def ir(valores: list[dict], pesos: dict, modo: str, troca: dict | None = None) -> tuple[float | None, int]:
    """IR em % e quantos componentes ficaram sem número. `troca` força o termo de uma sigla (prova da causa)."""
    termos, faltam = [], 0
    for v in valores:
        x = (troca or {}).get(chave(v["sigla"]), termo(v, modo))
        if x is None:
            faltam += 1
            continue
        termos.append((v.get("peso_usado") or pesos.get(chave(v["sigla"])), x))
    if not termos:
        return None, faltam
    if all(p is None for p, _ in termos):  # índice único: o primeiro valor é o índice principal
        return 100 * termos[0][1], faltam
    k = 100 if sum(p for p, _ in termos if p) > 1.5 else 1  # pesos escritos em %
    return 100 * sum((p or 0) / k * x for p, x in termos), faltam


def num(s: str) -> float | None:
    return None if s in ("", None) else float(s)


def sha256(p: Path) -> str:
    """Hash com fim de linha normalizado para LF: mesmo valor no Windows (autocrlf) e na CI."""
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def gerar() -> dict:
    tol = tolerancia_pp()
    linhas = list(csv.DictReader((CALCULO / "recalculo.csv").open(encoding="utf-8-sig")))
    por_doc = {}
    for r in linhas:
        k = (r["processo"], r["doc"])
        if k in por_doc:
            raise SystemExit(f"apuração repetida em recalculo.csv: {k}")
        por_doc[k] = r

    extracoes = sorted(CALCULO.glob("extracao_*.json"))
    casos = []
    for arq in extracoes:
        d = json.loads(arq.read_text(encoding="utf-8"))
        form = d.get("formula") or {}
        cdef = {chave(c["sigla"]): c for c in form.get("componentes", []) if c.get("sigla")}
        pesos = {k: c.get("peso") for k, c in cdef.items()}
        for a in d.get("apuracoes", []):
            vals = a.get("valores") or []
            r = por_doc.get((d["processo"], str(a.get("doc_id"))))
            if not vals or r is None or r["completa"] != "True" or r["confere"] == "":
                continue  # só apuração completa e avaliada pelo oráculo
            ir_i, falta_i = ir(vals, pesos, "indices")
            ir_v, falta_v = ir(vals, pesos, "variacoes")
            for nome, meu, dele in (("ir_pelos_indices", ir_i, r["ir_pelos_indices"]),
                                    ("ir_pelas_variacoes", ir_v, r["ir_pelas_variacoes"])):
                if (meu is None) != (num(dele) is None) or (meu is not None and round(meu, 4) != num(dele)):
                    raise SystemExit(f"{d['processo']} {a['doc_id']}: {nome} {meu} difere do oráculo {dele}")
            base = "numeros_indice" if r["confere_indices"] != "" else "variacoes"
            ir_rec = ir_i if base == "numeros_indice" else ir_v
            escrito = a["ir_pct"]
            confere = abs(ir_rec - escrito) <= tol
            if confere != (r["confere"] == "True"):
                raise SystemExit(f"{d['processo']} {a['doc_id']}: classificação difere do oráculo")

            soma_k = sum(p for p in (v.get("peso_usado") or pesos.get(chave(v["sigla"])) for v in vals) if p)
            k = 100 if soma_k > 1.5 else 1
            unico = all((v.get("peso_usado") or pesos.get(chave(v["sigla"]))) is None for v in vals)
            componentes = []
            for n, v in enumerate(vals):
                p = v.get("peso_usado") or pesos.get(chave(v["sigla"]))
                componentes.append({
                    "sigla": chave(v["sigla"]),
                    "sigla_no_texto": v["sigla"],
                    "indice": (cdef.get(chave(v["sigla"])) or {}).get("indice"),
                    "peso": None if p is None else round(p / k, 6),
                    "principal": (n == 0) if unico else None,
                    "o": v.get("o"), "o_texto": v.get("o_texto"),
                    "i": v.get("i"), "i_texto": v.get("i_texto"),
                    "variacao": None if var_escrita(v) is None else round(var_escrita(v), 8),
                    "variacao_texto": v.get("variacao_texto"),
                })
            outros = [{"nome": o["nome"], "pct": o["valor_pct"], "descricao": o.get("descricao")}
                      for o in a.get("outros_componentes", []) if o.get("valor_pct") not in (None, 1)]
            total_prod = total_soma = None
            if outros:
                m = 1 + escrito / 100
                for o in outros:
                    m *= 1 + o["pct"] / 100
                total_prod, total_soma = round(100 * (m - 1), 4), round(escrito + sum(o["pct"] for o in outros), 4)

            causa = CAUSAS.get((d["processo"], str(a["doc_id"])))
            if confere and causa:
                raise SystemExit(f"{d['processo']} {a['doc_id']}: tem causa registrada mas confere")
            if not confere and not causa:
                raise SystemExit(f"{d['processo']} {a['doc_id']}: diverge sem causa registrada em CAUSAS")
            causa_out = None
            if causa:
                causa_out = {"tipo": causa["tipo"], "descricao": causa["descricao"],
                             "fonte": "docs/LEVANTAMENTO_MOTOR_CALCULO.md, seção 2"}
                if "componente_arredondado" in causa:
                    s = causa["componente_arredondado"]
                    v_of = next(var_escrita(v) for v in vals if chave(v["sigla"]) == s)
                    ir_of, _ = ir(vals, pesos, "indices", troca={s: v_of})
                    causa_out["prova"] = {
                        "componente": s, "variacao_oficial": v_of,
                        "ir_com_variacao_oficial_pct": round(ir_of, 4),
                        "fecha_com_variacao_oficial": abs(ir_of - escrito) <= tol,
                    }
            testes = [causa["teste_aceitacao"]] if causa else ["AT-01"]
            testes += OUTROS_TESTES.get(d["processo"], []) if confere else []
            casos.append({
                "id": f"{d['processo']}#{a['doc_id']}",
                "processo": d["processo"],
                "doc": str(a["doc_id"]),
                "emissor": a.get("emissor"),
                "concessionaria": d.get("concessionaria"),
                "servico": d.get("servico"),
                "tipo_formula": form.get("tipo"),
                "periodo_referencia": a.get("periodo_referencia"),
                "base_conferencia": base,
                "entradas": {"componentes": componentes, "outros_componentes": outros},
                "esperado": {
                    "ir_escrito_pct": escrito,
                    "ir_escrito_texto": a.get("ir_texto"),
                    "ir_recalculado_pct": round(ir_rec, 4),
                    "ir_pelos_indices_pct": None if ir_i is None else round(ir_i, 4),
                    "ir_pelas_variacoes_pct": None if ir_v is None else round(ir_v, 4),
                    "total_escrito_pct": a.get("reajuste_total_pct"),
                    "total_pelo_produto_pct": total_prod,
                    "total_pela_soma_pct": total_soma,
                    "regra_total": r.get("regra_total") or None,
                    # o total só é teste do motor quando fecha pelo produto; no gás ele soma resíduo judicial,
                    # tributos e custo do gás, que estão fora do escopo (01_VISAO_ESCOPO.md, seção 3)
                    "total_conferivel": bool(outros) and r.get("regra_total") == "multiplicativa",
                },
                "classificacao": "ok" if confere else "divergente",
                "causa": causa_out,
                "testes_aceitacao": testes,
            })

    casos.sort(key=lambda c: (c["processo"], c["doc"]))
    resumo = json.loads((CALCULO / "resumo.json").read_text(encoding="utf-8").replace("NaN", "null"))
    ok = sum(c["classificacao"] == "ok" for c in casos)
    if len(casos) != resumo["apuracoes_avaliadas"] or ok != resumo["conferem"]:
        raise SystemExit(f"contagens ({len(casos)} casos, {ok} ok) diferem de resumo.json "
                         f"({resumo['apuracoes_avaliadas']}, {resumo['conferem']})")
    return {
        "versao": "1",
        "descricao": ("Apurações completas da coorte do P01 (28), recalculadas pelo oráculo: entradas, IR e total "
                      "esperados e classificação. Fonte dos testes AT-01 a AT-04 de especificacao/12_TESTES.md."),
        "regra": {
            "ir_parametrica": "IR = 100 × Σ peso_k × termo_k, com termo_k = i/o − 1 (numeros_indice) ou a variação escrita (variacoes)",
            "ir_indice_unico": "IR = 100 × termo do componente principal",
            "total_pelo_produto": "100 × ((1 + IR_escrito/100) × Π (1 + outro/100) − 1)",
            "tolerancia_pp": tol,
            "classificacao": "ok se |ir_recalculado_pct − ir_escrito_pct| ≤ tolerancia_pp, sem arredondar antes",
            "base_conferencia": "numeros_indice quando todos os componentes têm i e o; senão variacoes",
            "total_conferivel": "o total só é conferido quando há outros componentes e fecha pelo produto (regra_total multiplicativa)",
        },
        "origem": {"oraculo": "scripts/recalcular_reajuste.py",
                   "arquivos": {f"saida/levantamento/calculo/{p.name}": sha256(p)
                                for p in sorted([CALCULO / "recalculo.csv", CALCULO / "resumo.json", *extracoes])}},
        "contagens": {"casos": len(casos), "ok": ok, "divergentes": len(casos) - ok},
        "casos": casos,
    }


# ---------------------------------------------------------------- ciclos, marcos e prazos

def _perfil():
    spec = importlib.util.spec_from_file_location("perfil_rj", PERFIL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pascoa(ano: int) -> date:
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    return date(ano, (h + l_ - 7 * m + 114) // 31, ((h + l_ - 7 * m + 114) % 31) + 1)


def feriados() -> set[date]:
    """Mesma regra de scripts/comum.feriados: móveis contados da Páscoa e fixos (mês, dia) do perfil."""
    p = _perfil()
    out: set[date] = set()
    for ano in p.ANOS_FERIADOS:
        out |= {_pascoa(ano) + timedelta(days=k) for k in p.FERIADOS_MOVEIS}
        out |= {date(ano, m, d) for m, d in p.FERIADOS_FIXOS}
    return out


def util(d: date, fer: set[date]) -> bool:
    return d.weekday() < 5 and d not in fer


def dias_uteis(a: date, b: date, fer: set[date]) -> int:
    """Dias úteis em [a, b): início incluído, fim excluído (semântica de numpy.busday_count usada no oráculo)."""
    n, d = 0, a
    while d < b:
        n += util(d, fer)
        d += timedelta(days=1)
    return n


def somar_du(a: date, n: int, fer: set[date]) -> date:
    """Data n dias úteis depois de a (a não útil rola para o próximo útil antes de contar)."""
    d = a
    while not util(d, fer):
        d += timedelta(days=1)
    for _ in range(n):
        d += timedelta(days=1)
        while not util(d, fer):
            d += timedelta(days=1)
    return d


def proximo_util(d: date, fer: set[date]) -> date:
    d += timedelta(days=1)
    while not util(d, fer):
        d += timedelta(days=1)
    return d


def _dia(s: str) -> date:
    return date.fromisoformat(s[:10])


def _rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


def gerar_ciclos() -> dict:
    fer = feriados()
    casos = json.loads(CASOS.read_text(encoding="utf-8"))["casos"]
    conf: dict[str, dict] = {}
    for r in csv.DictReader(CONFORMIDADE.open(encoding="utf-8-sig")):
        conf.setdefault(r["caso"], {})[r["requisito"]] = {"resultado": r["resultado"], "detalhe": r["detalhe"]}
    saida = []
    for c in sorted(casos, key=lambda x: x["numero"]):
        oc = sorted(c["ocorrencias"], key=lambda o: (o["inicio"], o["fim"], o["atividade"]))
        marcos = [{"atividade": o["atividade"], "inicio": o["inicio"][:10], "fim": o["fim"][:10]} for o in oc]
        t1 = [o for o in marcos if o["atividade"] == "t1"]
        t13 = [o for o in marcos if o["atividade"] == "t13"]
        lead = dias_uteis(_dia(t1[0]["inicio"]), _dia(t13[-1]["fim"]), fer) if t1 and t13 else None
        if c["numero"] not in conf:
            raise SystemExit(f"{c['numero']} sem linha em conformidade_P01.csv")
        saida.append({
            "processo": c["numero"],
            "encerrado": c["encerrado"],
            "marcos": marcos,
            "lead_trilha_du": c["lead_du"],
            "lead_marcos_du": lead,
            "conformidade_esperada": dict(sorted(conf[c["numero"]].items())),
        })
    if len(saida) != len(conf):
        raise SystemExit("conformidade_P01.csv tem caso fora de casos_P01.json")

    # Ciclo-piloto: vencimentos que as regras de prazo do TO-BE dariam com as datas reais (08_REGRAS_NEGOCIO.md).
    p = next(x for x in saida if x["processo"] == CICLO_PILOTO)

    def ultima(at: str, campo: str = "inicio") -> date:
        return _dia([o for o in p["marcos"] if o["atividade"] == at][-1][campo])

    protocolo = _dia(next(o for o in p["marcos"] if o["atividade"] == "t1")["inicio"])
    t2_fim, t3, t7, t8 = ultima("t2", "fim"), ultima("t3"), ultima("t7"), ultima("t8")
    t9, t9_fim, t10, t13 = ultima("t9"), ultima("t9", "fim"), ultima("t10"), ultima("t13")
    venc_recursal = somar_du(t9, 10, fer)

    def prazo(nome, req, ini, regra, dias, ato, ato_em):
        dc = (ato_em - ini).days
        return {"prazo": nome, "requisito": req, "inicio": ini.isoformat(), "regra": regra,
                "vencimento": (ini + timedelta(days=dias)).isoformat(), "ato": ato, "ato_em": ato_em.isoformat(),
                "dias_corridos": dc, "no_prazo": dc <= dias}

    prazos = [
        prazo("pronunciamento sobre o pleito", "R-P01-05", protocolo, "30 dias corridos do protocolo", 30,
              "deliberação (t8)", t8),
        prazo("parecer jurídico", "R-P01-07", t2_fim, "15 dias corridos do último parecer técnico", 15,
              "parecer jurídico (t3)", t3),
        prazo("deliberação após razões finais", "R-P01-06", t7, "40 dias corridos do último ofício de razões finais",
              40, "deliberação (t8)", t8),
        prazo("início da conferência das faturas", "R-P01-16", t9_fim, "90 dias corridos da publicação", 90,
              "conferência das faturas (t10)", t10),
        {"prazo": "razões finais", "requisito": "R-P01-20", "inicio": t7.isoformat(),
         "regra": "10 dias úteis concedidos (RN-PRZ-04); o ato seguinte só depois do vencimento",
         "vencimento": somar_du(t7, 10, fer).isoformat(), "ato": "deliberação (t8)", "ato_em": t8.isoformat(),
         "dias_corridos": (t8 - t7).days, "minimo_respeitado": t8 > somar_du(t7, 10, fer)},
        {"prazo": "prazo recursal", "requisito": "R-P01-17", "inicio": t9.isoformat(),
         "regra": "10 dias úteis da publicação da deliberação (RF-PRZ-07, M-P01-02); certidão no dia útil seguinte",
         "vencimento": venc_recursal.isoformat(), "certidao_esperada_em": proximo_util(venc_recursal, fer).isoformat(),
         "ato": "certidão de ausência de recurso (t12)", "ato_em": None, "no_prazo": False},
    ]
    # As contas de prazo do piloto têm de reproduzir o detalhe do oráculo da conformidade.
    for pr in prazos:
        det = p["conformidade_esperada"][pr["requisito"]]["detalhe"]
        if "dias_corridos" in pr and not det.startswith(f"{pr['dias_corridos']} dc"):
            raise SystemExit(f"{pr['requisito']}: {pr['dias_corridos']} dc difere do oráculo ({det})")
        cumprido = pr.get("no_prazo", pr.get("minimo_respeitado"))
        if "dias_corridos" in pr and cumprido != (p["conformidade_esperada"][pr["requisito"]]["resultado"] == "conforme"):
            raise SystemExit(f"{pr['requisito']}: resultado difere do oráculo")
    piloto = {
        "processo": CICLO_PILOTO,
        "marcos_reais": {"protocolo_t1": protocolo.isoformat(), "ultimo_parecer_tecnico_t2_fim": t2_fim.isoformat(),
                         "parecer_juridico_t3": t3.isoformat(), "razoes_finais_t7": t7.isoformat(),
                         "deliberacao_t8": t8.isoformat(), "publicacao_t9_ultima": t9.isoformat(),
                         "conferencia_faturas_t10": t10.isoformat(), "certidao_t12": None,
                         "encerramento_t13": t13.isoformat()},
        "prazos": prazos,
        "encerramento": {"lista_de_verificacao": {"certidao_ausencia_recurso": False, "conferencia_faturas": True},
                         "deve_bloquear_termo": True,
                         "motivo": "t13 sem t12 antes (R-P01-17 não conforme nos autos)"},
    }
    return {
        "versao": "1",
        "descricao": ("Marcos reais dos 18 casos da coorte do P01, conformidade esperada de cada requisito R-P01 e "
                      "vencimentos do ciclo-piloto de Paraty 2026. Fonte dos testes AT-09 em diante de "
                      "especificacao/12_TESTES.md."),
        "regra": {
            "dias_uteis": "início incluído, fim excluído; sábado, domingo e feriados de perfis/rj_agenersa.py",
            "lead_marcos_du": "dias úteis do 1º t1 ao último t13 (definição do I-P01-01); null se não há t13",
            "lead_trilha_du": ("lead do caso na trilha do SEI (abertura ao último andamento ou à data de apuração), "
                               "como em insumos/mapeamento/casos_P01.json; serve de comparação, não de definição"),
            "conformidade": "resultado de scripts/conformidade.py gravado em insumos/mapeamento/conformidade_P01.csv",
        },
        "origem": {"arquivos": {_rel(f): sha256(f) for f in (CASOS, CONFORMIDADE, PERFIL)}},
        "contagens": {"casos": len(saida), "encerrados": sum(x["encerrado"] for x in saida)},
        "ciclo_piloto": piloto,
        "casos": saida,
    }


# ---------------------------------------------------------------- pleito real de Paraty 2026 e mutações

PLEITO = RAIZ / "saida" / "levantamento" / "pleito"
CADASTRO = RAIZ / "saida" / "levantamento" / "contratos" / "paraty_008_2014.json"
SAIDA_PARATY = RAIZ / "especificacao" / "fixtures" / "paraty_2026.json"
# Mutações do AT-05: as mesmas de tests/test_regras.py (test_validador_barra_ir_errado_mes_errado_e_parcela_errada),
# escritas como JSON Patch (RFC 6902) sobre o pleito real.
MUTACOES = [
    {"id": "AT-05a", "descricao": "IR declarado diferente do recalculado",
     "patch": [{"op": "replace", "path": "/resultado_declarado/ir_pct", "value": 4.5}],
     "esperado": {"regra": "V09", "contem_situacao": "erro"}},
    {"id": "AT-05b", "descricao": "mês de referência i fora da regra do terceiro mês anterior",
     "patch": [{"op": "replace", "path": "/periodo_referencia/i", "value": "2025-09"}],
     "esperado": {"regra": "V04", "contem_situacao": "erro"}},
    {"id": "AT-05c", "descricao": "parcela de realinhamento diferente da do cronograma",
     "patch": [{"op": "replace", "path": "/resultado_declarado/outros/0/pct", "value": 6.30}],
     "esperado": {"regra": "V10", "contem_situacao": "erro"}},
    {"id": "AT-05d", "descricao": "componente sem evidência",
     "patch": [{"op": "remove", "path": "/componentes/0/evidencia"}],
     "esperado": {"regra": "V01", "situacoes_exatas": ["erro"], "para_no_v01": True}},
]


def gerar_paraty() -> dict:
    validacao = json.loads((PLEITO / "exemplo_paraty_2026.validacao.json").read_text(encoding="utf-8"))
    cont = {s: sum(x["situacao"] == s for x in validacao) for s in ("ok", "aviso", "erro")}
    if cont != {"ok": 10, "aviso": 5, "erro": 1}:  # resultado publicado em docs/ESPECIFICACAO_DADOS_PLEITO.md, seção 5
        raise SystemExit(f"validação de Paraty 2026 mudou: {cont}")
    fontes = [PLEITO / "exemplo_paraty_2026.json", PLEITO / "exemplo_paraty_2026.validacao.json", CADASTRO]
    return {
        "versao": "1",
        "descricao": ("Pleito real de Paraty 2026 no layout 0.1, cadastro do contrato 008/2014 e resultado esperado "
                      "das regras V01 a V12 (AT-06), mais as mutações do AT-05. CNPJ e hashes do pleito são fictícios."),
        "origem": {"oraculo": "scripts/validar_pleito.py", "arquivos": {_rel(f): sha256(f) for f in fontes}},
        "contagens": {"itens_validacao": len(validacao), **cont, "mutacoes": len(MUTACOES)},
        "pleito": json.loads(fontes[0].read_text(encoding="utf-8")),
        "cadastro": json.loads(CADASTRO.read_text(encoding="utf-8")),
        "validacao_esperada": validacao,
        "mutacoes": MUTACOES,
        "limites": [
            "V02 depende dos textos do contrato e dos aditivos (INT-05); sem eles o oráculo dá aviso, não ok.",
            "V07 depende das séries públicas (INT-02); o teste usa respostas gravadas do IPEADATA (MSW).",
            "V08 depende dos valores de outros pleitos (saida/levantamento/calculo/componentes.csv).",
        ],
    }


def _gravar_ou_conferir(caminho: Path, dados: dict, conferir: bool) -> bool:
    texto = json.dumps(dados, ensure_ascii=False, indent=1) + "\n"
    if conferir:
        atual = caminho.read_text(encoding="utf-8") if caminho.exists() else ""
        print(f"{_rel(caminho)} {'confere' if atual == texto else 'está desatualizado; rode sem --conferir'}")
        return atual == texto
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")
    print(f"{_rel(caminho)}: " + ", ".join(f"{k} {v}" for k, v in dados["contagens"].items()))
    return True


def main() -> None:
    conferir = "--conferir" in sys.argv
    ok = _gravar_ou_conferir(SAIDA, gerar(), conferir)
    ok = _gravar_ou_conferir(SAIDA_CICLOS, gerar_ciclos(), conferir) and ok
    ok = _gravar_ou_conferir(SAIDA_PARATY, gerar_paraty(), conferir) and ok
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
