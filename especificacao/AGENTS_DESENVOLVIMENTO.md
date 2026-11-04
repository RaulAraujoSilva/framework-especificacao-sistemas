# Instruções para a IA de desenvolvimento do Reajusta

Copie este arquivo para a raiz do repositório do sistema como `AGENTS.md` e como `CLAUDE.md`. Leia-o inteiro antes de
cada tarefa. O pacote de especificação fica em `docs/especificacao/`; os caminhos abaixo são relativos a ele.

O Reajusta automatiza o reajuste tarifário anual (processo P01) da AGENERSA: recebe o pleito da concessionária no
layout, valida (V01 a V12), recalcula, controla prazos, gera documentos e minutas para revisão humana, confere faturas
e mede indicadores. **Ele não assina, não protocola e não homologa** (RNF-07).

## 1. Antes de cada tarefa

1. Leia a história no [`13_BACKLOG.md`](13_BACKLOG.md) e cada identificador que ela cita (RF, RNF, UC, TL, regra V,
   AT) em [`01_VISAO_ESCOPO.md`](01_VISAO_ESCOPO.md), [`03_REQUISITOS.md`](03_REQUISITOS.md),
   [`04_CASOS_DE_USO.md`](04_CASOS_DE_USO.md), [`08_REGRAS_NEGOCIO.md`](08_REGRAS_NEGOCIO.md) e
   [`11_TELAS.md`](11_TELAS.md).
2. Confira em [`05_ARQUITETURA.md`](05_ARQUITETURA.md) a pasta, a camada e a porta de cada parte da tarefa, e em
   [`06_MODELO_DADOS.md`](06_MODELO_DADOS.md) as entidades e as regras de integridade.
3. Procure no código o que já existe (§4). Só escreva o que falta.
4. Se algo da tarefa não está escrito na especificação, pare e pergunte (§10). Não adivinhe.

## 2. Linguagem do domínio

Use os termos do glossário (`01_VISAO_ESCOPO.md` §7) em nomes de entidade, função, variável, arquivo, rota e texto de
tela. Em português, sem acento no código, sem tradução para o inglês.

| Termo | No código | Não use |
|---|---|---|
| Ciclo de reajuste | `CicloReajuste`, `cicloReajuste`, `ciclo` | `cycle`, `process` |
| Pleito | `Pleito`, `pleito` | `request`, `claim` |
| Contrato | `Contrato` | `contract` |
| Versão contratual | `VersaoContratual`, `versaoContratual` | `contractVersion`, `revision` |
| Fórmula | `Formula` | |
| Componente | `Componente` (do cadastro), `ComponentePleito` (do pleito) | `index`, `item` |
| Fonte da regra | `FonteRegra` | `source` |
| Série | `SerieExterna`, `ValorSerieExterna`, `ValorMensal` | `timeseries` |
| Mês o, mês i | `mesO`, `mesI` | `baseMonth`, `currentMonth` |
| Interstício | `intersticio` | `interval` |
| IR | `ir`, `irDeclaradoPct`, `irCalculadoPct` | `rate` |
| Realinhamento | `realinhamento`, `ParcelaRealinhamento` | `adjustment` |
| Total | `total`, `totalCalculadoPct` | |
| Apuração | `Apuracao`, `TermoApuracao` | `calculation`, `result` |
| Regra de validação | `RegraValidacao` (`V01` a `V12`), `ItemValidacao`, `ResultadoValidacao` | `check`, `rule` |
| Pendência | `pendencia` (item de validação com `ERRO`) | `issue` |
| Marco | `Marco`, `TipoMarco` | `event`, `milestone` |
| Prazo | `Prazo`, `RegraPrazo`, `vencimento` | `deadline` |
| Peça | `Peca`, `TipoPeca` | `document` |
| Minuta | `Minuta` | `draft` |
| Citação | `Citacao` | `reference`, `quote` |
| Remessa de faturamento | `RemessaFaturamento`, `FaturaConferida`, `DivergenciaFatura` | `batch` |

Convenções:

| Item | Convenção | Exemplo |
|---|---|---|
| Tipos, entidades, componentes React | `PascalCase` | `VersaoContratual`, `TabelaResultadoValidacao` |
| Funções e variáveis | `camelCase`, função começa por verbo | `recalcularIr`, `resolverVersao` |
| Constantes de parâmetro | `MAIUSCULAS_COM_SUBLINHADO`, com a origem em comentário | `TOLERANCIA_RECALCULO_PP // RNF-01` |
| Arquivos e pastas | `kebab-case` | `recalcular-ir.ts`, `uc02-validar-pleito.ts` |
| Enums do Prisma | `MAIUSCULAS_COM_SUBLINHADO` | `A_RECONFERIR` |
| Nomes que o framework exige | como o framework exige | `page.tsx`, `route.ts`, `GET`, `POST` |
| Identificadores da especificação | iguais aos do pacote, nos testes e comentários | `// RF-CAL-01, V09` |

## 3. Camadas e dependências permitidas

Detalhe e configuração dos portões em `05_ARQUITETURA.md` §5 e §6. A dependência só aponta para dentro.

| Camada | Pasta | Pode importar | Nunca importa |
|---|---|---|---|
| contratos | `src/contratos` | `zod` | nada de `src` |
| dominio | `src/dominio/<mod>` | `contratos`, `dominio`, `decimal.js`, `ajv`, `ajv-formats` | `next`, `react`, `@prisma/client`, `node:*`, `fetch`, `process.env`, relógio do sistema |
| portas | `src/portas` | tipos de `dominio`, `contratos` | implementação |
| aplicacao | `src/aplicacao/<mod>` | `dominio`, `portas`, `contratos` | adaptadores, interface, bibliotecas de infraestrutura |
| adaptadores | `src/adaptadores/<sistema>` | `portas`, tipos de `dominio`, `contratos`, `adaptadores/comum` | `aplicacao`, `interface`, outro adaptador |
| composicao | `src/composicao` | todas, menos interface | — |
| interface | `src/app`, `src/components`, `src/interface`, `src/jobs` | casos de uso pelo contêiner, `contratos`, `import type` do `dominio` | `@prisma/client`, adaptadores, função do `dominio` |

Entre módulos do domínio vale a matriz de `05_ARQUITETURA.md` §4 (ARQ-11), sempre pelo `index.ts` do módulo
(ARQ-19). Um import proibido derruba o portão G-03: mova o código para a camada certa; nunca relaxe a regra.

## 4. Reuso: o que já existe e onde procurar

Antes de escrever código, procure. Duplicar componente ou regra é defeito.

**Interface.** Telas usam só os componentes do inventário de [`10_UX_UI.md`](10_UX_UI.md) §5, em
`src/components/reajusta/`, e só os tokens do bloco `@theme` de `src/app/globals.css` (`10_UX_UI.md` §3.3). Não escreva
cor, espaço, fonte ou sombra solta. Não instale biblioteca de componentes. Se a tela precisa de um componente que não está no
inventário, pare e peça a inclusão (§10). Textos de mensagem vêm de `src/interface/mensagens/`, conforme o guia de
`10_UX_UI.md`.

**Domínio.** As funções abaixo são a fonte única da regra. Chame-as; nunca reescreva a conta em outro lugar (nem no
componente, nem no adaptador, nem no teste de outra camada).

| Precisa de | Use | Onde |
|---|---|---|
| Arredondar, comparar percentuais, converter número recebido | `decimal`, `arredondar(valor, casas, modo)`, `diferencaPp(a, b)`, `casasDoNumero(texto)` | `dominio/comum/decimal.ts` |
| Mês `AAAA-MM`: somar, diferença, intervalo | `Mes`, `somarMeses`, `mesesEntre` | `dominio/comum/mes.ts` |
| Data civil, dias úteis, vencimento de prazo | `DataCivil`, `contarDiasUteis`, `somarDiasUteis`, `vencimentoPrazo` | `dominio/comum/calendario.ts` |
| Falha esperada | `Resultado`, `ok`, `falha` | `dominio/comum/resultado.ts` |
| Parâmetro com origem (tolerância etc.) | constantes de `parametros.ts` | `dominio/comum/parametros.ts` |
| Versão contratual com herança | `resolverVersao`, `versaoVigenteEm` | `dominio/cad` |
| Conferir trecho literal | `conferirTrechos` (espaços normalizados como o `norm()` do oráculo) | `dominio/cad` |
| Validar pleito | `validarPleito`, `concluirValidacao` | `dominio/ple` |
| IR, total, parcela, tabela, memória, encadeamento | `recalcularIr`, `comporTotal`, `parcelaDoCronograma`, `conferirTabela`, `montarMemoria`, `encadearCiclo` | `dominio/cal` |
| Conferir série pública, cruzada, energia | `conferirSeriePublica`, `conferenciaCruzada`, `conferirEnergia` | `dominio/ser` |
| Situação do ciclo, dono, prazos, encerramento | `transicaoCiclo`, `donoDaEtapa`, `abrirPrazos`, `alertasDevidos`, `podeEncerrar` | `dominio/prz` |
| Preencher modelo de documento | `preencherModelo`, `camposFaltantes`, `quesitosDasPendencias` | `dominio/doc` |
| Citação e taxa de edição | `verificarCitacao`, `podeAprovarMinuta`, `taxaEdicao` | `dominio/min` |
| Fatura | `conferirRemessa`, `recalcularFatura`, `contemDadoPessoal` | `dominio/fat` |
| Indicadores e testes R-P01 | `medirIndicador`, `executarTeste` | `dominio/ind` |
| Permissão | `permite(perfis, acao, recurso)` | `dominio/adm` |

Se a função que você precisa não está aqui nem no `index.ts` do módulo, crie-a no módulo certo, com teste, e exporte-a
pelo `index.ts`. Não crie `utils/`, `helpers/` ou `lib/` genéricos.

## 5. Proibições

| ID | Proibido | Faça assim |
|---|---|---|
| P-01 | Regra de negócio em componente React, página, route handler, job ou adaptador | regra no `dominio`; orquestração na `aplicacao`; a tela só exibe |
| P-02 | Número mágico: prazo, tolerância, percentual, peso, casas decimais, antecedência de alerta escritos no código | cadastro (`VersaoContratual`, `RegraPrazo`), ou `dominio/comum/parametros.ts` com a origem ao lado. Número sem fonte nas fontes do pacote: pergunte (§10) |
| P-03 | Chamada externa fora de adaptador: `fetch`, Prisma, SMTP, sistema de arquivos, SDK de modelo de linguagem | porta em `src/portas`, adaptador em `src/adaptadores`, ligação em `composicao/container.ts` |
| P-04 | `any`, `as any`, `// @ts-ignore`, `// @ts-expect-error` sem justificativa, `!` de não nulo | tipos explícitos, `unknown` com validação Zod na borda |
| P-05 | Dado pessoal em log, em mensagem de erro, em URL ou no token de sessão (nome, e-mail, CPF, telefone) | só `usuarioId`; redação do pino (`05_ARQUITETURA.md` §14) |
| P-06 | `number` para percentual, índice, peso ou tarifa | `Decimal` (ADR-0003) |
| P-07 | `Date` do JavaScript ou fuso no domínio; `Date.now()`, `new Date()` sem argumento, `Math.random()` no domínio e na aplicação | `DataCivil`, `Mes`, porta `Relogio` |
| P-08 | Alterar ou apagar versão contratual já usada, dado recebido do pleito, resultado de validação, apuração ou trilha de auditoria | versão nova, registro novo (`06_MODELO_DADOS.md` §5) |
| P-09 | Aprovar peça ou minuta sem ação humana; assinar, protocolar, homologar ou tramitar no SEI | o sistema gera minuta e proposta; a pessoa aprova (RNF-07) |
| P-10 | Número de minuta vindo do modelo de linguagem | números da apuração e dos marcos, inseridos pelo `preencherModelo` (ADR-0006) |
| P-11 | Série paga (licença `RESTRITA`) em painel, exportação, API pública ou envio ao modelo de linguagem | filtro por licença na aplicação (ADR-0008) |
| P-12 | Segredo no código, no repositório ou em log; `process.env` fora de `composicao/config.ts` | variável de ambiente validada (`05_ARQUITETURA.md` §15) |
| P-13 | Dependência nova (nome novo no `package.json`), troca de biblioteca, nova biblioteca de UI, imagem nova (nome de imagem novo no Dockerfile ou no `docker-compose.yml`), serviço novo no `docker-compose.yml` | pedir (§10); se aprovado, novo ADR. Atualização de versão de componente existente, inclusive major, não é P-13: chega pelo PR do Renovate, e o PR de major atualiza o registro de versões (SEG-SUP-03, SEG-SUP-09; ADR-0012, revisão de 01/11/2026) |
| P-14 | Desligar, pular (`.skip`, `.only`) ou afrouxar teste, regra de lint, limite de cobertura ou regra do dependency-cruiser para passar o portão | corrigir a causa |
| P-15 | Editar o esperado do oráculo ou o fixture para o teste passar | corrigir o sistema; se o oráculo estiver errado, registrar e pedir decisão (§10) |
| P-16 | Funcionalidade fora do escopo de `01_VISAO_ESCOPO.md` §3 (P02, custo do gás, conta gráfica, cálculo de ITS e IDG) | não fazer; perguntar |
| P-17 | Nome de pessoa ou caminho local de máquina em código, fixture, seed, mensagem ou documento | identificadores e caminhos relativos ao repositório |

## 6. Testes antes do código, com os fixtures de aceite

Para cada regra, caso de uso ou tela:

1. **Ache o caso de aceite.** Os testes AT-01 a AT-08 e os demais de [`12_TESTES.md`](12_TESTES.md) têm resultado
   esperado tirado dos autos. Os fixtures ficam em `docs/especificacao/fixtures/`; leia de lá, não copie.
2. **Escreva o teste primeiro e veja falhar.** No domínio: Vitest ao lado do arquivo. Para regras V01 a V12, compare
   também com o esperado do oráculo (`05_ARQUITETURA.md` §16.1): a sequência de `(regra, situacao)` tem de ser igual e os
   números de V09 e V10 dentro de 0,01 ponto percentual (RNF-01).
3. **Implemente o mínimo no domínio** até passar. Depois a porta e o adaptador (com MSW ou PostgreSQL de teste), o caso
   de uso (com `tests/fakes`) e, por último, a tela com os componentes do inventário.
4. **Cubra os casos negativos** que a especificação cita: IR declarado errado, mês de referência errado, parcela errada,
   componente sem evidência (AT-05); fonte indisponível (`A_REFAZER`); usuário de outra concessionária (sem
   permissão); versão contratual em uso (conflito).
5. **Rode o diferencial** (`npm run paridade`) quando mexer em V01 a V12, no recálculo ou no calendário.
6. Divergência com o oráculo fora de DIV-01 a DIV-07 é defeito do sistema até prova em contrário. Se você acha que o
   oráculo está errado, pare e peça decisão (§10). Não crie divergência por conta própria.

Testes de fluxo de tela (Playwright) usam só dados de fixture e usuários de teste do seed. Nunca dados reais de pessoas.

## 7. Portões

Uma tarefa só termina com todos verdes. Rode `npm run verificar` antes de cada commit.

| ID | Portão | Comando | Critério |
|---|---|---|---|
| G-01 | Tipos | `npm run typecheck` (`tsc --noEmit`, modo estrito) | zero erro |
| G-02 | Lint | `npm run lint` | zero erro e zero aviso |
| G-03 | Regra de dependência | `npm run depcruise` | zero violação |
| G-04 | Testes unitários e de aplicação | `npm run test` | todos passam |
| G-05 | Cobertura do domínio | `npm run test -- --coverage` | ≥ 90% de linhas e de ramos em `src/dominio` (RNF-12) |
| G-06 | Esquema do banco | `npx prisma validate` e `npx prisma migrate diff` sem diferença pendente | válido; migração gerada e versionada |
| G-07 | Integração | `npm run test:integracao` | adaptadores e gatilhos de integridade verdes |
| G-08 | Paridade com o oráculo | `npm run paridade` | nenhuma diferença fora de DIV-01 a DIV-07 |
| G-09 | Ponta a ponta | `npm run e2e` | fluxos de R1 verdes (cadastro, envio do pleito, validação, devolução com pendências, memória de cálculo) e, a cada release, os fluxos dela |
| G-10 | Acessibilidade | axe nos testes de componente e, dentro de G-09, @axe-core/playwright | nenhuma violação WCAG 2.2 AA de impacto sério ou crítico (RNF-08; `12_TESTES.md` §1.1) |
| G-11 | Build | `npm run build` | sem erro |

G-01 a G-06 rodam em todo commit. G-07 a G-11 rodam no CI em todo pull request.

## 8. Commits

- Em português, com prefixo convencional: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `build`, `ci`.
- Escopo é o módulo, em minúsculas: `feat(ple): …`, `fix(cal): …`, `test(prz): …`. Mudança transversal usa `arq`,
  `db` ou `ui`.
- Título no imperativo, até 72 caracteres, dizendo o efeito: `feat(cal): recalcular IR com os pesos da versão (V09)`.
- Corpo: o que mudou e por quê, com os identificadores atendidos (RF, UC, V, AT). Rodapé: `História: HIS-<MOD>-<nn>`,
  o ID da história no `13_BACKLOG.md`. O pedido de integração cita a mesma HIS-* e os RF-*.
- Um commit por passo verde (teste e código juntos). Nada de commit com portão vermelho.
- Migração do banco em commit próprio (`feat(db): …`), com o SQL complementar quando houver gatilho.
- Nunca commitar `.env`, segredo, `node_modules/`, build, arquivo de dados com nome ou e-mail de terceiros.

## 9. Como pegar uma história e quando ela está pronta

1. Pegue a próxima história (HIS-*) do [`13_BACKLOG.md`](13_BACKLOG.md) na ordem das releases (R1, R2, R3, R4), que
   cumpra a Definition of Ready (`13_BACKLOG.md` §4) e não tenha dependência aberta.
2. Leia os identificadores que ela cita (§1). Escreva, em poucas linhas, o plano: arquivos por camada, testes, portas.
3. Se a história depende de uma decisão aberta (§10), pare antes de codar a parte que depende dela e avise.
4. Faça em passos pequenos: teste, código, `npm run verificar`, commit.
5. Ao terminar, confira a Definition of Done (`13_BACKLOG.md` §5). Ela é a referência, inclusive a revisão por outra
   pessoa ou por outro agente às cegas. O mínimo verificável por máquina é:
   - [ ] critérios Dado/Quando/Então da história cobertos por teste automatizado;
   - [ ] portões G-01 a G-06 verdes no commit e G-07 a G-11 verdes no CI;
   - [ ] nenhuma proibição da §5 (revise a diferença inteira);
   - [ ] toda ação que muda dado grava `RegistroAuditoria` (RF-ADM-02) e tem teste disso;
   - [ ] telas novas com os estados vazio, carregando, erro e sem permissão (`11_TELAS.md`), só com componentes do
     inventário, e textos do guia de mensagens;
   - [ ] números exibidos com origem (RNF-02);
   - [ ] documentação atualizada quando a história muda contrato de API, modelo de dados ou regra (07, 06, 08).
6. Relate: o que foi feito, os identificadores atendidos, os testes novos e o que ficou em aberto.

## 10. O que pedir a um humano antes de decidir

Pare e pergunte, com as opções e a recomendação, quando a tarefa toca qualquer item abaixo. Não escolha sozinho.

**Decisões abertas da especificação** (PARADA 11 do `README.md`; DEC-01 a DEC-08 de `08_REGRAS_NEGOCIO.md`;
DA-ARQ-01 a DA-ARQ-03 de `05_ARQUITETURA.md` §18). Implemente o comportamento "até lá" e deixe a decisão no cadastro ou
na configuração, nunca no código:

| ID | Decisão | Quem decide | Comportamento até lá |
|---|---|---|---|
| DEC-01 | Regra de composição da energia (distribuidora, TUSD + TE, tributos, bandeira, desconto, mês da resolução) | CAPET | V11 exige a composição declarada e dá erro sem ela |
| DEC-02 | Interstício por mês de referência ou por dia | CAPET e Procuradoria | erro por mês; aviso por dia (V03) |
| DEC-03 | Instrumento que torna o layout obrigatório; canal de envio | Procuradoria, Conselho-Diretor, TI | layout 0.1 aceito pelos dois canais; nenhum texto de tela diz que é obrigatório |
| DEC-04 | Aplicação da tabela nas faturas (faixas, consumo mínimo) | CAPET | sem regra cadastrada, a conferência não roda |
| DEC-05 | Marcos iniciais dos prazos de 30 dias e recursal, redução de 1/3, contagem dos prazos internos e prorrogação | Procuradoria | as duas contagens na tela; vencimento nominal sem prorrogação |
| DEC-06 | Modo de arredondamento | CAPET | meio para o par |
| DEC-07 | Parcela de realinhamento com vigência fora do mês de referência | CAPET e Procuradoria | aviso |
| DEC-08 | Divergência do parecer de Paraty 2022 | CAPET | AT-02 espera erro em V09 |
| PARADA 11 | Integração com o SEI por webservice | TI | `SEI_MODO=manual` |
| PARADA 11 | Onde o sistema roda | TI | Docker e PostgreSQL |
| PARADA 11 | Provedor do modelo de linguagem e política de dados | TI e Procuradoria | `LLM_PROVEDOR=desligado` |
| DA-ARQ-01 a 03 | Armazenamento de arquivos, exportação do SEI, exportação da base do Especialista | TI | ver `05_ARQUITETURA.md` §18 |

**Sempre pergunte antes de:**

- usar um número que não está nas fontes do pacote (prazo, percentual, limite, antecedência);
- acrescentar entidade, campo, enum, perfil, permissão, tela, rota ou regra que não está na especificação;
- mudar o layout do pleito ou da remessa (são contrato com as concessionárias);
- aceitar divergência nova com o oráculo, ou concluir que o oráculo está errado;
- instalar dependência, trocar biblioteca, criar serviço novo ou mudar a stack (atualizar a versão de um componente
  existente, inclusive major, não é mudar a stack: segue SEG-SUP-03);
- criar componente fora do inventário de `10_UX_UI.md`;
- mudar texto que a concessionária lê (pendência, ofício, mensagem de validação) de forma que altere o sentido;
- tocar em dado de produção, migração destrutiva ou permissão do banco.

## 11. Segurança e privacidade

- Toda rota exige sessão, exceto a de entrada (TL-16). Toda ação passa por `permite` no caso de uso; a tela não é a
  barreira (ADR-0009).
- Usuário externo só vê o que é da sua concessionária. Todo caso de uso que lê ciclo, pleito, peça ou remessa filtra pela
  concessionária da sessão, e há teste de acesso cruzado.
- Layouts não têm dado pessoal. Remessa ou pleito com dado pessoal é recusado sem repetir o dado na mensagem (RNF-05).
- Entrada de arquivo: tipo e tamanho conferidos, SHA-256 recalculado e comparado ao declarado, nome do arquivo nunca
  usado como caminho.
- Nada de dado real de pessoas em teste, fixture, seed ou exemplo.
