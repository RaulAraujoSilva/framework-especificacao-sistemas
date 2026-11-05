"""Testes do caso resolvido (exemplo/reajusta): levantamento, validador do pleito e documentos para avaliação.

Garantem que o exemplo continua coerente e que os documentos gerados batem com a fonte. Rodar da raiz:
python -m pytest tests
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "exemplo" / "reajusta"
DOCS = RAIZ / "saida" / "documentos_para_avaliacao"


@pytest.fixture(autouse=True)
def _projeto_exemplo():
    import gerar_documentos as g
    g.definir_projeto(RAIZ)


# ------------------------------------------------------------------ fixtures de aceitação
def test_fixtures_conferem_com_o_levantamento():
    """Os fixtures do pacote saem do levantamento: regerar não pode mudar nada."""
    r = subprocess.run([sys.executable, "especificacao/ferramentas/gerar_fixtures.py", "--conferir"], cwd=RAIZ,
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr


def test_resumo_do_levantamento_tem_as_contagens_da_especificacao():
    resumo = json.loads((RAIZ / "saida/levantamento/calculo/resumo.json").read_text(encoding="utf-8"))
    assert resumo["numeros_indice_buscados"] == resumo["achados_na_serie_publica"] == 70


# ------------------------------------------------------------------ validador do pleito (prova de conceito)
def _pleito_paraty():
    from comum import LEVANTAMENTO, SERIES_CACHE, TEXTOS_CONTRATOS
    if not SERIES_CACHE.exists() or not TEXTOS_CONTRATOS.exists():
        pytest.skip("precisa do cache das séries públicas (dados/series) e dos textos dos contratos (TEXTOS_CONTRATOS)")
    pleito = json.loads((LEVANTAMENTO / "pleito" / "exemplo_paraty_2026.json").read_text(encoding="utf-8"))
    cadastro = json.loads((LEVANTAMENTO / "contratos" / "paraty_008_2014.json").read_text(encoding="utf-8"))
    return pleito, cadastro


def _situacao(res, regra):
    return {x["situacao"] for x in res if x["regra"] == regra}


def test_validador_aceita_o_calculo_real_de_paraty_2026():
    from validar_pleito import validar
    res = validar(*_pleito_paraty())
    assert _situacao(res, "V09") == {"ok"} and _situacao(res, "V10") == {"ok"}
    assert {x["regra"] for x in res if x["situacao"] == "erro"} == {"V11"}  # só a energia sem fonte, como no processo


def test_validador_barra_ir_errado_mes_errado_e_parcela_errada():
    from validar_pleito import validar
    pleito, cadastro = _pleito_paraty()
    p = copy.deepcopy(pleito); p["resultado_declarado"]["ir_pct"] = 4.5
    assert "erro" in _situacao(validar(p, cadastro), "V09")
    p = copy.deepcopy(pleito); p["periodo_referencia"]["i"] = "2025-09"
    assert "erro" in _situacao(validar(p, cadastro), "V04")
    p = copy.deepcopy(pleito); p["resultado_declarado"]["outros"][0]["pct"] = 6.30
    assert "erro" in _situacao(validar(p, cadastro), "V10")
    p = copy.deepcopy(pleito); del p["componentes"][0]["evidencia"]
    assert _situacao(validar(p, cadastro), "V01") == {"erro"}


def test_validacao_gravada_do_pleito_real():
    """Sem as bases locais, confere ao menos o resultado gravado: 10 ok, 5 avisos e 1 erro (energia sem fonte)."""
    res = json.loads((RAIZ / "saida/levantamento/pleito/exemplo_paraty_2026.validacao.json").read_text(encoding="utf-8"))
    itens = res["resultados"] if isinstance(res, dict) and "resultados" in res else res
    cont = {s: sum(1 for x in itens if x["situacao"] == s) for s in ("ok", "aviso", "erro")}
    assert cont == {"ok": 10, "aviso": 5, "erro": 1}


# ------------------------------------------------------------------ documentos para avaliação
def _cfg():
    return json.loads((RAIZ / "especificacao/documentos.json").read_text(encoding="utf-8"))


def test_documentos_estao_atualizados_com_a_fonte():
    """A impressão digital da fonte gravada no LEIA-ME tem de ser a da fonte atual: mudou a fonte, gere de novo."""
    import gerar_documentos as g
    leia = (RAIZ / "saida" / "LEIA-ME.md").read_text(encoding="utf-8")
    m = re.search(r"Impressão digital da fonte: `([0-9a-f]{16})`", leia)
    assert m, "LEIA-ME sem impressão digital: rode python scripts/gerar_documentos.py --projeto exemplo/reajusta"
    assert m.group(1) == g.impressao_digital(_cfg()), \
        "a fonte mudou depois da última geração: rode python scripts/gerar_documentos.py --projeto exemplo/reajusta"


def test_conjunto_completo_e_nomes_no_padrao():
    cfg = _cfg()
    esperados = {"00_Guia_de_avaliacao.pdf", "05_Planilha_de_avaliacao.xlsx", "06_Especificacao_completa.pdf",
                 "07_Prototipo_de_telas.pdf"}
    esperados |= {f'{c["arquivo"]}.pdf' for c in cfg["cadernos"]}
    esperados |= {f'capitulos/{c["arquivo"]}.pdf' for c in cfg["capitulos"]}
    existentes = {f.relative_to(DOCS).as_posix() for f in DOCS.rglob("*") if f.is_file()}
    assert esperados <= existentes, f"faltam: {sorted(esperados - existentes)}"
    assert existentes <= esperados, f"arquivo fora do conjunto definido em documentos.json: {sorted(existentes - esperados)}"
    padrao = re.compile(r"^\d{2}_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*\.(?:pdf|xlsx)$")
    assert all(padrao.match(Path(n).name) for n in existentes)


def test_leia_me_descreve_cada_arquivo_da_saida():
    leia = (RAIZ / "saida" / "LEIA-ME.md").read_text(encoding="utf-8")
    for pasta in ("documentos_para_avaliacao", "levantamento"):
        for f in (RAIZ / "saida" / pasta).rglob("*"):
            if f.is_file():
                rel = f.relative_to(RAIZ / "saida" / ("documentos_para_avaliacao" if pasta.startswith("doc") else ""))
                assert f"`{rel.as_posix()}`" in leia, f"{rel.as_posix()} sem linha no LEIA-ME"
    # toda linha do levantamento tem descrição
    for linha in leia.split("## levantamento/")[1].splitlines():
        if linha.startswith("| `"):
            assert linha.split("|")[2].strip(), f"arquivo sem descrição: {linha}"


def test_planilha_tem_cada_item_avaliavel_uma_vez_e_lista_de_parecer():
    from openpyxl import load_workbook
    import gerar_documentos as g
    wb = load_workbook(DOCS / "05_Planilha_de_avaliacao.xlsx")
    ws = wb["Itens"]
    ids = [r[2] for r in ws.iter_rows(min_row=2, values_only=True)]
    assert len(ids) == len(set(ids)) > 0
    assert ids == [i["id"] for i in g.itens_avaliaveis(_cfg())]
    validacoes = ws.data_validations.dataValidation
    assert any("Não aprovado" in (v.formula1 or "") for v in validacoes)
    assert wb["Decisões pendentes"].max_row > 1


def test_itens_da_planilha_existem_no_capitulo_dono():
    import gerar_documentos as g
    cfg = _cfg()
    por_id = {c["id"]: c for c in cfg["capitulos"]}
    textos = {cid: g.fontes(por_id[cid])[0].read_text(encoding="utf-8") for cid in set(cfg["itens_avaliaveis"].values())}
    for item in g.itens_avaliaveis(cfg):
        cid = item["documento"].split()[0]
        assert item["id"] in textos[cid]


def test_pdfs_com_versao_e_sem_caminho_local():
    fitz = pytest.importorskip("fitz")
    cfg = _cfg()
    for f in sorted(DOCS.rglob("*.pdf")):
        d = fitz.open(f)
        capa = d[0].get_text()
        assert f'Versão {cfg["versao"]}' in capa and cfg["situacao"] in capa, f.name
        texto = "".join(p.get_text() for p in d)
        assert not re.search(r"[A-Za-z]:\\Users|/Users/|AppData", texto), f.name
        assert d.get_toc(), f"{f.name} sem marcadores"


def test_exemplo_passa_na_conferencia_sem_erro():
    import conferir_especificacao as ce
    achados = ce.conferir(RAIZ, documentos=True)
    assert not [a for a in achados if a.nivel == "erro"], ce.resumo(achados)
