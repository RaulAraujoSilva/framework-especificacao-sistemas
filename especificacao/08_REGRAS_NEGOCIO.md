# 08. Regras de negócio

Regras normativas do Reajusta, com identificador `RN-*`, fórmula, origem e exemplo numérico real. O exemplo resolvido
é o pleito de **Águas de Paraty para a vigência de 01/01/2026** (processo SEI-480002/009982/2025, Contrato 008/2014,
versão contratual `3TA-2024`). Os números saem de:

- `saida/levantamento/pleito/exemplo_paraty_2026.json` (pleito no layout 0.1) e `exemplo_paraty_2026.validacao.json`;
- `saida/levantamento/contratos/paraty_008_2014.json` (cadastro de parâmetros);
- `saida/levantamento/calculo/recalculo.csv` e `componentes.csv` (casos da coorte);
- `insumos/mapeamento/casos_P01.json` e `insumos/mapeamento/conformidade_P01.csv` (datas e conformidade do caso);
- `insumos/mapeamento/normas_P01.json` (normas N-P01 e requisitos legais R-P01).

A implementação de referência é `scripts/validar_pleito.py` (V01 a V12), `scripts/recalcular_reajuste.py` (recálculo)
e `scripts/conformidade.py` (testes dos requisitos R-P01). Em divergência entre o sistema e essas rotinas nos casos de
teste, o sistema está errado até prova em contrário. Onde esta especificação é **mais estrita** que a referência, a
diferença está marcada com "(proposto)" e o resultado esperado dos casos de teste não muda.

Identificadores de módulo, perfil, caso de uso, requisito e tela são os de [01_VISAO_ESCOPO.md](01_VISAO_ESCOPO.md).
Os requisitos detalhados estão em [03_REQUISITOS.md](03_REQUISITOS.md); os contratos de dados em
[07_CONTRATOS_API.md](07_CONTRATOS_API.md) e na pasta `contratos/`.

## Sumário

| Grupo | Regras | Módulo |
|---|---|---|
| 1. Convenções numéricas | RN-NUM-01 a 03 | MOD-CAL, MOD-PLE |
| 2. Cadastro do contrato | RN-CAD-01 a 04 | MOD-CAD |
| 3. Validação do pleito (V01 a V12) | RN-VAL-00, RN-V01 a RN-V12 | MOD-PLE, MOD-CAL, MOD-SER |
| 4. Cálculo do reajuste | RN-CAL-01 a 08 | MOD-CAL |
| 5. Séries | RN-SER-01 a 04 | MOD-SER |
| 6. Calendário e prazos do rito | RN-PRZ-01 a 13 | MOD-PRZ |
| 7. Donos, alertas, reiteração, pauta, certidão e encerramento | RN-TRA-01 a 07 | MOD-PRZ, MOD-DOC |
| 8. Conferência de faturas | RN-FAT-01 a 04 | MOD-FAT |
| 9. Minutas e citações | RN-MIN-01 a 04 | MOD-MIN |
| 10. Auditoria contínua e indicadores | RN-IND-01 a 03 | MOD-IND |
| 11. Decisões em aberto | DEC-01 a 08 | — |

---

## 1. Convenções numéricas

### RN-NUM-01 Aritmética decimal

- O domínio calcula em aritmética decimal, nunca em ponto flutuante binário. Precisão mínima: 28 dígitos
  significativos (biblioteca decimal em TypeScript, tipo `Decimal` do Prisma no banco).
- Percentuais são guardados em pontos percentuais (3,967 significa 3,967%). Variações e índices de reajuste
  intermediários são guardados como fração (0,03967) só dentro do motor.
- Origem: RNF-01, RNF-03; divergência de 4,80% para 4,78% causada por insumo com 2 casas
  (`docs/LEVANTAMENTO_MOTOR_CALCULO.md`, seção 2).

### RN-NUM-02 Leitura sem perda das casas decimais

- O sistema lê os números do pleito **pelo texto** (parser JSON sem perda, que preserva `1222.36` e `1222.360` como
  escritos). O número de casas escritas é dado de entrada da RN-V07 e da RN-V08.
- Origem: o validador de referência conta as casas do valor enviado (`repr(x)`); o INCC de Paraty veio com 2 casas
  (1.222,36) e a série publica 3 (1.222,356).

### RN-NUM-03 Arredondamento

- O arredondamento é feito uma vez, no ponto que a regra manda (IR nas casas do contrato, tarifa nas casas da
  tabela), nunca em resultado intermediário.
- Modo: **meio para o par** (ABNT NBR 5891), que é o comportamento da função de arredondamento do oráculo. O cadastro
  pode trocar o modo por versão contratual (campo `formula.modo_arredondamento`, "(proposto)"). Ver DEC-06.
- Exemplo: IR de Paraty 2026 = 3,966904% → 3 casas → **3,967%**.

---

## 2. Cadastro do contrato

### RN-CAD-01 Versão contratual e herança

- Cada contrato tem uma ou mais versões contratuais. Uma versão nova nasce de cada ato (contrato, termo aditivo ou
  deliberação) que muda o reajuste.
- A versão aponta a anterior em `herda`. A versão resolvida é a anterior com as chaves de primeiro nível da versão nova
  por cima (herança rasa: quem muda a fórmula reescreve o objeto `formula` inteiro).
- A versão aplicável a um ciclo é a indicada em `contrato.versao_contratual` do pleito. Ela tem de existir no cadastro
  (RN-V02) e ter `vigente_desde` anterior ou igual à vigência pretendida.
- Exemplo: `3TA-2024` (vigente desde 16/12/2024) herda de `contrato-2014` a fórmula, os pesos e a regra do terceiro mês
  anterior, e acrescenta `combinacao = multiplicativa` e o cronograma de realinhamento.
- Origem: RF-CAD-01; 1º termo aditivo dos Blocos (15/10/2024), que mudou de uma vez data-base, energia e índice de
  químicos; `versao()` em `scripts/validar_pleito.py`.

### RN-CAD-02 Fonte da regra com trecho literal

- Todo parâmetro (periodicidade, mês de referência, código de série, índice, pesos, combinação, cada parcela de
  realinhamento) tem ao menos uma fonte: documento e trecho literal.
- Conferência: o trecho, com espaços normalizados (sequências de espaço, tabulação e quebra de linha viram um espaço;
  pontas aparadas), tem de estar contido no texto normalizado do documento na base do Especialista (INT-05).
- Uma versão com trecho não achado não pode ser publicada (UC-06). Ela fica em rascunho com a lista dos trechos que
  faltam.
- Exemplo: "2º: a partir da referência janeiro de 2026 — 2,72%" achado em `TerceiroTermoAditivo-Paraty.txt`; os 12
  trechos do cadastro de Paraty foram achados.
- Origem: RF-CAD-02; regra V02 de `scripts/validar_pleito.py`.

### RN-CAD-03 Pesos como escritos

- O motor usa os pesos exatamente como escritos na fonte, sem normalizar a soma para 1.
- Se a soma diferir de 1, o cadastro registra a observação e a memória de cálculo mostra a soma.
- Exemplo: os pesos do Anexo X de Paraty somam **0,9999** (0,1951 + 0,0974 + 0,1082 + 0,0405 + 0,0662 + 0,4925),
  embora o texto diga 1,000. O parecer de 2025 escreve P1 = 0,195, mas calcula com 0,1951, que é o do Anexo X.
- Origem: `observacao_pesos` do cadastro de Paraty.

### RN-CAD-04 Calendário de data-base

- Cada contrato tem data-base derivada da última vigência homologada mais a periodicidade da versão (12 meses em
  Paraty).
- O sistema calcula a data prevista do próximo pleito e alerta o dono da instrução (PER-SEC) e a CAPET (PER-ANA)
  com antecedência configurável. Padrão "(proposto)": 60 dias corridos antes da data-base, que é o prazo de envio da
  memória de cálculo dos Blocos (N-P01-25, R-P01-12).
- Exemplo: tarifa de Paraty em vigor desde 12/01/2025 e pleito para 01/01/2026; o próximo ciclo tem data-base em
  01/01/2027, alerta em 02/11/2026.
- Origem: RF-CAD-04; N-P01-25 (subcláusula 29.5 do Bloco 2).

---

## 3. Validação do pleito (V01 a V12)

### RN-VAL-00 Situação, severidade e decisão

- Cada regra produz um ou mais itens com situação **ok**, **aviso** ou **erro**. Um item pode ainda ser marcado
  **a refazer** quando a fonte externa não respondeu (RN-SER-04).
- Decisão do resultado:

| Condição | Decisão | Ação |
|---|---|---|
| algum item com erro | `devolver` | UC-04: minuta do ofício de complementação com as pendências; PER-ANA confirma |
| nenhum erro, algum item a refazer | `a_refazer` | revalidação automática quando a fonte voltar (UC-20); o ciclo segue para a CAPET com o destaque |
| nenhum erro, nenhum a refazer | `segue_para_analise` | o ciclo vai à CAPET com o recálculo e os avisos em destaque |

- Ordem de execução: V01, V02, V03, V04, V05, V06, V07, V08, V09, V10, V11, V12. **V01 com erro interrompe** a
  validação (o resto não é confiável). **V02 com versão contratual inexistente interrompe.** As demais rodam todas,
  para a concessionária receber a lista completa de pendências de uma vez (instrução em rodada única, M-P01-08).
- O resultado guarda: versão do layout, contrato e versão contratual, versão das regras, séries usadas com data da
  consulta e o modo (`previa` ou `registrada`). Contrato: `contratos/resultado_validacao.schema.json`.
- Mensagens: frase completa, na linguagem de quem analisa, números no formato brasileiro (vírgula decimal, ponto de
  milhar) e meses como "out/2024". Os números brutos vão também nos campos estruturados do item (RNF-09).
- Exemplo: Paraty 2026 dá **10 ok, 5 avisos, 1 erro** (16 itens), decisão `devolver`.
- Origem: RF-PLE-03, RF-PLE-04; `docs/ESPECIFICACAO_DADOS_PLEITO.md`, seções 4 e 5.

### Quadro das regras V01 a V12

| ID | Regra | Confere | Severidade se falhar | Ação |
|---|---|---|---|---|
| RN-V01 | V01 Layout | o arquivo segue `pleito_reajuste.schema.json` | erro (aviso: nunca) | devolve; interrompe |
| RN-V02 | V02 Cadastro | versão contratual existe; trechos do cadastro achados no texto | erro | devolve |
| RN-V03 | V03 Interstício | ao menos 12 meses de referência; dias | erro (menos meses); aviso (menos de 365 dias) | devolve se erro |
| RN-V04 | V04 Meses o e i | iguais aos da regra do contrato | erro | devolve |
| RN-V05 | V05 Componentes | siglas e códigos iguais aos do cadastro | erro | devolve |
| RN-V06 | V06 Série completa | todos os meses de o até i | erro (falta o ou i); aviso (só as pontas) | devolve se erro |
| RN-V07 | V07 Série pública | valor igual ao da série pública | erro (não achado); aviso (menos casas) | devolve se erro |
| RN-V08 | V08 Conferência cruzada | valor igual ao de outros pleitos do mesmo índice e mês | aviso | segue com destaque |
| RN-V09 | V09 Recálculo do IR | IR refeito com os pesos do cadastro | erro | devolve |
| RN-V10 | V10 Total e realinhamento | parcela do cronograma; total pela regra de combinação | erro | devolve |
| RN-V11 | V11 Energia | distribuidora, composição e resolução da ANEEL | erro | devolve |
| RN-V12 | V12 Tabela tarifária | proposta = vigente × (1 + total) | erro (não fecha); aviso (sem tabela) | devolve se erro |

### RN-V01 Layout

- **Condição:** o pleito valida contra `contratos/pleito_reajuste.schema.json` (JSON Schema 2020-12, layout 0.1),
  inclusive `format: date`.
- **Itens:** um item de erro por violação, com o caminho do campo (JSON Pointer) e a mensagem.
- **Mensagem padrão:** ok: "Layout {versao} válido." · erro: "Campo {caminho}: {problema}."
- **Exceção de privacidade:** propriedade fora do layout é recusada antes da validação, sem guardar o pacote (RNF-05;
  ver `07_CONTRATOS_API.md`, erro `campo-fora-do-layout`). Os campos de texto livre (nomes, atos, composição,
  descrições) e os cabeçalhos dos CSV passam por um detector de dado pessoal (CPF, e-mail, telefone, nome de pessoa)
  "(proposto)"; achado → recusa com o erro `dado-pessoal`, o campo apontado e nada guardado (AT-22).
- **Exemplo:** Paraty 2026 → ok. Sem `componentes[0].evidencia` → erro "Campo /componentes/0: falta a propriedade
  obrigatória evidencia" (teste AT-05).

### RN-V02 Cadastro

- **Condição:** (a) `contrato.versao_contratual` existe no cadastro do contrato; (b) todos os trechos das fontes de
  todas as versões do cadastro são achados no texto (RN-CAD-02).
- **Severidade:** (a) falhou → erro e interrompe; (b) falhou → erro com a lista `versão:parâmetro`.
- **Base indisponível:** se o texto dos contratos não estiver acessível, item **aviso** "trechos não conferidos" e
  marcação a refazer (RNF-06).
- **Mensagem padrão:** ok: "Todos os trechos do cadastro foram achados no contrato e nos aditivos." · erro (a): "A
  versão contratual {codigo} não está no cadastro do contrato {numero}." · erro (b): "Trechos do cadastro não achados
  no texto: {lista}."
- **Exemplo:** Paraty 2026, versão `3TA-2024` → ok, 12 trechos achados.

### RN-V03 Interstício

- **Fórmula:** `meses = mes(vigencia_pretendida) − mes(tarifa_em_vigor.vigente_desde)`, em que `mes(d) = 12 × ano +
  mês`; `dias = vigencia_pretendida − vigente_desde` em dias corridos.
- **Severidade:** `meses < periodicidade_meses` → erro; senão `dias < 365` → aviso; senão ok. A contagem por mês ou
  por dia está em aberto (DEC-02).
- **Mensagem padrão:** "{meses} meses de referência entre {vigente_desde} e {vigencia} ({dias} dias)." No aviso,
  acrescenta: "O interstício em dias é menor que 365; a contagem por dia está em decisão."
- **Exemplo:** 12/01/2025 → 01/01/2026: 12 meses, **354 dias** → aviso.
- **Origem:** N-P01-17 (Lei 10.192/2001, art. 2º, § 1º), N-P01-18 (Lei 11.445/2007, art. 37), R-P01-10; cláusula 20
  de Paraty ("a cada período de 12 (doze) meses").

### RN-V04 Meses de referência

- **Fórmula:** ver RN-CAL-05. Esperado `i = vigencia − n meses`, `o = vigente_desde − n meses`.
- **Severidade:** `{o, i}` informados diferentes dos esperados → erro.
- **Mensagem padrão:** "Meses informados o = {o}, i = {i}; a regra do contrato ({n} meses antes da vigência) dá
  o = {o_esp}, i = {i_esp}."
- **Exemplo:** Paraty 2026 → o = out/2024 e i = out/2025, iguais → ok. Com i = set/2025 → erro (AT-05).
- **Caso real de origem:** CEDAE interior (SEI-480002/009940/2024): a concessionária usou set/2023 a out/2024
  (5,2826%) e a CAPET ago/2023 a set/2024 (4,6963%). O mês de referência mudou o resultado.

### RN-V05 Componentes e códigos

- **Condição:** o conjunto de siglas do pleito é igual ao do cadastro; para cada sigla com `codigo_serie` no cadastro,
  o código do pleito é o mesmo.
- **Severidade:** sigla a mais, a menos ou código diferente → erro.
- **Mensagem padrão:** ok: "Componentes e códigos iguais aos do cadastro." · erro: "Siglas a mais ou a menos:
  {lista}; códigos diferentes: {lista}."
- **Exemplo:** Paraty 2026 → ok (IMO 159401, IEE, IPA 1006819, IPQ 1006820, IPC, ICC 160868).
- **Origem:** o mesmo IPC aparece com três nomes e códigos em três processos (`docs/aulas/aula2_especificacao.fonte.html`,
  RF05).

### RN-V06 Série mensal completa

- **Condição:** para cada componente, a série tem os meses o e i e todos os meses entre eles
  (`mes(i) − mes(o) + 1` valores).
- **Severidade:** falta o ou i → erro para o componente (ele sai do recálculo); faltam meses intermediários → um item
  de aviso com a lista das siglas.
- **Mensagem padrão:** aviso: "Séries só com as pontas, sem os meses intermediários: {siglas}." · erro: "{sigla}:
  faltam os meses o ou i na série."
- **Exemplo:** Paraty 2026 → aviso para as 6 siglas (o processo trouxe só as pontas).

### RN-V07 Série pública

- **Aplica-se a:** componentes com `serie_publica` no cadastro (em Paraty: IPC → IPEADATA IGP12_IPC12; ICC →
  IPEADATA IGP12_INCC12).
- **Fórmula:** para cada valor x enviado em o e i, com `c` casas escritas (RN-NUM-02), x é "achado" se
  `|x − s| ≤ 0,5 × 10^−c` para o valor s da série pública **no mesmo mês** (com `c = 0`, tolerância 0,5).
- **Severidade:** algum valor não achado → erro; achados, mas com `c < casas_decimais.indice` → aviso
  (arredondado em relação à série); senão ok.
- **Mensagem padrão:** ok: "{sigla}: o = {o} e i = {i} achados em {serie}." · aviso: "... achados, mas com menos casas
  que a série ({valor_serie})." · erro: "{sigla}: {valor} não achado em {serie} no mês {mes}."
- **Exemplo:** IPC 761,643 e 789,092 → ok. ICC 1.149,17 e 1.222,36 (2 casas; o pleito declara 3) contra 1.222,356
  na série → aviso.
- **Diferença em relação ao oráculo "(proposto)":** o oráculo procura o valor em toda a série; o sistema compara no
  mês de referência. Os resultados esperados dos casos não mudam.
- **Origem:** 70 de 70 números-índice públicos dos pareceres achados nas séries (`saida/levantamento/calculo/resumo.json`).

### RN-V08 Conferência cruzada das séries pagas

- Ver RN-SER-02 para a regra completa.
- **Severidade:** sempre aviso quando não confere ou não há base de comparação (a série paga não tem fonte de
  conferência própria, RNF-04).
- **Mensagem padrão:** ok: "{sigla} ({codigo}): {n} de 2 valores iguais aos de outros pleitos do mesmo mês." · aviso:
  "... sem outro pleito do mesmo índice e mês para comparar." ou "... diferente de {valor} em outro pleito do mesmo mês."
- **Exemplo:** IPA, IPQ e ICC → ok (Imperatriz e Condessa, out/2024 e out/2025); IMO 159401 → aviso (nenhum outro
  contrato usa o ICC-RJ de mão de obra).

### RN-V09 Recálculo do IR

- **Fórmula:** RN-CAL-01 (índices ponderados) ou RN-CAL-02 (índice único), arredondamento RN-NUM-03 em
  `formula.casas_decimais_ir`.
- **Pré-condição:** todos os componentes do cadastro com o e i válidos (RN-V06). Se faltar algum, V09 e V10 não rodam
  e o resultado mostra "Recálculo não feito: faltam {siglas}" como erro.
- **Severidade:** `|IR_arredondado − ir_pct declarado| > 0,01` → erro (RNF-01).
- **Mensagem padrão:** "Índice refeito {ir}% (arredondado {ir_arr}%); declarado {ir_decl}%."
- **Exemplo:** 3,9669% → 3,967%; declarado 3,967% → ok. Com 4,5% declarado → erro (AT-05).
- **Casos reais de erro:** Paraty 2022 (SEI-220007/004053/2022): parecer de 10,37%, índices dão 9,5601% (AT-02).
  Centro Sul 2025 (SEI-480002/009058/2025): parecer de 4,1245%, índices dão 5,3195% (AT-03).

### RN-V10 Parcela de realinhamento e total

- **Parcela:** a parcela do cronograma da versão com `referencia` igual ao mês da vigência pretendida (AAAA-MM). Se
  existir, o pleito tem de declarar em `resultado_declarado.outros` um item `nome = "realinhamento"` com o mesmo `pct`
  (tolerância 10^−9). Diferente ou ausente → erro.
- **Total:** RN-CAL-03, combinando o **IR declarado** com os `outros` declarados. Assim V10 isola o erro de combinação;
  o erro do IR já é apontado por V09. `|total − total_pct declarado| > 0,01` → erro.
- **Mensagem padrão:** "Total pela regra {combinacao}: {total}%; declarado {total_decl}%; parcela {k} do cronograma
  ({pct}%)." · erro de parcela: "Realinhamento de {mes}: cronograma {pct}%, declarado {pct_decl}%."
- **Exemplo:** vigência jan/2026 → parcela 2 = 2,72%; (1,03967 × 1,0272) − 1 = **6,7949%**; declarado 6,795% → ok.
  Com parcela declarada de 6,30% → erro (AT-05).

### RN-V11 Energia

- **Aplica-se a:** versão com componente de fonte ANEEL.
- **Condição:** o bloco `energia` informa `distribuidora` e `composicao` com conteúdo (não vazio e sem a expressão
  "não informad") e cada resolução com `reh` identificada.
- **Severidade:** qualquer lacuna → erro. Quando a regra de composição estiver no cadastro (DEC-01), V11 passa também a
  recompor o valor do índice de energia nos meses o e i pela RN-SER-03 e a comparar com a série do pleito (tolerância
  pelas casas, como RN-V07).
- **Mensagem padrão:** "Energia sem {lista}." · ok: "Energia com distribuidora, composição e resoluções."
- **Exemplo:** Paraty 2026 → **erro**: "Energia sem distribuidora, composição e resolução da ANEEL" (511,75 e 471,91
  sem origem). É o único erro do pleito real.

### RN-V12 Tabela tarifária

- **Fórmula:** para cada linha, `proposta_esperada = arred(vigente × (1 + total_pct/100); casas_decimais.tarifa)`.
- **Severidade:** sem tabela → aviso; `|proposta_esperada − proposta| > 10^−casas` em alguma linha → erro com as
  categorias que não fecham.
- **Mensagem padrão:** aviso: "Pleito sem tabela tarifária vigente e proposta." · erro: "Tarifas que não fecham:
  {categorias}." · ok: "{n} tarifas fecham."
- **Exemplo:** Paraty 2026 → aviso (sem tabela). Com tabela e total de 6,795%, uma tarifa vigente T tem proposta
  esperada `arred(T × 1,06795; 4)`.

---

## 4. Cálculo do reajuste

### RN-CAL-01 IR por índices ponderados

```
IR = 100 × Σ_k  P_k × (I_k,i / I_k,o − 1)
```

- `P_k`: peso do componente k na versão; `I_k,o` e `I_k,i`: números-índice nos meses o e i.
- A apuração guarda cada termo: variação `I_k,i / I_k,o − 1` e termo ponderado `P_k × variação`.
- Exemplo resolvido (Paraty 2026, out/2024 → out/2025):

| Componente | Peso | I o | I i | Variação | Termo ponderado (p.p.) |
|---|---|---|---|---|---|
| IMO (ICC-RJ mão de obra, 159401) | 0,1951 | 1.466,05 | 1.576,75 | 7,5509% | 1,4732 |
| IEE (energia, ANEEL) | 0,0974 | 511,75 | 471,91 | −7,7851% | −0,7583 |
| IPA (derivados de petróleo, 1006819) | 0,1082 | 367,637 | 356,857 | −2,9322% | −0,3173 |
| IPQ (produtos químicos, 1006820) | 0,0405 | 199,691 | 209,255 | 4,7894% | 0,1940 |
| IPC (IPC-Brasil) | 0,0662 | 761,643 | 789,092 | 3,6039% | 0,2386 |
| ICC (INCC, 160868) | 0,4925 | 1.149,17 | 1.222,36 | 6,3689% | 3,1367 |
| **IR** | soma 0,9999 | | | | **3,9669** → 3,967% |

- Origem: cláusula 20 de Paraty ("IR = Σ Pk × (Ik_i − Ik_o) / Ik_o"); 24 de 28 cálculos da coorte conferem até
  0,01 p.p. (`recalculo.csv`).

### RN-CAL-02 IR por índice único

```
IR = 100 × (I_i / I_o − 1)
```

- Exemplo: Vale do Café 2025 (SEI-480002/009594/2025), IPCA-E (IBGE SIDRA tabela 3065) set/2024 = 6.855,40 e
  set/2025 = 7.220,07 → **5,3195%**, igual ao deliberado.

### RN-CAL-03 Regra de combinação do total

A regra é parâmetro da versão contratual (`combinacao`), nunca inferida.

| Valor | Fórmula | Uso |
|---|---|---|
| `multiplicativa` (padrão) | `Total = 100 × [(1 + IR/100) × Π_j (1 + x_j/100) − 1]` | Paraty, Imperatriz, Condessa, Blocos (11 de 11 apurações completas fecham pelo produto) |
| `aditiva` | `Total = IR + Σ_j x_j` | só se o ato disser; nenhuma apuração completa da coorte fecha pela soma |

- `x_j`: outros componentes do total (parcela de realinhamento, ITS, IDG como insumo informado).
- Exemplo: Paraty 2026 multiplicativa → 6,7949%; a soma daria 6,687%, fora da tolerância do declarado (6,795%).
- Origem: 3º Termo Aditivo de Paraty ("aplicados cumulativamente ao reajuste ordinário anual");
  `docs/LEVANTAMENTO_MOTOR_CALCULO.md`, seção 1 (duas cartas de Blocos somam em vez de multiplicar).

### RN-CAL-04 Realinhamento por parcela

- O cronograma é uma lista `{parcela, referencia (AAAA-MM), pct}` da versão contratual.
- A parcela do ciclo é a de `referencia` igual ao mês da vigência pretendida (RN-V10).
- O sistema registra na apuração que a parcela k foi aplicada no ciclo. Uma parcela não pode ser aplicada em dois ciclos.
  Se o ciclo pular a referência de uma parcela (vigência em outro mês), o sistema dá aviso "parcela {k} de {referencia}
  sem ciclo correspondente" "(proposto)" e a CAPET decide (DEC-07).
- Exemplo: 3º Termo Aditivo de Paraty: 1ª parcela 6,30% (jan/2025), 2ª a 7ª 2,72% (jan/2026 a jan/2031). O ciclo de
  2026 aplica a 2ª.

### RN-CAL-05 Mês de referência

- Regra `meses_antes_da_vigencia` com `n` meses (n = 3 em Paraty):

```
i = mes(vigencia_pretendida) − n
o = mes(tarifa_em_vigor.vigente_desde) − n
```

- O dia não conta: uma vigência em 12/01/2025 e outra em 01/01/2025 dão o mesmo mês de referência.
- Exemplo: vigência 01/01/2026 → i = out/2025; tarifa em vigor desde 12/01/2025 → o = out/2024.
- Outras regras (quarto mês anterior, data-base fixa) são o mesmo tipo com outro `n` ou outra regra no cadastro.
- Origem: cláusula 20 de Paraty ("ao terceiro mês anterior ao da data de início de vigência da tarifa em vigor").

### RN-CAL-06 Interstício

- Ver RN-V03. O motor guarda os dois números (meses de referência e dias corridos) na apuração; o painel e a minuta do
  parecer jurídico (RF-MIN-02) mostram os dois até a DEC-02.

### RN-CAL-07 Encadeamento de ciclos

- O mês o de um ciclo é o mês i do ciclo anterior homologado do mesmo contrato.
- Se o ciclo anterior não foi homologado, o mês o recua até o i do último ciclo homologado e a variação acumula o
  período inteiro. O sistema mostra o acúmulo em meses.
- Verificação: ao abrir a apuração, o sistema compara o o do pleito com o i do ciclo anterior no histórico. Diferente →
  aviso "o mês o ({o}) não é o mês i do ciclo anterior ({i_ant})" "(proposto)", porque o histórico pode estar
  incompleto (AT-08 depende do 1º e do 2º termos aditivos de Paraty).
- Exemplo: o ciclo de Paraty com tarifa vigente desde 12/01/2025 tem i = out/2024; o ciclo de 2026 tem o = out/2024.
  Caso de acúmulo: Vale do Café e Centro Sul 2023 (SEI-480002/000036/2023 e 000037/2023), set/2021 a set/2023,
  IPCA-E acumulado de 24 meses = 13,3556%.
- Origem: RF-CAL-06.

### RN-CAL-08 Memória de cálculo

- A memória de cálculo é gerada só a partir da apuração gravada e mostra, para cada número, a origem:
  `pleito` (campo e anexo com SHA-256), `serie_publica` (base, código, data da consulta) ou `cadastro` (versão,
  documento e trecho).
- Conteúdo mínimo: contrato e versão; regra do mês de referência e meses o e i; tabela da RN-CAL-01; IR refeito e
  arredondado; parcela e regra de combinação; total; comparação com o declarado; avisos; versões do layout, das regras e
  do cadastro (RNF-02, RNF-03).
- Séries pagas aparecem só dentro do ciclo, nunca em painel público (RNF-04).

---

## 5. Séries

### RN-SER-01 Séries públicas

- Fontes: IPEADATA (INT-02; INCC-DI geral, IPC-Brasil, IGP-M) e IBGE SIDRA (INT-03; IPCA tabela 1737, IPCA-E tabela
  3065).
- Toda consulta guarda a data e hora, a URL ou parâmetros e o valor. O cache vale até a próxima atualização agendada
  (UC-20); valor já publicado não muda no cache sem nova consulta registrada.
- Divergência entre o cache e uma nova consulta para o mesmo mês gera alerta ao PER-ADM e ao PER-ANA (revisão de série
  pela fonte).

### RN-SER-02 Conferência cruzada de séries pagas

- **Base de comparação:** valores do mesmo `codigo_serie` e do **mesmo mês** em outros ciclos do sistema, mais a carga
  inicial dos casos extraídos (`saida/levantamento/calculo/componentes.csv`). O próprio ciclo fica fora da base "(proposto)".
- **Igualdade:** pela tolerância das casas do valor enviado (RN-V07).
- **Situação:** ok se o e i conferem com pelo menos um valor da base cada; aviso se algum não confere ou não há base.
- **Limite:** o número continua vindo das concessionárias; um erro copiado por todas não é visto. A assinatura da
  FGV Dados (INT-07) é opcional e, se houver, substitui a conferência cruzada pela série da fonte.
- **Exemplo real de divergência:** Bloco 3 (SEI-480002/007639/2024), ICC-SP (código 1472373): pleito com 1.331,066 e
  CAPET com 1.339,322, de outro mês depois da mudança de data-base.
- **Licença:** valores de séries pagas não saem do ciclo nem vão a painel público ou exportação aberta (RNF-04).

### RN-SER-03 Composição da energia (decisão em aberto)

- A regra de composição é parâmetro da versão contratual (bloco `energia` do cadastro, "(proposto)"), validada com a
  CAPET (DEC-01). Até lá, V11 exige que a concessionária declare a composição usada.
- Campos exigidos no pleito (`energia` do layout 0.1): `distribuidora`, `subgrupo`, `modalidade`, `posto`,
  `composicao` e, por resolução homologatória, `reh`, `vigencia_inicio`, `tusd_mwh`, `te_mwh`, `bandeira_mwh`,
  `desconto_pct`. Arquivo `energia.csv` com as mesmas colunas.
- Campos do cadastro que a decisão precisa fixar: distribuidora local; subgrupo e modalidade (Paraty: A4,
  Convencional); componentes somados (TUSD, TE); com ou sem tributos; com ou sem bandeira; desconto (CDE); regra do mês
  da resolução (a vigente no mês de referência ou média de 12 meses).
- Quando fixada, o valor do índice num mês é
  `E(m) = (tusd_mwh + te_mwh + [bandeira_mwh]) × (1 − [desconto_pct]/100)` com a resolução vigente em m, nas casas do
  cadastro, e a variação entra em RN-CAL-01 como os demais componentes.
- Exemplo: Paraty 2026 traz 511,75 (out/2024) e 471,91 (out/2025) sem distribuidora, composição nem resolução; o
  pedido de alteração do IEE (SEI-480002/003110/2024) foi remetido à revisão ordinária (art. 16 da Deliberação
  4.830/2024).

### RN-SER-04 Fonte indisponível

- Mês necessário já no cache: o sistema usa o cache, registra a data da consulta que o trouxe e o item tem situação
  normal (o resultado é o mesmo de uma consulta ao vivo; AT-23, cenário com cache).
- Mês necessário fora do cache e fonte sem resposta em 30 s "(proposto)" ou com erro: o item fica **a refazer**, sem
  situação definitiva; as demais regras rodam; o pleito não é devolvido só por isso; nova consulta é agendada.
- O fluxo não para (RNF-06). A revalidação automática (UC-20) roda quando a fonte volta e registra novo resultado
  ligado ao anterior.

---

## 6. Calendário e prazos do rito

### RN-PRZ-01 Dias úteis e feriados do estado

- **Dia útil:** segunda a sexta, exceto feriado do calendário da agência.
- **Feriados fixos** (mês/dia): 01/01 Confraternização; 20/01 São Sebastião (Rio); 21/04 Tiradentes; 23/04 São Jorge
  (RJ); 01/05 Trabalho; 07/09 Independência; 12/10 Aparecida; 28/10 Servidor Público; 02/11 Finados; 15/11
  República; 20/11 Consciência Negra; 25/12 Natal.
- **Feriados móveis**, em dias a partir da Páscoa (P): Carnaval P−48 e P−47; Sexta-feira Santa P−2; Corpus Christi
  P+60.
- Pontos facultativos decretados entram no calendário pelo PER-ADM (UC-19), com o ato que os decretou "(proposto)".
- **Contagem em dias úteis** (IN AGENERSA 115/2024, art. 1º; N-P01-15): exclui o dia do início e inclui o do
  vencimento; conta só dias úteis.
- **Contagem em dias corridos:** exclui o dia do início e inclui o do vencimento. O vencimento nominal é início + n
  dias, mesmo que caia em dia sem expediente (é o que o teste de conformidade mede, AT-09); nesse caso o alerta "vence
  hoje" sai no primeiro dia útil seguinte (RN-TRA-03). A prorrogação do vencimento para o dia útil seguinte está na
  DEC-05.
- **Qual contagem:** prazos para atos dos interessados (razões finais, recurso, resposta a diligência, envio de
  faturas) em dias úteis desde 14/03/2024; prazos da agência conforme a norma de cada um (tabela da RN-PRZ-02).
- Exemplo: ofício de razões finais de Paraty em 17/12/2025 + 10 dias úteis → vence em **02/01/2026** (25/12 e 01/01
  não contam).
- Origem: `perfis/rj_agenersa.py` (calendário usado em todo o mapeamento); N-P01-15.

### RN-PRZ-02 Quadro dos prazos do rito

Cada prazo é uma instância de `Prazo`, contada de um marco, com dono e alerta (RF-PRZ-01, RF-PRZ-03). Os testes de
conformidade são os dos requisitos R-P01 (RN-IND-01).

| ID | Prazo | Duração e contagem | Conta de | Dono | Norma | Requisito legal | Natureza |
|---|---|---|---|---|---|---|---|
| RN-PRZ-03 | Pronunciamento sobre o pleito | 30 dias corridos | protocolo do pleito (t1) até a deliberação (t8) | relator (PER-REL), com instrução da CAPET e da Procuradoria | N-P01-20 (Lei 2.869/1997, art. 8º, parágrafo único); N-P01-26 (Blocos, 29.7); N-P01-02 | R-P01-05 | legal |
| RN-PRZ-04 | Razões finais | 10 dias úteis concedidos à parte | notificação para razões finais (t7) | relator (PER-REL) | N-P01-07 (Regimento, art. 49, § 2º); N-P01-15 | R-P01-04, R-P01-20 | legal |
| RN-PRZ-05 | Deliberar após razões finais | 40 dias corridos (10 de razões finais + 30 para decidir) | último ofício de razões finais (t7) até a deliberação (t8) | relator (PER-REL) | N-P01-13 (Lei 5.427/2009, art. 45); N-P01-07 | R-P01-06 | legal |
| RN-PRZ-06 | Parecer da Procuradoria | 15 dias corridos, prorrogáveis por mais 15 | último parecer técnico (t2) até o parecer jurídico (t3) | Procuradoria (PER-PRO) | N-P01-05 (Regimento, art. 17, VI); N-P01-09 | R-P01-07 | meta interna |
| RN-PRZ-07 | Prazo recursal | 10 dias úteis | publicação da deliberação (t9); ciência da concessionária mostrada ao lado | Secretaria Executiva (PER-SEC) | N-P01-12 (Regimento, art. 79); N-P01-15 | R-P01-19 (segregação) | legal |
| RN-PRZ-08 | Início da conferência das faturas | 90 dias corridos | última publicação (t9) até o 1º ato de conferência (t10) | CAPET (PER-ANA) | N-P01-29 (IN 31/2012, art. 1º, § 2º); N-P01-30 (IN 141/2025, § 4º) | R-P01-16 | legal |
| RN-PRZ-09 | Envio das faturas pela concessionária | 10 dias úteis | recebimento da solicitação de faturas | CAPET (PER-ANA) acompanha | N-P01-30 (IN 141/2025, § 2º) | R-P01-15 | legal |
| RN-PRZ-10 | Publicidade antes da vigência | antecedência mínima de 30 dias corridos | publicação ou divulgação até a vigência da nova tarifa | Secretaria Executiva (PER-SEC); divulgação pela concessionária | N-P01-19 (Lei 11.445/2007, art. 39); N-P01-27; N-P01-31 | R-P01-09 | legal |
| RN-PRZ-11 | Envio à ALERJ | até 20 dias corridos antes da vigência, se houver majoração | ofício à ALERJ até a vigência | Secretaria Executiva (PER-SEC) e CAPET | N-P01-22 (Lei 5.619/2009, art. 1º) | R-P01-11 | legal; o reajuste fica suspenso se não cumprir |
| RN-PRZ-12 | Memória de cálculo nos Blocos | até 60 dias corridos antes da data-base | protocolo do pleito | concessionária; PER-SEC confere | N-P01-25 (Bloco 2, 29.5) | R-P01-12 | contratual |
| RN-PRZ-13 | Resposta a diligência | o prazo concedido no ofício | ofício de diligência (t4, t14) ou reiteração (t5) | unidade que expediu (PER-REL ou PER-SEC) | Regimento; M-P01-07 | — | concedido |

Regras de cada prazo:

- **RN-PRZ-03 Pronunciamento em 30 dias.** O sistema conta do protocolo (marco `protocolo`) e mostra também a contagem
  a partir da instrução completa (validação sem erro), porque o Regimento, art. 85, II (N-P01-10), condiciona o início
  dos prazos à instrução completa atestada pela câmara técnica. O teste de conformidade usa o protocolo, como o
  R-P01-05 (DEC-05). Exemplo: protocolo de Paraty em 17/11/2025 → limite 17/12/2025; deliberação em 24/02/2026 = **99
  dias corridos → não conforme**.
- **RN-PRZ-04 Razões finais.** O modelo do ofício de razões finais (MOD-DOC) traz 10 dias úteis fixos; o sistema não
  emite o ofício com prazo menor. O ato seguinte (inclusão em pauta) só é liberado depois do vencimento (R-P01-20).
  Exemplo: em Paraty o ofício de 17/12/2025 concedeu 5 dias → **não conforme** ao R-P01-04; com a regra, vence em
  02/01/2026.
- **RN-PRZ-05 Deliberar em 40 dias.** Conta do último ofício de razões finais. A prorrogação por igual período
  (Lei 5.427/2009, art. 45) só vale com motivação registrada no prazo. Exemplo: 17/12/2025 → limite 26/01/2026;
  deliberação em 24/02/2026 = **69 dias corridos → não conforme**.
- **RN-PRZ-06 Procuradoria em 15 dias.** Conta do último parecer técnico (M-P01-05). A dilação de mais 15 dias exige
  justificativa e autorização do Procurador-Geral, registradas no prazo. O Regimento, art. 55, parágrafo único
  (N-P01-09), reduz em um terço os prazos internos quando há prazo legal ou contratual; a aplicação ao reajuste está na
  DEC-05. Exemplo: parecer técnico em 05/12/2025, parecer jurídico em 14/12/2025 = 9 dias corridos → conforme.
- **RN-PRZ-07 Prazo recursal.** Conta da publicação da deliberação (marco `publicacao`), como manda o RF-PRZ-07. A
  N-P01-12 descreve a contagem "da ciência da deliberação"; se a ciência da concessionária (marco `notificacao`) for
  posterior, o sistema mostra as duas datas e o vencimento pela ciência, sem mudar o teste, até a DEC-05. Recurso ou
  embargos registrados suspendem a certidão (RN-TRA-05). Recurso é distribuído a relator diverso do que propôs a
  deliberação (R-P01-19): o sistema impede atribuir o recurso ao mesmo gabinete. Exemplo: publicação em 26/02/2026 +
  10 dias úteis → vence em **12/03/2026**; certidão no dia útil seguinte, 13/03/2026 (AT-09).
- **RN-PRZ-08 Conferência das faturas em 90 dias.** Conta da última publicação antes da conferência (uma publicação
  de decisão em reunião interna não abre o prazo). Exemplo: publicação concluída em 05/03/2026, 1º ato da conferência em
  10/03/2026 = 5 dias corridos → conforme.
- **RN-PRZ-10 Publicidade.** `vigencia − data_publicidade ≥ 30 dias corridos`; o sistema calcula a data mínima de
  vigência no momento da publicação e alerta se a vigência pretendida for anterior. Exemplo: publicação no jornal em
  30/11/2025 (campo `publicacao` do pleito) e vigência em 01/01/2026 = 32 dias → conforme.
- **RN-PRZ-11 ALERJ.** Com total maior que zero, o sistema cria o prazo `envio_alerj` com vencimento em
  `vigencia − 20 dias corridos` e gera a minuta do ofício por modelo. Exemplo: vigência 01/01/2026 → envio até
  **12/12/2025**.

---

## 7. Donos, alertas, reiteração, pauta, certidão e encerramento

### RN-TRA-01 Marcos do ciclo

Cada marco é ligado à atividade do BPMN (`insumos/mapeamento/modelo_P01.json`). Os marcos alimentam prazos, indicadores e
testes de conformidade.

| Tipo de marco | Atividade | Registro |
|---|---|---|
| `protocolo` | t1 | envio do pleito (UC-01) ou importação do SEI (INT-01) |
| `validacao` | — | resultado da validação registrada (UC-02) |
| `devolucao` | — | ofício de complementação juntado (UC-04) |
| `parecer_tecnico` | t2 | parecer da CAPET juntado |
| `parecer_juridico` | t3 | parecer da Procuradoria juntado |
| `diligencia` | t4, t14 | ofício de diligência juntado, com prazo concedido |
| `reiteracao` | t5 | reiteração juntada |
| `conciliacao` | t6 | ata de conciliação |
| `acesso_autos` | t16 | ofício de acesso aos autos |
| `razoes_finais` | t7 | notificação para razões finais, com prazo concedido |
| `decisao_reuniao_interna` | t15 | decisão em reunião interna |
| `inclusao_pauta` | — | inclusão na pauta (UC-13) "(proposto)" |
| `deliberacao` | t8 | deliberação do Conselho-Diretor |
| `publicacao`, `notificacao` | t9 | publicação no Diário Oficial; ciência da concessionária |
| `divulgacao`, `envio_alerj`, `vigencia_tarifa` | t9 | divulgação da tarifa, ofício à ALERJ, início da vigência "(proposto)" |
| `recurso` | — | recurso ou embargos protocolados "(proposto)" |
| `conferencia_faturas` | t10 | 1º ato da conferência; conclusão |
| `parecer_arquivamento` | t11 | só por exceção (RN-TRA-06) |
| `certidao_ausencia_recurso` | t12 | certidão juntada |
| `encerramento` | t13 | termo de encerramento |

### RN-TRA-02 Dono por etapa

- Todo ciclo aberto tem **exatamente um** dono (unidade e, quando houver, servidor). A troca é atômica: registra quem
  passou, para quem, quando e por qual marco. Não existe estado "sem unidade" (RF-PRZ-02; I-P01-06).
- Enquanto um prazo concedido a terceiro corre, o dono continua sendo a unidade que expediu o ofício (M-P01-07).

| Etapa | Atividades | Dono | Perfil | Origem |
|---|---|---|---|---|
| Recebimento, validação e devolução | t1 | Secretaria Executiva (SCEXEC); CAPET confirma a devolução | PER-SEC, PER-ANA | M-P01-08, M-P01-10 |
| Cálculo e parecer técnico | t2 | CAPET | PER-ANA | M-P01-09 |
| Parecer jurídico | t3 | Procuradoria | PER-PRO | M-P01-05 |
| Diligências, reiteração, conciliação, acesso aos autos, razões finais | t4, t5, t6, t16, t7 | gabinete do relator | PER-REL | M-P01-07 |
| Diligência pela Secretaria, decisão em reunião interna | t14, t15 | Secretaria Executiva | PER-SEC | M-P01-07 |
| Pauta e deliberação | t8 | gabinete do relator; Secretaria pauta | PER-REL, PER-SEC | M-P01-06 |
| Publicação, notificação, prazo recursal, certidão | t9, t12 | Secretaria Executiva | PER-SEC | M-P01-02, M-P01-14 |
| Da publicação à conclusão da conferência das faturas | t10 | CAPET | PER-ANA | M-P01-01 |
| Encerramento | t13 | Secretaria Executiva | PER-SEC | M-P01-03, M-P01-04 |

- Exemplo do AS-IS que a regra elimina: na coorte, mediana de 41 dias úteis sem nenhuma unidade com o processo aberto,
  sobretudo depois da deliberação (`insumos/mapeamento/fatos_P01.json`).

### RN-TRA-03 Alertas de prazo

- Cada prazo gera alertas ao dono: antes do vencimento ("a vencer"), no vencimento ("vence hoje"; se o vencimento cair
  em dia sem expediente, no primeiro dia útil) e, sem marco de cumprimento, no dia útil seguinte ("vencido"), este
  também à chefia da unidade dona. Antecedências padrão "(proposto)": 3 e 1 dias úteis antes; o PER-ADM ajusta por tipo
  de prazo.
- Canais: fila do usuário (TL-10) e correio eletrônico institucional (INT-08).
- Ciclo concluído no SEI sem termo de encerramento → alerta à Secretaria no dia seguinte (I-P01-06).
- Origem: RF-PRZ-03; M-P01-12.

### RN-TRA-04 Reiteração da diligência

- Vencido o prazo de uma diligência sem marco de resposta, no **dia útil seguinte** o sistema gera a minuta da
  reiteração pelo modelo único, com: referência ao ofício original, novo prazo, consequência do silêncio e partes.
- O novo prazo é, por padrão, igual ao original; o dono pode aumentar, nunca diminuir abaixo do original (M-P01-07).
- A minuta fica "pronta para assinatura" na fila do dono; o sistema não assina nem envia (RNF-07).
- Exemplo de contagem (datas ilustrativas, calendário real): diligência com 10 dias úteis expedida em 05/03/2026 vence em 19/03/2026; sem resposta, a reiteração fica
  pronta em 20/03/2026 com novo prazo de 10 dias úteis, que vence em **06/04/2026** (a Sexta-feira Santa, 03/04/2026,
  não conta).
- Origem: RF-PRZ-04; t5 do BPMN.

### RN-TRA-05 Pauta, certidão de ausência de recurso

- **Pauta (RF-PRZ-06, M-P01-06):** no vencimento das razões finais, se R-P01-01, R-P01-02 e R-P01-03 estiverem
  atendidos (pareceres técnico e jurídico juntados e partes instadas), o ciclo entra na lista de aptos da primeira
  sessão com pauta aberta (TL-11). Se algum faltar, o sistema mostra o que impede (Regimento, art. 53; N-P01-08).
- **Certidão (RF-PRZ-08, M-P01-02, M-P01-14):** no dia útil seguinte ao vencimento do prazo recursal, sem marco
  `recurso`, o sistema gera a minuta da certidão de ausência de recurso para conferência e assinatura da Secretaria.
  Com recurso ou embargos, a contagem para, o gabinete é avisado e a certidão não é gerada.

### RN-TRA-06 Encerramento por lista de verificação

O termo de encerramento só é gerado quando todos os itens bloqueantes estão atendidos (Resolução CODIR 787/2022,
art. 1º e parágrafo único; N-P01-16).

| Item | Bloqueia | Teste |
|---|---|---|
| Deliberação publicada e concessionária notificada | sim | R-P01-08 |
| Certidão de ausência de recurso juntada depois do vencimento do prazo recursal, ou recurso julgado e publicado | sim | R-P01-17 |
| Conferência das faturas concluída e juntada | sim | R-P01-18 |
| Providências determinadas na deliberação registradas como cumpridas | sim | N-P01-16 |
| Publicidade 30 dias antes da vigência; envio à ALERJ | não (informativo) | R-P01-09, R-P01-11 |

- Item bloqueante que falha: o termo não sai e o sistema sugere a consulta à Procuradoria (t11) só nesse caso
  (M-P01-03).
- O termo e a conclusão no SEI são registrados no mesmo dia (M-P01-04).
- Exemplo do AS-IS: o ciclo de Paraty foi encerrado em 16/04/2026 sem certidão antes (`conformidade_P01.csv`,
  R-P01-17 não conforme); com a regra, o termo ficaria bloqueado até a certidão de 13/03/2026 estar juntada.

### RN-TRA-07 Ofício de diligência único por fase

- CAPET e Procuradoria registram quesitos no ciclo; o sistema junta os quesitos abertos e as pendências da validação
  num único ofício por fase (instrução, pós-pareceres), com uma só porta de saída (gabinete ou Secretaria).
- Origem: RF-DOC-03; M-P01-08 (diligências pela Secretaria em 61% dos casos e pelo gabinete em 50%).

---

## 8. Conferência de faturas

### RN-FAT-01 Remessa sem dados pessoais

- A remessa segue `contratos/remessa_faturamento.schema.json`: competência, contrato, ato da tabela aplicada e, por
  fatura, código anônimo da economia, categoria, faixa (se informada), consumo, valor cobrado e mês.
- O código anônimo é gerado pela concessionária, estável entre remessas e sem chave de reidentificação na agência.
- Campo fora do layout → a remessa é recusada inteira e nada é guardado (RNF-05).
- Origem: RF-FAT-01; M-P01-11; bases de economias dos Blocos chegaram ao SEI com dados pessoais
  (`docs/LEVANTAMENTO_MOTOR_CALCULO.md`, seção 5).

### RN-FAT-02 Tabela homologada aplicável

- A tabela aplicável a uma fatura é a homologada no ciclo cuja vigência cobre o mês da fatura. Proposta homologada =
  vigente × (1 + total), nas casas da tarifa (RN-V12).

### RN-FAT-03 Recálculo de cada fatura

- `valor_esperado = Σ_faixas consumo_na_faixa × tarifa_da_faixa`, por categoria, pela **regra de aplicação da tabela**
  da versão contratual (progressiva por faixa, faixa única, consumo mínimo). A regra não está nos autos e é decisão da
  CAPET (DEC-04).
- Divergência: `|valor_cobrado − valor_esperado| > tolerância`; tolerância padrão "(proposto)": R$ 0,01 por fatura.
- O sistema lista **só as divergências**, agrupadas por categoria e faixa, com quantidade e soma da diferença
  (RF-FAT-02).
- Não há exemplo numérico real: nos 1.228 documentos dos 18 processos há uma única peça de fatura.

### RN-FAT-04 Prazo e conclusão

- A conferência começa em até 90 dias corridos da publicação (RN-PRZ-08) e a CAPET atesta a correção ou informa a
  inobservância ao Conselho-Diretor (N-P01-29). A conclusão é marco do ciclo e item da lista de encerramento.

---

## 9. Minutas e citações

### RN-MIN-01 Verificação de citação

- Toda citação de minuta tem: fonte (norma N-P01, documento do cadastro, deliberação ou peça do processo), dispositivo
  e trecho.
- **Válida** quando: (a) a fonte existe na base (INT-05, cadastro ou autos); (b) o dispositivo citado existe na fonte,
  quando a base indexa os dispositivos (artigo, parágrafo, inciso, cláusula); (c) o trecho, normalizado como na
  RN-CAD-02, está contido no texto normalizado da fonte; (d) a fonte estava vigente na data da peça, quando a vigência
  é conhecida.
- **Inválida** em qualquer outro caso; a minuta mostra a citação marcada e o motivo (`fonte_inexistente`,
  `dispositivo_inexistente`, `trecho_nao_achado`, `fora_de_vigencia`). Se a base não indexa o dispositivo, o revisor o
  confere.
- Minuta com citação inválida não pode ser marcada "revisada" (meta de 0 citação inválida em peça assinada,
  Q-P01-01 a 03).
- Exemplo: "os interessados serão instados a apresentar as suas razões finais, no prazo máximo de 10 (dez) dias"
  (Regimento, art. 49, § 2º; N-P01-07) → válida. A mesma citação com "15 (quinze) dias" → inválida,
  `trecho_nao_achado`.
- Origem: RF-MIN-04; M-P01-15 a 17.

### RN-MIN-02 Números da minuta

- Todo número de minuta de parecer, relatório, voto e deliberação vem da apuração gravada ou de marco do ciclo,
  ligado à origem, e é campo travado: o revisor não o edita no texto. Para mudar um número, corrige-se a origem
  (pleito, cadastro, marco) e a minuta é regenerada (AT-18). O texto em volta é editável e entra na taxa de edição.
- A minuta da deliberação traz os quatro elementos de motivação do R-P01-14: fórmula contratual, índices usados,
  percentual e razões de divergência em relação aos pareceres.

### RN-MIN-03 Taxa de edição

- `taxa_edicao = trechos alterados / trechos da minuta`, por parágrafo, comparando a minuta gerada com a versão
  marcada como revisada (Q-P01-03). Cada edição é registrada (RF-MIN-05).

### RN-MIN-04 Decisão humana

- O sistema não assina, não protocola e não homologa (RNF-07). A minuta só vira peça para exportação depois de marcada
  "revisada" pelo perfil dono da peça.

---

## 10. Auditoria contínua e indicadores

### RN-IND-01 Semântica dos testes dos requisitos R-P01

Os testes de `insumos/mapeamento/normas_P01.json` rodam sobre os marcos de cada ciclo (RF-IND-02), com a semântica de
`scripts/conformidade.py`. Resultado: `conforme`, `nao_conforme`, `sem_evidencia` ou `nao_aplicavel`.

| Tipo | Regra |
|---|---|
| `precede(a, b)` | não aplicável se b não ocorre; conforme se há a com data ≤ primeira b |
| `exige(se, entao)` | não aplicável se nenhuma de `se` ocorre; conforme se alguma de `entao` ocorre |
| `prazo_max(de, ate, max, unidade)` | conta da 1ª ocorrência de `de` anterior à 1ª de `ate` (ou da última, com `de_ocorrencia = ultima`); conforme se ≤ max |
| `prazo_min(de, ate, min, unidade)` | conta da última ocorrência de `de` anterior à 1ª de `ate`; conforme se ≥ min |
| `prazo_concedido_min(atividade, min)` | menor prazo concedido nos ofícios da atividade; sem prazo lido → sem evidência |
| `manual` | no SEI dependia de leitura; no sistema vira teste computável sobre marcos que o sistema passa a registrar (quadro em `03_REQUISITOS.md`, RF-IND-02) |

### RN-IND-02 Indicadores I-P01

- Calculados só a partir dos marcos e das peças (RF-IND-01), com a definição, a frequência e a meta de
  `insumos/mapeamento/controles_P01.json`. Horas por processo (I-P01-02) são hipótese até a calibração com servidores.

### RN-IND-03 Controles de qualidade Q-P01

- Q-P01-01 a 04 medidos sobre as minutas e as edições (RF-IND-03): taxa de erro de extração, taxa de citação inválida
  antes da revisão e em peça assinada, taxa de edição, retificações por divergência entre votado e juntado.

---

## 11. Decisões em aberto

| ID | Decisão | Quem decide | Comportamento até decidir |
|---|---|---|---|
| DEC-01 | Regra de composição da energia (distribuidora, TUSD + TE, tributos, bandeira, desconto, mês da resolução) | CAPET | V11 exige a composição declarada e dá erro sem ela (RN-V11, RN-SER-03) |
| DEC-02 | Interstício por mês de referência ou por dia | CAPET e Procuradoria | erro por mês; aviso por dia (RN-V03); parâmetro de configuração `intersticio_contagem` "(proposto)" |
| DEC-03 | Instrumento que torna o layout obrigatório; canal de envio (peticionamento do SEI ou envio direto) | Procuradoria, Conselho-Diretor, TI | a API aceita os dois canais (`canal = direto` ou `sei`) |
| DEC-04 | Regra de aplicação da tabela nas faturas (faixas, consumo mínimo) e competência pedida | CAPET | RN-FAT-03 parametrizada; sem regra cadastrada, a conferência não roda |
| DEC-05 | Marco inicial do prazo de 30 dias (protocolo ou instrução completa) e do prazo recursal (publicação ou ciência), redução de 1/3 do art. 55 e contagem dos prazos internos | Procuradoria | o sistema mostra as duas contagens; o teste usa o protocolo e a publicação |
| DEC-06 | Modo de arredondamento (o contrato não define) | CAPET | meio para o par (RN-NUM-03) |
| DEC-07 | Parcela de realinhamento quando a vigência cai em mês diferente da referência | CAPET e Procuradoria | aviso (RN-CAL-04) |
| DEC-08 | Divergência do parecer de Paraty 2022 (10,37% escrito, 9,56% pelos índices) | CAPET | AT-02 espera erro em V09 |
