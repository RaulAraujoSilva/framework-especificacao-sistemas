"""Gera as versões de leitura do pacote de especificação e o índice da pasta de saída.

O pacote técnico (`especificacao/*.md`, ADRs, relatórios do levantamento) é a fonte única. Este script não muda a
fonte: só a lê e escreve, em `saida/documentos_para_avaliacao/`,

- `00_Guia_de_avaliacao.pdf`: o que avaliar, quem avalia, como registrar o parecer, decisões pendentes, lista de arquivos;
- `01` a `04_Caderno_<público>.pdf`: os capítulos que cada público avalia, com as perguntas a responder na capa;
- `05_Planilha_de_avaliacao.xlsx`: um item avaliável por linha (RF, RNF, UC, RN, TL, AT, HIS, SEG, DEC...) com parecer;
- `06_Especificacao_completa.pdf`: todos os capítulos em ordem;
- `07_Prototipo_de_telas.pdf`: uma tela do protótipo por página;
- `capitulos/NN_<nome>.pdf`: um PDF por capítulo;

e `saida/LEIA-ME.md`, o índice da pasta de saída (cada arquivo, o que é e para quem).

O que vira documento, para quem e com que nome está em `especificacao/documentos.json`. Diagramas Mermaid são
desenhados no navegador (Chromium do Playwright) e impressos como vetor.

Uso, da raiz do repositório:
    python scripts/gerar_documentos.py            # gera tudo
    python scripts/gerar_documentos.py --rapido   # só guia, planilha e LEIA-ME (sem PDFs de capítulo e cadernos)

Portões (o script para com erro): fonte inexistente, caminho local da máquina no texto, diagrama que não desenhou,
nome de arquivo fora do padrão e os termos bloqueados de `documentos.json` (por padrão, frases que dizem que o
documento foi feito por IA). Nome de ferramenta de IA e menção a IA ou a modelo de linguagem dão só aviso: quando é
função do sistema (minuta assistida, provedor do modelo), fica; quando comenta como o documento foi feito, sai da fonte.

Precisa de: markdown-it-py, openpyxl, playwright (`python -m playwright install chromium`) e acesso à rede na geração
(fonte tipográfica e biblioteca Mermaid).
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import fnmatch
import html
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from markdown_it import MarkdownIt

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = RAIZ / "especificacao" / "documentos.json"
SAIDA = RAIZ / "saida"
DESTINO = SAIDA / "documentos_para_avaliacao"

MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@12.2.0/dist/mermaid.min.js"
MERMAID_SRI = "sha384-8xUhuLNMjW/cI2Dacg3DR4WliYznvIg0LVG1stctThKD/YVrJFI9TNCFxft5NYgp"
FONTES = ("https://fonts.googleapis.com/css2?family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400"
          "&family=JetBrains+Mono:wght@400;600&display=swap")

NOME_ARQUIVO = re.compile(r"^\d{2}_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*\.(?:pdf|xlsx)$")
CAMINHO_LOCAL = re.compile(r"(?:\b[A-Za-z]:[\\/](?:Users|Documents|Program)|/Users/|/home/|\\Users\\|AppData)")
AVISO_IA = re.compile(r"\b(?:IA|intelig[eê]ncia artificial|LLM|modelo de linguagem|Claude|ChatGPT|Codex|Copilot|"
                      r"Gemini|Anthropic|OpenAI)\b")
BLOQUEADOS: list[re.Pattern] = []  # "termos_bloqueados" de documentos.json

PARECERES = ["Aprovado", "Aprovado com ajustes", "Não aprovado", "Não se aplica"]
PREFIXOS = {
    "RF": "Requisito funcional", "RNF": "Requisito não funcional", "UC": "Caso de uso", "RN": "Regra de negócio",
    "DEC": "Decisão de negócio pendente", "INT": "Integração", "TL": "Tela", "AT": "Teste de aceitação",
    "HIS": "História do backlog", "SEG": "Requisito de segurança", "ADR": "Decisão de arquitetura registrada",
    "MOD": "Módulo do sistema", "PER": "Perfil de usuário", "CMP": "Componente de interface",
    "V01 a V12": "Regras de validação do pleito",
}


# ---------------------------------------------------------------- configuração e fonte
def ler_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def fontes(cap: dict) -> list[Path]:
    arqs: list[Path] = []
    for padrao in cap["fonte"]:
        achados = sorted(RAIZ.glob(padrao)) if any(c in padrao for c in "*?[") else [RAIZ / padrao]
        for a in achados:
            if not a.exists():
                raise SystemExit(f"fonte inexistente no capítulo {cap['id']}: {padrao}")
            arqs.append(a)
    if not arqs:
        raise SystemExit(f"capítulo {cap['id']} sem fonte")
    return arqs


def rebaixar_titulos(md: str, niveis: int) -> str:
    """Desce cada título `#` em `niveis` níveis, fora de blocos de código."""
    out, em_codigo = [], False
    for linha in md.splitlines():
        if linha.lstrip().startswith("```"):
            em_codigo = not em_codigo
        if not em_codigo and re.match(r"^#{1,6} ", linha):
            linha = "#" * niveis + linha
        out.append(linha)
    return "\n".join(out)


def texto_do_capitulo(cap: dict) -> list[tuple[Path, str]]:
    """Primeiro arquivo com o título do capítulo trocado pelo de documentos.json (o mesmo do nome do arquivo e do
    sumário); os demais (ex.: ADRs) viram anexo com títulos rebaixados."""
    arqs = fontes(cap)
    texto = re.sub(r"\A(?:\s*\n)*# [^\n]*", f'# {cap["id"]}. {cap["titulo"]}', arqs[0].read_text(encoding="utf-8"), 1)
    partes = [(arqs[0], texto)]
    if len(arqs) > 1:
        partes.append((arqs[0], "\n## Anexo: decisões registradas\n"))
        partes += [(a, rebaixar_titulos(a.read_text(encoding="utf-8"), 2)) for a in arqs[1:]]
    return partes


# ---------------------------------------------------------------- Markdown → HTML
def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60] or "secao"


def texto_simples(md_inline: str) -> str:
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md_inline)
    return re.sub(r"[`*]", "", t).strip()


@dataclass
class Render:
    html: str
    titulos: list[tuple[int, str, str]] = field(default_factory=list)  # (nível, texto, id)
    diagramas: int = 0


class Conversor:
    """Converte Markdown do pacote em HTML de impressão, com âncoras próprias e links resolvidos."""

    def __init__(self, capitulos: list[dict], incluidos: set[str]):
        self.mapa = {}  # caminho absoluto da fonte principal → capítulo
        for c in capitulos:
            self.mapa[fontes(c)[0].resolve()] = c
        self.incluidos = incluidos  # capítulos presentes neste documento (link vira âncora interna)
        self.md = MarkdownIt("commonmark", {"html": True, "typographer": False}).enable("table")
        self.md.add_render_rule("fence", self._fence)

    @staticmethod
    def _fence(self_r, tokens, idx, options, env):
        t = tokens[idx]
        if t.info.strip() == "mermaid":
            env["diagramas"] = env.get("diagramas", 0) + 1
            return f'<div class="diagrama"><pre class="mermaid">{html.escape(t.content)}</pre></div>\n'
        return f"<pre><code>{html.escape(t.content)}</code></pre>\n"

    def _destino(self, href: str, base: Path):
        """Classifica um link: ('manter', href) | ('interno', '#cap-NN') | ('texto', sufixo)."""
        if re.match(r"^(?:https?:|mailto:)", href):
            return "manter", href
        if href.startswith("#"):
            return "texto", ""  # âncora do Markdown original: os ids aqui são outros
        alvo = (base.parent / href.split("#")[0]).resolve()
        cap = self.mapa.get(alvo)
        if cap and cap["id"] in self.incluidos:
            return "interno", f"#cap-{cap['id']}"
        if cap:
            return "texto", f" (documento {cap['id']}, {cap['titulo']})"
        return "texto", ""

    def converter(self, md_texto: str, base: Path, prefixo: str, usados: set[str]) -> Render:
        env: dict = {}
        tokens = self.md.parse(md_texto, env)
        titulos = []
        for i, t in enumerate(tokens):
            if t.type == "heading_open":
                texto = texto_simples(tokens[i + 1].content)
                hid, k = f"{prefixo}-{slug(texto)}", 2
                while hid in usados:
                    hid, k = f"{prefixo}-{slug(texto)}-{k}", k + 1
                usados.add(hid)
                t.attrSet("id", hid)
                titulos.append((int(t.tag[1]), texto, hid))
            if t.type == "inline" and t.children:
                t.children = self._links(t.children, base)
        corpo = self.md.renderer.render(tokens, self.md.options, env)
        return Render(corpo, titulos, env.get("diagramas", 0))

    def _links(self, filhos, base: Path):
        from markdown_it.token import Token
        novos, pilha = [], []
        for c in filhos:
            if c.type == "link_open":
                acao, valor = self._destino(c.attrGet("href") or "", base)
                pilha.append((acao, valor))
                if acao == "manter":
                    novos.append(c)
                elif acao == "interno":
                    c.attrSet("href", valor)
                    novos.append(c)
                continue
            if c.type == "link_close":
                acao, valor = pilha.pop() if pilha else ("manter", "")
                if acao in ("manter", "interno"):
                    novos.append(c)
                elif valor:
                    t = Token("text", "", 0)
                    t.content = valor
                    novos.append(t)
                continue
            novos.append(c)
        return novos


# ---------------------------------------------------------------- página HTML de impressão
CSS = """
@page { size: A4; margin: 20mm 16mm 18mm 16mm; }
:root { --tinta:#17202b; --suave:#4d5866; --linha:#c3ccd8; --fundo:#eef2f7; --marca:#1351b4; --marca-esc:#0c326f; }
* { box-sizing: border-box; }
html { font-family: 'Public Sans', 'Segoe UI', Arial, sans-serif; font-size: 10pt; color: var(--tinta); line-height: 1.45; }
body { margin: 0; }
h1, h2, h3, h4, h5 { color: var(--marca-esc); line-height: 1.25; break-after: avoid; page-break-after: avoid; }
h1 { font-size: 20pt; margin: 0 0 10pt; padding-bottom: 6pt; border-bottom: 2pt solid var(--marca); }
h2 { font-size: 14pt; margin: 18pt 0 6pt; }
h3 { font-size: 11.5pt; margin: 14pt 0 4pt; }
h4, h5 { font-size: 10.5pt; margin: 12pt 0 4pt; }
p, li { orphans: 3; widows: 3; }
a { color: var(--marca); text-decoration: none; }
code { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 8.3pt; background: var(--fundo); padding: 0 2pt; border-radius: 2pt; overflow-wrap: anywhere; }
pre { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 7.8pt; background: var(--fundo); padding: 6pt 8pt; border-radius: 3pt; white-space: pre-wrap; overflow-wrap: anywhere; }
pre code { background: none; padding: 0; font-size: inherit; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; font-size: 8.4pt; }
thead { display: table-header-group; }
tr { break-inside: avoid; page-break-inside: avoid; }
th { background: #dde6f2; color: var(--marca-esc); text-align: left; font-weight: 700; }
th, td { border: 0.6pt solid var(--linha); padding: 3pt 4pt; vertical-align: top; overflow-wrap: break-word; }
tbody tr:nth-child(even) td { background: #f7f9fc; }
blockquote { margin: 8pt 0; padding: 4pt 10pt; border-left: 3pt solid var(--marca); background: var(--fundo); }
.diagrama { margin: 8pt 0 12pt; text-align: center; break-inside: avoid; page-break-inside: avoid; }
.diagrama svg { max-width: 100% !important; height: auto; max-height: 225mm; }
.capa { height: 252mm; display: flex; flex-direction: column; page-break-after: always; }
.capa .faixa { background: var(--marca-esc); color: #fff; padding: 14pt 16pt; border-radius: 4pt; }
.capa .orgao { font-size: 10pt; letter-spacing: .08em; text-transform: uppercase; opacity: .85; }
.capa .pacote { font-size: 12pt; margin-top: 4pt; }
.capa .titulo { font-size: 28pt; font-weight: 700; line-height: 1.15; color: var(--marca-esc); margin: 46pt 0 6pt; }
.capa .sub { font-size: 12pt; color: var(--suave); margin: 0 0 22pt; }
.capa table.ficha { width: auto; font-size: 9.5pt; margin-bottom: 18pt; }
.capa table.ficha th { width: 42mm; background: var(--fundo); }
.capa table.ficha td { min-width: 80mm; background: #fff; }
.caixa { border: 1pt solid var(--marca); border-radius: 4pt; padding: 8pt 12pt; background: #f3f7fd; break-inside: avoid; }
.caixa-titulo { font-size: 11pt; font-weight: 700; color: var(--marca-esc); margin: 0 0 4pt; }
.caixa ol, .caixa ul { margin: 2pt 0 0; padding-left: 16pt; }
.capa .rodape-capa { margin-top: auto; font-size: 8.5pt; color: var(--suave); border-top: .6pt solid var(--linha); padding-top: 6pt; }
.selo { display: inline-block; font-size: 8.5pt; font-weight: 700; color: #7a4b00; background: #fff3d6; border: .8pt solid #e0a92e; border-radius: 10pt; padding: 1pt 8pt; }
nav.sumario { page-break-after: always; }
nav.sumario h2 { margin-top: 0; }
nav.sumario ol { list-style: none; padding-left: 0; margin: 0; }
nav.sumario li { margin: 2pt 0; }
nav.sumario li.n1 { font-weight: 700; margin-top: 7pt; }
nav.sumario li.n2 { padding-left: 12pt; }
nav.sumario.longo ol { columns: 2; column-gap: 10mm; font-size: 8.8pt; }
section.capitulo { page-break-before: always; }
section.capitulo:first-of-type { page-break-before: auto; }
.tela { page-break-after: always; text-align: center; }
.tela img { max-width: 100%; max-height: 150mm; border: .6pt solid var(--linha); }
body.paisagem .capa { height: 168mm; }
body.paisagem .capa .titulo { margin-top: 18pt; }
body.paisagem .capa .sub { margin-bottom: 10pt; }
.tela h2 { text-align: left; }
"""


def cabecalho_rodape(cfg: dict, titulo_doc: str, data: str) -> tuple[str, str]:
    estilo = ("width:100%;font-size:7.5pt;color:#4d5866;padding:0 16mm;display:flex;justify-content:space-between;"
              "font-family:Arial,sans-serif")
    e = html.escape
    cab = (f'<div style="{estilo}"><span>{e(cfg["orgao"])} · {e(cfg["titulo_pacote"])}</span>'
           f'<span>{e(titulo_doc)}</span></div>')
    rod = (f'<div style="{estilo}"><span>Versão {e(cfg["versao"])} · {e(data)} · {e(cfg["situacao"])}</span>'
           '<span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span></div>')
    return cab, rod


def capa(cfg: dict, data: str, titulo: str, subtitulo: str, publico: str, leitura: str, caixa_html: str) -> str:
    e = html.escape
    linhas = [("Sistema", f'{cfg["sistema"]}: {cfg["subtitulo"]}'), ("Versão", cfg["versao"]), ("Data", data),
              ("Situação", cfg["situacao"]), ("Para quem", publico), ("Leitura estimada", leitura)]
    ficha = "".join(f"<tr><th>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in linhas if b)
    return (f'<section class="capa"><div class="faixa"><div class="orgao">{e(cfg["orgao"])}</div>'
            f'<div class="pacote">{e(cfg["titulo_pacote"])}</div></div>'
            f'<div class="titulo">{e(titulo)}</div><p class="sub">{e(subtitulo)}</p>'
            f'<p><span class="selo">{e(cfg["situacao"])}: não é versão aprovada</span></p>'
            f'<table class="ficha">{ficha}</table>{caixa_html}'
            f'<div class="rodape-capa">Documento gerado a partir do pacote de especificação versão {e(cfg["versao"])}. '
            f'Os números citados saem dos registros dos processos e são reproduzíveis. Horas e custos são hipótese até a '
            f'calibração com os servidores.</div></section>')


def sumario(titulos: list[tuple[int, str, str]], niveis=(1, 2), longo=False) -> str:
    itens = "".join(f'<li class="n{n}"><a href="#{i}">{html.escape(t)}</a></li>'
                    for n, t, i in titulos if n in niveis)
    return f'<nav class="sumario{" longo" if longo else ""}"><h2>Sumário</h2><ol>{itens}</ol></nav>'


def pagina(titulo: str, corpo: str, paisagem: bool = False) -> str:
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(titulo)}</title>'
            f'<link rel="stylesheet" href="{FONTES}"><style>{CSS}</style>'
            f'<script src="{MERMAID_URL}" integrity="{MERMAID_SRI}" crossorigin="anonymous"></script>'
            f'{"<style>@page { size: A4 landscape; }</style>" if paisagem else ""}'
            f'</head><body{" class=paisagem" if paisagem else ""}>{corpo}</body></html>')


def palavras(texto: str) -> int:
    return len(re.findall(r"\w+", texto))


def leitura(n_palavras: int, ppm: int) -> str:
    minutos = max(5, round(n_palavras / ppm / 5) * 5)
    return f"{minutos} min" if minutos < 60 else f"{minutos // 60} h {minutos % 60:02d} min".replace(" 00 min", "")


# ---------------------------------------------------------------- impressão
class Impressora:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        try:
            self.nav = self._pw.chromium.launch()
        except Exception:
            self.nav = self._pw.chromium.launch(channel="chrome")
        self.pagina = self.nav.new_page()

    def pdf(self, html_doc: str, destino: Path, cab: str, rod: str, diagramas: int, paisagem: bool = False,
            avisar: bool = True) -> None:
        p = self.pagina
        p.set_content(html_doc, wait_until="networkidle", timeout=120_000)
        desenhados = p.evaluate("""async () => {
            if (window.mermaid) {
              mermaid.initialize({startOnLoad: false, theme: 'neutral', securityLevel: 'strict',
                                  fontFamily: 'Public Sans, Arial, sans-serif'});
              await mermaid.run({querySelector: '.mermaid', suppressErrors: true});
            }
            await document.fonts.ready;
            return document.querySelectorAll('.mermaid svg').length;
        }""")
        if desenhados != diagramas:
            raise SystemExit(f"{destino.name}: {desenhados} de {diagramas} diagramas desenhados "
                             "(sem rede para a biblioteca Mermaid, ou diagrama com erro de sintaxe)")
        texto = p.evaluate("document.body.innerText")
        portao_texto(destino.name, texto, avisar)
        destino.parent.mkdir(parents=True, exist_ok=True)
        opcoes = dict(path=str(destino), format="A4", landscape=paisagem, print_background=True, display_header_footer=True,
                      header_template=cab, footer_template=rod,
                      margin={"top": "20mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
        try:
            p.pdf(**opcoes, outline=True, tagged=True)
        except TypeError:  # Playwright antigo: sem marcadores nem PDF marcado
            p.pdf(**opcoes)

    def capturas(self, arquivo: Path, altura: int = 740) -> list[tuple[str, str, int, bytes]]:
        """Capturas de cada tela do protótipo (seções com data-tela), na largura de desktop. Tela mais alta que uma
        página paisagem vira várias capturas de `altura` pixels, para não encolher o texto."""
        p = self.nav.new_page(viewport={"width": 1280, "height": 800})
        p.goto(arquivo.resolve().as_uri(), wait_until="networkidle")
        telas = p.evaluate("[...document.querySelectorAll('section[data-tela]')].map(s => [s.dataset.tela, s.dataset.titulo || ''])")
        out = []
        for tid, titulo in telas:
            p.evaluate("""(t) => { location.hash = t;
                document.querySelectorAll('section[data-tela]').forEach(s => s.hidden = (s.dataset.tela !== t)); }""", tid)
            p.wait_for_timeout(150)
            # até o fim da tela (o menu lateral, mais comprido, é cortado), mais o rodapé da página
            total = p.evaluate("""(t) => { const s = document.querySelector(`section[data-tela="${t}"]`);
                const fim = s.getBoundingClientRect().bottom + window.scrollY + 24;
                return Math.ceil(Math.min(fim, document.documentElement.scrollHeight)); }""", tid)
            for parte, y in enumerate(range(0, total, altura)):
                if parte and total - y < 160:  # sobra pequena: não vale uma página
                    break
                clip = {"x": 0, "y": y, "width": 1280, "height": min(altura, total - y)}
                out.append((tid, titulo, parte, p.screenshot(full_page=True, clip=clip)))
        p.close()
        return out

    def fechar(self):
        self.nav.close()
        self._pw.stop()


AVISOS: list[str] = []


def portao_texto(nome: str, texto: str, avisar: bool = True) -> None:
    m = CAMINHO_LOCAL.search(texto)
    if m:
        raise SystemExit(f"{nome}: caminho local da máquina no texto: {texto[max(0, m.start() - 40):m.end() + 40]!r}")
    for b in BLOQUEADOS:
        m = b.search(texto)
        if m:
            raise SystemExit(f"{nome}: termo bloqueado: {texto[max(0, m.start() - 60):m.end() + 60]!r}")
    achados = AVISO_IA.findall(texto)
    if achados and avisar:  # cadernos repetem os capítulos: o aviso sai só uma vez, no capítulo
        cont = ", ".join(f"{k} {achados.count(k)}" for k in sorted(set(achados)))
        AVISOS.append(f"{nome}: menções a revisar ({cont})")


# ---------------------------------------------------------------- documentos
def montar(cfg: dict, conv: Conversor, caps: list[dict]) -> tuple[str, list, int, int]:
    """HTML dos capítulos em ordem: (corpo, títulos, diagramas, palavras)."""
    corpo, titulos, diag, pal, usados = [], [], 0, 0, set()
    for cap in caps:
        blocos, prefixo = [], f"c{cap['id']}"
        for base, texto in texto_do_capitulo(cap):
            r = conv.converter(texto, base, prefixo, usados)
            blocos.append(r.html)
            titulos += r.titulos
            diag += r.diagramas
            pal += palavras(texto)
        corpo.append(f'<section class="capitulo" id="cap-{cap["id"]}">{"".join(blocos)}</section>')
    return "".join(corpo), titulos, diag, pal


def caixa_avaliacao(perguntas: list[str], planilha: str) -> str:
    itens = "".join(f"<li>{html.escape(q)}</li>" for q in perguntas)
    return (f'<div class="caixa"><div class="caixa-titulo">O que avaliar</div><ol>{itens}</ol>'
            f'<p style="margin:6pt 0 0">Registre o parecer na planilha <b>{html.escape(planilha)}</b>, uma linha por '
            'item (filtre pela coluna “Quem avalia”). Ajuste pedido vai escrito, com o identificador do item.</p></div>')


def gerar_pdfs(cfg: dict, imp: Impressora, data: str, planilha: str) -> dict[str, dict]:
    caps = cfg["capitulos"]
    por_id = {c["id"]: c for c in caps}
    ppm = cfg.get("palavras_por_minuto", 150)
    info: dict[str, dict] = {}

    # um PDF por capítulo
    for cap in caps:
        conv = Conversor(caps, {cap["id"]})
        corpo, titulos, diag, pal = montar(cfg, conv, [cap])
        publico = "; ".join(cd["publico"] for cd in cfg["cadernos"] if cap["id"] in cd["capitulos"]) or "Todos"
        caixa = caixa_avaliacao(["Os itens deste capítulo estão corretos e completos?",
                                 "Falta alguma regra, caso ou exceção que a sua área conhece?"], planilha)
        doc = capa(cfg, data, f'{cap["id"]}. {cap["titulo"]}', "Capítulo do pacote de especificação", publico,
                   leitura(pal, ppm), caixa) + sumario(titulos, (2,)) + corpo
        destino = DESTINO / "capitulos" / f'{cap["arquivo"]}.pdf'
        cab, rod = cabecalho_rodape(cfg, f'{cap["id"]}. {cap["titulo"]}', data)
        imp.pdf(pagina(cap["titulo"], doc), destino, cab, rod, diag)
        info[f"capitulos/{destino.name}"] = {"o_que": f'Capítulo {cap["id"]}: {cap["titulo"]}', "para_quem": publico,
                              "leitura": leitura(pal, ppm)}
        print(f"  {destino.relative_to(RAIZ).as_posix()}")

    # cadernos por público e especificação completa
    conjuntos = [(cd["arquivo"], cd["titulo"], cd["publico"], cd["o_que_avaliar"], cd["capitulos"])
                 for cd in cfg["cadernos"]]
    conjuntos.append(("06_Especificacao_completa", "Especificação completa", "Todos os avaliadores e a equipe de "
                      "desenvolvimento", ["Os capítulos são coerentes entre si (mesmos identificadores, nomes e números)?"],
                      [c["id"] for c in caps]))
    for arquivo, titulo, publico, perguntas, ids in conjuntos:
        sel = [por_id[i] for i in ids]
        conv = Conversor(caps, set(ids))
        corpo, titulos, diag, pal = montar(cfg, conv, sel)
        lista = "; ".join(f'{c["id"]} {c["titulo"]}' for c in sel)
        doc = capa(cfg, data, titulo, f"Capítulos: {lista}", publico, leitura(pal, ppm),
                   caixa_avaliacao(perguntas, planilha)) + sumario(titulos, (1, 2), longo=len(sel) > 6) + corpo
        destino = DESTINO / f"{arquivo}.pdf"
        cab, rod = cabecalho_rodape(cfg, titulo, data)
        imp.pdf(pagina(titulo, doc), destino, cab, rod, diag, avisar=False)
        info[destino.name] = {"o_que": f"{titulo} (capítulos {', '.join(ids)})", "para_quem": publico,
                              "leitura": leitura(pal, ppm)}
        print(f"  {destino.relative_to(RAIZ).as_posix()}")

    # protótipo de telas
    if cfg.get("prototipo"):
        telas = imp.capturas(RAIZ / cfg["prototipo"])
        blocos = "".join(
            f'<section class="tela"><h2>{html.escape(t)} · {html.escape(titulo)}{" (continuação)" if parte else ""}</h2>'
            f'<img alt="Tela {html.escape(t)}: {html.escape(titulo)}" src="data:image/png;base64,{base64.b64encode(png).decode()}"></section>'
            for t, titulo, parte, png in telas)
        n_telas = len({t for t, *_ in telas})
        caixa = caixa_avaliacao(["Cada tela mostra o que o usuário precisa para decidir, na ordem certa?",
                                 "Os textos, rótulos e mensagens são claros para quem usa?"], planilha)
        doc = capa(cfg, data, "Protótipo de telas", f"{n_telas} telas com dados reais de exemplo; as regras de "
                   "cada tela estão no capítulo 11", "Área técnica, gestão e TI", "", caixa) + blocos
        destino = DESTINO / "07_Prototipo_de_telas.pdf"
        cab, rod = cabecalho_rodape(cfg, "Protótipo de telas", data)
        imp.pdf(pagina("Protótipo de telas", doc, paisagem=True), destino, cab, rod, 0, paisagem=True)
        info[destino.name] = {"o_que": f"Protótipo de baixa fidelidade: {n_telas} telas, em páginas paisagem",
                              "para_quem": "Área técnica, gestão e TI", "leitura": ""}
        print(f"  {destino.relative_to(RAIZ).as_posix()}")
    return info


# ---------------------------------------------------------------- itens avaliáveis e decisões
def padrao_id(prefixo: str) -> str:
    return rf"{prefixo}-(?:[A-Z0-9]+-)*[A-Z]?\d+"


def limpar(t: str, limite: int = 160) -> str:
    t = texto_simples(t).strip(" —:-|")
    if len(t) > limite:
        corte = t[:limite]
        t = (corte[:corte.rfind(" ")] if " " in corte else corte) + "…"
    return t


def itens_avaliaveis(cfg: dict) -> list[dict]:
    por_id = {c["id"]: c for c in cfg["capitulos"]}
    itens, vistos = [], set()
    for prefixo, cap_id in cfg["itens_avaliaveis"].items():
        cap = por_id[cap_id]
        quem = "; ".join(cd["titulo"].replace("Caderno da ", "")[:1].upper() + cd["titulo"].replace("Caderno da ", "")[1:]
                         for cd in cfg["cadernos"] if cap_id in cd["capitulos"]) or "Todos"
        rid = padrao_id(prefixo)
        cab = re.compile(rf"^#{{2,5}}\s+(?:\d+(?:\.\d+)*\.?\s+)?({rid})\b\s*(.*)$")
        lin = re.compile(rf"^\|\s*\**({rid})\b\**([^|]*)\|([^|]*)\|")
        secao, em_codigo = "", False
        for f in fontes(cap)[:1]:
            for linha in f.read_text(encoding="utf-8").splitlines():
                if linha.lstrip().startswith("```"):
                    em_codigo = not em_codigo
                if em_codigo:
                    continue
                if re.match(r"^## ", linha):
                    secao = texto_simples(linha[3:])
                m = cab.match(linha)
                if m:
                    iid, titulo = m.group(1), m.group(2)
                else:
                    m = lin.match(linha)
                    if not m:
                        continue
                    iid, titulo = m.group(1), m.group(2).strip() or m.group(3)
                if iid in vistos:
                    continue
                vistos.add(iid)
                itens.append({"documento": f'{cap_id} {cap["titulo"]}', "secao": limpar(secao, 80), "id": iid,
                              "tipo": PREFIXOS.get(prefixo, prefixo), "titulo": limpar(titulo), "quem": quem})
    return itens


def tabela_da_secao(arquivo: Path, secao: str) -> list[list[str]]:
    """Linhas (sem cabeçalho) da primeira tabela da seção cujo título começa por `secao`."""
    linhas, dentro, out = arquivo.read_text(encoding="utf-8").splitlines(), False, []
    for l in linhas:
        if l.startswith("#"):
            if dentro:
                break
            dentro = re.sub(r"^#+\s*", "", l).startswith(secao)
            continue
        if dentro and l.startswith("|"):
            celulas = [texto_simples(c.strip()) for c in l.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in celulas):
                continue
            out.append(celulas)
    return out[1:]  # tira o cabeçalho


def gerar_planilha(cfg: dict, itens: list[dict], decisoes: list[list[str]], destino: Path, data: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.datavalidation import DataValidation

    azul, claro = "0C326F", "DDE6F2"
    fino = Side(style="thin", color="C3CCD8")
    borda = Border(left=fino, right=fino, top=fino, bottom=fino)
    wb = Workbook()

    ws = wb.active
    ws.title = "Como preencher"
    texto = [
        (f'{cfg["titulo_pacote"]}: planilha de avaliação', True),
        (f'Versão {cfg["versao"]} · {data} · {cfg["situacao"]}', False),
        ("", False),
        ("1. Leia o caderno do seu público (arquivos 01 a 04) ou o capítulo indicado na coluna “Documento”.", False),
        ("2. Na aba “Itens”, filtre a coluna “Quem avalia” pelo seu público.", False),
        ("3. Em “Parecer”, escolha uma opção da lista: " + ", ".join(PARECERES) + ".", False),
        ("4. Em “Aprovado com ajustes” e “Não aprovado”, escreva o ajuste pedido: o que mudar e por quê. "
         "Cite norma, cláusula ou caso quando houver.", False),
        ("5. Na aba “Decisões pendentes”, registre a decisão tomada, quem decidiu e a data.", False),
        ("6. Preencha “Avaliador” e “Data” e devolva a planilha ao responsável pela especificação.", False),
        ("", False),
        ("Item sem linha na planilha (por exemplo, uma tela que falta) vai como linha nova no fim da aba “Itens”, "
         "com o identificador “NOVO”.", False),
    ]
    for i, (t, negrito) in enumerate(texto, 1):
        c = ws.cell(row=i, column=1, value=t)
        c.font = Font(bold=negrito, size=13 if i == 1 else 11, color=azul if negrito else "17202B")
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 120

    def aba(nome, colunas, larguras, linhas, lista_parecer=None):
        w = wb.create_sheet(nome)
        w.append(colunas)
        for c in w[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=azul)
            c.alignment = Alignment(wrap_text=True, vertical="center")
            c.border = borda
        for l in linhas:
            w.append(l)
        for r in w.iter_rows(min_row=2):
            for c in r:
                c.alignment = Alignment(wrap_text=True, vertical="top")
                c.border = borda
        for r in range(2, w.max_row + 1):
            if r % 2 == 0:
                for c in w[r]:
                    c.fill = PatternFill("solid", fgColor="F7F9FC")
        for i, lg in enumerate(larguras):
            w.column_dimensions[chr(65 + i)].width = lg
        w.freeze_panes = "A2"
        w.auto_filter.ref = w.dimensions
        if lista_parecer:
            col, = lista_parecer
            dv = DataValidation(type="list", formula1='"' + ",".join(PARECERES) + '"', allow_blank=True)
            dv.error, dv.errorTitle = "Escolha uma opção da lista.", "Parecer"
            w.add_data_validation(dv)
            dv.add(f"{col}2:{col}{max(w.max_row, 2) + 200}")
            for c in w[1]:
                if c.column_letter == col:
                    c.fill = PatternFill("solid", fgColor="1351B4")
        return w

    aba("Itens", ["Documento", "Seção", "Identificador", "Tipo", "Título", "Quem avalia", "Parecer",
                  "Ajuste pedido ou comentário", "Avaliador", "Data"],
        [26, 26, 15, 20, 52, 22, 20, 50, 18, 12],
        [[i["documento"], i["secao"], i["id"], i["tipo"], i["titulo"], i["quem"], "", "", "", ""] for i in itens],
        lista_parecer=("G",))
    aba("Decisões pendentes", ["Decisão", "Quem decide", "Situação hoje (padrão adotado até a decisão)",
                               "Decisão tomada", "Responsável", "Data"],
        [55, 24, 55, 45, 20, 12], [d[:3] + ["", "", ""] for d in decisoes])
    resumo = wb.create_sheet("Resumo")
    resumo.append(["Tipo de item", "Quantidade"])
    for c in resumo[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=azul)
    cont: dict[str, int] = {}
    for i in itens:
        cont[i["tipo"]] = cont.get(i["tipo"], 0) + 1
    for k, v in cont.items():
        resumo.append([k, v])
    resumo.append(["Total", len(itens)])
    resumo.column_dimensions["A"].width = 40
    destino.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)


# ---------------------------------------------------------------- guia e índice da pasta
def guia_md(cfg: dict, info: dict, decisoes: list[list[str]], itens: list[dict], planilha: str) -> str:
    caps = {c["id"]: c for c in cfg["capitulos"]}
    l = [f'# Guia de avaliação',
         "",
         f'Este conjunto apresenta a especificação do sistema {cfg["sistema"]} ({cfg["subtitulo"].lower()}) na versão '
         f'{cfg["versao"]}, em situação de {cfg["situacao"].lower()}. Cada área avalia a parte que conhece. O parecer de '
         f'cada área vai numa planilha única, item por item. As decisões abaixo precisam ser tomadas antes do '
         f'desenvolvimento.',
         "",
         "## 1. Quem avalia o quê",
         "",
         "| Arquivo | Para quem | Capítulos | Leitura estimada |",
         "|---|---|---|---|"]
    for cd in cfg["cadernos"]:
        nome = f'{cd["arquivo"]}.pdf'
        lista = ", ".join(f'{i} {caps[i]["titulo"]}' for i in cd["capitulos"])
        l.append(f'| {nome} | {cd["publico"]} | {lista} | {info.get(nome, {}).get("leitura", "")} |')
    l += ["",
          "Cada caderno traz na capa as perguntas que aquele público responde. A especificação completa "
          "(06_Especificacao_completa.pdf) junta todos os capítulos, para quem precisa conferir a coerência entre eles. "
          "Cada capítulo também está sozinho na pasta capitulos.",
          "",
          "## 2. Como registrar o parecer",
          "",
          f"1. Leia o caderno do seu público.",
          f"2. Abra {planilha}. Na aba Itens, filtre a coluna Quem avalia pelo seu público. São {len(itens)} itens "
          "no total, cada um com o identificador usado nos documentos.",
          "3. Para cada item, escolha o parecer e, quando pedir ajuste, escreva o que mudar e por quê:",
          "",
          "| Parecer | Quando usar |",
          "|---|---|",
          "| Aprovado | O item está correto e completo como escrito |",
          "| Aprovado com ajustes | O item vale, mas precisa de correção pontual (descreva qual) |",
          "| Não aprovado | O item está errado, falta base ou não deve existir (explique) |",
          "| Não se aplica | O item não é da sua área ou não se aplica ao órgão |",
          "",
          "4. Na aba Decisões pendentes, registre a decisão tomada, quem decidiu e a data.",
          "5. Devolva a planilha ao responsável pela especificação. Itens com parecer “Não aprovado” voltam para revisão "
          "e geram nova versão do pacote, com nova data nesta capa.",
          "",
          "## 3. Decisões necessárias antes do desenvolvimento",
          "",
          "| Decisão | Quem decide | Situação hoje |",
          "|---|---|---|"]
    l += [f"| {d[0]} | {d[1]} | {d[2]} |" for d in decisoes]
    l += ["",
          "## 4. Arquivos desta pasta",
          "",
          "| Arquivo | O que é | Para quem |",
          "|---|---|---|",
          f"| 00_Guia_de_avaliacao.pdf | Este guia | Todos |"]
    for nome in sorted(info):
        if "/" not in nome and not nome.startswith("00_"):
            l.append(f'| {nome} | {info[nome]["o_que"]} | {info[nome]["para_quem"]} |')
    l.append("| capitulos/ | Um PDF por capítulo (01 a 17), com o mesmo conteúdo dos cadernos | Quem quer um capítulo "
             "sozinho |")
    l += ["",
          "## 5. Como ler os identificadores",
          "",
          "Todo item tem um identificador estável, usado em todos os documentos e na planilha.",
          "",
          "| Prefixo | Significa |",
          "|---|---|"]
    l += [f"| {k} | {v} |" for k, v in PREFIXOS.items()]
    return "\n".join(l) + "\n"


def descricao(cfg: dict, rel: str) -> tuple[str, str]:
    for padrao, o_que, quem in cfg.get("descricao_saida", []):
        if fnmatch.fnmatch(rel, padrao):
            return o_que, quem
    return "", ""


def leia_me(cfg: dict, info: dict, data: str) -> str:
    l = ["# Pasta de saída",
         "",
         "Índice gerado por `scripts/gerar_documentos.py`. Não edite à mão: rode o script de novo.",
         "",
         f'Pacote de especificação versão {cfg["versao"]} ({cfg["situacao"].lower()}), gerado em {data}.',
         "",
         f"Impressão digital da fonte: `{impressao_digital(cfg)}`. Se a fonte mudar e os documentos não forem gerados de "
         "novo, o teste `tests/test_especificacao.py` acusa documento desatualizado.",
         "",
         "| Pasta | O que tem | Quem produz |",
         "|---|---|---|",
         "| `levantamento/` | Dados que sustentam a especificação: cálculos da coorte refeitos, cadastro do contrato com "
         "trecho literal, layout do pleito e a validação do pleito real | agente (extração) + scripts (recálculo, validação) |",
         "| `documentos_para_avaliacao/` | Versões de leitura para as áreas avaliarem: guia, cadernos por público, "
         "planilha de parecer, especificação completa, protótipo e um PDF por capítulo | `scripts/gerar_documentos.py` |",
         "| `pareceres/` | `recebidos/`: planilhas de avaliação devolvidas pelas áreas; `00_Consolidado_dos_pareceres.xlsx`: "
         "todos os pareceres item por item | áreas avaliadoras + `scripts/consolidar_pareceres.py` |",
         "",
         "## documentos_para_avaliacao/",
         "",
         "Comece pelo `00_Guia_de_avaliacao.pdf`.",
         "",
         "| Arquivo | O que é | Para quem | Leitura |",
         "|---|---|---|---|",
         "| `00_Guia_de_avaliacao.pdf` | Quem avalia o quê, como registrar o parecer, decisões pendentes | Todos | 10 min |"]
    for nome in sorted(info, key=lambda n: (n.count("/"), n)):
        i = info[nome]
        l.append(f'| `{nome}` | {i["o_que"]} | {i["para_quem"]} | {i.get("leitura", "")} |')
    l += ["", "## levantamento/", "", "| Arquivo | O que é | Para quem |", "|---|---|---|"]
    for f in sorted((SAIDA / "levantamento").rglob("*")):
        if f.is_file():
            rel = f.relative_to(RAIZ).as_posix()
            o_que, quem = descricao(cfg, rel)
            l.append(f"| `{f.relative_to(SAIDA).as_posix()}` | {o_que} | {quem} |")
    return "\n".join(l) + "\n"


def impressao_digital(cfg: dict) -> str:
    """SHA-256 (16 primeiros dígitos) da configuração, das fontes dos capítulos, da seção de decisões e do protótipo,
    com fim de linha normalizado: muda quando qualquer texto que vai para os documentos muda."""
    import hashlib
    arqs = [CONFIG, RAIZ / cfg["decisoes_pendentes"]["fonte"]] + [f for c in cfg["capitulos"] for f in fontes(c)]
    if cfg.get("prototipo"):
        arqs.append(RAIZ / cfg["prototipo"])
    h = hashlib.sha256()
    for a in arqs:
        h.update(a.relative_to(RAIZ).as_posix().encode())
        h.update(a.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def data_da_versao() -> str:
    """Data do último commit que mexeu no pacote; sem git, a data de hoje."""
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", "especificacao", "docs"], cwd=RAIZ,
                           capture_output=True, text=True, timeout=10)
        iso = r.stdout.strip()
    except Exception:
        iso = ""
    d = dt.date.fromisoformat(iso) if iso else dt.date.today()
    return d.strftime("%d/%m/%Y")


def conferir_nomes() -> None:
    for f in DESTINO.rglob("*"):
        if f.is_file() and not NOME_ARQUIVO.match(f.name):
            raise SystemExit(f"nome fora do padrão NN_Palavras.ext: {f.relative_to(RAIZ).as_posix()}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rapido", action="store_true", help="só guia, planilha e LEIA-ME")
    args = ap.parse_args()
    cfg = ler_config()
    BLOQUEADOS.extend(re.compile(x, re.I) for x in cfg.get("termos_bloqueados", []))
    data = data_da_versao()
    planilha = "05_Planilha_de_avaliacao.xlsx"

    itens = itens_avaliaveis(cfg)
    dp = cfg["decisoes_pendentes"]
    decisoes = tabela_da_secao(RAIZ / dp["fonte"], dp["secao"])
    gerar_planilha(cfg, itens, decisoes, DESTINO / planilha, data)
    print(f"  {(DESTINO / planilha).relative_to(RAIZ).as_posix()}: {len(itens)} itens, {len(decisoes)} decisões")

    info: dict[str, dict] = {planilha: {"o_que": f"Planilha de parecer: {len(itens)} itens e {len(decisoes)} decisões "
                                                  "pendentes, com lista de parecer", "para_quem": "Todos os avaliadores",
                                         "leitura": ""}}
    imp = Impressora()
    try:
        if not args.rapido:
            info.update(gerar_pdfs(cfg, imp, data, planilha))
        else:  # índice com os PDFs que já existem, sem tempo de leitura
            for cap in cfg["capitulos"]:
                publico = "; ".join(cd["publico"] for cd in cfg["cadernos"] if cap["id"] in cd["capitulos"]) or "Todos"
                info[f'capitulos/{cap["arquivo"]}.pdf'] = {"o_que": f'Capítulo {cap["id"]}: {cap["titulo"]}',
                                                           "para_quem": publico, "leitura": ""}
            for cd in cfg["cadernos"]:
                info[f'{cd["arquivo"]}.pdf'] = {"o_que": f'{cd["titulo"]} (capítulos {", ".join(cd["capitulos"])})',
                                                "para_quem": cd["publico"], "leitura": ""}
            info["06_Especificacao_completa.pdf"] = {"o_que": "Especificação completa", "para_quem": "Todos", "leitura": ""}
            info["07_Prototipo_de_telas.pdf"] = {"o_que": "Protótipo de telas", "para_quem": "Área técnica, gestão e TI",
                                                 "leitura": ""}
            info = {k: v for k, v in info.items() if (DESTINO / k).exists()}
        md = guia_md(cfg, info, decisoes, itens, planilha)
        conv = Conversor(cfg["capitulos"], set())
        r = conv.converter(md, RAIZ / "especificacao" / "README.md", "g", set())
        caixa = ('<div class="caixa"><div class="caixa-titulo">Por onde começar</div><ol><li>Veja na seção 1 qual caderno é o seu.</li>'
                 f'<li>Leia o caderno e registre o parecer em <b>{planilha}</b>.</li>'
                 '<li>Veja na seção 3 as decisões que dependem da sua área.</li></ol></div>')
        doc = capa(cfg, data, "Guia de avaliação", "Como ler, avaliar e devolver o parecer sobre a especificação",
                   "Todos os avaliadores", "10 min", caixa) + r.html
        cab, rod = cabecalho_rodape(cfg, "Guia de avaliação", data)
        imp.pdf(pagina("Guia de avaliação", doc), DESTINO / "00_Guia_de_avaliacao.pdf", cab, rod, r.diagramas)
        print(f"  {(DESTINO / '00_Guia_de_avaliacao.pdf').relative_to(RAIZ).as_posix()}")
    finally:
        imp.fechar()

    (SAIDA / "LEIA-ME.md").write_text(leia_me(cfg, info, data), encoding="utf-8")
    conferir_nomes()
    print(f"  saida/LEIA-ME.md")
    for a in AVISOS:
        print("aviso:", a)


if __name__ == "__main__":
    main()
