# ADR-0008: Séries pagas pela conferência cruzada, sem redistribuição

- **Situação:** aceita
- **Data:** 2026-10-31
- **Origem:** INT-07; RF-SER-02; RNF-04; V08; `../docs/LEVANTAMENTO_MOTOR_CALCULO.md` §3 e §6;
  `../docs/metodologia/01_ESPECIFICACAO_SISTEMA.md` §4.

## Contexto

Dos 57 componentes distintos da coorte, 17 vêm de assinatura da FGV Dados (mão de obra e IPA-OG-DI). A agência não
tem a assinatura, e a licença proíbe redistribuir. Hoje o pleito anexa a série. O mesmo índice no mesmo mês aparece
com o mesmo número em pleitos de concessionárias diferentes, o que permite conferir sem assinatura e já pegou erro (Bloco
3, ICC-SP de 1.331,066 contra 1.339,322).

## Decisão

1. **Conferência cruzada (V08).** O valor de uma série paga, em um mês, é comparado com os valores do mesmo código de
   série e do mesmo mês já recebidos em outros pleitos. Resultado `OK` se bate com algum; `AVISO` se não há outro
   pleito para comparar ou se não bate.
2. **De onde vêm os valores de comparação.**
   - Pleitos já validados no próprio sistema: os `ValorMensal` dos `ComponentePleito` com o mesmo código de série.
   - Histórico da coorte, importado uma vez por seed: valores de `../saida/levantamento/calculo/componentes.csv`, numa
     `SerieExterna` de base `PLEITOS`, com `origem` (processo e documento). O mês de cada valor sai do período de
     referência da extração (`periodo` em `recalculo.csv`, ligado por processo e documento), porque `componentes.csv`
     não traz o mês. A comparação por mês é mais estrita que a do oráculo (DIV-02 em `05_ARQUITETURA.md` §16.4).
3. **Licença.** Série de licença `RESTRITA` (FGV) e os valores pagos que vêm em pleitos ficam marcados (`licencaRestrita`).
   Eles:
   - aparecem só dentro do ciclo, para os perfis internos e para a concessionária dona do pleito;
   - não entram em painel de gestão (TL-13), exportação, API pública nem minuta de documento público, a não ser o
     valor que a própria concessionária enviou no seu processo;
   - não são enviados ao modelo de linguagem.

   A regra está na aplicação (filtro por licença nas consultas) e é testada.
4. **Assinatura opcional (INT-07).** Se a agência assinar a FGV Dados, um adaptador `fgv-dados` entra atrás da mesma
   porta `FonteSeriePublica` e V08 passa a ter uma fonte primária. A restrição de redistribuição continua.

## Alternativas consideradas

- **Exigir a assinatura antes de R1.** Bloqueia o piloto por compra. Rejeitada; a assinatura é opcional (RNF-14).
- **Aceitar a série do pleito sem conferência.** Perde o erro que a cruzada pega. Rejeitada.
- **Publicar as séries para as concessionárias conferirem entre si.** Viola a licença (RNF-04). Rejeitada.

## Consequências

- Positivas: conferência sem custo de licença e sem redistribuição.
- Negativas: o número continua vindo das concessionárias; um erro copiado por todas passa (limite registrado no
  levantamento §6). O primeiro pleito de um índice num mês sempre dá `AVISO`, como o ICC-RJ de Paraty 2026 (AT-06).
