# Levantamento para a especificação do motor de cálculo do reajuste anual (P01)

Primeira onda da especificação do sistema do piloto P01. As três funções escolhidas na avaliação AS-IS, em ondas:

1. motor de cálculo do reajuste (atividade t2, CAPET);
2. minutas de parecer jurídico, relatório, voto e deliberação (t3 e t8);
3. conferência das tarifas nas faturas (t10).

Este documento trata da onda 1 e registra, para as ondas 2 e 3, só as fontes de dados.

Os números saem de `scripts/recalcular_reajuste.py` e ficam em `saida/levantamento/calculo/`: `recalculo.csv`, `componentes.csv` e `resumo.json`.

A entrada são as extrações `extracao_<processo>.json`, uma por processo da coorte. Cada uma traz a fórmula, os pesos, os números-índice, as variações e o IR de cada apuração (pleito, pareceres da CAPET, deliberação), copiados do texto das peças. Na extração, nenhum valor é calculado. O script não faz nenhum julgamento.

## 1. Casos

A coorte do P01 tem 18 processos com trilha nativa no SEI. Destes, 17 têm cálculo de reajuste com números no texto. O processo SEI-220007/001126/2023 trata só da aplicação do índice de tarifa social.

| Família de fórmula | Processos | Componentes | Exemplo |
|---|---|---|---|
| Índice único IBGE (IPCA, IPCA-E) | 5 | 1 | resíduos sólidos (Vale do Café, Centro Sul) e CEDAE interior |
| Índice único IGP-M com resíduo de decisão judicial | 2 | 2 | CEG e CEG Rio (gás); o reajuste incide só sobre a margem |
| Paramétrica de 6 componentes | 4 | 6 | Águas de Paraty (2022 e 2025), Imperatriz, Condessa |
| Paramétrica dos Blocos, com ITS e IDG | 4 | 5 + ITS e IDG | Águas do Rio 1 e 4, Iguá (Bloco 2), Rio+ (Bloco 3) |
| Paramétrica do preço da água da CEDAE | 2 | 3 | preço no atacado para os Blocos (acordo coletivo, energia, IPCA) |

Nas 11 apurações em que o texto traz o IR, os outros componentes e o total, o total sempre fecha pela multiplicação: (1 + IR) × (1 + realinhamento) × (1 + ITS) − 1. As 2 apurações em que nem soma nem produto fecham são as do gás, com resíduo (1 + A)/(1 + B). Mesmo assim, o texto de vários pareceres não escreve a regra, e as cartas de dois Blocos somam em vez de multiplicar. A regra de combinação tem de ser parâmetro do contrato, não inferência.

## 2. O cálculo é reproduzível?

Foram 33 apurações com números. Em 28 delas o IR está escrito e os componentes estão completos. **Em 24 o IR recalculado bate com o escrito até 0,01 ponto percentual.** As 4 que não batem:

| Processo e peça | IR escrito | Recalculado | Causa |
|---|---|---|---|
| SEI-220007/004053/2022, parecer da CAPET | 10,37% | 9,56% pelos números-índice | O parecer escreveu −0,0085 para a variação da energia, mas os índices citados dão −0,0840. Para o IPC escreveu 0,0546, mas os índices dão 0,0505. Os números-índice do IPC e do INCC citados no parecer batem com a série pública. Foram deliberados 10,37% (cenário B). **Confirmar com a CAPET pela planilha anexa, que não foi extraída.** |
| SEI-480002/009058/2025, parecer da CAPET | 4,1245% | 5,3195% | Os índices do próprio parecer dão 5,3195%, que foi o percentual deliberado. É erro de digitação no texto. |
| SEI-480002/001912/2024 e 001913/2024, pleito | 4,80% | 4,78% | O preço da água da CEDAE foi escrito com 2 casas (2,23/2,09). A variação oficial é 6,75%. É arredondamento do insumo. |

Ainda não dá para reproduzir pelo texto os pareceres finais dos Blocos de novembro de 2024 (IRC de 8,4688%), porque as fórmulas e tabelas estão em imagem. O mesmo vale para as 12 memórias de cálculo em planilha juntadas aos processos. As duas coisas são o próximo insumo a extrair.

## 3. Fontes de dados de cada componente

São 57 componentes distintos (processo × componente). A disponibilidade de cada um vem de `comum.FONTES_COMPONENTE`:

| Disponibilidade | Componentes | Onde buscar |
|---|---|---|
| Pública | 24 | IBGE SIDRA (IPCA, tabela 1737; IPCA-E, tabela 3065), IPEADATA (INCC-DI geral, IPC-Brasil, IGP-M) |
| Pública com regra | 10 | ANEEL, tarifas homologadas e bandeiras. A composição (subgrupo, modalidade, TUSD + TE, desconto CDE, bandeira, média de 12 meses) muda de contrato para contrato |
| Assinatura | 17 | FGV Dados: mão de obra (ICC-RJ, ICC-SP, INCC mão de obra) e IPA-OG-DI de derivados de petróleo e de produtos químicos. Não estão na base aberta do IPEA; hoje o pleito anexa a série |
| Outro reajuste | 4 | preço da água no atacado da CEDAE, que é deliberado em processo próprio e entra nos Blocos |
| Documento | 2 | cláusula de reajuste salarial do acordo coletivo da CEDAE |

Dos números-índice citados nos pareceres para componentes públicos, **70 de 70 foram achados com o mesmo valor na série pública** da sua fonte. Por isso o motor pode buscar sozinho esses índices.

Sete processos têm todos os componentes em fonte pública ou em decisão: os 5 de índice único IBGE e os 2 do gás. As paramétricas dependem de assinatura da FGV e da regra de energia.

## 4. Viabilidade da onda 1

O caso é viável, com três condições:

1. **Séries da FGV.** Assinar o FGV Dados para os subíndices ou, enquanto isso, ler a série que a concessionária anexa e conferir a coerência entre os meses.
2. **Cadastro de parâmetros por contrato, com versão.** Cada contrato e cada termo aditivo precisam registrar:
   - pesos, códigos de série, regra do mês de referência (3º ou 4º mês anterior, data-base) e regra de combinação;
   - casas decimais;
   - acúmulo quando o reajuste anterior não foi homologado.

   O 1º termo aditivo dos Blocos, de outubro de 2024, mudou de uma vez a data-base, a definição de Di/Do, a energia (de A4 para A2) e o índice de químicos (de IPA para IPCA).
3. **Regra da energia validada com a CAPET.** É o componente com mais variação entre contratos e o único que exige montar a tarifa mês a mês.

Pontos a favor:
- os 24 cálculos reproduzidos e os 4 explicados formam desde já o **conjunto de testes de aceitação**;
- as duas divergências do texto mostram o ganho da conferência independente;
- o volume estimado do P01 é de cerca de 51 processos por ano em toda a agência (matriz de priorização da fase 4).

Ficam fora do motor, como entradas:
- o ITS e o IDG, apurados com bases da concessionária e pelo verificador independente;
- o resíduo judicial;
- o custo do gás e a conta gráfica.

## 5. Fontes de dados das ondas 2 e 3

**Onda 2 (minutas)** tem dado suficiente:
- os textos estão no SEI: 30 peças do parecer jurídico, 68 do relatório e voto, 63 da publicação, todas com texto;
- as deliberações anteriores do mesmo contrato estão na base do Especialista;
- os 20 requisitos legais com teste estão em `insumos/mapeamento/normas_P01.json`;
- a saída do motor da onda 1 entra como fato do relatório.

**Onda 3 (faturas)** depende de um canal de dados que hoje não existe:
- nos 1.228 documentos dos 18 processos há uma única peça de fatura;
- a conferência da CAPET pede as faturas por ofício e as recebe fora dos autos;
- as bases de economias dos Blocos chegam ao SEI, mas trazem dados pessoais.

O primeiro passo da onda 3 é definir com as concessionárias uma amostra de faturas, ou um extrato da base comercial sem dados pessoais.

## 6. Séries pagas sem assinatura e regras dos contratos

**Séries da FGV vindas no processo.** Os valores das séries pagas entram nos autos pelo pleito e são repetidos no parecer da CAPET. O mesmo índice no mesmo mês aparece com o mesmo número em processos de concessionárias diferentes:
- os dois IPA (derivados de petróleo e químicos) de out/2024 e out/2025 em Paraty, Imperatriz e Condessa;
- o ICC-SP de mão de obra nos Blocos 1, 2 e 4;
- o INCC de mão de obra em Imperatriz e Condessa, que diferem só no arredondamento.

Isso permite uma conferência cruzada entre processos, sem assinatura. Ela também pega erro: no Bloco 3, o pleito usa 1.331,066 para o ICC-SP e a CAPET usa 1.339,322 (mês diferente depois da mudança de data-base). O limite é que o número continua vindo das concessionárias; um erro copiado por todas não seria visto.

**Regras dos contratos na base do Especialista.** A tabela `contratos_concessao` da base de conhecimento liga contrato e aditivos em linha do tempo. A categoria tem 198 documentos: 24 contratos, 39 aditivos, 62 anexos. Ela cobre 11 das 12 concessionárias da coorte. O texto traz a cláusula de reajuste com:
- a definição de cada componente;
- o mês de referência (terceiro ou quarto mês anterior);
- a fonte e o código da série.

O 1º termo aditivo dos Blocos, de 15/10/2024, também está lá: data-base em 1º de dezembro e período excepcional de 27/04/2023 a 01/12/2024.

Lacunas:
- de Águas da Condessa só há os aditivos e o acordo; falta o contrato-base. A proposta comercial está entre os anexos;
- os pesos ficam na proposta comercial ou em anexo, não na cláusula;
- parte do texto é OCR de página digitalizada, com a fórmula ilegível (Paraty);
- a linha do tempo junta os Blocos 1 e 4 na mesma concessionária e data os aditivos de 2024 pelo ano do contrato (2021). O cadastro de parâmetros tem de ser por contrato, não por concessionária.

## 7. Limites

- A extração foi feita por leitura das peças, com cada valor ligado ao documento. Não houve conferência independente por um segundo leitor; o recálculo confere a aritmética, não a transcrição.
- O componente de energia não foi conferido contra a base da ANEEL: a composição exata usada em cada contrato ainda é desconhecida.
- Horas e custos da matriz de priorização continuam sendo hipótese até a calibração com servidores.
