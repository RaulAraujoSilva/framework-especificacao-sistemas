# 01. Especificação do sistema do piloto

Fase 5 do método, em que o TO-BE vira sistema (no curso, capítulo 12). A priorização da automação, feita no [repositório de mapeamento](https://github.com/RaulAraujoSilva/mapeamento-processos-sei) (capítulo 11), aponta o tipo de processo-piloto. Este
capítulo transforma o piloto numa especificação que uma equipe, ou uma IA de desenvolvimento, consegue construir e
testar. A regra é a mesma do mapeamento: **nenhum requisito sem origem**. Cada requisito aponta uma cláusula de
contrato, uma peça de processo ou um caso real com resultado conhecido.

Caso de referência: motor de cálculo do reajuste tarifário anual (P01) da AGENERSA, contrato-piloto Águas de Paraty
(Contrato 008/2014). Leitura dos resultados: `docs/LEVANTAMENTO_MOTOR_CALCULO.md` e
`docs/ESPECIFICACAO_DADOS_PLEITO.md`. Página da aula: `docs/aulas/aula2_especificacao.html`. As versões de leitura para as áreas avaliarem saem pelo [capítulo 02](02_DOCUMENTOS_E_PASTA_DE_SAIDA.md).

## 1. Pré-requisitos

- Matriz de priorização e escolha do piloto registrada (PARADA 10 do mapeamento).
- Saídas do mapeamento do tipo-piloto copiadas para `insumos/mapeamento/` (lista em [00_VISAO_GERAL.md](00_VISAO_GERAL.md)).
- Avaliação AS-IS do tipo, com o potencial de IA por atividade: diz quais funções automatizar e em que ordem (ondas).
- Coorte do tipo com texto das peças (fase 2) e base normativa com os contratos e aditivos (fase 3).

## 2. Ondas

Especifique uma função de cada vez, começando pela de regra mais fechada e dado mais disponível. No caso de
referência:

| Onda | Função | Situação |
|---|---|---|
| 1 | Motor de cálculo do reajuste (refaz a conta, confere séries, aponta divergências) | especificada neste capítulo |
| 2 | Minutas de parecer jurídico, relatório, voto e deliberação | dados disponíveis; usa a saída da onda 1 |
| 3 | Conferência das tarifas nas faturas | falta canal de dados (1 fatura em 1.228 documentos) |

## 3. Levantar os casos: extrair sem calcular, recalcular por script

1. Para cada processo da coorte, um agente lê o pleito, os pareceres técnicos e a deliberação e grava
   `saida/levantamento/calculo/extracao_<processo>.json`. O agente copia fórmula, pesos, números-índice, variações e
   resultado **literalmente**, cita o documento de cada valor e não faz conta. Nenhum nome de pessoa.
2. `python scripts/recalcular_reajuste.py` refaz cada apuração de duas formas: pelos números-índice escritos e pelas
   variações escritas. Também testa a regra de combinação do total (produto ou soma) e grava `recalculo.csv` e
   `resumo.json`.
3. O que não fecha vira caso de teste. Classifique a causa: erro no texto, arredondamento de insumo ou regra
   diferente. Caso de referência: 24 de 28 cálculos conferem; as 4 divergências viraram os testes AT02 a AT04.

## 4. Fontes de dados de cada componente

O mesmo script classifica cada componente pela regra `FONTES_COMPONENTE` do `comum.py`, que o perfil pode trocar.
Depois procura cada número-índice citado na série pública da fonte, em `SERIES_PUBLICAS` (IPEADATA, IBGE SIDRA),
com cache em `dados/series/`.

| Disponibilidade | Tratamento no sistema |
|---|---|
| Pública | busca automática na API, com cache e data da consulta |
| Pública com regra (energia da ANEEL) | dados abertos mais a regra de composição do contrato, que precisa estar escrita |
| Paga (FGV Dados) | a série vem no pleito; o sistema compara com outros pleitos do mesmo mês. Assinatura é opcional, e a licença proíbe redistribuir |
| Outro reajuste | deliberação do outro processo, no próprio sistema |
| Documento | cláusula anexada ao pleito |

Caso de referência: 70 de 70 números-índice públicos achados nas séries.

## 5. Origem das regras: cadastro com trecho literal, versionado por aditivo

Para cada contrato do piloto, monte `saida/levantamento/contratos/<contrato>.json`. Cada parâmetro (periodicidade, mês de
referência, pesos, códigos de série, regra de combinação, cronograma de realinhamento) traz o documento e o
**trecho literal** que o sustenta. Uma versão nova é criada a cada termo aditivo que muda o reajuste; ela herda da
anterior e muda só o que o aditivo muda. O validador confere, palavra por palavra, que cada trecho existe no texto
do contrato (`TEXTOS_CONTRATOS` no `comum.py`).

Escolha do contrato-piloto: regras completas em texto, mais de um ciclo com deliberação, todas as famílias de fonte
exercitadas e, se houver, um caso de erro real. Escolha também um segundo contrato da mesma família, para provar
que o sistema troca de contrato trocando só o cadastro.

## 6. Especificar o que o regulado envia

O regulador pode exigir os dados no formato que a máquina lê (no saneamento, art. 25 da Lei 11.445/2007; nas
concessões, art. 30 da Lei 8.987/1995). O instrumento que torna o layout obrigatório é decisão da Procuradoria.

- Layout: `saida/levantamento/pleito/pleito_reajuste.schema.json` (JSON Schema 2020-12), com séries mensais completas,
  energia com resolução e regra de composição, resultado declarado, casas decimais e anexos com SHA-256.
- Validador: `python scripts/validar_pleito.py <pleito.json> <cadastro.json>` aplica V01 a V12 e grava
  `<pleito>.validacao.json`. Erro devolve o pleito para complementação; aviso segue para análise com destaque.
- Prova de conceito: o pleito real de Paraty 2026 no layout deu 10 ok, 5 avisos e 1 erro (energia sem fonte).

## 7. Artefatos da especificação

| Artefato | Norma de referência | No caso de referência |
|---|---|---|
| Requisitos funcionais e não funcionais, com origem | ISO/IEC/IEEE 29148 (requisitos); ISO/IEC 25010 (qualidade) | 14 RF, 8 RNF |
| Casos de uso e descrições | UML 2.5; descrição no estilo Cockburn | 6 casos de uso; UC02 detalhado |
| Modelo de domínio | UML 2.5 (diagrama de classes) | 12 classes; a versão contratual no centro |
| Sequência e estados | UML 2.5 | caso principal; estados do pleito |
| Layout de dados e validador | JSON Schema 2020-12 | layout 0.1; V01 a V12 |
| Protótipos de tela | baixa fidelidade, dados reais | fila, validação, memória de cálculo, cadastro |
| Testes de aceitação | ISO/IEC/IEEE 29119 | AT01 a AT08, com o resultado esperado tirado dos autos |

## 8. Pronta para desenvolvimento assistido por IA?

A especificação do caso de referência resolve bem a parte mais difícil, as regras de negócio. Elas já estão
executáveis: cadastro, layout, validador e testes com resultado conhecido. Para uma IA de desenvolvimento construir
o **sistema** com qualidade, e não só o motor, faltam artefatos que fixem as decisões que ela tomaria sozinha, e mal:

| Lacuna | Artefato que fecha | Por que importa para a IA |
|---|---|---|
| Stack e onde roda | ADRs (Architecture Decision Records) | sem decisão escrita, cada sessão escolhe um caminho |
| Fronteiras do código | arquitetura em camadas (domínio puro, portas, adaptadores) e diagrama de componentes C4 | mantém regra de cálculo fora de tela e de integração; permite trocar fonte de dados |
| Contratos entre partes | JSON Schema do cadastro e do resultado; OpenAPI da API | a IA gera código e testes a partir do contrato |
| Modelo físico | DDL a partir do diagrama de classes | evita esquema improvisado |
| Regras de código | `AGENTS.md` do repositório do sistema: linguagem do domínio, camadas, reuso, testes antes, portões de lint, tipos e cobertura | é o que a IA lê antes de cada tarefa |
| Fatiamento | backlog de histórias com critérios Dado/Quando/Então tirados dos testes de aceitação; Definition of Done | tarefas pequenas e verificáveis |
| Interface | guia de UI: design system de governo (padrão gov.br), acessibilidade (WCAG 2.2 AA, eMAG), inventário de telas com estados (vazio, carregando, erro, sem permissão), inventário de componentes reutilizáveis, guia de mensagens | telas consistentes entre si e com o serviço público |
| Operação | perfis de acesso, trilha de auditoria, LGPD, hospedagem | requisitos que a IA não deduz dos autos |

No caso de referência, essas lacunas estão fechadas no pacote [`especificacao/`](../../especificacao/README.md):
sistema completo do P01 (dez módulos), ADRs, arquitetura, modelo de dados em Prisma, contratos e OpenAPI, regras,
UX/UI com protótipo, testes, backlog e o arquivo de regras de código para a IA.

**PARADA 11 (área de negócio, Procuradoria e TI):** validar com a área técnica o cadastro, o layout, a regra da
energia e a contagem do interstício. Com a Procuradoria, decidir o instrumento que torna o layout obrigatório. Com a
TI, decidir a stack e onde o sistema roda. Ninguém dessas áreas lê Markdown num repositório: a avaliação é feita
pelos cadernos em PDF e pela planilha de parecer de `saida/documentos_para_avaliacao/`
([capítulo 02](02_DOCUMENTOS_E_PASTA_DE_SAIDA.md)). A aula de especificação termina aqui, com o pacote avaliado e
pronto para o desenvolvimento assistido por IA.

## 9. Limites

- A extração foi feita por IA e conferida pela aritmética, não por um segundo leitor.
- Nenhum valor de energia foi reproduzido pela base da ANEEL: a regra de composição usada nos pareceres não está nos
  autos.
- Textos de contrato vindos de OCR podem ter a fórmula ilegível. Reconstrua pela definição de cada índice e registre
  isso no cadastro.
- O cadastro e o layout do caso de referência ainda não foram validados com a área técnica do órgão.

## 10. Como replicar

1. Escolha a função da onda 1 pela avaliação AS-IS do piloto.
2. Extraia os cálculos de cada processo da coorte (formato do caso de referência em `saida/levantamento/calculo/`) e rode
   `python scripts/recalcular_reajuste.py`.
3. Ajuste `FONTES_COMPONENTE` e `SERIES_PUBLICAS` no perfil, se os índices do órgão forem outros.
4. Monte o cadastro do contrato-piloto com trechos literais. Aponte `TEXTOS_CONTRATOS` para os textos dos contratos
   (variável de ambiente ou perfil).
5. Escreva o pleito real no layout e rode `python scripts/validar_pleito.py`.
6. Confira com `python -m pytest tests -k validador`.
7. Escreva os artefatos da seção 7 e feche as lacunas da seção 8.
8. Gere os documentos para avaliação (`python scripts/gerar_documentos.py`, [capítulo 02](02_DOCUMENTOS_E_PASTA_DE_SAIDA.md)).
9. **PARADA 11**: as áreas avaliam pelos cadernos e devolvem a planilha de parecer.
