"""Validador do pleito de reajuste no layout 0.1 (fase 5, prova de conceito do motor de cálculo do P01).

Recebe o pleito em JSON (saida/levantamento/pleito/pleito_reajuste.schema.json) e o cadastro de parâmetros do contrato
(saida/levantamento/contratos/<contrato>.json), e aplica as regras abaixo. Cada regra dá ok, aviso ou erro; um erro
devolve o pleito para complementação.

- V01 layout: o arquivo valida contra o JSON Schema.
- V02 cadastro: cada trecho citado no cadastro existe, literalmente, no texto do contrato ou aditivo na base do
  Especialista (espaços normalizados); a versão contratual informada existe.
- V03 interstício: pelo menos 12 meses de referência entre a tarifa em vigor e a nova (aviso se em dias < 365).
- V04 mês de referência: i e o são os meses que a regra do contrato manda (n meses antes da vigência).
- V05 componentes: as mesmas siglas e códigos de série do cadastro.
- V06 série completa: todos os meses entre o e i (aviso se só as pontas).
- V07 séries públicas: o valor de o e i aparece na série pública da fonte, com as casas escritas.
- V08 cruzada: o mesmo índice no mesmo mês tem o mesmo valor nos outros pleitos já extraídos.
- V09 recálculo: IR = Σ peso × (i/o − 1) com os pesos do cadastro, arredondado às casas do contrato.
- V10 total: a parcela de realinhamento é a do cronograma e o total fecha pela regra de combinação do cadastro.
- V11 energia: distribuidora, composição e resolução da ANEEL informadas.
- V12 tabela tarifária: proposta = vigente × (1 + total), nas casas do pleito.

Uso: python validar_pleito.py <pleito.json> <cadastro.json>  → imprime e grava <pleito>.validacao.json."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import jsonschema
import pandas as pd

from comum import SAIDA, SERIES_PUBLICAS, TEXTOS_CONTRATOS, TOL_RECALCULO_PP
from recalcular_reajuste import achado

PASTA = SAIDA / "levantamento"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def mes(s: str) -> int:
    a, m = s[:7].split("-")
    return int(a) * 12 + int(m) - 1


def txt_mes(n: int) -> str:
    return f"{n // 12}-{n % 12 + 1:02d}"


def versao(cadastro: dict, codigo: str) -> dict:
    """Versão pedida com os campos herdados das anteriores."""
    por_cod = {v["versao"]: v for v in cadastro["versoes"]}
    v = dict(por_cod[codigo])
    while "herda" in v:
        pai = dict(por_cod[v.pop("herda")])
        pai.update(v)
        v = pai
    return v


def validar(pleito: dict, cadastro: dict) -> list[dict]:
    res: list[dict] = []

    def r(regra, situacao, msg):
        res.append(dict(regra=regra, situacao=situacao, mensagem=msg))

    schema = json.loads((PASTA / "pleito" / "pleito_reajuste.schema.json").read_text(encoding="utf-8"))
    erros = sorted(jsonschema.Draft202012Validator(schema).iter_errors(pleito), key=lambda e: list(e.path))
    if erros:
        for e in erros:
            r("V01", "erro", f"{'/'.join(map(str, e.path))}: {e.message}")
        return res
    r("V01", "ok", "layout 0.1 válido")

    faltam = []
    if not TEXTOS_CONTRATOS.exists():
        r("V02", "aviso", "textos dos contratos indisponíveis nesta instalação; trechos do cadastro não conferidos")
    for v in cadastro["versoes"] if TEXTOS_CONTRATOS.exists() else []:
        for f in v.get("fontes", []):
            arq = TEXTOS_CONTRATOS / f["documento"]
            if not arq.exists() or norm(f["trecho"]) not in norm(arq.read_text(encoding="utf-8", errors="ignore")):
                faltam.append(f'{v["versao"]}:{f["parametro"]}')
    cod = pleito["contrato"]["versao_contratual"]
    if cod not in {v["versao"] for v in cadastro["versoes"]}:
        r("V02", "erro", f"versão contratual {cod} não está no cadastro")
        return res
    if TEXTOS_CONTRATOS.exists():
        r("V02", "erro" if faltam else "ok",
          f"trechos não achados na base: {faltam}" if faltam else "todos os trechos do cadastro achados no contrato e aditivos")
    v = versao(cadastro, cod)
    form = v["formula"]

    vig, ant = pleito["vigencia_pretendida"], pleito["tarifa_em_vigor"]["vigente_desde"]
    meses, dias = mes(vig) - mes(ant), (date.fromisoformat(vig) - date.fromisoformat(ant)).days
    r("V03", "erro" if meses < v["periodicidade_meses"] else "aviso" if dias < 365 else "ok",
      f"{meses} meses de referência entre {ant} e {vig} ({dias} dias)")

    n = form["mes_referencia"]["meses"]
    esperado = {"i": txt_mes(mes(vig) - n), "o": txt_mes(mes(ant) - n)}
    pr = pleito["periodo_referencia"]
    r("V04", "ok" if pr == esperado else "erro",
      f"meses informados o={pr['o']}, i={pr['i']}; a regra ({n} meses antes da vigência) dá o={esperado['o']}, i={esperado['i']}")

    cad = {c["sigla"]: c for c in form["componentes"]}
    comp = {c["sigla"]: c for c in pleito["componentes"]}
    dif = sorted(set(cad) ^ set(comp))
    cod_dif = [s for s in set(cad) & set(comp) if cad[s].get("codigo_serie") and comp[s].get("codigo_serie") != cad[s]["codigo_serie"]]
    r("V05", "erro" if dif or cod_dif else "ok",
      f"siglas a mais ou a menos: {dif}; códigos diferentes: {cod_dif}" if dif or cod_dif else "componentes e códigos iguais ao cadastro")

    valores, incompletas = {}, []
    for s, c in comp.items():
        serie = {p["mes"]: p["valor"] for p in c["serie"]}
        if pr["o"] not in serie or pr["i"] not in serie:
            r("V06", "erro", f"{s}: faltam os meses o ou i na série")
            continue
        valores[s] = (serie[pr["o"]], serie[pr["i"]])
        if len(serie) < mes(pr["i"]) - mes(pr["o"]) + 1:
            incompletas.append(s)
    r("V06", "aviso" if incompletas else "ok",
      f"só as pontas, sem os meses intermediários: {incompletas}" if incompletas else "séries mensais completas")

    casas = pleito["casas_decimais"]["indice"]
    for s, (o, i) in valores.items():
        pub = cad.get(s, {}).get("serie_publica")
        if pub in SERIES_PUBLICAS:
            # compara nas casas do próprio valor enviado; menos casas que as declaradas é arredondamento a mais
            ok = all(achado(x, repr(x).replace(".", ","), pub) for x in (o, i))
            curtos = [x for x in (o, i) if len(repr(x).split(".")[-1]) < casas]
            r("V07", "erro" if not ok else "aviso" if curtos else "ok",
              f"{s}: o={o}, i={i} {'achados' if ok else 'não achados'} em {pub}"
              + (f"; {curtos} com menos de {casas} casas, arredondado em relação à série" if ok and curtos else ""))

    outros = pd.read_csv(SAIDA / "levantamento" / "calculo" / "componentes.csv")
    for s, (o, i) in valores.items():
        codigo = cad.get(s, {}).get("codigo_serie")
        if not codigo:
            continue
        mesmo = outros[outros.codigo_serie.astype(str) == codigo]
        vistos = set(mesmo.i.dropna()) | set(mesmo.o.dropna())
        bate = [x for x in (o, i) if x in vistos]
        r("V08", "ok" if bate else "aviso",
          f"{s} ({codigo}): {len(bate)} de 2 valores iguais aos de outros pleitos extraídos"
          + ("" if bate else "; sem outro pleito do mesmo mês para comparar"))

    if len(valores) == len(cad):
        ir = 100 * sum(cad[s]["peso"] * (i / o - 1) for s, (o, i) in valores.items())
        ir_r = round(ir, form["casas_decimais_ir"])
        decl = pleito["resultado_declarado"]["ir_pct"]
        r("V09", "ok" if abs(ir_r - decl) <= TOL_RECALCULO_PP else "erro",
          f"IR recalculado {ir:.4f}% (arredondado {ir_r}%) e declarado {decl}%")

        ref = vig[:7]
        parcela = next((p for p in v.get("realinhamento", []) if p["referencia"] == ref), None)
        decl_outros = pleito["resultado_declarado"]["outros"]
        rea = next((o_ for o_ in decl_outros if o_["nome"] == "realinhamento"), None)
        if parcela and (not rea or abs(rea["pct"] - parcela["pct"]) > 1e-9):
            r("V10", "erro", f"realinhamento de {ref}: cronograma {parcela['pct']}%, declarado {rea and rea['pct']}")
        total = 1 + decl / 100
        for o_ in decl_outros:
            total *= 1 + o_["pct"] / 100
        total = 100 * (total - 1)
        t_decl = pleito["resultado_declarado"]["total_pct"]
        r("V10", "ok" if abs(total - t_decl) <= TOL_RECALCULO_PP else "erro",
          f"total pela regra {v.get('combinacao', 'multiplicativa')}: {total:.4f}%; declarado {t_decl}%"
          + (f"; parcela {parcela['parcela']} do cronograma ({parcela['pct']}%)" if parcela else ""))

    e = pleito.get("energia")
    if any(c.get("fonte") == "ANEEL" for c in cad.values()):
        lacunas = [k for k in ("distribuidora", "composicao") if not e or "não informad" in str(e.get(k, ""))]
        sem_reh = not e or any("não informad" in x["reh"] for x in e["resolucoes"])
        r("V11", "erro" if lacunas or sem_reh else "ok",
          f"energia sem {lacunas + (['resolução ANEEL'] if sem_reh else [])}" if lacunas or sem_reh
          else "energia com distribuidora, composição e resoluções")

    tab = pleito.get("tabela_tarifaria")
    if not tab:
        r("V12", "aviso", "pleito sem tabela tarifária vigente e proposta")
    else:
        k = pleito["casas_decimais"]["tarifa"]
        t_decl = pleito["resultado_declarado"]["total_pct"]
        dif = [l["categoria"] for l in tab if abs(round(l["vigente"] * (1 + t_decl / 100), k) - l["proposta"]) > 10 ** -k]
        r("V12", "erro" if dif else "ok", f"tarifas que não fecham: {dif}" if dif else f"{len(tab)} tarifas fecham")
    return res


def main(arq_pleito: str, arq_cadastro: str) -> None:
    pleito = json.loads(Path(arq_pleito).read_text(encoding="utf-8"))
    cadastro = json.loads(Path(arq_cadastro).read_text(encoding="utf-8"))
    res = validar(pleito, cadastro)
    saida = Path(arq_pleito).with_suffix(".validacao.json")
    saida.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for x in res:
        print(f'{x["regra"]} {x["situacao"]:5} {x["mensagem"]}')
    cont = pd.Series([x["situacao"] for x in res]).value_counts().to_dict()
    print("resumo:", cont, "→", "devolver para complementação" if cont.get("erro") else "segue para a CAPET")


if __name__ == "__main__":
    main(*sys.argv[1:3])
