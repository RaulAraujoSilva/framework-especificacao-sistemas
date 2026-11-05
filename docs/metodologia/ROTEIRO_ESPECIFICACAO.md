# Roteiro: do processo TO-BE à especificação aprovada

Passo a passo para a IA do aluno (e para o aluno) especificar o sistema do próprio processo. Cada etapa tem ação,
comando, aceite e o artefato que fica na pasta certa do **projeto do aluno**. **PARADA** é ponto em que a IA para e
espera a pessoa indicada. Antes de cada etapa, leia o capítulo citado.

Nos comandos, `<projeto>` é a pasta do projeto do aluno. Os scripts rodam a partir da raiz deste repositório (ou de
`<projeto>/ferramentas/`, se o projeto foi criado com `--copiar-ferramentas`).

Pré-requisito: o processo está mapeado, com TO-BE aprovado e a função a automatizar escolhida (no repositório
[mapeamento-processos-sei](https://github.com/RaulAraujoSilva/mapeamento-processos-sei), até a PARADA 10).

## Etapa E0: preparação

Capítulos: [00](00_VISAO_GERAL.md), [01](01_INSUMOS_DO_PROCESSO.md) e [05](05_USO_DO_EXEMPLO.md).

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E0.1 | Instalar dependências | `pip install -r requirements.txt` e `python -m playwright install chromium` | `python -m pytest tests` passa neste repositório | — |
| E0.2 | Criar o projeto a partir dos modelos | `python scripts/iniciar_projeto.py <projeto> --sistema "..." --orgao SIGLA` | Pasta criada com `insumos/`, `especificacao/`, `saida/levantamento/` | `<projeto>/` |
| E0.3 | Trazer os insumos do processo | copiar para `<projeto>/insumos/` | `insumos/LEIA-ME.md` preenchido; o mínimo do capítulo 01 §2 presente; nenhum nome de pessoa | `insumos/` |
| E0.4 | Conferir o ponto de partida | `python scripts/conferir_especificacao.py --projeto <projeto>` | Só erros C02 (marcadores a preencher); nenhum C03 | — |

## Etapa E1: levantamento de casos e regras

Capítulo: [02](02_LEVANTAMENTO_DE_CASOS_E_REGRAS.md).

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E1.1 | Escolher a função da primeira onda | — | Regra mais fechada, dado mais disponível, maior peso no AS-IS; registrado no 01 | `especificacao/01_VISAO_ESCOPO.md` §ondas |
| E1.2 | Extrair cada caso real, sem calcular | agente, um arquivo por caso | Valores literais com documento de origem; nenhuma conta; nenhum nome | `saida/levantamento/casos/` |
| E1.3 | Registrar regras e parâmetros com trecho literal | agente | Todo parâmetro com dispositivo, trecho literal e vigência | `saida/levantamento/regras/` |
| E1.4 | Refazer os casos por script (oráculo) | script do projeto | Cada divergência com causa classificada (erro no processo, regra diferente) | `saida/levantamento/conferencias/` |
| E1.5 | Formato e validação do dado que vem de fora, se houver | — | Esquema verificável e um caso real validado | `especificacao/contratos/` |

**PARADA E1 (área de negócio):** conferir os casos, as regras e as divergências antes de especificar.

## Etapa E2: planejamento e pacote de especificação

Capítulo: [03](03_PLANEJAMENTO_DA_ESPECIFICACAO.md). Escreva na ordem da cadeia de derivação (§1). Depois de cada
documento, rode a conferência e trate o que ela aponta.

| # | Ação | Seção do 03 | Aceite | Artefato |
|---|---|---|---|---|
| E2.1 | Escopo, metas, módulos, ondas e listas de identificadores | §3.1 | Toda atividade do TO-BE com tratamento; metas com linha de base | `01_VISAO_ESCOPO.md` |
| E2.2 | Perfis e jornadas | §3.2 | Cada raia com perfil; jornada ponta a ponta com caso real | `02_PERFIS_E_JORNADAS.md` |
| E2.3 | Casos de uso, sequências e correspondência com o BPMN | §3.3 | C07 e C10 sem erro; toda atividade em escopo correspondida | `04_CASOS_DE_USO.md` |
| E2.4 | Requisitos funcionais e não funcionais | §3.4 | C06 e C09 sem erro; toda melhoria com requisito | `03_REQUISITOS.md` |
| E2.5 | Regras de negócio e decisões pendentes | §3.5 | Toda regra com fonte e exemplo; toda lacuna com DEC | `08_REGRAS_NEGOCIO.md`, README §Decisões pendentes |
| E2.6 | Modelo de domínio e máquina de estados | §3.6 | Diagrama de classes; estados com transições rotuladas (C16); casos reais percorrem a máquina | `06_MODELO_DADOS.md`, `04_CASOS_DE_USO.md` §estados |
| E2.7 | Componentes, arquitetura e ADRs | §3.7 | Contexto e componentes desenhados; todo módulo com componente; toda escolha com ADR | `05_ARQUITETURA.md`, `adr/` |
| E2.8 | Contratos, API e integrações | §3.8, §3.9 | Toda operação com caso de uso e perfil; toda integração com tratamento de falha | `07_CONTRATOS_API.md`, `09_INTEGRACOES.md`, `contratos/` |
| E2.9 | Interface, telas e protótipo | §3.10 | C08 sem erro; telas com os cinco estados; protótipo com uma seção por tela | `10_UX_UI.md`, `11_TELAS.md`, `prototipos/` |
| E2.10 | Testes de aceitação a partir dos casos | §3.11 | Todo caso do levantamento com teste; C11 tratado | `12_TESTES.md`, `fixtures/` |
| E2.11 | Backlog e releases | §3.12 | C15 tratado; R1 como esqueleto que anda | `13_BACKLOG.md` |
| E2.12 | Operação e segurança | §3.13 | Matriz de permissões; inventário de dado pessoal; requisitos SEG | `14_OPERACAO.md`, `15_SEGURANCA.md` |
| E2.13 | Regras para a IA de desenvolvimento | §3.14 | Camadas, proibições, portões e definição de pronto escritos | `AGENTS_DESENVOLVIMENTO.md` |
| E2.14 | Conferência e revisão cruzada | §4 e §5 | `conferir_especificacao.py` sem erro; cada aviso tratado ou justificado; lista do §5 respondida | — |

## Etapa E3: documentos para avaliação

Capítulo: [04](04_DOCUMENTOS_E_PASTA_DE_SAIDA.md).

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E3.1 | Configurar cadernos, públicos, itens avaliáveis e versão | editar `especificacao/documentos.json` | Todo capítulo em pelo menos um caderno; todo prefixo com capítulo dono; versão 1.0, "Minuta para avaliação" | `documentos.json` |
| E3.2 | Gerar | `python scripts/gerar_documentos.py --projeto <projeto>` | Conferência e portões sem erro; avisos lidos | `saida/documentos_para_avaliacao/`, `saida/LEIA-ME.md` |
| E3.3 | Conferir a atualização | `python scripts/conferir_especificacao.py --projeto <projeto> --documentos` | Sem C17 | — |
| E3.4 | Revisão humana das páginas | abrir os arquivos do capítulo 04 §6 | Aluno revisou guia, uma página de cada caderno, protótipo e planilha | — |
| E3.5 | Registrar a versão | `git commit` | Commit com a versão gerada | — |

## PARADA 11: avaliação pelas áreas

Dono: gestão do processo, área de negócio, jurídico e TI. A IA prepara e para.

| # | Ação | Quem | Aceite |
|---|---|---|---|
| P11.1 | Enviar a cada área o guia, o caderno dela e a planilha, com prazo | aluno | Envio registrado (e-mail ou processo administrativo) |
| P11.2 | Avaliar e devolver a planilha | cada área | Planilha devolvida em `saida/pareceres/recebidos/` |
| P11.3 | Decidir as decisões pendentes | quem a tabela de decisões indica | Decisão tomada, com responsável e data, na aba "Decisões pendentes" |

## Etapa E4: consolidar, corrigir e aprovar

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E4.1 | Consolidar os pareceres | `python scripts/consolidar_pareceres.py --projeto <projeto>` | Toda planilha recebida lida | `saida/pareceres/00_Consolidado_dos_pareceres.xlsx` |
| E4.2 | Cobrar os itens sem parecer | aba "Sem parecer" | Zero item sem parecer, ou dispensa registrada pelo dono do processo | — |
| E4.3 | Corrigir a fonte para cada "Não aprovado" e "Aprovado com ajustes" | editar `especificacao/` | Coluna "Tratamento" preenchida em cada item | `especificacao/`, consolidado |
| E4.4 | Nova versão | subir `versao`; gerar; conferir | Reenvio só do que mudou, com a lista de mudanças | `saida/documentos_para_avaliacao/` |
| E4.5 | Aprovar | `situacao` = "Versão aprovada em DD/MM/AAAA"; gerar | Nenhum "Não aprovado" aberto; decisões tomadas | versão aprovada |

Depois da E4.5, o pacote vai para o desenvolvimento. Copie `especificacao/AGENTS_DESENVOLVIMENTO.md` como `AGENTS.md`
na raiz do repositório do sistema, e o pacote para `docs/especificacao/`.
