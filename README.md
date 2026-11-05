# Especificação de sistemas a partir do processo TO-BE

Framework para levar um processo mapeado a uma **especificação completa de sistema**: escopo, perfis, casos de uso,
requisitos, regras, estados, componentes, dados, contratos, telas, testes, backlog, operação e segurança. A
especificação sai pronta para uma equipe, ou uma IA de desenvolvimento, construir. E sai também em **documentos que
as áreas do órgão conseguem ler, avaliar e aprovar**: cadernos em PDF por público e uma planilha de parecer item a
item.

É a segunda parte do curso de processos na administração pública. A primeira,
[mapeamento-processos-sei](https://github.com/RaulAraujoSilva/mapeamento-processos-sei), mapeia o processo, avalia o
AS-IS, desenha o TO-BE e escolhe o que automatizar.

## Como usar

O aluno traz o **seu processo** e indica este repositório à IA dele como referência de método e de saída. O
trabalho acontece num **projeto próprio**, criado a partir dos modelos:

```bash
python scripts/iniciar_projeto.py ../meu-sistema --sistema "Nome do sistema" --orgao SIGLA
```

```bash
python scripts/conferir_especificacao.py --projeto ../meu-sistema
```

```bash
python scripts/gerar_documentos.py --projeto ../meu-sistema
```

| Para quem | Comece por |
|---|---|
| A **IA** do aluno (Claude Code, Codex ou equivalente) | [`AGENTS.md`](AGENTS.md) |
| Quem vai **especificar** o sistema do próprio processo | [Visão geral](docs/metodologia/00_VISAO_GERAL.md) e [roteiro](docs/metodologia/ROTEIRO_ESPECIFICACAO.md) |
| Quem quer **ver o resultado** de uma especificação pronta | [`exemplo/reajusta/`](exemplo/reajusta/LEIA-ME.md) e os PDFs em `exemplo/reajusta/saida/documentos_para_avaliacao/` |

## Metodologia

| Capítulo | Assunto |
|---|---|
| [00 Visão geral](docs/metodologia/00_VISAO_GERAL.md) | Como usar o framework; fluxo do TO-BE à especificação aprovada; tipos de etapa |
| [01 Insumos do processo](docs/metodologia/01_INSUMOS_DO_PROCESSO.md) | O que trazer do TO-BE e o mínimo para começar |
| [02 Levantamento de casos e regras](docs/metodologia/02_LEVANTAMENTO_DE_CASOS_E_REGRAS.md) | Função da primeira onda; extrair sem calcular; oráculo por script; regras com trecho literal; dado que vem de fora |
| [03 Planejamento da especificação](docs/metodologia/03_PLANEJAMENTO_DA_ESPECIFICACAO.md) | **A cadeia de derivação** do TO-BE a cada artefato (escopo, perfis, casos de uso, requisitos, regras, domínio, estados, componentes, API, telas, testes, backlog, operação, segurança); convenção de identificadores; o que o conferidor verifica |
| [04 Documentos para avaliação e pasta de saída](docs/metodologia/04_DOCUMENTOS_E_PASTA_DE_SAIDA.md) | Cadernos em PDF por público, planilha de parecer, guia; organização e nomes da pasta de saída; ciclo de avaliação |
| [05 Uso do caso resolvido](docs/metodologia/05_USO_DO_EXEMPLO.md) | O que aproveitar do exemplo e as barreiras que impedem o conteúdo dele de vazar para a sua especificação |
| [Roteiro](docs/metodologia/ROTEIRO_ESPECIFICACAO.md) | Etapas E0 a E4 com comando, aceite, artefato e as PARADAs |

## Mapa do repositório

| Pasta | Conteúdo |
|---|---|
| [`docs/metodologia/`](docs/metodologia/) | O método |
| [`modelos/projeto/`](modelos/projeto/) | Estrutura do projeto do aluno: os 15 documentos de especificação, o README do pacote, o modelo de ADR, o protótipo e o `documentos.json`, com marcadores `{{...}}` e orientação de preenchimento. Neutros de domínio (há teste que garante) |
| [`scripts/`](scripts/) | `iniciar_projeto.py`, `conferir_especificacao.py` (rastreabilidade e isolamento do exemplo), `gerar_documentos.py` (PDFs, planilha e índice), `consolidar_pareceres.py` |
| [`exemplo/reajusta/`](exemplo/reajusta/LEIA-ME.md) | Caso resolvido de outro domínio, de ponta a ponta. Só referência de forma e de nível de detalhe |
| [`tests/`](tests/) | Testes do framework (modelos neutros, conferidor, iniciação, planilha, consolidação) e do caso resolvido |

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

Os testes devem passar logo após o clone. Dois testes do caso resolvido são pulados sem as bases locais dele (cache
de séries e textos de contrato), que não vão para o git.

## Regras que não se negociam

- **Nenhum requisito sem origem.** Melhoria do TO-BE, norma, cláusula, atividade do BPMN ou caso real.
- **Derivar, não inventar.** Cada artefato sai do anterior por uma regra escrita no capítulo 03.
- **O seu domínio, não o do exemplo.** O conferidor barra termos e marca trechos do caso resolvido.
- **Fonte única.** PDF e planilha são gerados da especificação; ninguém edita o PDF.
- **Pasta de saída legível.** Subpastas pelo conteúdo, nomes `NN_Palavras.ext`, versão na capa e no rodapé e um
  `LEIA-ME.md` gerado.
- **Hipótese marcada.** Horas, custos e valores propostos são hipótese até a calibração.
- **Dados pessoais fora do git.** Nenhum nome de pessoa na especificação; pareceres e textos com assinatura em pastas
  ignoradas.
