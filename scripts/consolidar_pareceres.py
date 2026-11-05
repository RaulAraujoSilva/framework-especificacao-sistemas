"""Junta as planilhas de avaliação devolvidas pelas áreas numa planilha consolidada, item por item.

Entrada: `saida/pareceres/recebidos/*.xlsx`, cópias preenchidas de `05_Planilha_de_avaliacao.xlsx` (nome livre; sugestão
`<Area>_<AAAA-MM-DD>.xlsx`). Saída: `saida/pareceres/00_Consolidado_dos_pareceres.xlsx`, com

- Itens: um item por linha, com a situação consolidada (o parecer mais restritivo vence: Não aprovado > Aprovado com
  ajustes > Aprovado > Não se aplica), todos os pareceres e comentários, e a coluna "Tratamento" para o autor da
  especificação registrar o que mudou (e em que versão);
- Sem parecer: itens que ninguém avaliou (cobrar antes de aprovar);
- Decisões: as decisões pendentes que alguma área registrou como tomadas;
- Resumo: contagem por situação.

Uso, da raiz deste repositório: python scripts/consolidar_pareceres.py --projeto <pasta do projeto>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path.cwd()
RECEBIDOS = RAIZ / "saida" / "pareceres" / "recebidos"
DESTINO = RAIZ / "saida" / "pareceres" / "00_Consolidado_dos_pareceres.xlsx"
MODELO = RAIZ / "saida" / "documentos_para_avaliacao" / "05_Planilha_de_avaliacao.xlsx"


def definir_projeto(pasta: Path) -> None:
    global RAIZ, RECEBIDOS, DESTINO, MODELO
    RAIZ = Path(pasta).resolve()
    RECEBIDOS = RAIZ / "saida" / "pareceres" / "recebidos"
    DESTINO = RAIZ / "saida" / "pareceres" / "00_Consolidado_dos_pareceres.xlsx"
    MODELO = RAIZ / "saida" / "documentos_para_avaliacao" / "05_Planilha_de_avaliacao.xlsx"
ORDEM = {"Não aprovado": 0, "Aprovado com ajustes": 1, "Aprovado": 2, "Não se aplica": 3}


def ler(planilha: Path) -> tuple[list[dict], list[dict]]:
    from openpyxl import load_workbook
    wb = load_workbook(planilha, read_only=True, data_only=True)
    itens, decisoes = [], []
    linhas = list(wb["Itens"].iter_rows(values_only=True))
    cab = [str(c or "").strip() for c in linhas[0]]
    for l in linhas[1:]:
        r = dict(zip(cab, l))
        if r.get("Identificador"):
            itens.append({k: ("" if v is None else str(v).strip()) for k, v in r.items()})
    if "Decisões pendentes" in wb.sheetnames:
        linhas = list(wb["Decisões pendentes"].iter_rows(values_only=True))
        cab = [str(c or "").strip() for c in linhas[0]]
        for l in linhas[1:]:
            r = {k: ("" if v is None else str(v).strip()) for k, v in zip(cab, l)}
            if r.get("Decisão tomada"):
                decisoes.append(r)
    return itens, decisoes


def consolidar(planilhas: list[Path]) -> dict:
    """{id: {...}} com a situação mais restritiva e a lista de pareceres; e as decisões registradas."""
    base: dict[str, dict] = {}
    if MODELO.exists():
        for r in ler(MODELO)[0]:
            base[r["Identificador"]] = {"titulo": r.get("Título", ""), "documento": r.get("Documento", ""),
                                        "quem": r.get("Quem avalia", ""), "pareceres": []}
    decisoes = []
    for p in planilhas:
        itens, dec = ler(p)
        for r in itens:
            item = base.setdefault(r["Identificador"], {"titulo": r.get("Título", ""), "documento": r.get("Documento", ""),
                                                        "quem": r.get("Quem avalia", ""), "pareceres": []})
            parecer = r.get("Parecer", "")
            if parecer:
                if parecer not in ORDEM:
                    raise SystemExit(f"{p.name}, {r['Identificador']}: parecer fora da lista: {parecer!r}")
                item["pareceres"].append({"arquivo": p.stem, "avaliador": r.get("Avaliador", ""), "parecer": parecer,
                                          "comentario": r.get("Ajuste pedido ou comentário", ""), "data": r.get("Data", "")})
        decisoes += [dict(d, arquivo=p.stem) for d in dec]
    for item in base.values():
        ps = item["pareceres"]
        item["situacao"] = min((x["parecer"] for x in ps), key=ORDEM.get) if ps else "Sem parecer"
    return {"itens": base, "decisoes": decisoes}


def gravar(res: dict, destino: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    def aba(wb, nome, colunas, larguras, linhas):
        w = wb.create_sheet(nome)
        w.append(colunas)
        for c in w[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="0C326F")
        for l in linhas:
            w.append(l)
        for row in w.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
        for i, lg in enumerate(larguras):
            w.column_dimensions[chr(65 + i)].width = lg
        w.freeze_panes = "A2"
        w.auto_filter.ref = w.dimensions

    itens = sorted(res["itens"].items(), key=lambda kv: (ORDEM.get(kv[1]["situacao"], 4), kv[0]))
    com = [(k, v) for k, v in itens if v["pareceres"]]
    sem = [(k, v) for k, v in itens if not v["pareceres"]]

    def texto(ps):
        return "\n".join(f'{x["arquivo"]}{" (" + x["avaliador"] + ")" if x["avaliador"] else ""}: {x["parecer"]}'
                         f'{" — " + x["comentario"] if x["comentario"] else ""}' for x in ps)

    wb = Workbook()
    wb.remove(wb.active)
    aba(wb, "Itens", ["Identificador", "Título", "Documento", "Situação consolidada", "Pareceres", "Tratamento"],
        [15, 45, 24, 20, 80, 40], [[k, v["titulo"], v["documento"], v["situacao"], texto(v["pareceres"]), ""]
                                   for k, v in com])
    aba(wb, "Sem parecer", ["Identificador", "Título", "Documento", "Quem avalia"], [15, 55, 26, 30],
        [[k, v["titulo"], v["documento"], v["quem"]] for k, v in sem])
    aba(wb, "Decisões", ["Decisão", "Quem decide", "Decisão tomada", "Responsável", "Data", "Planilha"],
        [50, 22, 50, 20, 12, 22], [[d.get("Decisão", ""), d.get("Quem decide", ""), d.get("Decisão tomada", ""),
                                    d.get("Responsável", ""), d.get("Data", ""), d["arquivo"]] for d in res["decisoes"]])
    cont: dict[str, int] = {}
    for _, v in itens:
        cont[v["situacao"]] = cont.get(v["situacao"], 0) + 1
    aba(wb, "Resumo", ["Situação", "Itens"], [26, 10],
        [[s, cont[s]] for s in sorted(cont, key=lambda s: ORDEM.get(s, 4))] + [["Total", len(itens)]])
    destino.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--projeto", default=".", help="pasta do projeto (a que contém saida/)")
    definir_projeto(Path(ap.parse_args().projeto))
    planilhas = sorted(p for p in RECEBIDOS.glob("*.xlsx") if not p.name.startswith("~$"))
    if not planilhas:
        RECEBIDOS.mkdir(parents=True, exist_ok=True)
        print(f"nenhuma planilha em {RECEBIDOS.relative_to(RAIZ).as_posix()}/ (coloque ali as planilhas devolvidas)")
        return
    res = consolidar(planilhas)
    gravar(res, DESTINO)
    cont: dict[str, int] = {}
    for v in res["itens"].values():
        cont[v["situacao"]] = cont.get(v["situacao"], 0) + 1
    print(f"{len(planilhas)} planilhas → {DESTINO.relative_to(RAIZ).as_posix()}: "
          + ", ".join(f"{k} {v}" for k, v in sorted(cont.items(), key=lambda kv: ORDEM.get(kv[0], 4))))


if __name__ == "__main__":
    main()
