# ADR-0004: PostgreSQL com Prisma e versionamento do cadastro contratual

- **Situação:** aceita
- **Data:** 2026-10-31
- **Origem:** RF-CAD-01, RF-CAD-02, RF-CAD-03, RNF-03, RNF-11, RNF-14; `../saida/levantamento/contratos/paraty_008_2014.json`;
  `../docs/LEVANTAMENTO_MOTOR_CALCULO.md` §4 (o 1º termo aditivo dos Blocos mudou de uma vez data-base, Di/Do, energia e
  índice de químicos).

## Contexto

As regras de reajuste mudam por termo aditivo. Um ciclo de 2026 de Paraty aplica o contrato de 2014 com o que o
3º termo aditivo mudou (combinação multiplicativa e cronograma de realinhamento). Um ciclo antigo precisa ser
reproduzido com as regras da época (RNF-03), mesmo depois de um aditivo novo. Uma apuração que cita uma versão não pode
ver essa versão mudar depois.

## Decisão

1. **PostgreSQL** como banco único (dados, fila do pg-boss, trilha de auditoria). **Prisma** (última estável; 7.x em 01/11/2026) como acesso, com
   migrações versionadas (`prisma migrate`). O que o Prisma não expressa (gatilhos, `CHECK`, `REVOKE`) vai em SQL
   dentro da própria migração (`06_MODELO_DADOS.md` §5).
2. **Versão contratual herda da anterior.** Cada termo aditivo que muda o reajuste cria uma `VersaoContratual` com
   `herdaDeId`. A versão resolvida é a fusão rasa por atributo de topo, igual à do oráculo (`versao()` em
   `../scripts/validar_pleito.py`): `periodicidadeMeses`, `combinacao`, data-base, a `Formula` inteira e o cronograma
   de realinhamento inteiro. O que a versão define substitui; o que não define vem da anterior. A fusão é a função pura
   `resolverVersao` de `src/dominio/cad`.
3. **Versão usada é imutável.** Depois de citada por uma `Apuracao` ou por um `ResultadoValidacao`, a versão e suas
   partes (`Formula`, `Componente`, `ParcelaRealinhamento`, `FonteRegra`) não mudam nem são apagadas. Só a coluna
   `situacao` pode passar de `PUBLICADA` a `SUBSTITUIDA`. A regra é imposta duas vezes: no caso de uso (erro
   `VERSAO_EM_USO`) e por gatilho no banco. Correção vira versão nova.
4. **Só versão publicada é usada.** Apuração e validação usam versão `PUBLICADA`. Rascunho é livre para edição.
5. **A apuração guarda o que usou** (RNF-03): `versaoContratualId`, `versaoRegras`, `versaoLayout` e, em cada
   `TermoApuracao`, o identificador do valor mensal do pleito ou do valor da série externa (com a data da consulta)
   e da fonte do peso.
6. **Dado recebido é imutável.** Conteúdo do pleito, valores mensais, evidências, itens de validação, termos de
   apuração, edições de minuta e a trilha de auditoria só aceitam inserção.
7. **Trilha de auditoria só de inserção**, com encadeamento por hash (`hashAnterior`, `hash`) e sem permissão de
   `UPDATE`, `DELETE` ou `TRUNCATE` para o papel da aplicação (RNF-11).

## Alternativas consideradas

- **Versão como cópia completa (sem herança).** Mais simples de ler, mas o aditivo que muda só o realinhamento
  obrigaria a copiar pesos e trechos, e a cópia pode divergir do contrato. Rejeitada: o cadastro de Paraty já usa
  herança e o oráculo a resolve assim.
- **Event sourcing do cadastro.** Reprodutível, mas pesado para um cadastro que muda poucas vezes por contrato.
  Rejeitada.
- **Imutabilidade só no código.** Um script de manutenção ou uma migração apagaria o histórico. Rejeitada; o gatilho
  é a segunda barreira.
- **Outro ORM (Drizzle, TypeORM) ou SQL puro.** A stack da casa é Prisma. Mantida.

## Consequências

- Positivas: qualquer ciclo é refeito com as regras e os valores da época; a fonte de cada número fica rastreável
  (RNF-02).
- Negativas: corrigir um erro de digitação numa versão já usada exige versão nova, com o ato que a sustenta. O
  gestor do cadastro (PER-GCA) precisa entender isso; a tela TL-06 explica.
- Os gatilhos ficam fora do `schema.prisma`. Toda migração nova que recria essas tabelas tem de repor o SQL; o teste
  de integração do banco confere que o gatilho existe.
