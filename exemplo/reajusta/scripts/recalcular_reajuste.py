"""Levantamento do motor de cálculo do reajuste anual (P01, fase 5): recálculo e fontes de dados.

Entrada: saida/levantamento/calculo/extracao_<processo>.json, um por processo da coorte, com a fórmula, os componentes e os
números de cada apuração (pleito, pareceres da CAPET, deliberação) copiados do texto das peças (extração por agente,
formato em scratchpad do levantamento; nenhum valor calculado na extração).

Três conferências, todas sem julgamento:
1. recálculo: IR = Σ peso × (i/o − 1) pelos números-índice escritos e pelas variações escritas; total combinado com os
   outros componentes (realinhamento, ITS, resíduo) de forma multiplicativa e aditiva — diz qual regra fecha;
2. fonte de cada componente pela regra de comum.FONTES_COMPONENTE (pública, pública com regra, assinatura, documento...);
3. busca de cada número-índice citado na série pública da sua fonte (IPEADATA, IBGE SIDRA): achado no mesmo valor
   (com as casas decimais escritas) ou não.

Saídas: saida/levantamento/calculo/recalculo.csv, componentes.csv, resumo.json."""
from __future__ import annotations

import json
import re
import sys
import urllib.request

import pandas as pd

from comum import FONTES_COMPONENTE, SAIDA, SERIES_CACHE, SERIES_PUBLICAS, TOL_RECALCULO_PP

PASTA = SAIDA / "levantamento" / "calculo"
CACHE = SERIES_CACHE


def chave(sigla: str) -> str:
    return re.split(r"[\s(]", sigla.strip())[0].upper()


def var_escrita(v: dict):
    x = v.get("variacao")
    if x is None:
        return None
    return x - 1 if x > 0.5 else x  # razão i/o escrita como 1,065231


def ir_de(vals, pesos, modo):
    """IR em % e quantos componentes ficaram sem número para o modo pedido."""
    termos, faltam = [], 0
    for v in vals:
        if modo == "indices":
            x = v["i"] / v["o"] - 1 if v.get("i") is not None and v.get("o") else None
        else:
            x = var_escrita(v)
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


def fonte(componente: dict) -> tuple[str, str]:
    # só a parte antes do primeiro parêntese: "IPCA (substituiu o IPA-OG-DI...)" é IPCA
    texto = f'{componente.get("sigla", "")} {str(componente.get("indice") or "").split("(")[0]}'
    for padrao, disp, onde in FONTES_COMPONENTE:
        if re.search(padrao, texto):
            return disp, onde
    return "a definir", ""


def serie(nome: str) -> list[float]:
    """Valores da série pública (todos os meses), com cache local."""
    CACHE.mkdir(parents=True, exist_ok=True)
    arq = CACHE / (re.sub(r"\W+", "_", nome) + ".json")
    if not arq.exists():
        tipo, cod = SERIES_PUBLICAS[nome]
        url = (f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{cod}')" if tipo == "ipeadata"
               else f"https://apisidra.ibge.gov.br/values/t/{cod}/p/all")
        with urllib.request.urlopen(url, timeout=120) as r:
            bruto = json.load(r)
        vals = ([x["VALVALOR"] for x in bruto["value"]] if tipo == "ipeadata"
                else [float(x["V"]) for x in bruto[1:] if x["V"] not in ("...", "-", "X")])
        arq.write_text(json.dumps(vals), encoding="utf-8")
    return json.loads(arq.read_text(encoding="utf-8"))


def casas(texto) -> int:
    t = str(texto or "").strip()
    return len(re.split(r",", t)[-1]) if "," in t else 0


def achado(valor, texto, nome) -> bool | None:
    if valor is None or nome not in SERIES_PUBLICAS:
        return None
    n = casas(texto)
    tol = 0.5 * 10 ** -n + 1e-9 if n else 0.5
    return any(abs(s - valor) <= tol for s in serie(nome))


def main(offline: bool = False) -> None:
    linhas, comps = [], []
    for f in sorted(PASTA.glob("extracao_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        form = d.get("formula") or {}
        cdef = {chave(c["sigla"]): c for c in form.get("componentes", []) if c.get("sigla")}
        pesos = {k: c.get("peso") for k, c in cdef.items()}
        for a in d.get("apuracoes", []):
            vals = a.get("valores") or []
            if not vals:
                continue
            ir_i, falta_i = ir_de(vals, pesos, "indices")
            ir_v, falta_v = ir_de(vals, pesos, "variacoes")
            e, t = a.get("ir_pct"), a.get("reajuste_total_pct")
            n_esperado = max(len(pesos) - (1 if form.get("tipo") == "índice único" else 0), 1)
            completa = len(vals) >= n_esperado and min(falta_i, falta_v) == 0
            r = dict(processo=d["processo"], concessionaria=d.get("concessionaria"), servico=d.get("servico"),
                     tipo_formula=form.get("tipo"), doc=a.get("doc_id"), emissor=a.get("emissor"),
                     periodo=a.get("periodo_referencia"), completa=completa, ir_escrito=e,
                     ir_pelos_indices=None if ir_i is None else round(ir_i, 4),
                     ir_pelas_variacoes=None if ir_v is None else round(ir_v, 4))
            r["confere_indices"] = None if e is None or ir_i is None or falta_i else abs(ir_i - e) <= TOL_RECALCULO_PP
            r["confere_variacoes"] = None if e is None or ir_v is None or falta_v else abs(ir_v - e) <= TOL_RECALCULO_PP
            r["confere"] = (None if not completa or e is None else
                            bool(r["confere_indices"]) if r["confere_indices"] is not None else bool(r["confere_variacoes"]))
            outros = [o["valor_pct"] for o in a.get("outros_componentes", []) if o.get("valor_pct") not in (None, 1)]
            r["total_escrito"] = t
            if outros and t is not None and e is not None:
                mult = 1 + e / 100
                for x in outros:
                    mult *= 1 + x / 100
                mult, adit = 100 * (mult - 1), e + sum(outros)
                r["regra_total"] = ("multiplicativa" if abs(mult - t) <= TOL_RECALCULO_PP else
                                    "aditiva" if abs(adit - t) <= TOL_RECALCULO_PP else "não fecha")
            linhas.append(r)
            for v in vals:
                c = cdef.get(chave(v["sigla"]), {"sigla": v["sigla"]})
                disp, onde = fonte(c)
                nome = next((n for n in SERIES_PUBLICAS if onde.startswith(n)), None)
                comps.append(dict(processo=d["processo"], doc=a.get("doc_id"), emissor=a.get("emissor"),
                                  sigla=v["sigla"], componente=chave(v["sigla"]), indice=c.get("indice"), codigo_serie=c.get("codigo_serie"),
                                  disponibilidade=disp, fonte=onde, i=v.get("i"), o=v.get("o"),
                                  i_na_serie=None if offline else achado(v.get("i"), v.get("i_texto"), nome),
                                  o_na_serie=None if offline else achado(v.get("o"), v.get("o_texto"), nome)))
    rec, cp = pd.DataFrame(linhas), pd.DataFrame(comps)
    rec.to_csv(PASTA / "recalculo.csv", index=False, encoding="utf-8-sig")
    cp.to_csv(PASTA / "componentes.csv", index=False, encoding="utf-8-sig")
    avaliadas = rec[rec.confere.notna()]
    busca = cp.melt(value_vars=["i_na_serie", "o_na_serie"]).dropna()
    resumo = dict(
        processos=int(rec.processo.nunique()), apuracoes_com_valores=len(rec), apuracoes_avaliadas=len(avaliadas),
        conferem=int(avaliadas.confere.sum()),
        divergem=avaliadas[~avaliadas.confere.astype(bool)][["processo", "doc", "emissor", "ir_escrito",
                                                              "ir_pelos_indices", "ir_pelas_variacoes"]].to_dict("records"),
        tipos_formula=rec.drop_duplicates("processo").tipo_formula.value_counts().to_dict(),
        regra_total=rec.regra_total.value_counts().to_dict() if "regra_total" in rec else {},
        componentes_por_disponibilidade=cp.drop_duplicates(["processo", "componente"]).disponibilidade.value_counts().to_dict(),
        numeros_indice_buscados=len(busca), achados_na_serie_publica=int(busca.value.sum()),
    )
    (PASTA / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(offline="--offline" in sys.argv)
