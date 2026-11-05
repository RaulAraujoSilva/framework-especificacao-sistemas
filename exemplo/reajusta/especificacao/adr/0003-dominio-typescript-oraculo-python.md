# ADR-0003: Domínio reimplementado em TypeScript, com o Python como oráculo

- **Situação:** aceita; o modo de arredondamento é decisão aberta (DEC-06 de `08_REGRAS_NEGOCIO.md`).
- **Data:** 2026-10-31
- **Origem:** briefing do pacote ("a implementação em Python é referência e oráculo"); `README.md` do pacote; RNF-01,
  RNF-03, RNF-12; `../scripts/validar_pleito.py`, `../scripts/recalcular_reajuste.py`.

## Contexto

As regras V01 a V12 e o recálculo já rodam em Python e foram provados contra os autos: 24 de 28 cálculos conferem e as
4 divergências viraram casos de teste (`../docs/LEVANTAMENTO_MOTOR_CALCULO.md` §2); o pleito de Paraty 2026 dá 10 ok,
5 avisos e 1 erro (`../saida/levantamento/pleito/exemplo_paraty_2026.validacao.json`). O sistema é TypeScript (ADR-0001).
O código de referência lê arquivo e rede dentro da regra (cache de séries, `componentes.csv`, textos dos contratos) e
usa ponto flutuante binário.

## Decisão

1. O domínio é reescrito em TypeScript puro, em `src/dominio`, como funções sem efeito colateral. Tudo que o Python lê
   de arquivo ou rede chega ao domínio como argumento, trazido pela aplicação por uma porta.
2. O Python fica como **oráculo**. Ele não roda em produção. Ele é usado nos testes de três formas
   (`05_ARQUITETURA.md` §16):
   - arquivos esperados (*golden*): os fixtures de aceite de `12_TESTES.md`, gerados pelo oráculo com
     `ferramentas/gerar_fixtures.py` e versionados;
   - teste diferencial no CI: o mesmo pleito alterado por gerador (fast-check) passa pelo oráculo e pelo sistema;
   - conferência do recálculo dos 28 cálculos de `../saida/levantamento/calculo/recalculo.csv`.
3. **Divergência é defeito do sistema** até prova em contrário. As únicas divergências aceitas estão listadas em
   `05_ARQUITETURA.md` §16.4 (DIV-01 a DIV-07) e cada uma precisa de aprovação humana. Divergência nova não entra
   sem decisão registrada.
4. **Aritmética decimal.** Percentuais, números-índice, pesos e tarifas são `Decimal` (decimal.js), nunca `number`.
   O texto do número recebido é guardado para contar as casas informadas (V07). O arredondamento é feito só por
   `arredondar(valor, casas, modo)` em `src/dominio/comum/decimal.ts`. O modo vem da fórmula da versão contratual
   (`Formula.modoArredondamento`); o padrão é meio para o par (`ROUND_HALF_EVEN`, RN-NUM-03 de `08_REGRAS_NEGOCIO.md`).
   Ele reproduz o `round()` do oráculo fora dos empates exatos e é a regra da ABNT NBR 5891. A confirmação é da CAPET
   (DEC-06). A tolerância de comparação é a de RNF-01 (0,01 ponto percentual, `comum.TOL_RECALCULO_PP`).
5. Cada resultado guarda `versaoRegras`, a versão semântica do pacote de regras do domínio
   (`src/dominio/ple/versao.ts`). Toda mudança de regra sobe essa versão (RNF-03).

## Alternativas consideradas

- **Serviço em Python (FastAPI) chamado pelo Next.js.** Reaproveita o código, mas traz duas stacks, dois deploys e o
  código de referência, que lê arquivo e rede dentro da regra, para produção. Rejeitada.
- **Python no navegador ou no servidor por WebAssembly (Pyodide).** Pesado e frágil para pandas e jsonschema.
  Rejeitada.
- **Reescrever sem oráculo, só com os fixtures.** Perde o teste diferencial, que pega casos que nenhum fixture cobre.
  Rejeitada.
- **`number` (ponto flutuante) no domínio, como o Python.** Paridade mais fácil, mas erro de representação em tarifa e
  em arredondamento de casas do contrato. Rejeitada; a tolerância de RNF-01 absorve a diferença no IR.

## Consequências

- Positivas: domínio sem dependência de framework e com teste rápido (RNF-12); a mesma regra é provada duas vezes, por
  duas implementações independentes.
- Negativas: a regra existe em duas linguagens. Quem muda a regra no sistema muda também o oráculo (no repositório do
  curso) ou registra a divergência. O CI precisa de Python para o job de paridade.
- O oráculo fica fixado num commit do repositório do curso (`oraculo/VERSAO`). Atualizar o commit é tarefa própria.
