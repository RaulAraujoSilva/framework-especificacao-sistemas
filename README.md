# Especificação de sistemas a partir do processo mapeado

Segunda parte do curso de processos SEI na regulação. A primeira parte,
[mapeamento-processos-sei](https://github.com/RaulAraujoSilva/mapeamento-processos-sei), mapeia os processos da
agência a partir do SEI e escolhe o processo-piloto de um sistema. Este repositório ensina o passo seguinte:
**transformar o piloto numa especificação de sistema que uma IA de desenvolvimento consegue construir, e em
documentos que as áreas da agência conseguem ler, avaliar e aprovar**.

Traz o método, os scripts e um **exemplo resolvido de ponta a ponta**: o Reajusta, sistema do reajuste tarifário
anual da AGENERSA (RJ), com o contrato-piloto Águas de Paraty.

## O que você encontra aqui

| Para quem | Comece por |
|---|---|
| Quem vai **avaliar** a especificação do caso de referência (gestão, área técnica, Procuradoria, TI) | [`saida/documentos_para_avaliacao/00_Guia_de_avaliacao.pdf`](saida/documentos_para_avaliacao/00_Guia_de_avaliacao.pdf) e o caderno do seu público |
| Quem vai **replicar** o método no próprio órgão | [Visão geral](docs/metodologia/00_VISAO_GERAL.md) e [roteiro](docs/metodologia/ROTEIRO_ESPECIFICACAO.md) |
| A **IA** do aluno (Claude Code, Codex ou equivalente) | [`AGENTS.md`](AGENTS.md) |
| Quem vai **desenvolver** o sistema | [`especificacao/README.md`](especificacao/README.md) e [`especificacao/AGENTS_DESENVOLVIMENTO.md`](especificacao/AGENTS_DESENVOLVIMENTO.md) |

## Metodologia

| Capítulo | Assunto |
|---|---|
| [00 Visão geral](docs/metodologia/00_VISAO_GERAL.md) | Do processo mapeado ao sistema especificado; insumos que vêm do mapeamento; tipos de etapa |
| [01 Especificação do sistema](docs/metodologia/01_ESPECIFICACAO_SISTEMA.md) | Ondas; levantar os casos (extrair sem calcular, recalcular por script); fontes de dados; cadastro com trecho literal; layout do que o regulado envia; artefatos da especificação; o que falta para a IA de desenvolvimento |
| [02 Documentos para avaliação e pasta de saída](docs/metodologia/02_DOCUMENTOS_E_PASTA_DE_SAIDA.md) | Cadernos em PDF por público, planilha de parecer item a item, guia de avaliação; organização e nomes da pasta de saída; ciclo de avaliação até a versão aprovada |
| [Roteiro](docs/metodologia/ROTEIRO_ESPECIFICACAO.md) | Etapas E0 a E5 com comando, aceite, artefato e a PARADA 11 |

## Mapa do repositório

| Pasta | Conteúdo |
|---|---|
| [`docs/metodologia/`](docs/metodologia/) | **O método**: o que a IA do aluno lê para replicar |
| [`insumos/mapeamento/`](insumos/mapeamento/) | Saídas do mapeamento do processo-piloto (BPMN, fatos, avaliação, melhorias, normas, controles) usadas como origem dos requisitos |
| [`especificacao/`](especificacao/README.md) | **O pacote técnico** do caso de referência, fonte única de tudo: 15 documentos, ADRs, contratos (JSON Schema e OpenAPI), modelo Prisma, protótipo, fixtures de aceite e `documentos.json`, a definição das versões de leitura |
| [`saida/`](saida/LEIA-ME.md) | O que foi produzido, organizado pelo conteúdo e descrito no [`LEIA-ME.md`](saida/LEIA-ME.md): `levantamento/` (cálculos refeitos, cadastro do contrato, pleito e validação) e `documentos_para_avaliacao/` (PDFs e planilha) |
| [`scripts/`](scripts/) | `recalcular_reajuste.py`, `validar_pleito.py`, `gerar_documentos.py`, `consolidar_pareceres.py` |
| [`perfis/`](perfis/) | Parâmetros do órgão (feriados, fontes de índice). `rj_agenersa.py` é o caso de referência |
| [`tests/`](tests/) | Fixtures conferem com o levantamento, validador do pleito, documentos atualizados e íntegros, consolidação dos pareceres |
| [`docs/`](docs/) (raiz) | Relatórios do levantamento e a página da aula |

## Instalação

Python 3.12.

```bash
pip install -r requirements.txt
```

```bash
python -m playwright install chromium
```

```bash
python -m pytest tests
```

Os testes devem passar logo após o clone. Dois testes do validador são pulados sem as bases locais (cache das séries
públicas e textos dos contratos), que não vão para o git. Para gerar de novo os documentos de leitura:

```bash
python scripts/gerar_documentos.py
```

## Regras que não se negociam

- **Nenhum requisito sem origem.** Melhoria do TO-BE, norma, cláusula de contrato ou caso real com resultado conhecido.
- **Número só do código.** A especificação cita fatos e resultados de script.
- **Fonte única.** PDF e planilha são gerados do pacote técnico; ninguém edita o PDF.
- **Pasta de saída legível.** Subpastas pelo conteúdo, nomes `NN_Palavras.ext` que dizem o que o arquivo é, versão na
  capa e no rodapé (nunca no nome) e um `LEIA-ME.md` gerado que descreve cada arquivo.
- **Hipótese marcada.** Horas e custos são hipótese até a calibração com os servidores.
- **Dados pessoais fora do git.** Nomes de pessoas citadas nas peças foram trocados pela função. Pareceres com nome de
  avaliador, textos de contrato e caches ficam em pastas ignoradas.

## Sobre esta versão pública

Os números de processo SEI e as unidades da agência vêm da Pesquisa Pública do SEI. O desenvolvimento do sistema
(aula 3) fica em outro repositório.
