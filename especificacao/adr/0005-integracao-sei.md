# ADR-0005: Integração com o SEI — manual na fase 1, webservice depois

- **Situação:** aceita para a fase 1; o webservice depende da TI (decisão aberta da PARADA 11).
- **Data:** 2026-10-31
- **Origem:** INT-01; RF-PLE-06, RF-DOC-02; RNF-07 (o sistema não assina nem protocola); `01_VISAO_ESCOPO.md` §3
  (assinatura e protocolo continuam no SEI).

## Contexto

O processo oficial é o do SEI. O sistema precisa do número do processo, das datas dos atos (marcos) e de entregar as
peças em formato que o SEI aceita. Não há garantia de que a TI libere o webservice do SEI no início, e o sistema não
pode depender disso para a release R1.

## Decisão

1. Uma porta `Sei` (`src/portas/externas/sei.ts`) com as operações de que o sistema precisa:
   - `vincularProcesso(cicloId, numeroSei)`;
   - `registrarJuntada(pecaId, numeroDocumentoSei, data)`;
   - `listarAndamentos(numeroSei)`;
   - `entregarPeca(peca)`.
2. **Fase 1, adaptador `sei-manual`.** O servidor exporta a peça em DOCX e PDF (RF-DOC-02), junta e assina no SEI e
   informa no sistema o número do documento e a data. O número do processo é digitado ao abrir o ciclo (RF-PLE-06) e
   conferido pelo formato. Os andamentos são registrados como marcos pela tela do ciclo (TL-02). A importação de um
   arquivo de andamentos exportado do SEI fica como opção, com formato a definir com a TI.
3. **Depois, adaptador `sei-webservice`**, se a TI liberar o webservice do SEI para o sistema: consulta do processo e
   dos andamentos e inclusão do documento como minuta não assinada. A escolha é por `SEI_MODO`.
4. Em nenhum modo o sistema assina, protocola ou tramita em nome de alguém (RNF-07). Peça juntada pelo webservice
   entra sem assinatura; a assinatura é sempre no SEI, pela pessoa.
5. Todo marco tem `origem` (`MANUAL`, `SISTEMA`, `IMPORTACAO_SEI`) e autor, para a auditoria contínua saber de onde
   veio a data (RF-IND-02).

## Alternativas consideradas

- **Esperar o webservice para começar.** Bloqueia R1, que não precisa do SEI para validar e recalcular. Rejeitada.
- **Robô de tela (RPA) no SEI.** Frágil, depende de credencial de pessoa e pode violar a política de uso do SEI.
  Rejeitada.
- **Peticionamento eletrônico do SEI como canal do pleito.** É uma das opções em aberto para o canal de envio
  (`../docs/ESPECIFICACAO_DADOS_PLEITO.md` §6, pendência 6). Fica compatível: o validador roda sobre o pacote
  qualquer que seja o canal.

## Consequências

- Positivas: R1 e R2 funcionam sem integração; trocar para webservice é trocar adaptador.
- Negativas: na fase 1 há digitação do número do documento e da data. A tela pede o mínimo e confere o formato. A
  medição de indicadores (I-P01) depende da disciplina desse registro; o painel TL-13 mostra marcos faltantes.
