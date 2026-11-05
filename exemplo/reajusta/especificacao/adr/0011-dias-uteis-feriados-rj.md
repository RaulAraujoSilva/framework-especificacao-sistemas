# ADR-0011: Dias úteis com calendário de feriados do Rio de Janeiro

- **Situação:** aceita; a prorrogação dos prazos em dias corridos que vencem em dia sem expediente é decisão aberta
  (DEC-05 de `08_REGRAS_NEGOCIO.md`).
- **Data:** 2026-10-31
- **Origem:** RF-PRZ-01, RF-PRZ-03 a RF-PRZ-08, RF-IND-01; N-P01-15 (Instrução Normativa AGENERSA nº 115/2024, art.
  1º); N-P01-07, N-P01-12; requisitos R-P01-04 a R-P01-07, R-P01-16, R-P01-20 (`../insumos/mapeamento/normas_P01.json`);
  calendário do perfil `../perfis/rj_agenersa.py`; funções `somar_du` e `dias_uteis` de `../scripts/comum.py`.

## Contexto

O sistema conta prazos e mede indicadores. São duas contas diferentes:

- **Contagem de prazo processual**, que diz quando um prazo vence. Para os atos dos interessados (recorrer, falar nos
  autos, cumprir providências), a IN AGENERSA nº 115/2024 manda excluir o dia do início, incluir o do vencimento e
  considerar só os dias úteis (N-P01-15). Outros prazos de norma são em dias corridos (por exemplo, o pronunciamento em
  30 dias do pleito, R-P01-05).
- **Medição** de duração e espera (indicadores I-P01, fatos do AS-IS). O mapeamento mediu em dias úteis com a função
  `dias_uteis` do oráculo, que conta os dias úteis de `[início, fim)` (semântica de `numpy.busday_count`), e
  `somar_du`, que avança para o dia útil seguinte antes de somar.

Os feriados que fecham o expediente da agência estão no perfil do órgão: móveis contados da Páscoa (Carnaval, nos dois
dias; Sexta-feira Santa; Corpus Christi) e fixos nacionais, estaduais e do município do Rio.

## Decisão

1. **Calendário em tabela**, `Feriado` (proposto), com data, nome, abrangência (nacional, estadual, municipal, ponto
   facultativo) e fonte. O seed gera os anos do perfil a partir das regras de `../perfis/rj_agenersa.py`. O PER-ADM
   acrescenta ponto facultativo ou feriado decretado pela tela TL-15, com o ato como fonte.
2. **Datas civis, sem fuso no domínio.** O domínio trabalha com `DataCivil` (`AAAA-MM-DD`) e `Mes` (`AAAA-MM`), nunca
   com `Date` do JavaScript. A conversão do instante para data civil é feita na borda, com `FUSO_HORARIO`
   (`America/Sao_Paulo`).
3. **Funções puras em `src/dominio/comum/calendario.ts`**, que recebem o calendário como argumento:
   - `contarDiasUteis(inicio, fim, calendario)` e `somarDiasUteis(inicio, n, calendario)`: mesma semântica do oráculo,
     usadas na medição (RF-IND-01) e conferidas contra `dias_uteis` e `somar_du` no teste de paridade;
   - `vencimentoPrazo(marcoInicial, regra, calendario)`: contagem processual. Em dias úteis, exclui o dia do início,
     conta só dias úteis e inclui o do vencimento (N-P01-15). Em dias corridos, conta os dias corridos a partir do dia
     seguinte ao início.
4. **Cada prazo diz como conta.** A `RegraPrazo` (proposto) traz duração, unidade de contagem (`DIAS_UTEIS` ou
   `DIAS_CORRIDOS`), marco inicial, marco final, dono e fonte normativa, uma por linha do quadro RN-PRZ-02 de
   `08_REGRAS_NEGOCIO.md`. Nenhum prazo está escrito no código.
5. **Prazo em dias corridos que vence em dia sem expediente:** o vencimento nominal não é prorrogado; o alerta "vence
   hoje" sai no primeiro dia útil seguinte (RN-PRZ-01, RN-TRA-03). A prorrogação é decisão da Procuradoria (DEC-05).
6. **Ponto facultativo** (Carnaval) conta como dia sem expediente, como no perfil do órgão. Mudar isso é decisão da
   Secretaria Executiva, registrada como alteração da tabela.

## Alternativas consideradas

- **Biblioteca de feriados nacionais.** Não cobre os feriados estaduais e municipais nem os pontos facultativos.
  Rejeitada.
- **Uma função só para prazo e medição.** As duas contas dão resultados diferentes no mesmo intervalo. Misturar quebra
  a paridade dos indicadores ou conta prazo errado. Rejeitada.
- **Calendário no código.** Muda por decreto. Rejeitada.

## Consequências

- Positivas: prazo com fonte normativa e calendário auditável; indicadores comparáveis com a linha de base do AS-IS.
- Negativas: o calendário precisa ser mantido a cada ano (o seed cobre os anos do perfil; o PER-ADM recebe alerta
  quando falta o ano seguinte).
- A regra de contagem dos prazos internos da agência (Procuradoria, CAPET) está nos requisitos R-P01 em dias corridos;
  se a Procuradoria decidir outra contagem, muda só a `RegraPrazo`.
