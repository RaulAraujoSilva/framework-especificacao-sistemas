"""Testes do framework: modelos sem vestígio do caso resolvido, conferidor de rastreabilidade, iniciação de projeto,
extração de itens da planilha e consolidação dos pareceres.

Rodar da raiz: python -m pytest tests
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MODELOS = RAIZ / "modelos" / "projeto"


# ------------------------------------------------------------------ modelos
def _textos_dos_modelos():
    for f in sorted(MODELOS.rglob("*")):
        if f.is_file() and f.suffix in {".md", ".json", ".html"}:
            yield f, f.read_text(encoding="utf-8")


def test_modelos_sem_termo_do_caso_resolvido():
    import conferir_especificacao as ce
    termos = ce.termos_do_exemplo()
    achados = [f"{f.relative_to(RAIZ).as_posix()}: {t}" for f, texto in _textos_dos_modelos()
               for t, rx in termos if rx.search(texto)]
    assert not achados, "termos do exemplo nos modelos:\n" + "\n".join(achados)


def test_modelos_sem_trecho_copiado_do_caso_resolvido():
    import conferir_especificacao as ce
    janelas = ce.janelas_do_exemplo()
    achados = []
    for f, texto in _textos_dos_modelos():
        if f.suffix == ".md":
            achados += [f"{f.relative_to(RAIZ).as_posix()}: {t}" for t in ce.copias(texto, janelas)]
    assert not achados, "trechos iguais aos do exemplo nos modelos:\n" + "\n".join(achados)


def test_modelos_tem_todos_os_documentos_obrigatorios():
    import conferir_especificacao as ce
    faltam = [n for n in ce.OBRIGATORIOS if not (MODELOS / "especificacao" / n).exists()]
    assert not faltam, faltam


# ------------------------------------------------------------------ projeto sintético mínimo
DOCS_MINIMOS = {
    "01_VISAO_ESCOPO.md": """# 01. Visão

## Módulos

| ID | Módulo |
|---|---|
| MOD-ANL | Análise do pedido |

## Casos de uso

| ID | Caso de uso | Ator |
|---|---|---|
| UC-01 | Registrar pedido | PER-ANA |

## Requisitos funcionais

| ID | Requisito |
|---|---|
| RF-ANL-01 | Registrar o pedido |

## Telas

| ID | Tela |
|---|---|
| TL-01 | Fila de pedidos |
""",
    "02_PERFIS_E_JORNADAS.md": "# 02. Perfis\n\n### PER-ANA Analista\n\nAnalisa o pedido em TL-01.\n",
    "03_REQUISITOS.md": """# 03. Requisitos

### RF-ANL-01 Registrar o pedido

- **Descrição:** o sistema deve registrar o pedido com data e hora.
- **Origem:** melhoria M-X-01; atividade t1 do TO-BE.
- **Critério de aceite:**
  1. O pedido do caso 1 fica registrado com a data do protocolo, pela RN-ANL-01.
- **UC:** UC-01 · **TL:** TL-01 · **Release:** R1
""",
    "04_CASOS_DE_USO.md": """# 04. Casos de uso

```mermaid
flowchart LR
  A["PER-ANA"] --> U1(["UC-01"])
```

### UC-01 Registrar pedido

1. O analista informa o pedido (RF-ANL-01).

```mermaid
sequenceDiagram
  Analista->>Sistema: registra
```

```mermaid
stateDiagram-v2
  [*] --> Registrado: UC-01
  Registrado --> Encerrado: prazo vencido (evento de tempo)
  Encerrado --> [*]
```
""",
    "05_ARQUITETURA.md": "# 05. Arquitetura\n\n```mermaid\nflowchart LR\n  W[\"Web\"] --> D[\"Domínio\"]\n```\n",
    "06_MODELO_DADOS.md": "# 06. Dados\n\n```mermaid\nclassDiagram\n  class Pedido\n```\n",
    "07_CONTRATOS_API.md": "# 07. Contratos\n",
    "08_REGRAS_NEGOCIO.md": "# 08. Regras\n\n### RN-ANL-01 Data do protocolo\n\nA data é a do recebimento.\n",
    "09_INTEGRACOES.md": "# 09. Integrações\n",
    "10_UX_UI.md": "# 10. Interface\n",
    "11_TELAS.md": "# 11. Telas\n\n## TL-01 Fila de pedidos\n\nServe ao UC-01.\n",
    "12_TESTES.md": "# 12. Testes\n\n### AT-01 Caso 1\n\nCobre RF-ANL-01.\n",
    "13_BACKLOG.md": "# 13. Backlog\n\n| ID | História | Itens |\n|---|---|---|\n| HIS-ANL-01 | Registrar | UC-01, RF-ANL-01 |\n",
    "14_OPERACAO.md": "# 14. Operação\n",
    "15_SEGURANCA.md": "# 15. Segurança\n",
    "README.md": "# Pacote\n\n## Decisões pendentes\n\n| Decisão | Quem decide | Situação hoje |\n|---|---|---|\n",
    "AGENTS_DESENVOLVIMENTO.md": "# Instruções\n",
}


def _projeto(tmp_path: Path, alterar: dict[str, str] | None = None, cfg: dict | None = None) -> Path:
    esp = tmp_path / "proj" / "especificacao"
    esp.mkdir(parents=True)
    for nome, texto in {**DOCS_MINIMOS, **(alterar or {})}.items():
        (esp / nome).write_text(texto, encoding="utf-8")
    (esp / "documentos.json").write_text(json.dumps(cfg or {"sistema": "Teste"}), encoding="utf-8")
    return tmp_path / "proj"


def _codigos(projeto: Path, nivel: str | None = None) -> set[str]:
    import conferir_especificacao as ce
    return {a.codigo for a in ce.conferir(projeto) if nivel is None or a.nivel == nivel}


def test_projeto_minimo_coerente_passa_sem_achado(tmp_path):
    import conferir_especificacao as ce
    achados = ce.conferir(_projeto(tmp_path))
    assert not achados, [(a.codigo, a.mensagem) for a in achados]


def test_requisito_sem_origem_e_erro(tmp_path):
    texto = DOCS_MINIMOS["03_REQUISITOS.md"].replace("melhoria M-X-01; atividade t1 do TO-BE.", "—")
    assert "C06" in _codigos(_projeto(tmp_path, {"03_REQUISITOS.md": texto}), "erro")


def test_identificador_citado_sem_definicao_e_erro(tmp_path):
    texto = DOCS_MINIMOS["11_TELAS.md"] + "\nTambém abre o UC-09.\n"
    assert "C05" in _codigos(_projeto(tmp_path, {"11_TELAS.md": texto}), "erro")


def test_caso_de_uso_sem_descricao_e_tela_sem_secao_sao_erro(tmp_path):
    texto = DOCS_MINIMOS["01_VISAO_ESCOPO.md"] + "| UC-02 | Outro | PER-ANA |\n| TL-02 | Outra tela |\n"
    erros = _codigos(_projeto(tmp_path, {"01_VISAO_ESCOPO.md": texto}), "erro")
    assert {"C07", "C08"} <= erros


def test_falta_de_diagrama_de_estados_e_erro(tmp_path):
    texto = DOCS_MINIMOS["04_CASOS_DE_USO.md"].split("```mermaid\nstateDiagram-v2")[0]
    assert "C10" in _codigos(_projeto(tmp_path, {"04_CASOS_DE_USO.md": texto}), "erro")


def test_transicao_sem_evento_e_aviso(tmp_path):
    texto = DOCS_MINIMOS["04_CASOS_DE_USO.md"].replace("  Encerrado --> [*]",
                                                       "  Registrado --> Encerrado\n  Encerrado --> [*]")
    assert "C16" in _codigos(_projeto(tmp_path, {"04_CASOS_DE_USO.md": texto}), "aviso")


def test_marcador_do_modelo_e_erro(tmp_path):
    texto = DOCS_MINIMOS["14_OPERACAO.md"] + "\n{{Nome do sistema}} roda no órgão.\n"
    assert "C02" in _codigos(_projeto(tmp_path, {"14_OPERACAO.md": texto}), "erro")


def test_termo_do_exemplo_e_erro_e_pode_ser_permitido_com_justificativa(tmp_path):
    texto = DOCS_MINIMOS["02_PERFIS_E_JORNADAS.md"] + "\nO pedido de reajuste chega pelo protocolo.\n"
    assert "C03" in _codigos(_projeto(tmp_path / "a", {"02_PERFIS_E_JORNADAS.md": texto}), "erro")
    ok = {"sistema": "Teste", "termos_permitidos": {"reajuste": "o processo trata do reajuste de bolsas (Lei nº 1/2000)"}}
    assert "C03" not in _codigos(_projeto(tmp_path / "b", {"02_PERFIS_E_JORNADAS.md": texto}, ok))
    sem = {"sistema": "Teste", "termos_permitidos": {"reajuste": ""}}
    assert "C03" in _codigos(_projeto(tmp_path / "c", {"02_PERFIS_E_JORNADAS.md": texto}, sem), "erro")


def test_trecho_copiado_do_exemplo_e_aviso(tmp_path):
    import conferir_especificacao as ce
    origem = (ce.EXEMPLO / "especificacao" / "05_ARQUITETURA.md").read_text(encoding="utf-8")
    paragrafo = next(p for p in origem.split("\n\n")
                     if len(ce.palavras(p)) >= 20 and not p.lstrip().startswith(("#", "|", "`")))
    texto = DOCS_MINIMOS["05_ARQUITETURA.md"] + "\n" + paragrafo + "\n"
    assert "C04" in _codigos(_projeto(tmp_path, {"05_ARQUITETURA.md": texto}), "aviso")


def test_exemplo_declarado_nao_aplica_barreira_contra_si_mesmo(tmp_path):
    texto = DOCS_MINIMOS["02_PERFIS_E_JORNADAS.md"] + "\nO pleito chega pelo protocolo.\n"
    assert "C03" not in _codigos(_projeto(tmp_path, {"02_PERFIS_E_JORNADAS.md": texto}, {"exemplo": True}))


# ------------------------------------------------------------------ iniciação do projeto
def test_iniciar_projeto_cria_estrutura_dos_modelos_sem_vestigio_do_exemplo(tmp_path):
    import conferir_especificacao as ce
    import iniciar_projeto as ip
    destino = tmp_path / "meu-sistema"
    ip.iniciar(destino, "Sistema Teste", "ORG")
    assert (destino / "especificacao" / "documentos.json").exists()
    assert (destino / "insumos" / "LEIA-ME.md").exists()
    assert (destino / "saida" / "levantamento" / "casos").is_dir()
    assert "Sistema Teste" in (destino / "especificacao" / "documentos.json").read_text(encoding="utf-8")
    codigos = {a.codigo for a in ce.conferir(destino)}
    assert "C01" not in codigos and "C03" not in codigos and "C04" not in codigos
    assert "C02" in codigos  # marcadores a preencher


def test_iniciar_projeto_recusa_pasta_do_exemplo_e_pasta_com_conteudo(tmp_path):
    import iniciar_projeto as ip
    with pytest.raises(SystemExit):
        ip.iniciar(RAIZ / "exemplo" / "reajusta" / "novo", None, None)
    (tmp_path / "cheia").mkdir()
    (tmp_path / "cheia" / "x.txt").write_text("x")
    with pytest.raises(SystemExit):
        ip.iniciar(tmp_path / "cheia", None, None)


# ------------------------------------------------------------------ planilha e consolidação
def test_titulos_de_capitulo_com_identificador_sao_extraidos(tmp_path):
    import gerar_documentos as g
    md = "## 1. MOD-X\n\n### RF-X-01 Faz algo\n\n```\n### RF-X-02 dentro de código\n```\n| RF-X-03 Linha | texto |\n"
    (tmp_path / "especificacao").mkdir()
    (tmp_path / "especificacao" / "documentos.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cap.md").write_text(md, encoding="utf-8")
    g.definir_projeto(tmp_path)
    cfg = {"capitulos": [{"id": "99", "fonte": ["cap.md"], "arquivo": "99_X", "titulo": "X"}],
           "cadernos": [], "itens_avaliaveis": {"RF": "99"}}
    assert [i["id"] for i in g.itens_avaliaveis(cfg)] == ["RF-X-01", "RF-X-03"]


def test_consolidacao_usa_o_parecer_mais_restritivo(tmp_path, monkeypatch):
    from openpyxl import Workbook
    import consolidar_pareceres as cp
    monkeypatch.setattr(cp, "MODELO", tmp_path / "nao_existe.xlsx")
    cab = ["Documento", "Seção", "Identificador", "Tipo", "Título", "Quem avalia", "Parecer",
           "Ajuste pedido ou comentário", "Avaliador", "Data"]

    def planilha(nome, linhas):
        wb = Workbook()
        ws = wb.active
        ws.title = "Itens"
        ws.append(cab)
        for l in linhas:
            ws.append(l)
        p = tmp_path / nome
        wb.save(p)
        return p

    a = planilha("Negocio.xlsx", [["03", "", "RF-1", "", "t", "", "Aprovado", "", "A", ""],
                                  ["03", "", "RF-2", "", "t", "", "Aprovado", "", "A", ""]])
    b = planilha("Juridico.xlsx", [["03", "", "RF-1", "", "t", "", "Não aprovado", "falta base legal", "B", ""],
                                   ["03", "", "RF-2", "", "t", "", "", "", "", ""]])
    res = cp.consolidar([a, b])
    assert res["itens"]["RF-1"]["situacao"] == "Não aprovado"
    assert res["itens"]["RF-2"]["situacao"] == "Aprovado"
    assert len(res["itens"]["RF-1"]["pareceres"]) == 2
    cp.gravar(res, tmp_path / "00_Consolidado.xlsx")
    assert (tmp_path / "00_Consolidado.xlsx").exists()
