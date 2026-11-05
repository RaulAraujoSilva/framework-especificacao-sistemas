# Caso resolvido: Reajusta (exemplo, não modelo)

> **Este é um exemplo de outro domínio.** Serve para ver como fica cada artefato do método quando está pronto: a
> estrutura das seções, o nível de detalhe, a rastreabilidade e os documentos para avaliação. **Não copie conteúdo
> daqui para a sua especificação**: nomes, regras, fórmulas, prazos, perfis, módulos, telas, números ou frases. O seu
> projeto nasce de `modelos/projeto/` (`scripts/iniciar_projeto.py`). O conferidor barra termos deste exemplo na sua
> especificação. Leia antes o capítulo [05 da metodologia](../../docs/metodologia/05_USO_DO_EXEMPLO.md).

O Reajusta é o sistema do reajuste tarifário anual das concessões de saneamento de uma agência reguladora estadual
(AGENERSA, RJ), especificado a partir do processo mapeado no SEI. O contrato-piloto é Águas de Paraty (Contrato
008/2014).

## Onde ver cada etapa do método

| Etapa do método | Capítulo | Neste exemplo |
|---|---|---|
| Insumos do processo | [01](../../docs/metodologia/01_INSUMOS_DO_PROCESSO.md) | [`insumos/mapeamento/`](insumos/mapeamento/) |
| Levantamento de casos e regras | [02](../../docs/metodologia/02_LEVANTAMENTO_DE_CASOS_E_REGRAS.md) | [`saida/levantamento/`](saida/levantamento/), [`docs/LEVANTAMENTO_MOTOR_CALCULO.md`](docs/LEVANTAMENTO_MOTOR_CALCULO.md), [`docs/ESPECIFICACAO_DADOS_PLEITO.md`](docs/ESPECIFICACAO_DADOS_PLEITO.md), scripts em [`scripts/`](scripts/) |
| Planejamento e pacote de especificação | [03](../../docs/metodologia/03_PLANEJAMENTO_DA_ESPECIFICACAO.md) | [`especificacao/`](especificacao/README.md) |
| Documentos para avaliação | [04](../../docs/metodologia/04_DOCUMENTOS_E_PASTA_DE_SAIDA.md) | [`saida/documentos_para_avaliacao/`](saida/documentos_para_avaliacao/) e [`saida/LEIA-ME.md`](saida/LEIA-ME.md) |
| Como o caso foi feito, com os limites | — | [`docs/COMO_FOI_FEITO.md`](docs/COMO_FOI_FEITO.md) |
| Página da aula | — | [`docs/aulas/aula2_especificacao.html`](docs/aulas/aula2_especificacao.html) |

## Comandos (da raiz do repositório)

```bash
python scripts/conferir_especificacao.py --projeto exemplo/reajusta
```

```bash
python scripts/gerar_documentos.py --projeto exemplo/reajusta
```

```bash
python exemplo/reajusta/scripts/recalcular_reajuste.py
```

```bash
python exemplo/reajusta/scripts/validar_pleito.py exemplo/reajusta/saida/levantamento/pleito/exemplo_paraty_2026.json exemplo/reajusta/saida/levantamento/contratos/paraty_008_2014.json
```

Os scripts de `scripts/` deste exemplo (recálculo dos reajustes, validação do pleito e parâmetros em `perfis/`) são
**do domínio do exemplo**. O seu projeto terá os próprios scripts de levantamento, escritos para as suas regras. O
`--offline` do recálculo pula a busca nas séries públicas e zera as contagens de `resumo.json`; não o use para
regravar o resumo.

O `documentos.json` deste exemplo tem `"exemplo": true`: é o que desliga, só aqui, a barreira contra os termos do
próprio exemplo.
