# 01. Visão, escopo e identificadores

Documento-base do pacote. Ele define módulos, perfis, glossário, casos de uso, requisitos, entidades, telas e
integrações, sempre com identificador. **Os demais documentos usam só estes identificadores e estes nomes.** Se um
documento precisar de um item novo, ele é acrescentado aqui antes.

Sistema: **Reajusta**, o sistema de reajuste tarifário anual da AGENERSA (processo P01 do catálogo). O nome é de
trabalho.

## 1. Problema

O mapeamento AS-IS a partir do SEI (coorte de 18 processos com trilha nativa) mostrou:

- **Duração:** mediana de 337,5 dias úteis por caso. A mediana da espera entre atividades é de 137,5 dias úteis,
  contra 26,5 dias úteis de execução.
- **Caminhos:** 18 casos seguiram 17 caminhos distintos, por diligências repetidas (Secretaria em 61% dos casos,
  gabinete em 50%), pedidos de acesso aos autos (50%) e decisões fora da sessão (44%).
- **Gargalo:** o processo sem dono. Fica no gabinete (mediana de 74,5 dias úteis por caso) ou sem unidade nenhuma
  (41 dias úteis), sobretudo depois da deliberação.
- **Prazos legais:** pronunciamento em até 30 dias do pleito em 17,6% dos casos; ofício de razões finais com 10 dias
  em 22,2%; encerramento só depois da certidão de ausência de recurso em 25%.
- **Cálculo:** feito à mão, com memória de cálculo pedida por ofício. Em 28 cálculos refeitos, 2 pareceres não
  fecham com os próprios índices; num deles o percentual escrito foi o homologado (a confirmar com a CAPET).

Fontes: `insumos/mapeamento/fatos_P01.json`, `insumos/mapeamento/conformidade_P01.json`, `saida/levantamento/calculo/recalculo.csv`.

## 2. Objetivo e metas

Levar o reajuste anual do protocolo ao arquivamento com: pleito completo na entrada, cálculo conferido por máquina,
prazos com dono e alerta, documentos de rotina gerados por modelo, minutas assistidas com citação verificada e
decisão sempre humana.

| Indicador (de `insumos/mapeamento/controles_P01.json`) | Linha de base | Meta |
|---|---|---|
| I-P01-01 Duração do pleito ao encerramento (mediana) | 337,5 du | 155,8 du na fase 1; 149,3 na fase 2; 145,5 na fase 3 (simulação, cenário esperado) |
| I-P01-02 Horas de trabalho por processo (mediana, teto) | 64,0 h | 63,4 h na fase 1; 60,0 na fase 2 (hipótese até calibração) |
| I-P01-06 Dias sem nenhuma unidade com o processo aberto | 41 du | 23 du na fase 1; 5 na fase 2 |
| I-P01-07 Pareceres de cálculo refeitos ou cancelados | 5 casos | 0 na fase 2 |
| I-P01-10 Encerramento precedido da certidão de ausência de recurso | 25% | 100% |

As fases das metas são as fases do TO-BE: 1 ajusta o fluxo, 2 automatiza regras e dados, 3 usa IA.

## 3. Escopo

**Dentro:**
- O P01 de ponta a ponta, com as 16 atividades do BPMN (`insumos/mapeamento/modelo_P01.json`).
- Contratos de saneamento e resíduos com fórmula de índices ponderados ou de índice único.
- Piloto em Águas de Paraty (008/2014). Generalização provada com Águas da Imperatriz.

**Fora (por ora):**
- Revisão tarifária quinquenal (P02).
- Custo do gás e conta gráfica.
- Cálculo do índice de tarifa social (ITS) e do índice de desempenho (IDG): entram como insumo informado, com evidência.
- Assinatura e protocolo, que continuam no SEI.
- A decisão de homologar, que é do Conselho-Diretor.

## 4. Stack

Padrão da casa: Next.js (App Router), React, TypeScript estrito, Tailwind, Zod, Prisma com PostgreSQL, TanStack Query
e Table, react-hook-form, NextAuth, Vitest, Testing Library, MSW e Playwright, cada um na última versão estável
(fotografia de 01/11/2026: Next.js 16.x, Prisma 7.x, Node.js 26 LTS, PostgreSQL 18; ADR-0012). A interface segue o
padrão digital de governo (Design System gov.br). Detalhes e exceções nos ADRs (`05_ARQUITETURA.md`, pasta `adr/`).

## 5. Módulos

| ID | Módulo | O que faz | Melhorias do TO-BE (`melhorias_P01.json`) |
|---|---|---|---|
| MOD-PLE | Pleitos | Recebe o pleito no layout, valida na entrada, devolve com pendências | M-P01-08, M-P01-10 |
| MOD-CAD | Cadastro de contratos | Contratos, versões por aditivo, parâmetros com trecho literal, calendário de data-base | M-P01-09 |
| MOD-CAL | Motor de cálculo | Recalcula índice e total, confere séries, gera a memória de cálculo | M-P01-09, M-P01-15 |
| MOD-SER | Séries | Busca, cache e conferência de séries públicas e pagas | M-P01-09 |
| MOD-PRZ | Prazos e tramitação | Marcos, prazos, donos, alertas, reiteração, pauta, prazo recursal, encerramento por lista de verificação | M-P01-02 a 07, M-P01-12, M-P01-14 |
| MOD-DOC | Documentos por modelo | Ofícios, notificações, certidões e termos gerados com os dados do processo | M-P01-13 |
| MOD-MIN | Minutas assistidas | Minutas de parecer técnico, parecer jurídico, relatório, voto e deliberação, com citação verificada | M-P01-15 a 18 |
| MOD-FAT | Conferência de faturas | Remessa periódica de faturamento, conferência contra a tabela homologada | M-P01-01, M-P01-11 |
| MOD-IND | Indicadores e auditoria contínua | Indicadores I-P01, controles de qualidade Q-P01, testes contínuos dos requisitos R-P01 | controles_P01.json |
| MOD-ADM | Administração | Usuários, perfis, modelos de documento, integrações, trilha de auditoria | — |

## 6. Perfis (atores)

| ID | Perfil | Quem | Faz |
|---|---|---|---|
| PER-CON | Concessionária | usuário externo da regulada | envia o pleito, vê a validação e as pendências, responde diligências, envia remessa de faturamento |
| PER-ANA | Analista da CAPET | servidor da Câmara de Política Econômica e Tarifária | confere o cálculo, revisa e emite o parecer técnico, confere faturas |
| PER-GCA | Gestor do cadastro | servidor da CAPET designado | mantém contratos, versões e parâmetros |
| PER-PRO | Procurador | servidor da Procuradoria | revisa a minuta e emite o parecer jurídico |
| PER-SEC | Secretaria Executiva | servidor da SCEXEC | recebe, distribui, notifica, publica, certifica e encerra |
| PER-REL | Gabinete do relator | conselheiro-relator e assessoria | conduz diligências, revisa minutas de relatório, voto e deliberação |
| PER-GES | Gestão | Conselho-Diretor, gerentes, controle interno | consulta painéis e indicadores (somente leitura) |
| PER-ADM | Administrador | TI da agência | usuários, perfis, integrações, modelos |
| SIS-EXT | Sistemas externos | IPEADATA, IBGE SIDRA, ANEEL, base do Especialista, SEI, modelo de linguagem | fornecem ou recebem dados |

## 7. Glossário (linguagem do domínio)

Use estes termos no código (nomes de entidade, função e tela), sem tradução para o inglês.

| Termo | Significado |
|---|---|
| Ciclo de reajuste | Um reajuste anual de um contrato, do pleito ao encerramento. Corresponde a um processo SEI |
| Pleito | Pedido da concessionária para um ciclo, no layout de dados (`pleito_reajuste.schema.json`) |
| Contrato | Contrato de concessão ou de programa, com número e concessionária |
| Versão contratual | Conjunto de regras de reajuste vigente a partir de um ato (contrato, termo aditivo, deliberação). Herda da anterior |
| Fórmula | Tipo (índices ponderados, índice único), mês de referência, casas decimais |
| Componente | Índice da fórmula, com sigla, peso, fonte e código de série |
| Fonte da regra | Documento e trecho literal que sustentam um parâmetro |
| Série | Valores mensais de um índice (número-índice) |
| Mês o, mês i | Meses de referência da tarifa em vigor e da nova tarifa |
| Interstício | Intervalo mínimo entre dois reajustes |
| IR | Índice de reajuste da fórmula |
| Realinhamento | Percentual adicional fixado por aditivo ou deliberação, em parcelas, combinado ao IR |
| Total | Percentual final aplicado à tabela tarifária |
| Apuração | Resultado do motor de cálculo: termos ponderados, IR, total, memória |
| Regra de validação | V01 a V12; cada uma dá ok, aviso ou erro |
| Pendência | Erro de validação a corrigir pela concessionária |
| Marco | Evento datado do ciclo (protocolo, parecer técnico, razões finais, deliberação, publicação, certidão, encerramento) |
| Prazo | Intervalo contado de um marco, com dono e alerta |
| Peça | Documento do processo (ofício, parecer, relatório, voto, deliberação, certidão, termo) |
| Minuta | Versão de peça gerada pelo sistema, para revisão humana |
| Citação | Referência a norma, contrato ou deliberação dentro de uma minuta, com trecho verificado |
| Remessa de faturamento | Arquivo periódico enviado pela concessionária para a conferência das faturas |

## 8. Casos de uso

| ID | Caso de uso | Ator principal | Módulo |
|---|---|---|---|
| UC-01 | Enviar pleito | PER-CON | MOD-PLE |
| UC-02 | Validar pleito na entrada | sistema (gatilho: UC-01) | MOD-PLE |
| UC-03 | Recalcular e conferir séries | sistema (incluído em UC-02) | MOD-CAL, MOD-SER |
| UC-04 | Devolver pleito com pendências | PER-ANA confirma | MOD-PLE, MOD-DOC |
| UC-05 | Emitir memória e minuta do parecer técnico | PER-ANA | MOD-CAL, MOD-MIN |
| UC-06 | Manter cadastro do contrato | PER-GCA | MOD-CAD |
| UC-07 | Consultar histórico do contrato | PER-ANA, PER-GES | MOD-CAD, MOD-CAL |
| UC-08 | Acompanhar prazos e marcos do ciclo | PER-SEC, PER-REL, PER-ANA, PER-PRO | MOD-PRZ |
| UC-09 | Emitir documento por modelo | PER-SEC, PER-REL | MOD-DOC |
| UC-10 | Conduzir diligência em rodada única | PER-REL, PER-SEC | MOD-PRZ, MOD-DOC |
| UC-11 | Emitir minuta do parecer jurídico | PER-PRO | MOD-MIN |
| UC-12 | Emitir minutas de relatório, voto e deliberação | PER-REL | MOD-MIN |
| UC-13 | Pautar o reajuste no Conselho-Diretor | PER-SEC | MOD-PRZ |
| UC-14 | Publicar, notificar e contar o prazo recursal | PER-SEC | MOD-PRZ, MOD-DOC |
| UC-15 | Certificar ausência de recurso e encerrar | PER-SEC | MOD-PRZ, MOD-DOC |
| UC-16 | Enviar remessa de faturamento | PER-CON | MOD-FAT |
| UC-17 | Conferir faturas contra a tabela homologada | PER-ANA | MOD-FAT |
| UC-18 | Acompanhar indicadores e auditoria contínua | PER-GES | MOD-IND |
| UC-19 | Administrar usuários, perfis, modelos e integrações | PER-ADM | MOD-ADM |
| UC-20 | Atualizar séries externas | sistema (agendado) | MOD-SER |

## 9. Requisitos funcionais

Forma: "o sistema deve…". A origem está em `03_REQUISITOS.md`.

| ID | Requisito (resumo) |
|---|---|
| RF-PLE-01 | Receber o pleito como pacote no layout 0.1, com evidências e hash SHA-256 |
| RF-PLE-02 | Validar o layout e listar cada campo faltante ou fora do formato (V01) |
| RF-PLE-03 | Aplicar as regras V01 a V12 e registrar o resultado com as versões usadas |
| RF-PLE-04 | Devolver o pleito com erro, com a lista de pendências e a minuta do ofício de complementação |
| RF-PLE-05 | Permitir à concessionária validar o pacote antes de enviar (mesmas regras, sem registro) |
| RF-PLE-06 | Abrir o ciclo de reajuste e vinculá-lo ao número do processo SEI |
| RF-CAD-01 | Manter contratos e versões contratuais, cada versão herdando da anterior |
| RF-CAD-02 | Exigir documento e trecho literal para cada parâmetro e conferir o trecho no texto (V02) |
| RF-CAD-03 | Manter o cronograma de realinhamento por versão |
| RF-CAD-04 | Manter o calendário de data-base de cada contrato e alertar antes do início da instrução |
| RF-CAL-01 | Recalcular o IR com os pesos da versão e arredondar nas casas do contrato (V09) |
| RF-CAL-02 | Compor o total pela regra de combinação da versão e conferir a parcela de realinhamento (V10) |
| RF-CAL-03 | Conferir interstício e meses de referência (V03, V04) |
| RF-CAL-04 | Conferir a tabela tarifária proposta (V12) |
| RF-CAL-05 | Gerar a memória de cálculo com cada termo e a origem de cada número |
| RF-CAL-06 | Encadear ciclos: o mês o de um ciclo é o mês i do anterior |
| RF-SER-01 | Buscar séries públicas (IPEADATA, IBGE SIDRA) com cache e data da consulta (V07) |
| RF-SER-02 | Comparar séries pagas com o mesmo índice e mês de outros pleitos (V08) |
| RF-SER-03 | Ler tarifas da ANEEL e aplicar a regra de composição de energia da versão (V11) |
| RF-SER-04 | Marcar a conferência como "a refazer" quando a fonte estiver indisponível |
| RF-PRZ-01 | Registrar os marcos do ciclo e calcular os prazos em dias úteis, com feriados do estado |
| RF-PRZ-02 | Atribuir dono a cada etapa; nenhum ciclo fica sem unidade responsável |
| RF-PRZ-03 | Alertar o dono antes e no vencimento de cada prazo |
| RF-PRZ-04 | Gerar a reiteração da diligência no dia seguinte ao vencimento, pronta para assinatura |
| RF-PRZ-05 | Contar o prazo interno da Procuradoria a partir do parecer técnico |
| RF-PRZ-06 | Incluir o reajuste na pauta no vencimento das razões finais |
| RF-PRZ-07 | Contar o prazo recursal a partir da publicação |
| RF-PRZ-08 | Emitir a certidão de ausência de recurso pela regra e encerrar por lista de verificação |
| RF-PRZ-09 | Mostrar o painel de prazos e da idade de cada ciclo por unidade |
| RF-DOC-01 | Gerar peças de rotina por modelo versionado com os dados do ciclo |
| RF-DOC-02 | Exportar a peça em formato aceito pelo SEI (DOCX e PDF) |
| RF-DOC-03 | Gerar ofício de diligência único por fase, com os quesitos das pendências |
| RF-MIN-01 | Gerar a minuta do parecer técnico a partir da apuração |
| RF-MIN-02 | Gerar a minuta do parecer jurídico com o checklist legal (R-P01) e os precedentes do contrato |
| RF-MIN-03 | Gerar as minutas de relatório, voto e deliberação a partir dos autos |
| RF-MIN-04 | Verificar cada citação da minuta contra o texto da fonte e marcar a inválida |
| RF-MIN-05 | Registrar as edições do revisor para medir a taxa de edição (Q-P01-03) |
| RF-FAT-01 | Receber a remessa periódica de faturamento no layout próprio, sem dados pessoais |
| RF-FAT-02 | Recalcular cada fatura da remessa contra a tabela homologada e listar só as divergências |
| RF-IND-01 | Calcular os indicadores I-P01-01 a 10 a partir dos marcos |
| RF-IND-02 | Rodar os testes dos requisitos R-P01 sobre cada ciclo (auditoria contínua) |
| RF-IND-03 | Medir os controles de qualidade da IA (Q-P01-01 a 04) |
| RF-ADM-01 | Gerir usuários e perfis com autenticação; usuário externo vinculado à concessionária |
| RF-ADM-02 | Registrar trilha de auditoria de toda ação que muda dado ou peça |
| RF-ADM-03 | Gerir modelos de documento, com versão |

## 10. Requisitos não funcionais

| ID | Característica (ISO/IEC 25010) | Requisito |
|---|---|---|
| RNF-01 | Exatidão | Tolerância de 0,01 ponto percentual entre índice refeito e declarado, depois do arredondamento do contrato |
| RNF-02 | Rastreabilidade | Todo número exibido aponta a origem (pleito, série com data da consulta, trecho do contrato) |
| RNF-03 | Reprodutibilidade | Toda apuração guarda as versões do cadastro, do layout, das regras e das séries |
| RNF-04 | Conformidade de licença | Séries pagas não saem do processo nem vão para painel público |
| RNF-05 | Privacidade (LGPD) | Layouts sem dados pessoais; dado pessoal recebido por engano é recusado |
| RNF-06 | Disponibilidade | Fonte externa fora do ar não bloqueia o fluxo: cache e marcação "a refazer" |
| RNF-07 | Decisão humana | O sistema não assina, não protocola e não homologa; minuta sempre revisada |
| RNF-08 | Acessibilidade | WCAG 2.2 AA e eMAG em todas as telas |
| RNF-09 | Usabilidade | Resultado da validação legível numa tela, na linguagem de quem analisa |
| RNF-10 | Segurança | Autenticação, perfis por papel, sessão com expiração, segredos fora do código |
| RNF-11 | Auditabilidade | Trilha de auditoria imutável de quem fez o quê e quando |
| RNF-12 | Manutenibilidade | Domínio sem dependência de framework; cobertura mínima de 90% no domínio |
| RNF-13 | Desempenho | Validação de um pleito em menos de 60 s com as séries em cache |
| RNF-14 | Portabilidade | Sobe com Docker; banco PostgreSQL; nenhuma dependência de serviço pago obrigatória |

## 11. Entidades principais

`Concessionaria`, `Contrato`, `VersaoContratual`, `Formula`, `Componente`, `ParcelaRealinhamento`, `FonteRegra`,
`CicloReajuste`, `Pleito`, `ComponentePleito`, `ValorMensal`, `Evidencia`, `SerieExterna`, `ValorSerieExterna`,
`ResultadoValidacao`, `ItemValidacao`, `Apuracao`, `TermoApuracao`, `Marco`, `Prazo`, `Alerta`, `Peca`,
`ModeloDocumento`, `Minuta`, `Citacao`, `EdicaoMinuta`, `RemessaFaturamento`, `FaturaConferida`,
`DivergenciaFatura`, `Indicador`, `MedicaoIndicador`, `TesteRequisito`, `Usuario`, `Perfil`, `RegistroAuditoria`,
e os incorporados no detalhamento (seção 15): `Unidade`, `RegraPrazo`, `Feriado`, `ExecucaoTesteRequisito`, `Quesito`.
Os atributos ficam em `06_MODELO_DADOS.md` e no `prisma/schema.prisma`.

## 12. Telas

| ID | Tela | Perfis |
|---|---|---|
| TL-01 | Painel do ciclo (fila de ciclos com situação, dono, prazo e idade) | todos os internos |
| TL-02 | Detalhe do ciclo (linha do tempo de marcos, peças, pendências, apuração) | internos |
| TL-03 | Envio do pleito e validação prévia | PER-CON |
| TL-04 | Resultado da validação (V01 a V12) | PER-CON, PER-ANA |
| TL-05 | Memória de cálculo | PER-ANA, PER-PRO, PER-REL |
| TL-06 | Cadastro do contrato: versões e parâmetros com trecho | PER-GCA |
| TL-07 | Histórico do contrato (ciclos encadeados) | PER-ANA, PER-GES |
| TL-08 | Editor de minuta com citações verificadas | PER-ANA, PER-PRO, PER-REL |
| TL-09 | Emissão de documento por modelo | PER-SEC, PER-REL |
| TL-10 | Prazos e alertas (minha fila) | internos |
| TL-11 | Pauta do Conselho-Diretor | PER-SEC |
| TL-12 | Remessa de faturamento e divergências | PER-CON, PER-ANA |
| TL-13 | Indicadores e auditoria contínua | PER-GES |
| TL-14 | Séries externas (situação do cache e consultas) | PER-ANA, PER-ADM |
| TL-15 | Administração: usuários, perfis, modelos, integrações | PER-ADM |
| TL-16 | Entrada (login) e escolha de perfil | todos |

## 13. Integrações

| ID | Sistema | Uso | Forma |
|---|---|---|---|
| INT-01 | SEI | número do processo, juntada de peças, andamentos | fase 1 manual (exporta e importa); depois webservice do SEI, se a TI liberar |
| INT-02 | IPEADATA | INCC, IPC-Brasil, IGP-M | API OData pública |
| INT-03 | IBGE SIDRA | IPCA, IPCA-E (IPCA-15) | API SIDRA pública |
| INT-04 | ANEEL dados abertos | tarifas homologadas e bandeiras | arquivo do portal de dados abertos |
| INT-05 | Base do Especialista AGENERSA | textos de contratos e aditivos, deliberações anteriores | leitura da base (exportação periódica) |
| INT-06 | Modelo de linguagem | extração, minutas, verificação de citação | API por adaptador; provedor configurável |
| INT-07 | FGV Dados | séries pagas | opcional, se houver licença |
| INT-08 | Correio eletrônico institucional | alertas de prazo | SMTP |

## 14. Releases

| Release | Conteúdo | Módulos | Prova de aceite |
|---|---|---|---|
| R1 Núcleo do cálculo | Cadastro, pleito, validação V01 a V12, motor, memória, devolução com pendências | MOD-CAD, MOD-PLE, MOD-CAL, MOD-SER | AT-01 a AT-08 (`12_TESTES.md`) |
| R2 Prazos e documentos | Marcos, prazos, donos, alertas, documentos por modelo, pauta, prazo recursal, encerramento | MOD-PRZ, MOD-DOC | ciclo de Paraty 2026 reproduzido do protocolo ao encerramento |
| R3 Minutas assistidas | Parecer técnico, jurídico, relatório, voto e deliberação com citação verificada | MOD-MIN | Q-P01-01 a 03 medidos em ciclos reais |
| R4 Faturas e indicadores | Remessa de faturamento, conferência, indicadores e auditoria contínua | MOD-FAT, MOD-IND | I-P01 calculados; divergências de fatura listadas |
| Transversal | Usuários, perfis, auditoria, modelos | MOD-ADM | desde R1 |

## 15. Itens incorporados no detalhamento

Os documentos 02 a 14 propuseram itens novos ("(proposto)"). Os abaixo foram incorporados na revisão do pacote e
valem como parte deste documento-base. Os demais "(proposto)" dos documentos (valores padrão de alerta, sessão,
backup, rotas de tela) são padrões de partida, trocáveis sem mudar requisito.

| Item | Onde está definido | Por quê |
|---|---|---|
| Entidades `Unidade`, `RegraPrazo`, `Feriado`, `ExecucaoTesteRequisito` | `06_MODELO_DADOS.md`, `prisma/schema.prisma` | dono por etapa, prazos parametrizados, dias úteis do RJ, histórico da auditoria contínua |
| Entidade `Quesito` | `prisma/schema.prisma`, `contratos/openapi.yaml`, RN-TRA-07 | diligência em rodada única com quesitos da CAPET e da Procuradoria |
| Situação de tarefa em segundo plano (`Tarefa` na API) | `contratos/openapi.yaml`, `05_ARQUITETURA.md` §12 | é o estado do job na fila, sem tabela própria |
| Estados e subestados do ciclo (`SituacaoCiclo`, `SubsituacaoCiclo`) | `04_CASOS_DE_USO.md` §5, iguais no Prisma e na API | máquina de estados única |
| Identificadores CMP-* (componentes), RN-* (regras), DEC-* (decisões de negócio), ADR-*, ARQ-*, DIV-* (divergências com o oráculo), DA-ARQ-* (decisões de TI), JOB-*, AT-* (testes), EP-* e HIS-* (backlog) | documentos 05, 08, 10, 12 e 13 | vocabulário dos documentos de detalhe |
| Requisitos de segurança SEG-* | `15_SEGURANCA.md` | lacuna achada no início da aula 3 |

