# 09. Integrações

Uma seção por integração fixada em [01_VISAO_ESCOPO.md](01_VISAO_ESCOPO.md) (seção 13). Cada uma diz o que se troca,
o endereço ou formato, os exemplos já testados no levantamento, a frequência, o cache, o que fazer na falha, a
segurança e a licença, a porta do domínio que a consome e o que está decidido ou em aberto.

## 1. Princípios comuns

| Princípio | Regra | Origem |
|---|---|---|
| Domínio não chama rede | O domínio fala só com portas (interfaces TypeScript). Os adaptadores ficam fora do domínio e são trocáveis | RNF-12; `05_ARQUITETURA.md` |
| Fonte fora do ar não para o fluxo | Usa o cache; sem cache, marca a conferência "a refazer" e segue | RF-SER-04, RNF-06 |
| Toda consulta deixa rastro | Cada valor externo guarda fonte, código, data da consulta e hash da resposta | RNF-02, RNF-03 |
| Revisão de série não muda o passado | Valor novo vira nova linha; a apuração gravada continua apontando o valor usado | RNF-03 |
| Segredo fora do código | Chaves e senhas só por variável de ambiente vinda do cofre ([14_OPERACAO.md](14_OPERACAO.md)) | RNF-10 |
| Teste sem rede | Toda integração tem dublê MSW com respostas gravadas ([12_TESTES.md](12_TESTES.md)) | RNF-12 |

### Portas do domínio

As portas, as operações e os adaptadores são os de [05_ARQUITETURA.md](05_ARQUITETURA.md), seção 9; os jobs que as
chamam estão na seção 12 do mesmo documento.

| Porta | Integrações | Operações | Adaptadores | Jobs |
|---|---|---|---|---|
| `Sei` | INT-01 | `vincularProcesso`, `registrarJuntada`, `listarAndamentos`, `entregarPeca` | `sei-manual`, `sei-webservice` | — |
| `FonteSeriePublica` | INT-02, INT-03, INT-07 | `buscarSerie(serie)` | `ipeadata`, `sidra`, `fgv-dados` (opcional) | JOB-01, JOB-04 |
| `FonteTarifasAneel` | INT-04 | `buscarResolucoes(distribuidora, periodo)` | `aneel` | JOB-01 |
| `BaseEspecialista` | INT-05 | `textoDocumento`, `deliberacoesDoContrato`, `versaoDaExportacao` | `especialista-arquivo`, `especialista-api` | JOB-06 |
| `ModeloLinguagem` | INT-06 | `gerarEstruturado({ tarefa, versaoPrompt, entrada, esquemaSaida })` | `desligado`, `openai-compativel`, `anthropic` | — |
| `Correio` | INT-08 | `enviar(mensagem)` | `smtp`; `memoria` nos testes | JOB-05 |

Todo adaptador devolve os valores com mês, casas decimais e data da consulta, ou a falha tipada
`FalhaFonteExterna { fonte, tipo }` (`TEMPO_ESGOTADO`, `HTTP`, `FORMATO`, `INDISPONIVEL`). O domínio decide pelo
resultado, nunca pela exceção do adaptador, e nenhuma resposta bruta passa da porta.

### Quadro geral

| ID | Sistema | Sentido | Forma | Frequência | Situação |
|---|---|---|---|---|---|
| INT-01 | SEI | ida e volta | manual na fase 1; webservice depois | a cada ato do rito | fase 1 decidida; webservice em aberto |
| INT-02 | IPEADATA | entrada | API OData 4 pública | diária e na validação | decidida e testada |
| INT-03 | IBGE SIDRA | entrada | API SIDRA pública | diária e na validação | decidida e testada |
| INT-04 | ANEEL dados abertos | entrada | arquivo do portal (CKAN) | semanal | acesso testado; regra de composição em aberto |
| INT-05 | Base do Especialista | entrada | exportação periódica | semanal e sob demanda | decidida; forma da exportação em aberto |
| INT-06 | Modelo de linguagem | ida e volta | API por adaptador | sob demanda | adaptador decidido; provedor e política em aberto |
| INT-07 | FGV Dados | entrada | a definir com o contrato | mensal | opcional; sem licença hoje |
| INT-08 | Correio institucional | saída | SMTP | diária e nos eventos | decidida |

## 2. INT-01 SEI

**O que se troca**

| Do SEI para o sistema | Do sistema para o SEI |
|---|---|
| Número do processo (abre o vínculo do ciclo, RF-PLE-06) | Peças geradas em DOCX e PDF (RF-DOC-02), para assinatura e juntada |
| Número de cada documento juntado (fecha o marco, RF-PRZ-01) | — |
| Andamentos do processo (marcos, posse por unidade), para conferência e indicadores | — |

**Formato**

- Número do processo: máscara `SEI-NNNNNN/NNNNNN/AAAA` (como `SEI-480002/009982/2025`), validada por expressão
  regular; número de documento: inteiro (como `120172748`).
- Peças: DOCX gerado pelo sistema e PDF/A para conferência. O nome do arquivo segue
  `<processo>_<tipo de peça>_<versão do modelo>.docx`.
- Andamentos (fase 1): importação de arquivo exportado da pesquisa de andamentos do SEI, em CSV com
  `processo,data_hora,unidade,descricao`. A descrição é a do SEI ("Processo remetido pela unidade ..."), a mesma que
  o mapeamento leu (`scripts/comum.py`, expressão `_RE_REMETIDO`).

**Fase 1 (decidida): troca manual**

1. O usuário baixa a peça gerada, inclui no SEI, assina e informa o número do documento no sistema.
2. A Secretaria informa o número do processo ao abrir o ciclo.
3. Uma vez por semana, ou quando quiser conferir, a Secretaria importa os andamentos. O sistema compara com os marcos
   registrados e lista o que falta ou diverge, sem sobrescrever.

**Fase 2 (em aberto): webservice do SEI**

- O SEI oferece serviços web (SOAP) para sistemas cadastrados, com operações de consulta de procedimento, listagem
  de andamentos e inclusão de documento. A versão do SEI-RJ, o cadastro do sistema cliente, as operações liberadas e
  a identificação de serviço são decisão da TI da agência (README, PARADA 11).
- Com o webservice, a porta `Sei` passa a consultar andamentos todo dia e a incluir a minuta como documento externo
  ou interno não assinado. **A assinatura continua humana** (RNF-07).

| Item | Regra |
|---|---|
| Frequência | a cada ato (manual); importação semanal de andamentos |
| Cache | não se aplica; o número informado é dado do ciclo |
| Falha e reprocesso | número inválido é recusado na hora; importação com erro em uma linha grava as demais e lista a linha recusada |
| Segurança | sem credencial do SEI no sistema na fase 1; na fase 2, credencial de sistema no cofre, nunca de usuário |
| Licença | não se aplica |
| Porta | `Sei` (adaptadores `sei-manual` e `sei-webservice`) |
| Decidido | troca manual na R1 e R2; número do documento fecha o marco |
| Em aberto | webservice (TI); canal de envio do pleito: peticionamento eletrônico do SEI com o validador na entrada, ou envio direto ao sistema com recibo (TI e Secretaria; `docs/ESPECIFICACAO_DADOS_PLEITO.md`, seção 6) |

## 3. INT-02 IPEADATA

**O que se troca:** números-índice mensais do INCC-DI, do IPC-Brasil e do IGP-M, para V07 (RF-SER-01).

**Endpoint testado no levantamento** (`scripts/recalcular_reajuste.py`, função `serie`):

```
GET http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='IGP12_INCC12')
GET http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='IGP12_IPC12')
GET http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='IGP12_IGPM12')
```

Os códigos estão em `scripts/comum.py` (`SERIES_PUBLICAS`) e vão para o cadastro do componente
(`serie_publica`, como em `saida/levantamento/contratos/paraty_008_2014.json`).

**Formato da resposta:** JSON OData com a lista `value`; cada item traz `SERCODIGO`, `VALDATA` (data ISO do mês) e
`VALVALOR` (número). O adaptador converte `VALDATA` em mês `AAAA-MM` e guarda `VALVALOR` sem arredondar.

```json
{"value": [{"SERCODIGO": "IGP12_INCC12", "VALDATA": "2025-10-01T00:00:00-03:00", "VALVALOR": 1222.356}]}
```

O valor do exemplo é o do INCC de out/2025 citado no levantamento ("a série publica 3 casas, 1.222,356";
`docs/ESPECIFICACAO_DADOS_PLEITO.md`, seção 5). O formato do restante do item deve ser conferido na resposta gravada.

**Testado:** os 70 números-índice públicos citados nos pareceres da coorte foram achados com o mesmo valor
(`saida/levantamento/calculo/resumo.json`, `achados_na_serie_publica`). Em Paraty 2026, o IPC (761,643 e 789,092) foi
achado; o INCC (1.149,17 e 1.222,36) foi achado com menos casas que a série, o que dá aviso em V07.

| Item | Regra |
|---|---|
| Frequência | diária pelo JOB-01 (UC-20) e na validação (JOB-04), se o mês pedido não estiver no cache |
| Cache | tabela `ValorSerieExterna` por série e mês, com data da consulta e hash; o cache nunca expira, só ganha linhas novas |
| Comparação | nas casas do valor enviado: tolerância de meia unidade da última casa escrita (oráculo `achado`) |
| Falha e reprocesso | tempo-limite de 120 s (o do oráculo); 3 tentativas com espera crescente; depois, `situacao = "indisponivel"`, V07 "a refazer" e reprocesso na próxima janela de UC-20 |
| Segurança | API pública sem chave; o endereço usa http: o adaptador tenta https primeiro e registra qual respondeu |
| Licença | dados públicos do IPEA; citar a fonte na memória de cálculo |
| Porta | `FonteSeriePublica`, adaptador `ipeadata`; endereço em `IPEADATA_URL_BASE` |
| Decidido | fonte do INCC-DI geral, IPC-Brasil e IGP-M |
| Em aberto | nenhum para a R1. O IPEADATA não tem os subíndices da FGV (mão de obra, IPA por produto): esses vêm por INT-07 ou pelo pleito (V08) |

## 4. INT-03 IBGE SIDRA

**O que se troca:** números-índice do IPCA (tabela 1737) e do IPCA-E (tabela 3065, número-índice do IPCA-15), para
V07.

**Endpoint testado** (`scripts/comum.py`, `SERIES_PUBLICAS`, mais o sufixo de período do oráculo):

```
GET https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all
GET https://apisidra.ibge.gov.br/values/t/3065/n1/all/v/1117/p/all
```

**Formato da resposta:** lista JSON. O primeiro elemento é o cabeçalho, com o rótulo de cada coluna; os demais são
linhas com o valor em `V` (texto). O adaptador:

- localiza a coluna do mês pelo rótulo do cabeçalho ("Mês (Código)", no formato `AAAAMM`), não pela posição;
- descarta as linhas com `V` igual a `...`, `-` ou `X` (como o oráculo);
- converte `V` em número sem arredondar.

**Testado:** IPCA-E de set/2024 (6.855,40) e de set/2025 (7.220,07), iguais aos do processo de Vale do Café
(Aula 2, etapa 5). O IPCA-E é o número-índice do IPCA-15, por isso a tabela 3065.

| Item | Regra |
|---|---|
| Frequência | diária pelo JOB-01 (UC-20); o IBGE publica uma vez por mês, mas a consulta diária pega revisões |
| Cache | igual ao INT-02 |
| Falha e reprocesso | igual ao INT-02 |
| Segurança | API pública sem chave, https |
| Licença | dados públicos do IBGE; citar a fonte |
| Porta | `FonteSeriePublica`, adaptador `sidra`; endereço em `SIDRA_URL_BASE` |
| Decidido | tabelas e variáveis acima |
| Em aberto | nenhum para a R1 |

## 5. INT-04 ANEEL dados abertos

**O que se troca:** tarifas homologadas das distribuidoras (TUSD e TE por resolução, subgrupo, modalidade e posto) e
bandeiras tarifárias, para conferir o componente de energia (V11, RF-SER-03).

**Formato testado no levantamento:** o conjunto de tarifas homologadas das distribuidoras do portal
`dadosabertos.aneel.gov.br`, baixado em parquet, com cerca de 657 mil linhas (Aula 2, etapa 5). Colunas conferidas
no arquivo do levantamento:

| Coluna | Uso |
|---|---|
| `DscREH` | resolução homologatória (vai para `energia.csv`, campo `reh`) |
| `SigAgente`, `NumCNPJDistribuidora` | distribuidora |
| `DatInicioVigencia`, `DatFimVigencia` | vigência da tarifa |
| `DscBaseTarifaria` | "Tarifa de Aplicação" ou "Base Econômica" |
| `DscSubGrupo`, `DscModalidadeTarifaria`, `NomPostoTarifario` | subgrupo (A4, A2), modalidade (Azul, Verde, Convencional), posto (ponta, fora ponta) |
| `DscClasse`, `DscSubClasse`, `DscDetalhe` | classe e detalhe |
| `DscUnidadeTerciaria` | unidade (kW, MWh) |
| `VlrTUSD`, `VlrTE` | valores |
| `DatGeracaoConjuntoDados` | data de geração do arquivo (vai para a data da consulta) |

As bandeiras vêm do conjunto "bandeiras-tarifarias" do mesmo portal, que já aparece citado nos autos da coorte (pleitos
da CEDAE). O portal usa CKAN: o adaptador descobre o recurso pela API de metadados do portal
(`/api/3/action/package_show`) e guarda o identificador do recurso em configuração (TL-15).

**Testado:** acesso ao arquivo e filtros por distribuidora, subgrupo e modalidade. **Nenhum valor de energia dos
pareceres foi reproduzido**, porque a regra de composição usada não está nos autos
(`docs/LEVANTAMENTO_MOTOR_CALCULO.md`, seção 7). Em Paraty 2026, os valores 511,75 e 471,91 são os mesmos do pleito
da Águas da Imperatriz, que os calcula com a tarifa A4 Azul fora de ponta (TUSD + TE) mais bandeira, e não com a
modalidade Convencional da definição contratual (`saida/levantamento/calculo/extracao_SEI-480002_009982_2025.json`).

| Item | Regra |
|---|---|
| Frequência | semanal pelo JOB-01; e na validação, se a resolução citada no pleito não estiver no cache |
| Cache | arquivo baixado guardado com hash e data de geração; tabela derivada só com as linhas das distribuidoras e subgrupos usados nos cadastros |
| Falha e reprocesso | download interrompido: mantém o arquivo anterior; V11 usa o cache e marca "a refazer" se a resolução pedida não estiver nele |
| Segurança | download público, https; o arquivo é dado não confiável: validar colunas e tipos antes de gravar |
| Licença | dados abertos da ANEEL; citar a fonte |
| Porta | `FonteTarifasAneel`, adaptador `aneel`; endereço em `ANEEL_URL_BASE` |
| Decidido | fonte das tarifas e das bandeiras; o pleito traz `energia.csv` com resolução, distribuidora, subgrupo, modalidade, posto, TUSD, TE, bandeira e desconto (`docs/ESPECIFICACAO_DADOS_PLEITO.md`, seção 3) |
| Em aberto | **regra de composição da energia de cada contrato** (CAPET): distribuidora, TUSD + TE, com ou sem tributos, bandeira, desconto, média de 12 meses e mês da resolução. Até a decisão, V11 só confere se o pleito informa distribuidora, composição e resolução, e dá erro se não informa (como em Paraty 2026). Depois da decisão, a regra entra como parâmetro da versão contratual (UC-06) e V11 passa a recalcular o valor |

## 6. INT-05 Base do Especialista AGENERSA

**O que se troca:** textos integrais de contratos, aditivos e anexos (para V02, RF-CAD-02), deliberações anteriores do
mesmo contrato (precedentes de RF-MIN-02 e padrão de RF-MIN-03) e textos de normas (verificação de citação,
RF-MIN-04).

**Formato:** a base é um SQLite com tabelas de contratos, normativos e deliberações, mais os textos em arquivo
(`data/txt/biblioteca/...`, relativo à base; `scripts/comum.py`, `TEXTOS_CONTRATOS`). A tabela de contratos liga
contrato e aditivos em linha do tempo; a categoria de contratos tem 198 documentos (24 contratos, 39 aditivos, 62
anexos) e cobre 11 das 12 concessionárias da coorte (`docs/LEVANTAMENTO_MOTOR_CALCULO.md`, seção 6).

O sistema recebe uma **exportação periódica** em pacote: os textos em UTF-8, um índice JSON por documento
(`id`, `tipo`, `titulo`, `data`, `contrato`, `hash`) e o hash do pacote. O sistema não lê o SQLite de produção do
Especialista.

**Testado:** os 12 trechos do cadastro de Paraty foram achados literalmente
(`docs/ESPECIFICACAO_DADOS_PLEITO.md`, seção 1); os 31 trechos de norma de `insumos/mapeamento/normas_P01.json` foram
conferidos contra o texto integral por `scripts/verificar_normas.py`.

| Item | Regra |
|---|---|
| Frequência | semanal pelo JOB-06; sob demanda quando o gestor cadastra um aditivo novo |
| Cache | cada documento guardado com hash; documento alterado vira nova versão; trecho conferido aponta a versão do texto |
| Comparação | trecho literal com espaços normalizados (oráculo `norm` em `scripts/validar_pleito.py`) |
| Falha e reprocesso | pacote com hash errado é recusado inteiro; sem pacote, V02 dá aviso "trechos não conferidos nesta execução" |
| Segurança | documentos públicos; o pacote chega por canal interno da agência |
| Licença | atos públicos; nenhuma restrição |
| Porta | `BaseEspecialista`, adaptador `especialista-arquivo` (ou `especialista-api`, se houver); `ESPECIALISTA_MODO` |
| Decidido | a base é a fonte dos textos; o cadastro é por contrato, não por concessionária (a linha do tempo da base junta os Blocos 1 e 4) |
| Em aberto | forma da exportação (pacote de arquivos ou API do Especialista), dono da rotina e frequência final (TI). Texto de OCR com fórmula ilegível (Paraty) exige reconstrução registrada no cadastro. Falta o contrato-base da Águas da Condessa |

## 7. INT-06 Modelo de linguagem

**O que se troca:** pedido de redação ou de extração com o contexto do ciclo; resposta com texto e citações
propostas. Usos: minutas (RF-MIN-01 a RF-MIN-03), extração de dados do pleito em PDF (M-P01-15) e proposta de
citações. **A verificação da citação não é feita pelo modelo**: é conferência literal do trecho contra o texto da
fonte (INT-05, RF-MIN-04).

**Formato:** a operação é `gerarEstruturado({ tarefa, versaoPrompt, entrada, esquemaSaida })` da porta
`ModeloLinguagem`. Exemplo de chamada para a minuta do relatório (forma ilustrativa; o esquema de saída fica em
[07_CONTRATOS_API.md](07_CONTRATOS_API.md)):

```json
{
  "tarefa": "minuta_relatorio",
  "versaoPrompt": "relatorio-reajuste@1",
  "entrada": {
    "fatos": ["linha do tempo dos marcos do ciclo", "conclusões dos pareceres"],
    "precedentes": ["identificadores das deliberações anteriores do contrato"],
    "marcadores": {"IR": "{{apuracao.ir_pct}}", "TOTAL": "{{apuracao.total_pct}}"}
  },
  "esquemaSaida": "minuta com texto, marcadores intactos e lista de citações {norma, dispositivo, trecho}"
}
```

A resposta traz o texto com os marcadores intactos e as citações propostas. O sistema substitui os marcadores pelos
números da apuração depois da resposta, para que **nenhum número venha do modelo** (RNF-02), e confere cada citação
contra o texto da fonte antes de mostrar a minuta.

| Item | Regra |
|---|---|
| Frequência | sob demanda (pedido de minuta) |
| Cache | por hash de (tarefa, versão do modelo de documento, contexto, provedor, modelo); mesma entrada devolve a mesma minuta sem nova chamada |
| Registro | cada `Minuta` guarda provedor, modelo, versão, hash do pedido e data, para os controles Q-P01-01 a 03 |
| Falha e reprocesso | tempo-limite configurável; 2 tentativas; depois a minuta sai só com as partes por modelo de documento e o texto corrido em branco, sem bloquear o rito |
| Segurança | o pedido não leva dado pessoal (nomes de signatários e servidores são removidos antes do envio) nem valores de séries pagas (RNF-04); chave de API no cofre |
| Licença | termos do provedor contratado; o texto gerado é minuta da agência |
| Porta | `ModeloLinguagem`, adaptadores `desligado`, `openai-compativel` e `anthropic`; `LLM_PROVEDOR` |
| Decidido | adaptador com provedor configurável; decisão sempre humana (RNF-07); números por campo; citação verificada por regra |
| Em aberto | provedor, modelo e política de dados (TI e Procuradoria; README, PARADA 11): onde o dado é processado, retenção pelo provedor e uso para treino |

## 8. INT-07 FGV Dados

**O que se troca:** séries pagas da FGV: mão de obra (ICC-RJ, ICC-SP, INCC mão de obra) e IPA-OG-DI de derivados de
petróleo e de produtos químicos. São 17 dos 57 componentes da coorte (`saida/levantamento/calculo/resumo.json`,
`componentes_por_disponibilidade`).

**Formato:** a definir com o contrato de assinatura. Até lá, a série vem no pleito (`series.csv`) e o sistema faz a
conferência cruzada entre pleitos (V08). Ela pegou uma diferença real no Bloco 3 (1.331,066 no pleito e 1.339,322 na
CAPET, de outro mês) e confirma os IPA de out/2024 e out/2025 iguais em Paraty, Imperatriz e Condessa.

| Item | Regra |
|---|---|
| Frequência | mensal, se contratada |
| Cache | igual ao INT-02, com marca "série paga" |
| Falha e reprocesso | sem a integração, V08 é a conferência; com ela fora do ar, V08 continua valendo |
| Segurança | credencial da assinatura no cofre |
| Licença | **a licença proíbe publicar ou redistribuir as séries** (contratos públicos da FGV: R$ 15 mil por 10 séries em 2019; R$ 30 mil por 20 séries em 2021; Aula 2, etapa 5). As séries pagas não saem do processo, não vão para painel público, não vão para o modelo de linguagem e aparecem para PER-GES só como variação (RNF-04) |
| Porta | `FonteSeriePublica`, adaptador `fgv-dados`; `FGV_DADOS_URL` e `FGV_DADOS_CHAVE` |
| Decidido | integração opcional; o sistema funciona sem ela |
| Em aberto | contratar ou não (Gestão); limite da conferência cruzada: um erro copiado por todas as concessionárias não seria visto |

## 9. INT-08 Correio eletrônico institucional

**O que se troca:** alertas de prazo ao dono e à chefia (RF-PRZ-03), aviso de pleito devolvido à concessionária e
aviso de série revisada ao analista.

**Formato:** SMTP com STARTTLS. A mensagem tem assunto padronizado
(`[Reajusta] <processo SEI> – <prazo> vence em <data>`), o nome do contrato, o prazo, o vencimento, o dono e o link
para a TL-10. Não leva anexo nem número de série paga.

| Item | Regra |
|---|---|
| Frequência | alertas criados pelo JOB-02 (diário, `JOB_PRAZOS_CRON`) e enviados pelo JOB-05; devolução de pleito na hora |
| Cache | fila de envio persistente; cada alerta tem identificador e não é enviado duas vezes |
| Falha e reprocesso | 3 tentativas com espera crescente; falha final fica registrada no `Alerta` e visível na TL-10; o alerta na tela vale mesmo sem correio |
| Segurança | conta de serviço com senha no cofre; destinatário só o endereço institucional do usuário cadastrado |
| Licença | não se aplica |
| Porta | `Correio`, adaptador `smtp`; enviado pelo JOB-05 |
| Decidido | correio como canal secundário; a fila da TL-10 é o canal principal |
| Em aberto | servidor, conta e limites de envio (TI) |
