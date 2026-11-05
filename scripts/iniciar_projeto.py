"""Cria a estrutura do projeto de especificação do aluno a partir de `modelos/projeto/`.

O projeto nasce dos modelos, nunca de uma cópia do caso resolvido (`exemplo/`): é o que impede que regras, nomes e
números do exemplo vazem para a especificação de outro processo.

Uso, da raiz deste repositório:
    python scripts/iniciar_projeto.py <pasta do projeto> --sistema "Nome do sistema" --orgao SIGLA
    python scripts/iniciar_projeto.py <pasta> --sistema "..." --orgao SIGLA --copiar-ferramentas

A pasta não pode existir com conteúdo nem ficar dentro de `exemplo/`. Com `--copiar-ferramentas`, os scripts do
framework (conferir, gerar documentos, consolidar pareceres) vão para `<pasta>/ferramentas/`, para o projeto rodar
sozinho num repositório próprio.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

FERRAMENTA = Path(__file__).resolve().parents[1]
MODELOS = FERRAMENTA / "modelos" / "projeto"
SCRIPTS = ["conferir_especificacao.py", "gerar_documentos.py", "consolidar_pareceres.py", "termos_do_exemplo.json"]


def iniciar(destino: Path, sistema: str | None, orgao: str | None, copiar_ferramentas: bool = False) -> list[Path]:
    destino = destino.resolve()
    if (FERRAMENTA / "exemplo") in destino.parents or destino == FERRAMENTA / "exemplo":
        raise SystemExit("o projeto não pode ficar dentro de exemplo/: ali está só o caso resolvido")
    if destino.exists() and any(destino.iterdir()):
        raise SystemExit(f"{destino.name}/ já existe e não está vazia; escolha outra pasta")
    shutil.copytree(MODELOS, destino, dirs_exist_ok=True)
    trocas = {}
    if sistema:
        trocas["{{Nome do sistema}}"] = sistema
    if orgao:
        trocas["{{Sigla do órgão}}"] = orgao
    criados = []
    for f in sorted(destino.rglob("*")):
        if not f.is_file():
            continue
        criados.append(f)
        if f.suffix in {".md", ".json", ".html"} and trocas:
            texto = f.read_text(encoding="utf-8")
            for de, para in trocas.items():
                texto = texto.replace(de, para)
            f.write_text(texto, encoding="utf-8")
    if copiar_ferramentas:
        (destino / "ferramentas").mkdir(exist_ok=True)
        for nome in SCRIPTS:
            shutil.copy2(FERRAMENTA / "scripts" / nome, destino / "ferramentas" / nome)
            criados.append(destino / "ferramentas" / nome)
    return criados


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("destino", help="pasta do projeto do aluno (nova ou vazia)")
    ap.add_argument("--sistema", help="nome do sistema, para trocar o marcador {{Nome do sistema}}")
    ap.add_argument("--orgao", help="sigla do órgão, para trocar o marcador {{Sigla do órgão}}")
    ap.add_argument("--copiar-ferramentas", action="store_true", help="copia os scripts para <destino>/ferramentas/")
    args = ap.parse_args()
    criados = iniciar(Path(args.destino), args.sistema, args.orgao, args.copiar_ferramentas)
    raiz = Path(args.destino).resolve()
    print(f"{len(criados)} arquivos criados em {raiz.name}/")
    for f in criados:
        print(f"  {f.relative_to(raiz).as_posix()}")
    cmd = "python ferramentas/" if args.copiar_ferramentas else "python scripts/"
    alvo = "." if args.copiar_ferramentas else args.destino
    print("\nPróximos passos:")
    print(f"  1. Copie as saídas do processo para {raiz.name}/insumos/ (veja insumos/LEIA-ME.md).")
    print(f"  2. Preencha especificacao/ na ordem do capítulo 03 da metodologia.")
    print(f"  3. Confira: {cmd}conferir_especificacao.py --projeto {alvo}")
    print(f"  4. Gere os documentos: {cmd}gerar_documentos.py --projeto {alvo}")


if __name__ == "__main__":
    main()
