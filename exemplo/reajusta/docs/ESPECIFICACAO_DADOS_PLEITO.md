# Contrato-piloto e especificação dos dados do pleito de reajuste (P01, onda 1)

Rascunho 0.1. São dois pontos da especificação do motor de cálculo:
- o contrato em que o conceito é testado;
- o que a agência pede à concessionária, e em que formato, para que o pleito seja processado sem digitação.

Os resultados saem de `scripts/validar_pleito.py`, que roda sobre os arquivos a seguir:
- o layout `saida/levantamento/pleito/pleito_reajuste.schema.json`;
- o exemplo real `exemplo_paraty_2026.json`;
- o cadastro `saida/levantamento/contratos/paraty_008_2014.json`.

## 1. Contrato-piloto: Águas de Paraty (Contrato de Concessão nº 008/2014)

| Critério | Águas de Paraty | Águas da Imperatriz | Vale do Café / Centro Sul | Blocos 1 a 4 | Águas da Condessa |
|---|---|---|---|---|---|
| Ciclos com deliberação na base | 4 (2022 a 2025) | 2 | 4 | não levantado | 4 |
| Ciclos com trilha completa no SEI | 2 | 1 | 2 | 1 cada | 1 |
| Contrato e aditivos na base | contrato, 3 aditivos, Anexo X com os pesos | contrato e 1 aditivo | contrato | contrato, interdependência, 1 aditivo | falta o contrato-base |
| Fórmula | paramétrica, 6 componentes | paramétrica, 6 componentes | índice único (IPCA-E) | paramétrica, 5 componentes, mais ITS e IDG | paramétrica, 6 componentes |
| Fontes exercitadas | pública, paga, ANEEL e realinhamento | as mesmas | só pública | todas, mais preço da CEDAE e bases de economias | as mesmas |
| Recálculo | 2025 confere; 2022 diverge (caso de teste negativo) | confere | confere | parecer final em imagem | confere |

**Por que Paraty:**
- tem a história mais longa;
- todas as regras estão em texto na base do Especialista: a cláusula 20 com os índices e códigos das séries e a regra do terceiro mês anterior, os pesos literais no Anexo X e o cronograma do realinhamento no 3º termo aditivo. Os 12 trechos citados no cadastro foram achados literalmente;
- exercita os quatro tipos de fonte;
- já tem um caso de erro real para o motor pegar (2022).

**O que fica pendente em Paraty:**
- o componente de energia: a composição usada não está nos autos, e o pedido de alteração do IEE (SEI-480002/003110/2024) foi remetido à revisão ordinária;
- o 1º e o 2º termos aditivos, que trazem as parcelas anteriores de realinhamento, ainda não entraram no cadastro.

**Águas da Imperatriz** é o segundo contrato da mesma família, para provar que o motor generaliza trocando só o cadastro. Os pesos e os códigos são outros, mas em out/2025 os índices são os mesmos de Paraty. O pleito dela é o mais completo da coorte: memória de cálculo, séries mensais e cálculo da energia com as resoluções da ANEEL anexadas.

## 2. Por que especificar o pleito

Hoje o pleito chega como ofício em PDF, e a memória de cálculo vem em planilha ou em imagem. Na coorte:
- em Paraty 2025, a CAPET teve de pedir os arquivos em Excel por ofício, com prazo de 3 dias úteis;
- 12 memórias de cálculo estão em planilha, e os pareceres finais dos Blocos trazem as tabelas em imagem;
- as séries vêm só com os meses das pontas, e cada processo dá outro nome e outro código à mesma série;
- a energia vem sem a resolução da ANEEL nem a regra de composição;
- as casas decimais variam: o preço da água com 2 casas muda o IR do Bloco 1 de 4,80% para 4,78%.

**Base para exigir:** o art. 25 da Lei 11.445/2007 obriga o prestador de saneamento a fornecer à reguladora os dados necessários às suas atividades, na forma das normas e do contrato. O art. 30 da Lei 8.987/1995 dá ao poder concedente acesso aos dados técnicos, econômicos e financeiros da concessionária. Falta confirmar com a Procuradoria qual instrumento da agência fixa o layout: deliberação ou manual anexo.

## 3. O que a concessionária envia

Um pacote por pleito, anexado ao ofício no SEI:

| Arquivo | Formato | Conteúdo |
|---|---|---|
| `pleito.json` | JSON no layout 0.1 | contrato e versão contratual, vigência pretendida, tarifa em vigor, meses de referência, componentes com as séries, energia, resultado declarado, casas decimais, lista dos anexos com hash SHA-256 |
| `series.csv` | CSV UTF-8, separador vírgula, ponto decimal | `sigla,fonte,codigo_serie,mes,valor`: todos os meses de o até i, como publicados pela fonte |
| `energia.csv` | CSV | `reh,distribuidora,subgrupo,modalidade,posto,vigencia_inicio,tusd_mwh,te_mwh,bandeira_mwh,desconto_pct`: uma linha por resolução ou bandeira usada |
| `tabela_tarifaria.csv` | CSV | `categoria,faixa_inicio,faixa_fim,unidade,vigente,proposta` |
| exportação da fonte | PDF ou CSV original | a página ou o arquivo da FGV, do IBGE ou da ANEEL de onde saiu cada série (evidência) |
| memória de cálculo | PDF assinado | a mesma conta em forma legível, para o processo |
| publicação | PDF | jornal com a tabela publicada |

Regras gerais:
- **Formato:** datas em ISO 8601, números sem separador de milhar e valores como publicados pela fonte, sem arredondar.
- **Dados pessoais:** nenhum. A tarifa social entra como agregado.
- **Identificação:** a sigla de cada componente e a versão contratual são as do cadastro de parâmetros da agência. A agência publica o cadastro de cada contrato, e a concessionária não escolhe nome nem código.

## 4. O que o sistema confere na entrada

| Regra | Confere | Se falhar |
|---|---|---|
| V01 | o arquivo segue o layout | devolve |
| V02 | o cadastro se apoia no texto do contrato e a versão contratual existe | devolve |
| V03 | interstício de 12 meses de referência | devolve; aviso se for menos de 365 dias |
| V04 | os meses o e i são os da regra do contrato | devolve |
| V05 | componentes e códigos iguais aos do cadastro | devolve |
| V06 | série mensal completa | aviso |
| V07 | valor igual à série pública (IBGE, IPEA) | devolve; aviso se vier arredondado |
| V08 | valor igual ao de outros pleitos do mesmo mês (séries pagas) | aviso |
| V09 | IR recalculado com os pesos do cadastro | devolve |
| V10 | parcela de realinhamento do cronograma e total pela regra de combinação | devolve |
| V11 | energia com distribuidora, composição e resolução | devolve |
| V12 | tabela proposta = vigente × (1 + total) | devolve |

Um pleito sem erro segue para a CAPET já com o recálculo e os avisos. Um pleito com erro volta à concessionária com a lista do que corrigir, sem passar por análise.

## 5. Teste do conceito: Paraty 2026

O pleito real de Paraty para 2026 foi montado no layout com os números dos autos. As séries ficaram só com as pontas, porque foi o que o processo trouxe. O CNPJ e os hashes do exemplo são fictícios.

**Resultado: 10 ok, 5 avisos, 1 erro.** O pleito voltaria para complementação. Os testes do projeto repetem isto.

**O que fecha:**
- o IR recalculado, 3,9669%, arredondado a 3,967% como o declarado;
- o total de 6,7949%, pelo produto com a 2ª parcela de 2,72% do cronograma;
- os meses out/2024 e out/2025, iguais aos da regra do terceiro mês anterior;
- o IPC, achado na série pública;
- os dois IPA e o INCC, iguais aos dos pleitos de Imperatriz e Condessa do mesmo mês.

**O único erro: a energia.** O processo não diz de que distribuidora, com que composição e de que resolução saíram 511,75 e 471,91. É o mesmo ponto que o pedido de alteração do IEE levou à revisão ordinária.

**Os avisos:**
- O INCC veio com 2 casas (1.222,36), mas a série publica 3 (1.222,356).
- As séries vieram sem os meses intermediários.
- O interstício tem 12 meses de referência, mas só 354 dias: a tarifa em vigor desde 12/01/2025 e a nova a partir de 01/01/2026. A CAPET e a Procuradoria precisam dizer se o interstício se conta por mês de referência, como o 3º termo aditivo sugere ("a partir da referência janeiro"), ou por dia.
- Não há outro pleito que use o ICC-RJ de mão de obra (código 159401) para comparar.
- Falta a tabela tarifária.

Os testes também conferem que o validador barra um IR declarado diferente, um mês de referência errado, a parcela de realinhamento errada e um componente sem evidência.

## 6. Pendências

1. Regra da energia de Paraty com a CAPET: distribuidora, tarifa (TUSD + TE, com ou sem tributos e bandeira) e mês da resolução.
2. Contagem do interstício, por mês de referência ou por dia (CAPET e Procuradoria).
3. Cadastro de Águas da Imperatriz, para provar a generalização.
4. 1º e 2º termos aditivos de Paraty no cadastro, para validar os ciclos de 2022 a 2024.
5. Instrumento que torna o layout obrigatório (Procuradoria).
6. Canal de envio: anexos no peticionamento eletrônico do SEI, com o validador rodando na entrada, ou envio direto ao sistema com recibo.
