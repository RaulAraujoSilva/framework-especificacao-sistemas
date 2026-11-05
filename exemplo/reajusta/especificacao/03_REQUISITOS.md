# 03. Requisitos

Detalhamento dos requisitos funcionais (RF-*) e não funcionais (RNF-*) de [01_VISAO_ESCOPO.md](01_VISAO_ESCOPO.md),
na forma da ISO/IEC/IEEE 29148: obrigação do sistema, origem, critério de aceite verificável, casos de uso, telas e
release. As regras com fórmula, mensagem e exemplo estão em [08_REGRAS_NEGOCIO.md](08_REGRAS_NEGOCIO.md) (RN-*); os
contratos de dados e a API em [07_CONTRATOS_API.md](07_CONTRATOS_API.md). Os testes de aceitação AT-* estão em
`12_TESTES.md`; as histórias HIS-* em `13_BACKLOG.md`.

**Origens usadas.** Melhorias do TO-BE `M-P01-01` a `18` (`insumos/mapeamento/melhorias_P01.json`); normas `N-P01-*` e
requisitos legais `R-P01-*` (`insumos/mapeamento/normas_P01.json`); indicadores `I-P01-*` e controles `Q-P01-*`
(`insumos/mapeamento/controles_P01.json`); regras `V01` a `V12` (`scripts/validar_pleito.py`); casos reais da coorte
(`saida/levantamento/calculo/recalculo.csv`, `insumos/mapeamento/casos_P01.json`); achados do levantamento
(`docs/LEVANTAMENTO_MOTOR_CALCULO.md`, `docs/ESPECIFICACAO_DADOS_PLEITO.md`); atividades `t1` a `t16` do BPMN
(`insumos/mapeamento/modelo_P01.json`).

**Convenção.** "Deve" é obrigatório. Item marcado "(proposto)" não está no documento-base nem nos insumos e depende de
confirmação. Horas e custos citados são hipótese até a calibração com servidores.

## Sumário

| Módulo | Requisitos | Release |
|---|---|---|
| MOD-PLE Pleitos | RF-PLE-01 a 06 | R1 |
| MOD-CAD Cadastro de contratos | RF-CAD-01 a 04 | R1 (alerta de data-base em R2) |
| MOD-CAL Motor de cálculo | RF-CAL-01 a 06 | R1 |
| MOD-SER Séries | RF-SER-01 a 04 | R1 |
| MOD-PRZ Prazos e tramitação | RF-PRZ-01 a 09 | R2 |
| MOD-DOC Documentos por modelo | RF-DOC-01 a 03 | R2 (ofício de complementação já em R1) |
| MOD-MIN Minutas assistidas | RF-MIN-01 a 05 | R3 |
| MOD-FAT Conferência de faturas | RF-FAT-01 e 02 | R4 |
| MOD-IND Indicadores e auditoria contínua | RF-IND-01 a 03 | R4 |
| MOD-ADM Administração | RF-ADM-01 a 03 | Transversal (desde R1) |
| Não funcionais | RNF-01 a 14 | todas |

---

## 1. MOD-PLE Pleitos

### RF-PLE-01 Receber o pleito como pacote

- **Descrição:** o sistema deve receber o pleito como pacote: `pleito.json` no layout 0.1
  (`contratos/pleito_reajuste.schema.json`) e os anexos (`series.csv`, `energia.csv`, `tabela_tarifaria.csv`,
  evidências da fonte, memória de cálculo assinada, publicação). Deve calcular o SHA-256 de cada arquivo, comparar com
  `anexos[].sha256` do pleito, guardar o pacote de forma imutável, registrar o marco `protocolo` e responder com o
  registro. O envio é idempotente pelo cabeçalho `Idempotency-Key`. Anexo com SHA-256 diferente do declarado gera item
  de erro de V01 "(proposto)".
- **Origem:** M-P01-10; Paraty 2025, em que a CAPET pediu a memória em Excel por ofício com prazo de 3 dias úteis; 12
  memórias em planilha e tabelas em imagem nos pareceres dos Blocos (`docs/ESPECIFICACAO_DADOS_PLEITO.md`, seção 2).
- **Critério de aceite:**
  1. O pacote de Paraty 2026 (`fixtures/paraty_2026.json`) enviado responde 201 com `sha256` e `confere` por anexo e
     cria o marco `protocolo`.
  2. Repetir o envio com a mesma `Idempotency-Key` e o mesmo corpo responde 200 com o mesmo registro; com corpo
     diferente, 409 `idempotencia-conflito`.
  3. Um anexo com conteúdo alterado depois do hash dá erro de V01 apontando o arquivo.
  4. Pacote com propriedade fora do layout ou dado pessoal responde 422 e nada é guardado (RNF-05).
- **UC:** UC-01 · **TL:** TL-03 · **Release:** R1 · **API:** `POST /ciclos/{ciclo_id}/pleitos`

### RF-PLE-02 Validar o layout (V01)

- **Descrição:** o sistema deve validar o `pleito.json` contra o JSON Schema do layout (Draft 2020-12, com `format`) e
  listar cada campo faltante ou fora do formato, com o caminho do campo (JSON Pointer) e mensagem legível. V01 com erro
  interrompe a validação (RN-V01, RN-VAL-00).
- **Origem:** V01; `docs/ESPECIFICACAO_DADOS_PLEITO.md`, seção 4; as séries vêm com nomes e códigos diferentes para o
  mesmo índice em cada processo.
- **Critério de aceite:**
  1. Paraty 2026 → V01 ok, "Layout 0.1 válido".
  2. Paraty 2026 sem `componentes[0].evidencia` → um item V01 erro com caminho `/componentes/0` e nenhuma regra
     seguinte executada (AT-05).
  3. Data `2026-13-01` em `vigencia_pretendida` → V01 erro de formato.
- **UC:** UC-02 · **TL:** TL-03, TL-04 · **Release:** R1

### RF-PLE-03 Aplicar V01 a V12 e registrar o resultado

- **Descrição:** o sistema deve aplicar as regras V01 a V12 (RN-V01 a RN-V12) na ordem, produzir os itens com
  situação ok, aviso ou erro e a decisão (`devolver`, `segue_para_analise`, `a_refazer`), e registrar o resultado no
  formato `contratos/resultado_validacao.schema.json`, com versão do layout, versão contratual e revisão do cadastro,
  versão das regras e séries usadas com data da consulta.
- **Origem:** V01 a V12; prova de conceito de Paraty 2026 (10 ok, 5 avisos, 1 erro); RNF-03.
- **Critério de aceite:**
  1. Paraty 2026 como está nos autos → 16 itens: 10 ok, 5 avisos, 1 erro (V11), decisão `devolver` (AT-06).
  2. Cada uma das 4 mutações do AT-05 dá erro na regra esperada: IR declarado 4,5% → V09; i = 2025-09 → V04; parcela
     6,30% → V10; sem evidência → V01.
  3. O resultado registrado valida contra `resultado_validacao.schema.json` e traz `versao_regras`, `versao_layout` e
     `series_usadas`.
- **UC:** UC-02, UC-03 · **TL:** TL-04 · **Release:** R1

### RF-PLE-04 Devolver o pleito com pendências

- **Descrição:** com decisão `devolver`, o sistema deve montar a lista de pendências (itens de erro, com o que corrigir)
  e a minuta do ofício de complementação por modelo (RF-DOC-01). O analista da CAPET confirma a devolução; o sistema
  registra o marco `devolucao`, abre o prazo de resposta (RN-PRZ-13) com dono e mantém o ciclo com dono enquanto
  espera (RN-TRA-02). O pleito com erro não segue para análise.
- **Origem:** M-P01-08 (rodada única), M-P01-10; AS-IS: diligências pela Secretaria em 61% dos casos e pelo gabinete em
  50% (`insumos/mapeamento/fatos_P01.json`).
- **Critério de aceite:**
  1. Para Paraty 2026, a minuta do ofício lista a pendência V11 (energia sem distribuidora, composição e resolução) e
     os avisos que a concessionária pode corrigir, com processo, contrato e prazo (AT-17).
  2. Sem confirmação do PER-ANA, nenhum ofício sai e o ciclo fica em `em_validacao` com a pendência visível.
  3. Resultado sem erro não oferece a ação de devolução.
- **UC:** UC-04 · **TL:** TL-04, TL-09 · **Release:** R1

### RF-PLE-05 Validação prévia pela concessionária

- **Descrição:** o sistema deve oferecer à concessionária a validação do pacote antes do envio, com as mesmas regras e
  a mesma versão do envio, sem registrar o pacote, o resultado nem os valores na base de conferência cruzada.
- **Origem:** M-P01-10 ("devolvem à concessionária, no mesmo dia, a lista do que falta"); Aula 2, UC01 ("ela pode rodar
  a mesma validação antes de enviar").
- **Critério de aceite:**
  1. A validação prévia do pacote de Paraty 2026 dá os mesmos 16 itens do AT-06, com `modo = previa` e sem `id`.
  2. Depois da prévia, nenhuma linha nova existe nas tabelas de pleito, resultado e valores (consulta direta ao banco).
  3. A prévia de um pacote com o bloco `energia` completo dá decisão `segue_para_analise`.
- **UC:** UC-01, UC-02 · **TL:** TL-03 · **Release:** R1 · **API:** `POST /pleitos/validacao-previa`

### RF-PLE-06 Abrir o ciclo e vincular o processo SEI

- **Descrição:** o sistema deve abrir o ciclo de reajuste de um contrato para uma vigência pretendida (no primeiro
  envio ou pela Secretaria) e vinculá-lo ao número do processo SEI no formato `SEI-NNNNNN/NNNNNN/AAAA`. Não pode haver
  dois ciclos abertos do mesmo contrato para a mesma vigência.
- **Origem:** glossário (ciclo = processo SEI); INT-01 fase 1 manual; RF-PRZ-02.
- **Critério de aceite:**
  1. Abrir o ciclo de Paraty com vigência 01/01/2026 e processo `SEI-480002/009982/2025` → 201; segundo pedido igual
     → 409.
  2. Número fora do formato → 400 com o campo apontado.
  3. O ciclo nasce com dono (Secretaria Executiva) e aparece na TL-01.
- **UC:** UC-01, UC-08 · **TL:** TL-01, TL-02 · **Release:** R1

---

## 2. MOD-CAD Cadastro de contratos

### RF-CAD-01 Contratos e versões com herança

- **Descrição:** o sistema deve manter contratos e versões contratuais no formato
  `contratos/cadastro_contrato.schema.json`. Cada versão nasce de um ato, aponta a anterior (`herda`) e é resolvida
  por herança rasa (RN-CAD-01). Versão publicada não muda; mudança gera versão nova. O motor troca de contrato trocando
  só o cadastro, sem mudar código.
- **Origem:** M-P01-09; 1º termo aditivo dos Blocos (15/10/2024), que mudou data-base, energia (A4 para A2) e índice de
  químicos (IPA para IPCA); `saida/levantamento/contratos/paraty_008_2014.json`.
- **Critério de aceite:**
  1. O cadastro de Paraty importado valida no schema; a versão `3TA-2024` resolvida tem os 6 componentes de
     `contrato-2014`, `combinacao = multiplicativa` e 7 parcelas.
  2. Águas da Imperatriz com cadastro próprio dá V09 ok com 2,79% sem mudança de código (AT-07; o cadastro
     é criado pela HIS-CAD-04).
  3. Tentativa de alterar versão publicada → 409.
- **UC:** UC-06 · **TL:** TL-06 · **Release:** R1

### RF-CAD-02 Fonte com trecho literal conferido (V02)

- **Descrição:** o sistema deve exigir, para cada parâmetro, documento e trecho literal, e conferir o trecho no texto
  do documento da base do Especialista (INT-05) com espaços normalizados (RN-CAD-02). Versão com trecho não achado
  fica em rascunho e não pode ser publicada nem usada por pleito.
- **Origem:** V02; 12 de 12 trechos do cadastro de Paraty achados literalmente; texto de OCR com fórmula ilegível em
  Paraty (`docs/LEVANTAMENTO_MOTOR_CALCULO.md`, seção 6).
- **Critério de aceite:**
  1. Conferência do cadastro de Paraty → 12 achados, 0 não achados.
  2. Trocar "2,72%" por "2,73%" no trecho da 2ª parcela → não achado; publicação recusada com 422 `regra-negocio`
     (RN-CAD-02).
  3. Base indisponível → V02 aviso "trechos não conferidos" e item a refazer.
- **UC:** UC-06 · **TL:** TL-06 · **Release:** R1

### RF-CAD-03 Cronograma de realinhamento por versão

- **Descrição:** o sistema deve manter, por versão, o cronograma de realinhamento (`parcela`, `referencia` AAAA-MM,
  `pct`) com fonte por parcela, e registrar em que ciclo cada parcela foi aplicada (RN-CAL-04).
- **Origem:** 3º Termo Aditivo de Paraty, cláusula quarta (6,30% em jan/2025; 2,72% de jan/2026 a jan/2031);
  `scripts/validar_pleito.py` (V10).
- **Critério de aceite:**
  1. Vigência 01/01/2026 seleciona a 2ª parcela (2,72%).
  2. Pleito com 6,30% declarado para jan/2026 → V10 erro (AT-05).
  3. Aplicar a mesma parcela em dois ciclos → bloqueado com mensagem que cita o ciclo anterior.
- **UC:** UC-06 · **TL:** TL-06 · **Release:** R1

### RF-CAD-04 Calendário de data-base e alerta

- **Descrição:** o sistema deve manter a data-base de cada contrato (derivada da última vigência e da periodicidade, ou
  informada) e alertar a Secretaria e a CAPET antes do início da instrução, com antecedência configurável (padrão de
  60 dias corridos "(proposto)", RN-CAD-04).
- **Origem:** M-P01-09 ("data-base, último reajuste"); N-P01-25 e R-P01-12 (memória de cálculo dos Blocos 60 dias antes
  da data).
- **Critério de aceite:**
  1. Paraty com última vigência em 01/01/2026 e periodicidade 12 → data-base 01/01/2027; alerta criado em 02/11/2026
     para PER-SEC e PER-ANA.
  2. Alterar a antecedência para 90 dias recalcula o alerta.
- **UC:** UC-06, UC-08 · **TL:** TL-06, TL-10 · **Release:** R1 (calendário), R2 (alerta)

---

## 3. MOD-CAL Motor de cálculo

### RF-CAL-01 Recalcular o IR (V09)

- **Descrição:** o sistema deve recalcular o IR com os pesos da versão (índices ponderados, RN-CAL-01, ou índice
  único, RN-CAL-02), em aritmética decimal, arredondar nas casas do contrato (RN-NUM-03) e comparar com o declarado
  com tolerância de 0,01 p.p. (RNF-01).
- **Origem:** M-P01-09; 24 de 28 cálculos da coorte conferem; Paraty 2022 e Centro Sul 2025 não fecham com os próprios
  índices (`saida/levantamento/calculo/recalculo.csv`).
- **Critério de aceite:**
  1. Paraty 2026: IR 3,9669% → 3,967%, V09 ok.
  2. Os 24 cálculos que conferem dão V09 ok (AT-01); Paraty 2022 dá 9,5601% contra 10,37% escritos, V09 erro (AT-02);
     Centro Sul 2025 dá 5,3195% contra 4,1245% (AT-03).
  3. Blocos 1 e 4: preço da água com 2 casas dá 4,78% contra 4,80% e o sistema aponta o arredondamento do insumo
     (AT-04).
- **UC:** UC-03 · **TL:** TL-04, TL-05 · **Release:** R1

### RF-CAL-02 Total e parcela de realinhamento (V10)

- **Descrição:** o sistema deve compor o total pela regra de combinação da versão (`multiplicativa` ou `aditiva`,
  RN-CAL-03), conferir a parcela de realinhamento do cronograma (RN-V10) e comparar o total com o declarado (0,01 p.p.).
  A regra nunca é inferida.
- **Origem:** 11 de 11 apurações completas fecham pelo produto; duas cartas de Blocos somam em vez de multiplicar
  (`docs/LEVANTAMENTO_MOTOR_CALCULO.md`, seção 1); 3º Termo Aditivo de Paraty ("cumulativamente").
- **Critério de aceite:**
  1. Paraty 2026: (1,03967 × 1,0272) − 1 = 6,7949% contra 6,795% declarado → V10 ok.
  2. A mesma versão com `combinacao = aditiva` daria 6,687% → V10 erro.
  3. Versão sem `combinacao` resolve para `multiplicativa`, e a memória mostra a regra usada.
- **UC:** UC-03 · **TL:** TL-04, TL-05 · **Release:** R1

### RF-CAL-03 Interstício e meses de referência (V03, V04)

- **Descrição:** o sistema deve conferir o interstício em meses de referência e em dias (RN-V03) e os meses o e i pela
  regra do contrato (RN-CAL-05, RN-V04).
- **Origem:** V03, V04; cláusula 20 de Paraty (terceiro mês anterior); N-P01-17 e N-P01-18; CEDAE interior
  (SEI-480002/009940/2024), em que o mês de referência mudou o resultado de 5,2826% para 4,6963%.
- **Critério de aceite:**
  1. Paraty 2026: 12 meses de referência e 354 dias → V03 aviso; o = 2024-10 e i = 2025-10 → V04 ok.
  2. i = 2025-09 → V04 erro (AT-05).
  3. Vigência pretendida 11 meses depois da tarifa em vigor → V03 erro.
- **UC:** UC-03 · **TL:** TL-04 · **Release:** R1

### RF-CAL-04 Tabela tarifária proposta (V12)

- **Descrição:** o sistema deve conferir cada linha da tabela proposta contra `vigente × (1 + total)`, nas casas da
  tarifa (RN-V12), e dar aviso quando o pleito vem sem tabela.
- **Origem:** V12; Condessa e Imperatriz sem tabela; tabelas do Diário Oficial com números quebrados (Aula 2, RF11).
- **Critério de aceite:**
  1. Paraty 2026 sem tabela → V12 aviso.
  2. Tabela sintética com total de 6,795% e uma linha com proposta errada na 4ª casa → V12 erro com a categoria.
- **UC:** UC-03 · **TL:** TL-04, TL-05 · **Release:** R1

### RF-CAL-05 Memória de cálculo com origem

- **Descrição:** o sistema deve gerar a memória de cálculo a partir da apuração gravada, com cada termo, IR, parcela,
  total e a origem de cada número (pleito e anexo, série com data da consulta, trecho do cadastro), exportável em
  DOCX e PDF (RN-CAL-08).
- **Origem:** RNF-02; protótipo da memória de cálculo da Aula 2; a memória chega hoje em planilha ou imagem.
- **Critério de aceite:**
  1. A memória de Paraty 2026 tem as 6 linhas da tabela da RN-CAL-01, IR 3,967%, total 6,795% e a 2ª parcela de 2,72%
     (AT-18).
  2. Cada número da memória tem origem não vazia.
  3. A soma dos pesos (0,9999) aparece com a observação do Anexo X.
- **UC:** UC-05 · **TL:** TL-05 · **Release:** R1

### RF-CAL-06 Encadear ciclos

- **Descrição:** o sistema deve guardar o histórico por contrato e conferir que o mês o de um ciclo é o mês i do ciclo
  anterior homologado; se um ciclo não foi homologado, mostrar o acúmulo do período (RN-CAL-07).
- **Origem:** acúmulo de 24 meses em resíduos sólidos 2023 (Vale do Café e Centro Sul, 13,3556%); Aula 2, RF14.
- **Critério de aceite:**
  1. Ciclo de Paraty com tarifa vigente desde 12/01/2025 (i = 2024-10) e ciclo de 2026 (o = 2024-10) → encadeados.
  2. Ciclos de Paraty de 2022 a 2025 encadeados quando o 1º e o 2º termos aditivos estiverem no cadastro (AT-08).
  3. o diferente do i anterior → aviso no resultado e marca na TL-07.
- **UC:** UC-07, UC-03 · **TL:** TL-07 · **Release:** R1

---

## 4. MOD-SER Séries

### RF-SER-01 Séries públicas com cache (V07)

- **Descrição:** o sistema deve buscar as séries públicas no IPEADATA (INT-02) e no IBGE SIDRA (INT-03), guardar valor,
  parâmetros e data da consulta, servir do cache e comparar cada valor do pleito no mês, nas casas enviadas (RN-V07,
  RN-SER-01).
- **Origem:** 70 de 70 números-índice públicos dos pareceres achados nas séries (`saida/levantamento/calculo/resumo.json`);
  M-P01-09.
- **Critério de aceite:**
  1. IPC de Paraty (761,643 e 789,092) achado em IPEADATA IGP12_IPC12 → V07 ok; ICC 1.222,36 contra 1.222,356 → V07
     aviso de arredondamento.
  2. IPCA-E de Vale do Café (6.855,40 e 7.220,07) achado na tabela 3065 do SIDRA.
  3. Cada item de V07 traz a série e a data da consulta.
- **UC:** UC-03, UC-20 · **TL:** TL-04, TL-14 · **Release:** R1

### RF-SER-02 Conferência cruzada de séries pagas (V08)

- **Descrição:** o sistema deve comparar cada valor de série paga com o mesmo código e mês em outros ciclos (e na carga
  inicial dos casos extraídos), fora o próprio ciclo, e dar aviso quando não confere ou não há base (RN-SER-02). Os
  valores pagos não saem do ciclo (RNF-04).
- **Origem:** M-P01-09; IPA e IPQ de out/2024 e out/2025 iguais em Paraty, Imperatriz e Condessa; diferença real no
  Bloco 3 (ICC-SP 1.331,066 no pleito contra 1.339,322 da CAPET).
- **Critério de aceite:**
  1. Paraty 2026: IPA, IPQ e ICC → V08 ok; IMO (159401) → V08 aviso "sem outro pleito do mesmo índice e mês".
  2. O caso do Bloco 3 dá V08 aviso com o valor divergente.
- **UC:** UC-03 · **TL:** TL-04 · **Release:** R1

### RF-SER-03 Energia da ANEEL e regra de composição (V11)

- **Descrição:** o sistema deve exigir no pleito a distribuidora, a composição e as resoluções da ANEEL do componente
  de energia (RN-V11) e, quando a regra de composição estiver validada no cadastro (DEC-01), ler as tarifas da ANEEL
  (INT-04) e recompor o índice nos meses o e i (RN-SER-03).
- **Origem:** energia de Paraty sem fonte (511,75 e 471,91); pedido de alteração do IEE (SEI-480002/003110/2024)
  remetido à revisão ordinária; nenhum valor de energia dos pareceres foi reproduzido sem a regra.
- **Critério de aceite:**
  1. Paraty 2026 → V11 erro "Energia sem distribuidora, composição e resolução da ANEEL".
  2. Bloco `energia` completo e regra no cadastro em `a confirmar` → V11 ok sem recomposição.
  3. Com regra `validada`, a recomposição usa a resolução vigente no mês e o resultado aponta a REH.
- **UC:** UC-03 · **TL:** TL-04 · **Release:** R1 (exigência); recomposição depois da DEC-01

### RF-SER-04 Fonte indisponível: "a refazer"

- **Descrição:** o sistema deve usar o cache quando o mês já estiver nele e, sem cache e com a fonte fora do ar, marcar
  o item como "a refazer", seguir com as demais regras e revalidar quando a fonte voltar (RN-SER-04).
- **Origem:** RNF-06; Aula 2, UC02, exceção 5a.
- **Critério de aceite:**
  1. IPEADATA respondendo 503 com cache → resultado igual ao AT-06 (AT-23 a).
  2. Sem cache → V07 a refazer, decisão `a_refazer` (sem outro erro), e o ciclo não é devolvido (AT-23 b).
  3. Fonte de volta → revalidação automática com resultado ligado ao anterior.
- **UC:** UC-03, UC-20 · **TL:** TL-04, TL-14 · **Release:** R1

---

## 5. MOD-PRZ Prazos e tramitação

### RF-PRZ-01 Marcos e prazos em dias úteis

- **Descrição:** o sistema deve registrar os marcos do ciclo (RN-TRA-01) e calcular os prazos do rito (RN-PRZ-02) em
  dias úteis ou corridos conforme a norma, com o calendário de feriados do estado e da cidade do Rio e os pontos
  facultativos (RN-PRZ-01).
- **Origem:** M-P01-12; N-P01-15 (IN 115/2024, dias úteis); feriados de `perfis/rj_agenersa.py`.
- **Critério de aceite:**
  1. Marcos reais de Paraty 2026 → prazos e resultados da tabela do AT-09 (pronunciamento vence em 17/12/2025;
     Procuradoria em 20/12/2025; deliberação após razões finais em 26/01/2026; recursal em 12/03/2026).
  2. Diligência de 3 dias úteis juntada em 19/11/2025 vence em 25/11/2025 (20/11 não conta) (AT-11).
  3. Ponto facultativo incluído pelo PER-ADM recalcula os vencimentos abertos.
- **UC:** UC-08 · **TL:** TL-02, TL-10 · **Release:** R2

### RF-PRZ-02 Dono por etapa

- **Descrição:** o sistema deve atribuir a cada ciclo exatamente um dono (unidade e, se houver, servidor) por etapa
  (RN-TRA-02), com troca atômica e registrada; enquanto corre prazo de terceiro, o dono é quem expediu o ofício. Nenhum
  ciclo fica sem unidade responsável.
- **Origem:** M-P01-01, M-P01-04, M-P01-07; I-P01-06 (41 dias úteis sem nenhuma unidade, mediana da coorte); gargalo
  "processo sem dono" (`01_VISAO_ESCOPO.md`, seção 1).
- **Critério de aceite:**
  1. Em todo instante dos marcos de Paraty 2026 reproduzidos, a consulta de dono devolve uma unidade.
  2. Depois da publicação, o dono passa a CAPET até a conclusão da conferência das faturas.
  3. Tentar tirar o dono sem indicar outro → 422.
- **UC:** UC-08 · **TL:** TL-01, TL-10 · **Release:** R2

### RF-PRZ-03 Alertas antes e no vencimento

- **Descrição:** o sistema deve alertar o dono antes do vencimento, no vencimento e, vencido sem cumprimento, no dia
  útil seguinte, também à chefia, na fila (TL-10) e por correio eletrônico (INT-08) (RN-TRA-03).
- **Origem:** M-P01-12; R-P01-05 a R-P01-07 com conformidade de 17,6%, 71,4% e 58,8% na coorte.
- **Critério de aceite:**
  1. Prazo da Procuradoria de Paraty (vence em 20/12/2025) gera "a vencer" 3 e 1 dias úteis antes e "vence hoje"; na
     variante sem juntada, "vencido" no dia útil seguinte (AT-10).
  2. Prazo cumprido não gera alerta posterior.
- **UC:** UC-08 · **TL:** TL-10 · **Release:** R2

### RF-PRZ-04 Reiteração no dia seguinte ao vencimento

- **Descrição:** o sistema deve gerar, no dia útil seguinte ao vencimento de diligência sem resposta, a minuta da
  reiteração por modelo, com novo prazo nunca menor que o original e a consequência do silêncio, pronta para
  assinatura (RN-TRA-04).
- **Origem:** M-P01-07; t5 do BPMN; reiterações da Secretaria e do gabinete na coorte.
- **Critério de aceite:**
  1. Diligência de 3 dias úteis de 19/11/2025 sem resposta → reiteração pronta em 26/11/2025 (AT-11).
  2. O novo prazo menor que o original é recusado.
  3. Resposta registrada antes do vencimento cancela a geração.
- **UC:** UC-10 · **TL:** TL-10, TL-09 · **Release:** R2

### RF-PRZ-05 Prazo da Procuradoria

- **Descrição:** o sistema deve abrir o prazo de 15 dias corridos da Procuradoria no último parecer técnico, com
  dilação de mais 15 só com justificativa e autorização registradas (RN-PRZ-06).
- **Origem:** M-P01-05; N-P01-05 (Regimento, art. 17, VI); R-P01-07 (58,8% de conformidade).
- **Critério de aceite:**
  1. Paraty 2026: parecer técnico em 05/12/2025 → vence em 20/12/2025; parecer jurídico em 14/12/2025 → cumprido, 9
     dias corridos (AT-09).
  2. Prorrogação sem justificativa → 400; com justificativa e autorização → vencimento em 04/01/2026.
- **UC:** UC-08, UC-11 · **TL:** TL-10 · **Release:** R2

### RF-PRZ-06 Pauta no vencimento das razões finais

- **Descrição:** o sistema deve, no vencimento do prazo de razões finais, pôr o ciclo na lista de aptos da primeira
  sessão com pauta aberta, se os pareceres técnico e jurídico estiverem juntados e as partes instadas; senão, mostrar o
  impedimento (RN-TRA-05).
- **Origem:** M-P01-06; N-P01-08 (Regimento, art. 53); R-P01-01 a 03 e R-P01-20.
- **Critério de aceite:**
  1. Razões finais de Paraty notificadas em 17/12/2025 com 10 dias úteis → apto em 02/01/2026.
  2. Sem parecer jurídico → não apto, impedimento "R-P01-01".
  3. Inclusão em pauta antes do vencimento das razões finais → 422.
- **UC:** UC-13 · **TL:** TL-11 · **Release:** R2

### RF-PRZ-07 Prazo recursal

- **Descrição:** o sistema deve contar o prazo recursal de 10 dias úteis a partir da publicação (RN-PRZ-07), suspender
  a certidão com recurso ou embargos registrados e impedir a distribuição do recurso ao gabinete do relator da
  deliberação recorrida.
- **Origem:** M-P01-02, M-P01-14; N-P01-12 (Regimento, art. 79); R-P01-19.
- **Critério de aceite:**
  1. Paraty 2026: publicação em 26/02/2026 → vence em 12/03/2026 (AT-09).
  2. Recurso registrado em 05/03/2026 → certidão não gerada e alerta ao gabinete.
  3. Recurso atribuído ao gabinete do relator originário → 422 (R-P01-19).
- **UC:** UC-14 · **TL:** TL-10, TL-02 · **Release:** R2

### RF-PRZ-08 Certidão pela regra e encerramento por lista de verificação

- **Descrição:** o sistema deve gerar a minuta da certidão de ausência de recurso no dia útil seguinte ao vencimento
  recursal, sem recurso registrado, e só gerar o termo de encerramento com os itens bloqueantes da lista atendidos
  (RN-TRA-05, RN-TRA-06).
- **Origem:** M-P01-02, M-P01-03, M-P01-14; N-P01-16 (Resolução 787/2022); R-P01-17 (25% na coorte) e R-P01-18;
  I-P01-10.
- **Critério de aceite:**
  1. Paraty 2026 com a conferência juntada e sem certidão → termo recusado, "falta a certidão de ausência de recurso";
     com a certidão de 13/03/2026, termo gerado (AT-13).
  2. Item bloqueante falho sugere consulta à Procuradoria; sem falha, nenhuma consulta é aberta.
- **UC:** UC-15 · **TL:** TL-09, TL-02 · **Release:** R2

### RF-PRZ-09 Painel de prazos e idade por unidade

- **Descrição:** o sistema deve mostrar a fila de ciclos com situação, dono, próximo prazo e idade em dias úteis, por
  unidade, e destacar ciclos parados acima do limiar por ato de rotina.
- **Origem:** M-P01-12; I-P01-01 e I-P01-06; mediana de espera de 137,5 dias úteis contra 26,5 de execução.
- **Critério de aceite:**
  1. A TL-01 com os 18 casos de `fixtures/ciclos_coorte.json` mostra dono e idade de cada um; a idade de Paraty 2026
     pelos marcos é a do AT-15.
  2. Filtro por unidade dona e ordenação por idade funcionam pela API (`GET /ciclos`).
- **UC:** UC-08, UC-18 · **TL:** TL-01, TL-10 · **Release:** R2

---

## 6. MOD-DOC Documentos por modelo

### RF-DOC-01 Peças de rotina por modelo versionado

- **Descrição:** o sistema deve gerar ofícios, notificações, certidões e termos por modelo versionado, com os dados do
  ciclo, sem marcador vazio, e guardar a versão do modelo na peça. Modelos do rito: recebimento, complementação,
  diligência, reiteração, razões finais (10 dias úteis fixos), acesso aos autos, notificação da deliberação, ofício à
  ALERJ, pedido de faturas, certidão de ausência de recurso, termo de encerramento.
- **Origem:** M-P01-13; N-P01-07 e R-P01-04 (prazo de 10 dias, 22,2% de conformidade); N-P01-22 (ALERJ).
- **Critério de aceite:**
  1. Notificação para razões finais de Paraty com processo, concessionária, contrato, prazo de 10 dias e versão do
     modelo; R-P01-04 passa a conforme (AT-16).
  2. Modelo com campo obrigatório sem valor → geração recusada apontando o campo.
- **UC:** UC-09 · **TL:** TL-09 · **Release:** R2 (o ofício de complementação entra em R1, para o RF-PLE-04)

### RF-DOC-02 Exportação para o SEI

- **Descrição:** o sistema deve exportar a peça em DOCX e PDF aceitos pelo SEI e registrar a juntada (número do
  documento SEI e data), que cria o marco correspondente. O sistema não assina nem protocola (RNF-07).
- **Origem:** INT-01 fase 1 manual; escopo (assinatura e protocolo continuam no SEI).
- **Critério de aceite:**
  1. DOCX e PDF da peça do AT-16 abrem e têm o mesmo texto.
  2. Registrar a juntada cria o marco e fecha ou abre os prazos ligados.
- **UC:** UC-09 · **TL:** TL-09 · **Release:** R2

### RF-DOC-03 Ofício de diligência único por fase

- **Descrição:** o sistema deve juntar os quesitos abertos de CAPET, Procuradoria e gabinete e as pendências da
  validação num único ofício por fase e por destinatário, com a unidade de origem de cada quesito (RN-TRA-07).
- **Origem:** M-P01-08; 18 casos em 17 caminhos distintos por diligências repetidas.
- **Critério de aceite:**
  1. 2 quesitos da CAPET e 1 da Procuradoria na mesma fase → um ofício com os 3 (AT-12).
  2. Quesito novo depois da expedição vai para a fase seguinte ou exige justificativa.
- **UC:** UC-10, UC-04 · **TL:** TL-09 · **Release:** R2

---

## 7. MOD-MIN Minutas assistidas

### RF-MIN-01 Minuta do parecer técnico

- **Descrição:** o sistema deve gerar a minuta do parecer técnico a partir da apuração (fatos, análise, apuração,
  conclusão), com os números travados e ligados à origem e as citações das cláusulas verificadas (RN-MIN-01,
  RN-MIN-02). O analista revisa e assina no SEI.
- **Origem:** M-P01-15; avaliação AS-IS (potencial alto de IA na atividade t2, `insumos/mapeamento/avaliacao_P01.json`);
  Q-P01-01.
- **Critério de aceite:**
  1. A minuta de Paraty 2026 traz IR 3,967%, total 6,795% e a 2ª parcela, iguais à apuração; tentar editar um número
     no texto é recusado (AT-18).
  2. Toda citação da minuta passa pela verificação antes de "revisada".
- **UC:** UC-05 · **TL:** TL-08 · **Release:** R3 (a memória de cálculo do RF-CAL-05 já em R1)

### RF-MIN-02 Minuta do parecer jurídico com checklist legal

- **Descrição:** o sistema deve gerar a minuta do parecer jurídico com a linha do tempo da instrução, o resumo do
  pleito e da apuração, os reajustes anteriores do mesmo contrato (precedentes) e o checklist legal dos requisitos
  R-P01 aplicáveis ao ciclo, com o resultado de cada teste (RF-IND-02) e as normas com trecho verificado.
- **Origem:** M-P01-16; 20 requisitos legais com teste em `insumos/mapeamento/normas_P01.json`; Q-P01-02.
- **Critério de aceite:**
  1. A minuta para Paraty 2026 lista o interstício com os dois números (12 meses de referência e 354 dias, DEC-02), a
     antecedência de 30 dias e a ordem dos pareceres, cada item com a norma N-P01 e o resultado do teste.
  2. As deliberações anteriores do contrato 008/2014 aparecem como precedentes, com número e trecho verificado.
  3. Nenhuma citação inválida na versão "revisada".
- **UC:** UC-11 · **TL:** TL-08 · **Release:** R3

### RF-MIN-03 Minutas de relatório, voto e deliberação

- **Descrição:** o sistema deve gerar as minutas de relatório, voto e deliberação a partir dos autos (marcos, peças,
  apuração, manifestações), no padrão das deliberações anteriores do contrato, com os quatro elementos de motivação do
  R-P01-14: fórmula contratual, índices usados, percentual e razões de eventual divergência dos pareceres.
- **Origem:** M-P01-17, M-P01-18; N-P01-14 (Lei 5.427/2009, art. 48); 68 peças de relatório e voto com texto na
  coorte; Q-P01-03 e Q-P01-04.
- **Critério de aceite:**
  1. A minuta de deliberação de Paraty 2026 tem os quatro elementos e os números iguais aos do parecer técnico.
  2. Faltando algum elemento, a minuta não pode ser marcada "revisada".
- **UC:** UC-12 · **TL:** TL-08 · **Release:** R3

### RF-MIN-04 Verificação de citação

- **Descrição:** o sistema deve verificar cada citação da minuta contra o texto da fonte (existência, dispositivo,
  trecho literal normalizado, vigência) e marcar a inválida com o motivo; minuta com citação inválida não é marcada "revisada"
  (RN-MIN-01).
- **Origem:** M-P01-15 a 17; Q-P01-01 a 03 (meta de 0 citação inválida em peça assinada).
- **Critério de aceite:**
  1. As 31 citações com o trecho de `normas_P01.json` são válidas; a mesma citação com uma palavra trocada no trecho
     é inválida, `trecho_nao_achado`, e com dispositivo inexistente, `dispositivo_inexistente`; a inválida bloqueia a
     exportação (AT-19). Exemplo: art. 49, § 2º, do Regimento com "10 (dez) dias" é válida; com "15 (quinze) dias",
     inválida.
  2. Citação de norma inexistente na base → `fonte_inexistente`.
- **UC:** UC-05, UC-11, UC-12 · **TL:** TL-08 · **Release:** R3

### RF-MIN-05 Edições do revisor e taxa de edição

- **Descrição:** o sistema deve registrar cada edição do revisor (trecho, texto antes e depois, autor, hora) e calcular
  a taxa de edição por minuta (RN-MIN-03), que alimenta o Q-P01-03.
- **Origem:** Q-P01-03 (taxa de edição da minuta).
- **Critério de aceite:**
  1. Minuta sintética com 20 trechos e 3 editados tem taxa 0,15; a taxa aparece no Q-P01-03 da TL-13 (AT-20).
  2. As edições aparecem na trilha de auditoria.
- **UC:** UC-05, UC-11, UC-12, UC-18 · **TL:** TL-08, TL-13 · **Release:** R3

---

## 8. MOD-FAT Conferência de faturas

### RF-FAT-01 Remessa de faturamento sem dados pessoais

- **Descrição:** o sistema deve receber a remessa periódica no layout `contratos/remessa_faturamento.schema.json`, com
  código anônimo da economia, categoria, faixa, consumo, valor cobrado e mês, e recusar inteira, sem guardar nada, a
  remessa com propriedade fora do layout ou dado pessoal (RN-FAT-01).
- **Origem:** M-P01-11; 1 fatura nos 1.228 documentos da coorte; bases de economias dos Blocos com dados pessoais no
  SEI (`docs/LEVANTAMENTO_MOTOR_CALCULO.md`, seção 5); RNF-05.
- **Critério de aceite:**
  1. Remessa válida → 201 com quantidade de faturas.
  2. Remessa com coluna `cpf` ou nome de usuário → 422, nada gravado, mensagem com a coluna (AT-22).
- **UC:** UC-16 · **TL:** TL-12 · **Release:** R4

### RF-FAT-02 Recálculo contra a tabela homologada

- **Descrição:** o sistema deve recalcular cada fatura contra a tabela homologada vigente no mês, pela regra de
  aplicação da tabela da versão (RN-FAT-03, DEC-04), e listar só as divergências acima da tolerância, agrupáveis por
  categoria e faixa. A conclusão da conferência é marco e item do encerramento.
- **Origem:** M-P01-01, M-P01-11; N-P01-29 e N-P01-30; R-P01-15, R-P01-16 (50% na coorte).
- **Critério de aceite:**
  1. Tabela com total de 6,795% e 3 faturas sintéticas (tarifa nova, tarifa antiga, faixa errada) → 2 divergências; a
     correta não aparece (AT-21).
  2. Sem regra de aplicação cadastrada → remessa fica `sem_regra_de_aplicacao` e a conferência não roda.
- **UC:** UC-17 · **TL:** TL-12 · **Release:** R4

---

## 9. MOD-IND Indicadores e auditoria contínua

### RF-IND-01 Indicadores I-P01-01 a 10

- **Descrição:** o sistema deve calcular os indicadores I-P01-01 a 10 a partir dos marcos e das peças, com definição,
  frequência, linha de base e metas de `insumos/mapeamento/controles_P01.json` (RN-IND-02). I-P01-02 (horas) é hipótese até a
  calibração com servidores e a tela diz isso.
- **Origem:** `controles_P01.json`; metas do documento-base (seção 2).
- **Critério de aceite:**
  1. Com os 18 casos da coorte: I-P01-03 = 50,0% (6 de 12), I-P01-04 = 58,8% (10 de 17), I-P01-05 = 71,4% (10 de 14),
     I-P01-09 = 17,6% (3 de 17), I-P01-10 = 25,0% (2 de 8) (AT-15).
  2. Cada medição guarda período, número de casos e data do cálculo.
- **UC:** UC-18 · **TL:** TL-13 · **Release:** R4

### RF-IND-02 Auditoria contínua dos requisitos R-P01

- **Descrição:** o sistema deve rodar os testes dos 20 requisitos legais sobre cada ciclo, a cada marco registrado e
  diariamente, com a semântica de `scripts/conformidade.py` (RN-IND-01), e mostrar o resultado por ciclo e por
  requisito. Os testes `manual` do levantamento passam a ser computáveis sobre marcos que o sistema registra (quadro
  abaixo); os que dependem de leitura humana ficam como lista de verificação da revisão.
- **Origem:** `insumos/mapeamento/normas_P01.json`; programa de auditoria A-P01-01 a 11; `controles_P01.json`
  (auditoria contínua A-P01-01 a 05, 09, 10).
- **Critério de aceite:**
  1. Com os marcos dos 18 casos, o resultado de cada teste computável é igual ao de `conformidade_P01.csv`, com o mesmo
     número de dias no detalhe (AT-14).
  2. No ciclo de Paraty 2026, R-P01-05 dá "99 dc (máx. 30)" não conforme e R-P01-17 "t13 sem t12 antes" não conforme.
  3. Teste não conforme gera alerta ao dono da etapa e entra no I-P01 correspondente.
- **UC:** UC-18 · **TL:** TL-13 · **Release:** R4 (os testes de ordem e de prazo já servem às travas de R2)

#### Regras de auditoria contínua R-P01-01 a 20

"Teste existente" é o de `normas_P01.json`. "No sistema" diz como o teste roda sobre os marcos do Reajusta
(RN-TRA-01). Linha de base: `insumos/mapeamento/conformidade_P01.json` (18 casos).

| ID | Exigência | Teste existente | No sistema | Linha de base | Trava em |
|---|---|---|---|---|---|
| R-P01-01 | Parecer jurídico antes da deliberação | `precede(t3, t8)` | `precede(parecer_juridico, deliberacao)` | 100% (17) | pauta (RN-TRA-05) |
| R-P01-02 | Cálculo da CAPET antes da deliberação | `precede(t2, t8)` | `precede(parecer_tecnico, deliberacao)` | 100% (17) | pauta |
| R-P01-03 | Razões finais antes da deliberação | `precede(t7, t8)` | `precede(razoes_finais, deliberacao)` | 82,4% (14 de 17) | pauta |
| R-P01-04 | Razões finais com 10 dias | `prazo_concedido_min(t7, 10)` | prazo concedido registrado na juntada do ofício de razões finais ≥ 10 | 22,2% (4 de 18) | modelo do ofício (RN-PRZ-04) |
| R-P01-05 | Pronunciamento em 30 dias | `prazo_max(t1, t8, 30 dc)` | `prazo_max(protocolo, deliberacao, 30 dc)` | 17,6% (3 de 17) | alerta (RN-PRZ-03) |
| R-P01-06 | Deliberação em 40 dias das razões finais | `prazo_max(t7, t8, 40 dc, última)` | `prazo_max(razoes_finais, deliberacao, 40 dc, última)` | 71,4% (10 de 14) | alerta |
| R-P01-07 | Procuradoria em 15 dias do parecer técnico | `prazo_max(t2, t3, 15 dc, última)` | `prazo_max(parecer_tecnico, parecer_juridico, 15 dc, última)` | 58,8% (10 de 17) | alerta (RN-PRZ-06) |
| R-P01-08 | Deliberação publicada e comunicada | `exige(t8 → t9)` | `exige(deliberacao → publicacao e notificacao)` | 100% (17) | encerramento (RN-TRA-06) |
| R-P01-09 | Vigência 30 dias depois da publicidade | `manual` | `prazo_min(publicacao ou divulgacao, vigencia_tarifa, 30 dc)` "(proposto)" | não medido | alerta na publicação (RN-PRZ-10) |
| R-P01-10 | 12 meses entre reajustes | `manual` | meses entre `vigencia_tarifa` de ciclos sucessivos do contrato ≥ periodicidade; o mesmo cálculo da V03 | não medido | V03 |
| R-P01-11 | Planilhas à ALERJ 20 dias antes da vigência | `manual` | se total > 0: `prazo_min(envio_alerj, vigencia_tarifa, 20 dc)` "(proposto)" | não medido | prazo e modelo do ofício (RN-PRZ-11) |
| R-P01-12 | Memória de cálculo dos Blocos 60 dias antes | `manual` | se a versão tiver a cláusula: `prazo_min(protocolo, data-base, 60 dc)` "(proposto)" | não medido | alerta de data-base (RN-CAD-04) |
| R-P01-13 | Verificador independente nos Blocos | `manual` | se a versão exigir: `precede(manifestacao_verificador, deliberacao)` com marco "(proposto)" | não medido | pauta |
| R-P01-14 | Deliberação motivada (fórmula, índices, percentual, divergências) | `manual` | lista de verificação da minuta (RN-MIN-02): os quatro elementos presentes na versão revisada; leitura humana confirma | não medido | revisão da minuta |
| R-P01-15 | Conferência das faturas após a homologação | `exige(t9 → t10)` | `exige(publicacao → conferencia_faturas)` | 70,6% (12 de 17) | encerramento |
| R-P01-16 | Conferência iniciada em 90 dias | `prazo_max(t9, t10, 90 dc, última)` | `prazo_max(publicacao, conferencia_faturas, 90 dc, última)` | 50,0% (6 de 12) | alerta (RN-PRZ-08) |
| R-P01-17 | Certidão antes do encerramento | `precede(t12, t13)` | `precede(certidao_ausencia_recurso, encerramento)` | 25,0% (2 de 8) | encerramento |
| R-P01-18 | Conferência das faturas antes do encerramento | `precede(t10, t13)` | `precede(conferencia_faturas, encerramento)` | 87,5% (7 de 8) | encerramento |
| R-P01-19 | Recurso com relator diverso | `manual` | unidade do relator do marco `recurso` ≠ unidade do relator da deliberação | não medido | registro do recurso (RN-PRZ-07) |
| R-P01-20 | Ato seguinte só depois do prazo de razões finais | `prazo_min(t7, t8, 10 dc)` | `prazo_min(razoes_finais, deliberacao, 10 dc)`; com IN 115/2024, a trava usa 10 dias úteis | 64,3% (9 de 14) | pauta |

### RF-IND-03 Controles de qualidade da IA

- **Descrição:** o sistema deve medir Q-P01-01 a 04: taxa de erro de extração (campos corrigidos / extraídos), taxa de
  citação inválida antes da revisão e em peça assinada, taxa de edição da minuta e retificações por divergência entre
  versão votada e juntada (RN-IND-03).
- **Origem:** `controles_P01.json` (controles_qualidade_ia).
- **Critério de aceite:**
  1. Com as edições do AT-20, Q-P01-03 mostra a taxa da minuta e a média do período.
  2. Cada controle mostra a meta de `controles_P01.json` ao lado do valor.
- **UC:** UC-18 · **TL:** TL-13 · **Release:** R3 (coleta), R4 (painel)

---

## 10. MOD-ADM Administração

### RF-ADM-01 Usuários, perfis e autenticação

- **Descrição:** o sistema deve gerir usuários e perfis PER-* com autenticação por credenciais e sessão JWT com
  expiração (NextAuth); o usuário externo (PER-CON) é sempre vinculado a uma concessionária e só alcança os dados
  dela.
- **Origem:** stack decidida; seção 6 do documento-base; RNF-10.
- **Critério de aceite:**
  1. PER-CON de Águas de Paraty não vê ciclo de outra concessionária (404) (AT-25).
  2. Criar PER-CON sem concessionária → 400.
  3. Sessão expirada → 401 e volta à TL-16.
- **UC:** UC-19 · **TL:** TL-15, TL-16 · **Release:** Transversal

### RF-ADM-02 Trilha de auditoria

- **Descrição:** o sistema deve registrar, de forma imutável, toda ação que muda dado ou peça: quem, perfil, quando,
  operação, entidade, hash antes e depois.
- **Origem:** RNF-11; competências legais (decisão humana registrada, RNF-07).
- **Critério de aceite:**
  1. Cada operação de escrita do AT-27 deixa um registro (AT-26).
  2. Tentativa de alterar ou apagar registro, inclusive por PER-ADM, é recusada pelo banco.
- **UC:** UC-19 · **TL:** TL-15 · **Release:** Transversal

### RF-ADM-03 Modelos de documento com versão

- **Descrição:** o sistema deve gerir modelos de documento com versão; peça gerada guarda a versão do modelo; versão
  nova não altera peças anteriores.
- **Origem:** M-P01-13.
- **Critério de aceite:**
  1. Nova versão do modelo de razões finais; a peça do AT-16 continua apontando a versão anterior.
  2. Modelo sem campo obrigatório declarado não é publicado.
- **UC:** UC-19, UC-09 · **TL:** TL-15 · **Release:** Transversal

---

## 11. Requisitos não funcionais

| ID | Requisito detalhado | Origem | Critério de aceite | Release | Teste |
|---|---|---|---|---|---|
| RNF-01 Exatidão | Tolerância de 0,01 p.p. entre o IR e o total refeitos e os declarados, depois do arredondamento do contrato; cálculo em decimal (RN-NUM-01) | 24 de 28 cálculos na tolerância | AT-01 a AT-04 com os resultados esperados; nenhum `number` de ponto flutuante no domínio de cálculo (regra de lint) | R1 | AT-01 a AT-04 |
| RNF-02 Rastreabilidade | Todo número exibido aponta a origem (pleito e anexo, série e data da consulta, trecho do cadastro) | regra do método: nenhum número digitado à mão | na TL-04 e na TL-05, todo número tem origem acessível; na memória, origem não vazia em 100% das linhas | R1 | AT-02, AT-04, AT-18 |
| RNF-03 Reprodutibilidade | Toda apuração guarda versão do cadastro, do layout, das regras e das séries; a mesma entrada dá o mesmo resultado | aditivos mudam a regra no meio do ciclo (Blocos, 2024) | revalidar um resultado antigo com as mesmas versões dá itens idênticos; mudar a versão das regras gera resultado novo ligado ao antigo | R1 | AT-06 repetido "(proposto)" |
| RNF-04 Licença | Séries pagas não saem do ciclo, não vão a painel nem ao modelo de linguagem; só a variação aparece fora | contratos públicos de licença da FGV com cláusula de não divulgação | AT-24 | R1 | AT-24 |
| RNF-05 Privacidade (LGPD) | Layouts sem dado pessoal; propriedade fora do layout ou dado pessoal → recusa sem guardar | bases de economias com dados pessoais no SEI | AT-22 | R1 | AT-22 |
| RNF-06 Disponibilidade | Fonte externa fora do ar não bloqueia: cache e "a refazer" (RN-SER-04) | dependência de APIs públicas | AT-23 | R1 | AT-23 |
| RNF-07 Decisão humana | O sistema não assina, não protocola, não homologa; minuta só vira peça depois de "revisada" pelo perfil dono | competência legal do Conselho-Diretor e da CAPET | nenhuma operação da API assina ou protocola; peça sem revisão não é exportável como final | todas | AT-18, AT-27 |
| RNF-08 Acessibilidade | WCAG 2.2 AA e eMAG em todas as telas | padrão digital de governo | Playwright com axe sem violação nas telas tocadas | todas | AT-27 e portão de CI |
| RNF-09 Usabilidade | Resultado da validação numa tela, na linguagem de quem analisa, números no formato brasileiro | protótipo da Aula 2 | a TL-04 de Paraty 2026 mostra os 16 itens sem rolagem horizontal em 1366 × 768 | R1 | AT-06 |
| RNF-10 Segurança | Autenticação, perfis por papel, sessão com expiração, segredos fora do código | operação | AT-25; varredura de segredos no repositório sem achado | todas | AT-25 |
| RNF-11 Auditabilidade | Trilha imutável de quem fez o quê e quando | competências legais | AT-26 | todas | AT-26 |
| RNF-12 Manutenibilidade | Domínio sem dependência de framework; cobertura mínima de 90% no domínio | arquitetura em camadas | portão de CI com 90% de linhas e ramos em `src/dominio`; nenhum import de Next.js, Prisma ou React no domínio | todas | portão de CI (`12_TESTES.md`, 1.4) |
| RNF-13 Desempenho | Validação de um pleito em menos de 60 s com as séries em cache | uso na entrada | AT-06 cronometrado com cache aquecido < 60 s | R1 | AT-06 |
| RNF-14 Portabilidade | Sobe com Docker; PostgreSQL; nenhum serviço pago obrigatório | TI da agência; FGV opcional | `docker compose up` em máquina limpa sobe a aplicação e passa o AT-06 sem chave de serviço pago | todas | teste de implantação "(proposto)" |

---

## 12. Matriz de rastreabilidade

RF × UC × TL × teste de aceitação (`12_TESTES.md`) × história (`13_BACKLOG.md`). As histórias são as que citam o RF
no backlog.

| RF | UC | TL | Testes de aceitação | História | Release |
|---|---|---|---|---|---|
| RF-PLE-01 | UC-01 | TL-03 | AT-06, AT-22 | HIS-PLE-02, HIS-PLE-05 | R1 |
| RF-PLE-02 | UC-02 | TL-03, TL-04 | AT-05 | HIS-PLE-01 | R1 |
| RF-PLE-03 | UC-02, UC-03 | TL-04 | AT-05, AT-06 | HIS-PLE-01, HIS-PLE-02, HIS-PLE-03 | R1 |
| RF-PLE-04 | UC-04 | TL-04, TL-09 | AT-06, AT-17 | HIS-PLE-06 | R1 |
| RF-PLE-05 | UC-01, UC-02 | TL-03 | AT-06 em modo prévio (a criar) | HIS-PLE-05 | R1 |
| RF-PLE-06 | UC-01, UC-08 | TL-01, TL-02 | AT-27 | HIS-PLE-02 | R1 |
| RF-CAD-01 | UC-06 | TL-06 | AT-07 | HIS-CAD-01, HIS-CAD-02, HIS-CAD-04, HIS-CAD-05 | R1 |
| RF-CAD-02 | UC-06 | TL-06 | AT-06 (V02 ok) | HIS-CAD-02 | R1 |
| RF-CAD-03 | UC-06 | TL-06 | AT-05, AT-06 | HIS-CAD-01, HIS-CAD-03 | R1 |
| RF-CAD-04 | UC-06, UC-08 | TL-06, TL-10 | a criar | HIS-CAD-03 | R1, R2 |
| RF-CAL-01 | UC-03 | TL-04, TL-05 | AT-01 a AT-07 | HIS-CAD-04, HIS-CAL-01 | R1 |
| RF-CAL-02 | UC-03 | TL-04, TL-05 | AT-01, AT-05, AT-06, AT-07 | HIS-CAL-01 | R1 |
| RF-CAL-03 | UC-03 | TL-04 | AT-05, AT-06, AT-08 | HIS-CAL-02 | R1 |
| RF-CAL-04 | UC-03 | TL-04, TL-05 | AT-06 | HIS-PLE-01 | R1 |
| RF-CAL-05 | UC-05 | TL-05 | AT-18 | HIS-CAL-02, HIS-CAL-03, HIS-MIN-03 | R1 |
| RF-CAL-06 | UC-07, UC-03 | TL-07 | AT-08 | HIS-CAD-05, HIS-CAL-04 | R1 |
| RF-SER-01 | UC-03, UC-20 | TL-04, TL-14 | AT-06, AT-23 | HIS-SER-01, HIS-SER-04 | R1 |
| RF-SER-02 | UC-03 | TL-04 | AT-04, AT-06 | HIS-SER-02 | R1 |
| RF-SER-03 | UC-03 | TL-04 | AT-06 | HIS-SER-03 | R1 |
| RF-SER-04 | UC-03, UC-20 | TL-04, TL-14 | AT-23 | HIS-SER-01, HIS-SER-04 | R1 |
| RF-PRZ-01 | UC-08 | TL-02, TL-10 | AT-09, AT-11, AT-27 | HIS-DOC-03, HIS-PRZ-01, HIS-PRZ-09 | R2 |
| RF-PRZ-02 | UC-08 | TL-01, TL-10 | AT-09, AT-12, AT-17, AT-27 | HIS-PRZ-02 | R2 |
| RF-PRZ-03 | UC-08 | TL-10 | AT-10, AT-27 | HIS-PRZ-03 | R2 |
| RF-PRZ-04 | UC-10 | TL-10, TL-09 | AT-11, AT-27 | HIS-PRZ-04 | R2 |
| RF-PRZ-05 | UC-08, UC-11 | TL-10 | AT-09, AT-10, AT-27 | HIS-PRZ-02 | R2 |
| RF-PRZ-06 | UC-13 | TL-11 | AT-27 | HIS-PRZ-05 | R2 |
| RF-PRZ-07 | UC-14 | TL-10, TL-02 | AT-09, AT-27 | HIS-PRZ-06 | R2 |
| RF-PRZ-08 | UC-15 | TL-09, TL-02 | AT-13, AT-27 | HIS-PRZ-07 | R2 |
| RF-PRZ-09 | UC-08, UC-18 | TL-01, TL-10 | AT-27 | HIS-PLE-04, HIS-PRZ-08 | R2 |
| RF-DOC-01 | UC-09 | TL-09 | AT-16, AT-27 | HIS-DOC-01, HIS-DOC-02, HIS-DOC-03, HIS-PLE-06 | R2 (complementação em R1) |
| RF-DOC-02 | UC-09 | TL-09 | AT-16, AT-27 | HIS-DOC-01 | R2 |
| RF-DOC-03 | UC-10, UC-04 | TL-09 | AT-12, AT-17, AT-27 | HIS-PLE-06, HIS-PRZ-04 | R2 |
| RF-MIN-01 | UC-05 | TL-08 | AT-18 | HIS-MIN-01, HIS-MIN-03 | R3 |
| RF-MIN-02 | UC-11 | TL-08 | AT-19 (citações); checklist legal a criar | HIS-MIN-04 | R3 |
| RF-MIN-03 | UC-12 | TL-08 | a criar (quatro elementos do R-P01-14) | HIS-MIN-05 | R3 |
| RF-MIN-04 | UC-05, UC-11, UC-12 | TL-08 | AT-19 | HIS-MIN-02, HIS-MIN-04, HIS-MIN-05 | R3 |
| RF-MIN-05 | UC-05, UC-11, UC-12, UC-18 | TL-08, TL-13 | AT-20 | HIS-MIN-06 | R3 |
| RF-FAT-01 | UC-16 | TL-12 | AT-22 | HIS-FAT-01 | R4 |
| RF-FAT-02 | UC-17 | TL-12 | AT-21 | HIS-FAT-02 | R4 |
| RF-IND-01 | UC-18 | TL-13 | AT-15 | HIS-IND-01, HIS-IND-03 | R4 |
| RF-IND-02 | UC-18 | TL-13 | AT-13, AT-14 | HIS-IND-02 | R4 |
| RF-IND-03 | UC-18 | TL-13 | AT-20 | HIS-IND-03, HIS-MIN-06 | R3, R4 |
| RF-ADM-01 | UC-19 | TL-15, TL-16 | AT-25 | HIS-ADM-02, HIS-ADM-04, HIS-ADM-06 | Transversal |
| RF-ADM-02 | UC-19 | TL-15 | AT-26 | HIS-ADM-03, HIS-IND-03 | Transversal |
| RF-ADM-03 | UC-19, UC-09 | TL-15 | AT-16 | HIS-ADM-05, HIS-DOC-02 | Transversal |

Cobertura: os 45 RF têm UC e TL; 41 têm teste de aceitação em `12_TESTES.md`. Faltam testes de aceitação próprios para
RF-PLE-05 (validação prévia sem registro), RF-CAD-04 (alerta de data-base), RF-MIN-02 (checklist legal) e RF-MIN-03
(quatro elementos de motivação); os critérios de aceite acima servem de base para eles.

### Telas sem RF próprio

Todas as telas TL-01 a TL-16 aparecem na matriz. A TL-16 (entrada) atende RF-ADM-01; a TL-14 (séries) atende
RF-SER-01 e RF-SER-04.
