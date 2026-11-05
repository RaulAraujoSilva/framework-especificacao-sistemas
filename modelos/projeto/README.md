# Especificação do sistema {{Nome do sistema}}

<!-- COMO PREENCHER: este é o README do seu projeto. Troque os marcadores e mantenha a tabela de pastas. O método
está no repositório framework-especificacao-sistemas (docs/metodologia/). -->

{{Uma frase: qual processo do órgão o sistema atende e o que ele muda}}.

Especificação feita pelo método do repositório
[framework-especificacao-sistemas](https://github.com/RaulAraujoSilva/framework-especificacao-sistemas): do processo TO-BE à
especificação completa, com documentos para as áreas avaliarem.

## Pastas

| Pasta | O que tem | Quem escreve |
|---|---|---|
| `insumos/` | Saídas do mapeamento do processo: TO-BE, melhorias, normas, indicadores, casos | copiado do mapeamento |
| `especificacao/` | O pacote de especificação, fonte única de tudo (15 documentos, ADRs, contratos, protótipo, `documentos.json`) | a equipe, documento por documento |
| `saida/levantamento/` | Casos reais com resultado conhecido, regras com trecho literal, conferências refeitas por script | extração com fonte + scripts |
| `saida/documentos_para_avaliacao/` | PDFs por público e planilha de parecer | gerado por script; não editar |
| `saida/pareceres/` | Planilhas devolvidas pelas áreas e o consolidado | fora do git (nome dos avaliadores) |

## Comandos

```bash
python <framework>/scripts/conferir_especificacao.py --projeto .
```

```bash
python <framework>/scripts/gerar_documentos.py --projeto .
```

```bash
python <framework>/scripts/consolidar_pareceres.py --projeto .
```

## Situação

| Etapa | Situação |
|---|---|
| Insumos do processo | {{pendente, em andamento ou concluída}} |
| Levantamento de casos e regras | {{...}} |
| Pacote de especificação | {{...}} |
| Avaliação pelas áreas | {{...}} |
