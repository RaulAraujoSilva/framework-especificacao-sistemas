# 02. Levantamento de casos e regras: o chão da especificação

Antes de especificar, prove que você entende a regra do processo, refazendo os casos reais. É o levantamento que
transforma "o sistema deve calcular o prazo" em "o sistema deve calcular o prazo assim, e nestes cinco casos o
resultado tem de ser este". Sem ele, os critérios de aceite são inventados e os testes não provam nada.

## 1. Escolher a função da primeira onda

Especifique uma função de cada vez. Comece pela que tem:

- **regra mais fechada**, escrita em norma ou contrato, com pouco julgamento;
- **dado mais disponível**, nos autos, em sistema ou em fonte pública;
- **maior peso** na avaliação AS-IS (tempo, retrabalho, erro).

Registre a escolha e as próximas ondas no documento 01 do pacote. As demais funções do processo entram na lista de
escopo, com a onda em que serão detalhadas.

## 2. Extrair os casos sem calcular

Para cada caso real da coorte, grave um arquivo em `saida/levantamento/casos/` com:

1. os valores **copiados literalmente** das peças (datas, quantias, percentuais, decisões), cada um com o documento
   de origem;
2. o **resultado** que os autos registram (o prazo concedido, o valor homologado, a decisão);
3. nenhuma conta, nenhuma interpretação e nenhum nome de pessoa.

Quem extrai não calcula. A separação é o que permite conferir: se a extração já vem "corrigida", o erro do
processo some e o teste perde o valor.

## 3. Refazer por script e classificar as divergências

Escreva um script que refaz o resultado de cada caso a partir dos valores extraídos e da regra escrita. Grave o
resultado em `saida/levantamento/conferencias/`. Cada caso termina numa de três situações:

| Situação | Significa | Vira |
|---|---|---|
| Confere | A regra escrita reproduz o resultado dos autos | Teste de aceitação com o resultado esperado |
| Diverge por erro no processo | Os autos têm erro de conta, de data ou de transcrição | Teste em que o sistema **acusa** o erro |
| Diverge por regra diferente | A regra aplicada não é a escrita (arredondamento, contagem, interpretação) | Decisão pendente (`DEC`) com dono, e teste com o padrão provisório |

Esse script é o **oráculo**: a implementação do sistema tem de dar o mesmo resultado nos mesmos casos, e a
divergência entre os dois se explica caso a caso.

## 4. Regras e parâmetros com trecho literal

Para cada norma ou contrato que governa a função, grave em `saida/levantamento/regras/` os parâmetros (prazos,
percentuais, condições, fórmulas, documentos exigidos). Cada parâmetro leva:

- o documento e o dispositivo (artigo, cláusula, item);
- o **trecho literal** que o sustenta, conferido palavra por palavra contra o texto (de preferência por script);
- a **vigência**: quando muda (alteração da norma, aditivo), cria-se uma versão nova, que herda da anterior e muda
  só o que mudou.

Texto de OCR ilegível ou norma omissa não se completa de cabeça: vira lacuna registrada e decisão pendente.

## 5. O que vem de fora: formato e validação

Quando o processo depende de dados que um terceiro envia (requerente, regulado, outro órgão), especifique:

- o **formato** em que o dado deve chegar, como esquema verificável (JSON Schema), com tipos, obrigatoriedade, casas
  decimais e anexos;
- as **validações** que o sistema aplica na entrada, cada uma com identificador, severidade (erro devolve, aviso
  segue com destaque) e a regra de onde vem;
- a **prova de conceito**: um caso real escrito no formato e validado por script.

A base legal que torna o formato obrigatório para o terceiro é decisão do jurídico do órgão. Registre-a como decisão
pendente até lá.

## 6. Fontes de dados

Para cada dado que o sistema usa, classifique a disponibilidade:

| Disponibilidade | Tratamento no sistema |
|---|---|
| Pública, com interface de dados | busca automática, com cache e data da consulta |
| Pública, sem interface | importação periódica com conferência |
| Paga ou restrita | o terceiro informa; o sistema confere por amostra ou por cruzamento |
| Interna (outro sistema do órgão) | integração, ou exportação manual na primeira onda |
| Documento | anexo com leitura assistida e conferência humana |

Cada fonte vira uma integração (`INT-nn`) no documento 09, com o tratamento de falha.

## 7. Limites a registrar

Diga o que o levantamento **não** prova. Exemplos: extração conferida só pela aritmética, sem um segundo leitor;
regra reconstruída por falta de texto legível; cadastro ainda não validado com a área de negócio. Esses limites vão
para o README do pacote.

## 8. Pronto quando

- [ ] A função da primeira onda está escolhida e justificada.
- [ ] Cada caso da coorte tem extração com origem de cada valor, sem conta e sem nome.
- [ ] O script refaz todos os casos e cada divergência tem causa classificada.
- [ ] Cada parâmetro tem trecho literal conferido e vigência.
- [ ] O dado que vem de fora tem formato e validações, provados com um caso real.
- [ ] Cada lacuna virou decisão pendente com dono.
