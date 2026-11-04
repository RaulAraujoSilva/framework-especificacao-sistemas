# ADR-0007: Séries públicas com cache e marcação "a refazer"

- **Situação:** aceita
- **Data:** 2026-10-31
- **Origem:** INT-02, INT-03, INT-04; RF-SER-01, RF-SER-03, RF-SER-04; UC-20; RNF-03, RNF-06, RNF-13;
  `../docs/LEVANTAMENTO_MOTOR_CALCULO.md` §3 (70 de 70 números-índice públicos achados na série); `SERIES_PUBLICAS`
  de `../scripts/comum.py`.

## Contexto

V07 confere os valores do pleito contra a série pública da fonte. As APIs do IPEADATA (OData) e do IBGE SIDRA são
públicas, mas lentas e às vezes fora do ar. O oráculo usa tempo máximo de 120 s por consulta e cache em arquivo. Uma
validação precisa terminar em menos de 60 s com as séries em cache (RNF-13), e a fonte fora do ar não pode travar o
fluxo (RNF-06). A fonte pode revisar um valor publicado; a apuração antiga tem de continuar reproduzível.

## Decisão

1. **Catálogo de séries** em `SerieExterna` (base, código, licença) e **valores** em `ValorSerieExterna`, com mês, valor,
   casas publicadas e `consultadaEm`.
2. **O job JOB-01 (UC-20)** atualiza o cache em horário agendado (`05_ARQUITETURA.md` §12), uma série por vez, com
   tempo máximo por consulta (`FONTES_TIMEOUT_S`, valor inicial 120 s, o mesmo do oráculo). A validação **não** espera
   a rede: lê o cache.
3. **Valor revisado pela fonte** não sobrescreve o antigo. O registro anterior ganha `substituidoEm` e um registro novo
   entra com a nova `consultadaEm`. A apuração aponta o registro exato que usou.
4. **Fonte indisponível ou mês ausente do cache.** O item de V07 fica `A_REFAZER`, com a data da última consulta. O
   pleito fica `A_RECONFERIR` (RF-SER-04) e o resto da validação segue. Quando o JOB-01 traz o mês que faltava, ele
   reenfileira a validação dos pleitos `A_RECONFERIR` que dependem daquela série.
5. **Mês certo.** O adaptador guarda o mês de cada valor: `VALDATA` no IPEADATA e o código do período (`D3C`) no SIDRA.
   V07 compara no mês o e no mês i, não em qualquer mês da série. Isso é mais estrito que o oráculo (DIV-01 em
   `05_ARQUITETURA.md` §16.4).
6. **ANEEL (INT-04)** segue o mesmo padrão: o JOB-01 baixa o arquivo de tarifas homologadas e bandeiras do portal de dados
   abertos e grava por resolução. A regra de composição da energia é parâmetro da versão contratual e depende de decisão
   da CAPET (PARADA 11). Até lá, V11 só confere se distribuidora, composição e resolução foram informadas.
7. Endereços e códigos de série ficam no cadastro (`SerieExterna`) e na configuração (`IPEADATA_URL_BASE`,
   `SIDRA_URL_BASE`, `ANEEL_URL_BASE`), nunca no código.

## Alternativas consideradas

- **Consultar a fonte na hora da validação.** Faz a validação depender da rede e estoura RNF-13. Rejeitada.
- **Sobrescrever o valor revisado.** Quebra a reprodutibilidade (RNF-03). Rejeitada.
- **Bloquear o pleito até a fonte voltar.** Contraria RNF-06. Rejeitada; a marcação "a refazer" deixa a análise
  seguir e mostra o que falta conferir.

## Consequências

- Positivas: validação rápida e reprodutível; tela TL-14 mostra a situação de cada série e a data da última consulta.
- Negativas: um valor publicado no mesmo dia pode ainda não estar no cache. A conferência fica "a refazer" até o
  próximo JOB-01, ou até o administrador disparar a atualização pela TL-14.
