# ADR-NNNN: {{Título da decisão, como frase afirmativa}}

<!-- COMO PREENCHER: copie este arquivo para adr/NNNN-nome-curto.md (quatro dígitos, em sequência, sem lacunas; nome
curto em minúsculas com hífen) e troque NNNN no título pelo mesmo número. Este modelo não entra no PDF: só os arquivos
adr/[0-9]*.md entram. Siga o capítulo 03 da metodologia, §3.7, item 8: toda escolha com alternativa real vira ADR
(stack, banco, autenticação, hospedagem, integração, design system, cadeia de suprimentos, uso de modelo de linguagem
quando houver). Escolha que depende da TI do órgão fica "proposta" até a avaliação. Pronto quando: o contexto diz o
problema sem antecipar a resposta; há pelo menos duas opções reais, com prós e contras; a decisão é verificável; as
consequências dizem o que muda no código, nos portões ou na operação; a origem cita os identificadores que motivaram a
decisão. Os ADRs do caso resolvido (exemplo/reajusta/especificacao/adr/) servem só de referência de formato: não copie
decisão nem frase deles. Depois de aceita, a decisão não é reescrita: decisão nova substitui a antiga num ADR novo, e a
antiga passa a "substituída por ADR-NNNN". -->

- **Situação:** {{Proposta, aceita, substituída por outro ADR ou retirada}}
- **Data:** {{AAAA-MM-DD}}
- **Quem decide:** {{Unidade ou instância que aprova}}

## Contexto

<!-- O problema e as forças em jogo: requisito, restrição da TI, norma, prazo, custo, equipe que vai manter. Escreva
como se a decisão ainda não tivesse sido tomada. -->

{{Qual é o problema, por que é preciso decidir agora e o que restringe a escolha}}.

## Opções consideradas

<!-- Pelo menos duas opções reais. "Não fazer nada" ou "manter como está" conta como opção quando for viável. -->

| Opção | A favor | Contra |
|---|---|---|
| {{Opção A}} | {{Vantagens}} | {{Desvantagens}} |
| {{Opção B}} | {{Vantagens}} | {{Desvantagens}} |

## Decisão

<!-- A escolha, dita de modo que se possa verificar no código ou na operação: versão, configuração, regra que um portão
confere. -->

{{Opção escolhida e como ela se aplica no sistema}}.

## Consequências

- **Positivas:** {{O que fica mais fácil ou mais seguro}}.
- **Negativas:** {{Custo, limitação ou risco aceito}}.
- **O que muda no código, nos portões ou na operação:** {{Pastas, configuração, testes ou rotinas afetados}}.
- **Quando revisar:** {{Condição ou data que reabre a decisão}}.

## Origem

<!-- Os identificadores que motivaram a decisão: RNF, RF, INT, DEC, SEG, e a seção do documento que pediu o ADR. -->

{{Requisitos, integrações, decisões pendentes e seções do pacote que levaram a esta decisão}}.
