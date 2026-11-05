"""Confere a especificação de um projeto: completude, rastreabilidade e isolamento do exemplo.

Lê `<projeto>/especificacao/` e aplica as regras do capítulo 03 da metodologia (convenção de identificadores e
cadeia de rastreabilidade). Cada achado tem código, nível (erro ou aviso), arquivo, linha e mensagem.

    erro   a especificação não pode seguir para avaliação (gerar_documentos.py também para)
    aviso  a pessoa revisa; ou corrige, ou registra por que fica

Regras:
    C01 erro   documento obrigatório ausente
    C02 erro   marcador de preenchimento do modelo ({{...}}) ainda no texto
    C03 erro   termo do caso resolvido (exemplo/reajusta) na especificação, fora de termos_permitidos
    C04 aviso  trecho de 12 palavras ou mais igual ao do caso resolvido
    C05 erro   identificador citado que não foi definido em nenhum documento
    C06 erro   requisito funcional sem origem ou sem critério de aceite
    C07 erro   caso de uso listado no 01 sem descrição no 04, ou descrito no 04 sem estar no 01
    C08 erro   tela listada no 01 sem descrição no 11, ou descrita no 11 sem estar no 01
    C09 erro   requisito funcional listado no 01 sem descrição no 03, ou descrito no 03 sem estar no 01
    C10 erro   diagrama obrigatório ausente (casos de uso, sequência e estados no 04; componentes no 05; classes no 06)
    C11 aviso  requisito funcional que nenhum teste de aceitação nem história cita
    C12 aviso  caso de uso que não cita requisito funcional
    C13 aviso  regra de negócio que nenhum outro documento cita
    C14 aviso  módulo sem requisito funcional
    C15 aviso  história do backlog que não cita requisito nem caso de uso
    C16 aviso  transição de estado sem evento ou caso de uso no rótulo
    C17 erro   (com --documentos) documentos para avaliação desatualizados em relação à fonte

Uso, da raiz deste repositório:
    python scripts/conferir_especificacao.py --projeto <pasta do projeto>
    python scripts/conferir_especificacao.py --projeto <pasta> --documentos   # inclui C17
    python scripts/conferir_especificacao.py --projeto <pasta> --json conferencia.json

Sai com código 1 se houver erro.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

FERRAMENTA = Path(__file__).resolve().parents[1]
EXEMPLO = FERRAMENTA / "exemplo" / "reajusta"
TERMOS = Path(__file__).resolve().parent / "termos_do_exemplo.json"

DOCUMENTOS = {
    "01": "01_VISAO_ESCOPO.md", "02": "02_PERFIS_E_JORNADAS.md", "03": "03_REQUISITOS.md",
    "04": "04_CASOS_DE_USO.md", "05": "05_ARQUITETURA.md", "06": "06_MODELO_DADOS.md",
    "07": "07_CONTRATOS_API.md", "08": "08_REGRAS_NEGOCIO.md", "09": "09_INTEGRACOES.md", "10": "10_UX_UI.md",
    "11": "11_TELAS.md", "12": "12_TESTES.md", "13": "13_BACKLOG.md", "14": "14_OPERACAO.md",
    "15": "15_SEGURANCA.md",
}
OBRIGATORIOS = list(DOCUMENTOS.values()) + ["README.md", "AGENTS_DESENVOLVIMENTO.md", "documentos.json"]

# Famílias de identificador (capítulo 03 da metodologia, seção 2)
_SIGLA = r"[A-Z]{2,5}"
FAMILIAS = {
    "MOD": rf"MOD-{_SIGLA}", "PER": rf"PER-{_SIGLA}", "EP": rf"EP-{_SIGLA}",
    "UC": r"UC-\d{2,3}", "RF": rf"RF-{_SIGLA}-\d{{2,3}}", "RNF": r"RNF-\d{2,3}",
    "RN": r"RN-[A-Z]{1,5}-?\d{2,3}", "TL": r"TL-\d{2,3}", "CMP": r"CMP-\d{2,3}", "INT": r"INT-\d{2,3}",
    "AT": r"AT-\d{2,3}", "HIS": rf"HIS-{_SIGLA}-\d{{2,3}}", "DEC": r"DEC-\d{2,3}",
    "SEG": rf"SEG-{_SIGLA}-\d{{2,3}}", "ADR": r"ADR-\d{4}",
}
QUALQUER_ID = re.compile(r"(?<![\w-])(" + "|".join(f"(?:{p})" for p in FAMILIAS.values()) + r")(?![\w-])")
MARCADOR = re.compile(r"\{\{\s*[A-ZÀ-Ú][^}]*\}\}")  # {{Nome do sistema}}; {{variavel}} minúscula é sintaxe de modelo
COMENTARIO = re.compile(r"<!--.*?-->", re.S)
CABECALHO = re.compile(r"^(#{1,6})\s+(?:\d+(?:\.\d+)*\.?\s+)?(.*)$")
JANELA = 12  # palavras seguidas iguais ao exemplo que contam como cópia


@dataclass
class Achado:
    codigo: str
    nivel: str
    arquivo: str
    linha: int
    mensagem: str


# ---------------------------------------------------------------- leitura
@dataclass
class Doc:
    nome: str
    rel: str
    linhas: list[str]          # texto sem comentários HTML, preservando a numeração de linhas
    codigo: list[bool]         # linha dentro de bloco de código


def ler_doc(arq: Path, raiz: Path) -> Doc:
    bruto = arq.read_text(encoding="utf-8")
    sem = COMENTARIO.sub(lambda m: "\n" * m.group(0).count("\n"), bruto)  # mantém o número das linhas
    linhas = sem.splitlines()
    codigo, dentro = [], False
    for l in linhas:
        if l.lstrip().startswith("```"):
            dentro = not dentro
            codigo.append(True)
            continue
        codigo.append(dentro)
    return Doc(arq.name, arq.relative_to(raiz).as_posix(), linhas, codigo)


def definicoes(doc: Doc) -> dict[str, int]:
    """Identificadores definidos no documento: título de seção que começa pelo id, ou primeira célula de tabela."""
    out: dict[str, int] = {}
    for i, l in enumerate(doc.linhas):
        if doc.codigo[i]:
            continue
        m = CABECALHO.match(l)
        alvo = m.group(2) if m and len(m.group(1)) >= 2 else None
        if alvo is None and l.startswith("|"):
            alvo = l.strip().strip("|").split("|")[0].strip().strip("*` ")
        if alvo:
            mid = QUALQUER_ID.match(alvo.strip("*` "))
            if mid:
                out.setdefault(mid.group(1), i + 1)
    return out


def blocos(doc: Doc, familia: str) -> dict[str, tuple[int, str]]:
    """Seções cujo título começa por um id da família: id -> (linha, texto da seção até o próximo título igual ou maior)."""
    padrao = re.compile(rf"^(#{{2,5}})\s+(?:\d+(?:\.\d+)*\.?\s+)?({FAMILIAS[familia]})\b")
    out: dict[str, tuple[int, str]] = {}
    i = 0
    while i < len(doc.linhas):
        m = None if doc.codigo[i] else padrao.match(doc.linhas[i])
        if not m:
            i += 1
            continue
        nivel, ini = len(m.group(1)), i
        i += 1
        while i < len(doc.linhas):
            c = None if doc.codigo[i] else CABECALHO.match(doc.linhas[i])
            if c and len(c.group(1)) <= nivel:
                break
            i += 1
        out.setdefault(m.group(2), (ini + 1, "\n".join(doc.linhas[ini:i])))
    return out


def ids_de(texto: str, familia: str | None = None) -> set[str]:
    achados = set(QUALQUER_ID.findall(texto))
    if familia:
        achados = {a for a in achados if re.fullmatch(FAMILIAS[familia], a)}
    return achados


def ids_definidos_no(doc: Doc, familia: str) -> dict[str, int]:
    return {k: v for k, v in definicoes(doc).items() if re.fullmatch(FAMILIAS[familia], k)}


def campo(bloco: str, nome: str) -> str | None:
    """Valor de um campo `- **Nome:** valor` (ou linha de tabela `| Nome | valor |`) dentro de uma seção."""
    m = re.search(rf"^\s*[-*]\s*\*\*{nome}[^*]*:\*\*\s*(.*(?:\n(?!\s*[-*]\s*\*\*)\s+.*)*)", bloco, re.M | re.I)
    if not m:
        m = re.search(rf"^\|\s*\**{nome}[^|]*\|\s*(.*?)\s*\|\s*$", bloco, re.M | re.I)
    return m.group(1).strip() if m else None


def vazio(valor: str | None) -> bool:
    return valor is None or not valor.strip(" —-–.") or bool(MARCADOR.search(valor))


# ---------------------------------------------------------------- isolamento do exemplo
def termos_do_exemplo() -> list[tuple[str, re.Pattern]]:
    if not TERMOS.exists():
        return []
    cfg = json.loads(TERMOS.read_text(encoding="utf-8"))
    out = []
    for grupo in ("nomes", "dominio", "identificadores"):
        for t in cfg.get(grupo, []):
            fim = r"(?![A-Za-z0-9])" if grupo == "identificadores" else r"(?![\w-])"  # RF-XXX pega RF-XXX-01
            out.append((t, re.compile(rf"(?<![\w-]){re.escape(t)}{fim}", re.I if grupo == "dominio" else 0)))
    return out


def palavras(texto: str) -> list[str]:
    return re.findall(r"[a-zà-ú0-9]+", texto.lower())


def texto_comparavel(texto: str) -> str:
    """Texto corrido, sem o que coincide por convenção e não por cópia: comentários, blocos de código e diagramas,
    código em linha (nomes de arquivo, comandos), destinos de link, nomes de arquivo e identificadores."""
    texto = COMENTARIO.sub(" ", texto)
    texto = re.sub(r"```.*?```", " ", texto, flags=re.S)
    texto = re.sub(r"`[^`\n]*`", " ", texto)
    texto = re.sub(r"\]\([^)]*\)", "] ", texto)
    texto = re.sub(r"https?://\S+", " ", texto)
    texto = re.sub(r"\b[\w-]+\.(?:md|json|html|py|csv|xlsx|pdf)\b", " ", texto)
    return QUALQUER_ID.sub(" ", texto)


def trechos(texto: str) -> list[list[str]]:
    """Unidades de texto corrido (parágrafo, item de lista, célula de tabela), em palavras. Títulos e cabeçalhos de
    tabela ficam de fora: são estrutura, e imitar a estrutura do exemplo é o que se espera."""
    linhas = texto_comparavel(texto).splitlines()
    out, atual = [], []
    for i, l in enumerate(linhas):
        s = l.strip()
        cabecalho_tabela = s.startswith("|") and i + 1 < len(linhas) and re.match(r"^\|?\s*:?-{3,}", linhas[i + 1].strip())
        if not s or s.startswith("#") or s.startswith("|") or re.match(r"^([-*]|\d+[.)])\s", s):
            if atual:
                out.append(atual)
            atual = []
            if s.startswith("|") and not cabecalho_tabela and not re.match(r"^\|?\s*:?-{3,}", s):
                out += [palavras(c) for c in s.strip("|").split("|")]
            elif re.match(r"^([-*]|\d+[.)])\s", s):
                atual = palavras(s)
            continue
        atual += palavras(s)
    if atual:
        out.append(atual)
    out = [[w for w in t if not w.isdigit()] for t in out]  # números de norma e de seção coincidem sem cópia
    return [t for t in out if len(t) >= JANELA]


def janelas_do_exemplo() -> set[tuple[str, ...]]:
    pasta = EXEMPLO / "especificacao"
    if not pasta.exists():
        return set()
    out: set[tuple[str, ...]] = set()
    for arq in pasta.rglob("*.md"):
        for p in trechos(arq.read_text(encoding="utf-8")):
            out.update(tuple(p[i:i + JANELA]) for i in range(len(p) - JANELA + 1))
    return out


def copias(texto: str, janelas: set[tuple[str, ...]]) -> list[str]:
    """Trechos de JANELA palavras ou mais iguais aos do exemplo, já emendados."""
    achados = []
    for p in trechos(texto):
        i = 0
        while i <= len(p) - JANELA:
            if tuple(p[i:i + JANELA]) in janelas:
                j = i + JANELA
                while j < len(p) and tuple(p[j - JANELA + 1:j + 1]) in janelas:
                    j += 1
                achados.append(" ".join(p[i:j]))
                i = j
            else:
                i += 1
    return achados


# ---------------------------------------------------------------- conferência
def conferir(projeto: Path, documentos: bool = False) -> list[Achado]:
    projeto = projeto.resolve()
    esp = projeto / "especificacao"
    achados: list[Achado] = []

    def add(cod, nivel, doc_rel, linha, msg):
        achados.append(Achado(cod, nivel, doc_rel, linha, msg))

    # C01
    for nome in OBRIGATORIOS:
        if not (esp / nome).exists():
            add("C01", "erro", f"especificacao/{nome}", 0, "documento obrigatório ausente")
    cfg_arq = esp / "documentos.json"
    cfg = json.loads(cfg_arq.read_text(encoding="utf-8")) if cfg_arq.exists() else {}
    if cfg_arq.exists():
        for i, l in enumerate(cfg_arq.read_text(encoding="utf-8").splitlines(), 1):
            for m in MARCADOR.finditer(l):
                add("C02", "erro", "especificacao/documentos.json", i, f"marcador de preenchimento: {m.group(0)}")
    e_exemplo = bool(cfg.get("exemplo"))
    permitidos = {k.lower(): v for k, v in (cfg.get("termos_permitidos") or {}).items()}

    # arquivos que começam com "_" são modelos de apoio (por exemplo adr/_MODELO.md) e não entram na conferência
    arquivos = sorted(a for a in esp.rglob("*.md") if not a.name.startswith("_")) if esp.exists() else []
    docs = {a.name: ler_doc(a, projeto) for a in arquivos}
    doc = lambda n: docs.get(DOCUMENTOS[n])

    # C02, C03, C04: texto
    termos = [] if e_exemplo else termos_do_exemplo()
    janelas = set() if e_exemplo else janelas_do_exemplo()
    for d in docs.values():
        for i, l in enumerate(d.linhas, 1):
            for m in MARCADOR.finditer(l):
                add("C02", "erro", d.rel, i, f"marcador de preenchimento: {m.group(0)}")
            for t, rx in termos:
                if t.lower() in permitidos:
                    continue
                if rx.search(l):
                    add("C03", "erro", d.rel, i, f"termo do caso resolvido: “{t}” (se for do seu domínio, declare em "
                        "termos_permitidos do documentos.json, com a justificativa)")
        if janelas:
            for trecho in copias("\n".join(d.linhas), janelas):
                n = len(trecho.split())
                add("C04", "aviso", d.rel, 0, f"trecho igual ao do caso resolvido ({n} palavras): “{trecho[:140]}…”")
    for t, just in permitidos.items():
        if not str(just).strip():
            add("C03", "erro", "especificacao/documentos.json", 0, f"termo permitido sem justificativa: “{t}”")

    # C05: todo id citado tem definição
    definidos: dict[str, tuple[str, int]] = {}
    for d in docs.values():
        for k, v in definicoes(d).items():
            definidos.setdefault(k, (d.rel, v))
    for arq in (esp / "adr").glob("*.md") if (esp / "adr").exists() else []:
        m = re.match(r"(\d{4})-", arq.name)
        if m:
            definidos.setdefault(f"ADR-{m.group(1)}", (arq.relative_to(projeto).as_posix(), 1))
    ja = set()
    for d in docs.values():
        for i, l in enumerate(d.linhas, 1):
            for iid in QUALQUER_ID.findall(l):
                if iid not in definidos and (iid, d.rel) not in ja:
                    ja.add((iid, d.rel))
                    add("C05", "erro", d.rel, i, f"{iid} citado e não definido em nenhum documento (defina no 01 ou "
                        "no documento dono, como título de seção ou primeira coluna de tabela)")

    # C06, C09: requisitos funcionais
    d01, d03, d04, d11 = doc("01"), doc("03"), doc("04"), doc("11")
    rf_blocos = blocos(d03, "RF") if d03 else {}
    for rid, (linha, texto) in rf_blocos.items():
        for nome in ("Origem", "Crit[ée]rio de aceite"):
            if vazio(campo(texto, nome)):
                rotulo = "origem" if nome == "Origem" else "critério de aceite"
                add("C06", "erro", d03.rel, linha, f"{rid} sem {rotulo}")
    if d01 and d03:
        rf01 = ids_definidos_no(d01, "RF")
        for rid, linha in rf01.items():
            if rid not in rf_blocos:
                add("C09", "erro", d01.rel, linha, f"{rid} listado no 01 sem seção própria no 03")
        for rid, (linha, _) in rf_blocos.items():
            if rid not in rf01:
                add("C09", "erro", d03.rel, linha, f"{rid} descrito no 03 e ausente da lista do 01")

    # C07, C12, C16
    uc_blocos = blocos(d04, "UC") if d04 else {}
    if d01 and d04:
        uc01 = ids_definidos_no(d01, "UC")
        for uid, linha in uc01.items():
            if uid not in uc_blocos:
                add("C07", "erro", d01.rel, linha, f"{uid} listado no 01 sem descrição no 04")
        for uid, (linha, _) in uc_blocos.items():
            if uid not in uc01:
                add("C07", "erro", d04.rel, linha, f"{uid} descrito no 04 e ausente da lista do 01")
    for uid, (linha, texto) in uc_blocos.items():
        if not ids_de(texto, "RF"):
            add("C12", "aviso", d04.rel, linha, f"{uid} não cita requisito funcional")

    # C08
    if d01 and d11:
        tl01, tl11 = ids_definidos_no(d01, "TL"), blocos(d11, "TL")
        for tid, linha in tl01.items():
            if tid not in tl11:
                add("C08", "erro", d01.rel, linha, f"{tid} listada no 01 sem descrição no 11")
        for tid, (linha, _) in tl11.items():
            if tid not in tl01:
                add("C08", "erro", d11.rel, linha, f"{tid} descrita no 11 e ausente da lista do 01")

    # C10: diagramas
    exigidos = [("04", "flowchart|graph|usecase", "diagrama de casos de uso"),
                ("04", "sequenceDiagram", "diagrama de sequência"),
                ("04", "stateDiagram", "diagrama de estados"),
                ("05", "flowchart|graph|C4Context|C4Container|C4Component", "diagrama de contexto ou de componentes"),
                ("06", "classDiagram|erDiagram", "diagrama de classes ou entidade-relacionamento")]
    for n, rx, nome in exigidos:
        d = doc(n)
        if d is None:
            continue
        texto = "\n".join(d.linhas)
        if not re.search(rf"```mermaid\s*\n\s*(?:%%.*\n\s*)*(?:{rx})", texto):
            add("C10", "erro", d.rel, 0, f"falta {nome} (bloco mermaid)")

    # C11: RF testável
    citados_teste: set[str] = set()
    for n in ("12", "13"):
        d = doc(n)
        if d:
            citados_teste |= ids_de("\n".join(d.linhas), "RF")
    for rid, (linha, _) in rf_blocos.items():
        if rid not in citados_teste:
            add("C11", "aviso", d03.rel, linha, f"{rid} não é citado por nenhum teste de aceitação (12) nem história (13)")

    # C13: RN citada fora do 08
    d08 = doc("08")
    if d08:
        fora = set()
        for d in docs.values():
            if d.nome != d08.nome:
                fora |= ids_de("\n".join(d.linhas), "RN")
        for rid, linha in ids_definidos_no(d08, "RN").items():
            if rid not in fora:
                add("C13", "aviso", d08.rel, linha, f"{rid} não é citada por requisito, caso de uso, tela ou teste")

    # C14: módulo com requisito
    if d01:
        rf_todos = set(rf_blocos) | set(ids_definidos_no(d01, "RF"))
        siglas = {r.split("-")[1] for r in rf_todos}
        for mid, linha in ids_definidos_no(d01, "MOD").items():
            if mid.split("-")[1] not in siglas:
                add("C14", "aviso", d01.rel, linha, f"{mid} sem requisito funcional RF-{mid.split('-')[1]}-nn")

    # C15: história rastreável
    d13 = doc("13")
    if d13:
        for hid, (linha, texto) in blocos(d13, "HIS").items():
            if not (ids_de(texto, "RF") or ids_de(texto, "UC")):
                add("C15", "aviso", d13.rel, linha, f"{hid} não cita requisito nem caso de uso")
        # histórias definidas em tabela: a linha da tabela é o bloco
        for i, l in enumerate(d13.linhas, 1):
            if l.startswith("|") and QUALQUER_ID.match(l.strip().strip("|").split("|")[0].strip("*` ")):
                hid = QUALQUER_ID.match(l.strip().strip("|").split("|")[0].strip("*` ")).group(1)
                if hid.startswith("HIS-") and not (ids_de(l, "RF") or ids_de(l, "UC")):
                    add("C15", "aviso", d13.rel, i, f"{hid} não cita requisito nem caso de uso")

    # C16: transições de estado com evento
    if d04:
        dentro_estado = False
        for i, l in enumerate(d04.linhas, 1):
            if l.strip().startswith("stateDiagram"):
                dentro_estado = True
            elif l.strip().startswith("```"):
                dentro_estado = False
            elif dentro_estado and "-->" in l and "[*]" not in l and ":" not in l:
                add("C16", "aviso", d04.rel, i, f"transição sem evento: {l.strip()}")

    # C17: documentos atualizados
    if documentos:
        leia = projeto / "saida" / "LEIA-ME.md"
        if not leia.exists():
            add("C17", "erro", "saida/LEIA-ME.md", 0, "documentos para avaliação ainda não gerados")
        else:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import gerar_documentos as gd
            gd.definir_projeto(projeto)
            atual = gd.impressao_digital(gd.ler_config())
            if atual not in leia.read_text(encoding="utf-8"):
                add("C17", "erro", "saida/LEIA-ME.md", 0, "a fonte mudou depois da geração: rode gerar_documentos.py")

    ordem = {"erro": 0, "aviso": 1}
    achados.sort(key=lambda a: (ordem[a.nivel], a.codigo, a.arquivo, a.linha))
    return achados


def resumo(achados: list[Achado]) -> str:
    cont = defaultdict(int)
    for a in achados:
        cont[(a.nivel, a.codigo)] += 1
    erros = sum(1 for a in achados if a.nivel == "erro")
    avisos = len(achados) - erros
    partes = ", ".join(f"{c} {n}" for (_, c), n in sorted(cont.items(), key=lambda x: (x[0][0] != "erro", x[0][1])))
    return f"{erros} erro(s), {avisos} aviso(s)" + (f" [{partes}]" if partes else "")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--projeto", default=".", help="pasta do projeto (a que contém especificacao/)")
    ap.add_argument("--documentos", action="store_true", help="confere também se os documentos estão atualizados (C17)")
    ap.add_argument("--json", help="grava os achados neste arquivo")
    ap.add_argument("--limite", type=int, default=200, help="máximo de achados impressos")
    args = ap.parse_args()
    achados = conferir(Path(args.projeto), args.documentos)
    for a in achados[:args.limite]:
        onde = f"{a.arquivo}:{a.linha}" if a.linha else a.arquivo
        print(f"{a.nivel:5} {a.codigo} {onde}  {a.mensagem}")
    if len(achados) > args.limite:
        print(f"... e mais {len(achados) - args.limite} (use --json para a lista completa)")
    print(resumo(achados))
    if args.json:
        Path(args.json).write_text(json.dumps([asdict(a) for a in achados], ensure_ascii=False, indent=1),
                                   encoding="utf-8")
    sys.exit(1 if any(a.nivel == "erro" for a in achados) else 0)


if __name__ == "__main__":
    main()
