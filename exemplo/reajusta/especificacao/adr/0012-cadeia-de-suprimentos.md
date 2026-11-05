# ADR-0012: Cadeia de suprimentos — lockfile, Renovate com idade mínima, SBOM e nenhum merge automático

- **Situação:** aceita (provisório de aula até a PARADA 14); a escolha entre o aplicativo do Renovate e a action oficial
  fica para o D11. **Revisada em 01/11/2026** (seção "Revisão de 01/11/2026"): todo componente fica na última versão
  estável; os trechos marcados "Substituído em 01/11/2026" deixaram de valer e ficam só como histórico.
- **Data:** 2026-10-31; revisão em 2026-11-01
- **Origem:** P-13 (`../AGENTS_DESENVOLVIMENTO.md` §5); RNF-10, RNF-14; ADR-0001 (stack fixa, npm com
  `package-lock.json`); SEG-SUP-01 a 08 e SEG-VUL-01 a 08 (`../15_SEGURANCA.md` §12 e §13); lacuna achada no início da
  aula 3.

## Contexto

O sistema depende de algumas centenas de pacotes npm, quase todos transitivos, e de três imagens base (`node`,
`postgres`, `gotenberg`). Cada um pode trazer uma vulnerabilidade ou, pior, uma versão maliciosa publicada no registro.
O caso que a aula usa é o CVE-2025-29927, desvio de autorização no middleware do Next.js, corrigido nas versões
12.3.5, 13.5.9, 14.2.25 e 15.2.3: quem fica parado numa versão antiga continua exposto.

Duas forças puxam em sentidos opostos. Atualizar rápido fecha vulnerabilidade conhecida. Atualizar no dia da publicação
expõe à versão maliciosa que ainda não foi retirada do registro. A P-13 já proíbe dependência nova sem ADR e sem
perguntar, e o agente de segurança da aula tem de obedecer a essa regra.

## Decisão

1. **Lockfile e instalação reprodutível.**
   - `package-lock.json` versionado; `npm ci` na CI e no Dockerfile, nunca `npm install`.
   - Versões exatas no `package.json` (`save-exact=true` no `.npmrc`).
   - Um só registro, `registry.npmjs.org`; a CI falha se um `resolved` do lockfile apontar outro host.
2. **Renovate para as atualizações**, com o `renovate.json` versionado:
   - idade mínima de versão de 3 dias (`minimumReleaseAge`), com o PR só aberto depois dela (`internalChecksFilter`
     estrito);
   - gerenciadores de npm, Dockerfile, `docker-compose.yml` e GitHub Actions; imagens e actions fixadas por digest ou
     SHA de commit (`pinDigests`);
   - patch e minor de dependência existente: um PR por atualização, com a CI completa (G-01 a G-11 e `seguranca-ci.yml`);
     *(Substituído em 01/11/2026 pelo item R3 da revisão: patch, minor e major têm PR automático.)*
   - ~~major: só pelo painel de dependências com aprovação (`dependencyDashboardApproval`), rótulo `requer-adr`, e só
     segue com ADR novo e decisão humana (P-13);~~ *(Substituído em 01/11/2026 pelos itens R3 e R5 da revisão: major tem
     PR automático com o rótulo `major`, sem aprovação no painel e sem ADR novo.)*
   - manutenção semanal do lockfile, também por PR;
   - `automerge` desligado em toda regra.
3. **Correção de vulnerabilidade sem idade mínima.** O PR que corrige vulnerabilidade (alertas de vulnerabilidade do
   Renovate, rótulo `seguranca`) não espera os 3 dias, porque o prazo de uma crítica é 72 h (`../15_SEGURANCA.md`
   SEG-VUL-03). Em troca, passa pela revisão humana com a conferência das assinaturas (item 6) e da diferença do SBOM.
   *(Ampliado em 01/11/2026 pelo item R4 da revisão: toda atualização que corrige vulnerabilidade conhecida, de
   qualquer severidade, entra sem quarentena.)*
4. **Dependência nova, imagem nova ou serviço novo exige ADR.** O job `dependencias-novas` do `seguranca-ci.yml`
   compara o PR com o ramo de destino e falha se aparecer nome novo no `package.json`, imagem nova no Dockerfile ou
   serviço novo no `docker-compose.yml` sem arquivo novo em `docs/especificacao/adr/` no mesmo PR. *(Esclarecido em
   01/11/2026 pelo item R6 da revisão: imagem nova é nome de imagem novo; etiqueta nova da mesma imagem é atualização.)*
5. **Nenhum merge automático.**
   - O Renovate abre PR e não faz merge.
   - O token do GitHub Actions não aprova PR (configuração do repositório).
   - O agente de segurança abre issue e PR, nunca faz merge.
   - Um humano aprova cada PR.
6. **Proveniência.**
   - `npm audit signatures` na CI: falha com assinatura inválida e relata os pacotes sem atestado.
   - Actions referidas por SHA de commit, nunca por etiqueta móvel; `permissions` mínimos em cada workflow.
   - Imagens base por digest. A imagem do Postgres do Railway é a exceção: a recuperação a ponto no tempo exige a
     etiqueta da versão maior (ADR-0013), e a atualização dela passa pela mesma revisão.
   - A imagem do sistema é implantada por digest. Se o plano do GitHub permitir em repositório privado, recebe atestado
     de proveniência no build, conferido no deploy (`../15_SEGURANCA.md` EXC-SEG-04).
7. **SBOM CycloneDX a cada build.**
   - Um do lockfile (`npm sbom --sbom-format cyclonedx`) e um da imagem (Syft).
   - Guardados como artefato da execução, com a versão.
   - Comparados com o anterior: a diferença entra no relatório semanal.
8. **Alertas de cadeia** (sem bloqueio, viram issue para triagem): pacote novo na árvore, inclusive transitivo;
   mantenedor trocado em dependência direta (`npm view <pacote> maintainers` comparado com a véspera); pacote novo com
   script de instalação (`npm query ":attr(scripts, [postinstall])"` e equivalentes).
9. **Python do oráculo** no job de paridade com versões fixas e hashes (`pip install --require-hashes`).
10. **Fontes de vulnerabilidade e prazos** como em `../15_SEGURANCA.md` §13. Os alertas do Dependabot ficam ligados,
    como mais uma fonte. As atualizações de versão do Dependabot ficam desligadas, para não duplicar os PRs do Renovate.

## Alternativas consideradas

- **Dependabot para as atualizações.** Nativo do GitHub e sem instalação. Rejeitado como ferramenta de atualização: a
  aula fixa o Renovate, e o painel com aprovação de major e as regras por pacote do Renovate casam melhor com a P-13.
  Fica como fonte de alertas. *(Motivo do painel com aprovação de major substituído em 01/11/2026; a escolha do
  Renovate continua, pelas regras por pacote, pela quarentena e pelos alertas de vulnerabilidade sem quarentena.)*
- **Merge automático de patch com CI verde.** Fecha vulnerabilidade mais rápido, mas tira o humano da decisão e deixa
  passar a versão maliciosa que a CI não detecta. Rejeitado.
- **Atualizar sem idade mínima.** Expõe à versão maliciosa ainda não retirada do registro. Rejeitado, salvo a correção
  de vulnerabilidade com revisão humana (item 3).
- **Copiar `node_modules` para o repositório.** Congela as versões, mas esconde a árvore da varredura e da revisão.
  Rejeitado.
- **Desligar todo script de instalação (`ignore-scripts`).** Mais seguro, mas quebra o Prisma e o argon2 da stack
  (ADR-0001). Rejeitado; o alerta de script novo (item 8) cobre o risco.

## Consequências

- Positivas: toda mudança de dependência passa por um humano com a CI completa; versão nova espera 3 dias; o SBOM mostra
  o que mudou; o exercício do D11 (Next.js anterior a 15.2.3) tem caminho definido: registro, issue, PR do Renovate.
- Negativas: mais PRs para revisar. A idade mínima atrasa correção que não está marcada como vulnerabilidade. Parte da
  proveniência depende do plano do GitHub em repositório privado.
- O agente de segurança tem limites escritos: propõe e abre, não aprova nem faz merge.

## Revisão de 01/11/2026: sempre na última versão estável

- **Situação:** aceita em 2026-11-01.
- **Quem decide:** dono do projeto.
- **Origem:** decisão do dono do projeto em 01/11/2026: "usar sempre a versão mais atualizada dos componentes; estamos
  tendo vários problemas de segurança e precisamos estar no pacote mais atual". Requisitos: SEG-SUP-02, SEG-SUP-03,
  SEG-SUP-09, SEG-VUL-05 e SEG-VUL-07 (`../15_SEGURANCA.md`); P-13 (`../AGENTS_DESENVOLVIMENTO.md` §5).
- **O que substitui:** no item 2, o tratamento de major (painel com aprovação, rótulo `requer-adr`, ADR por major); no
  item 3, o limite da dispensa de quarentena à vulnerabilidade de prazo curto; na alternativa "Dependabot", o motivo do
  painel com aprovação de major. Os demais itens continuam valendo.

### Contexto da revisão

A regra original tratava a versão major como exceção. Isso deixa o sistema numa linha antiga, que recebe correção por
menos tempo e acumula diferença para a linha corrente. Quando sai a correção de uma vulnerabilidade só na linha nova, a
migração inteira vira urgência. O dono do projeto decidiu inverter a regra: estar na última versão estável é o normal, e
ficar atrás dela é a exceção.

### Decisão da revisão

- **R1. Última versão estável.** Todo componente fica na última versão estável publicada: pacotes npm, Python do
  oráculo (interpretador e pacotes do job de paridade), imagens (`node`, `postgres`, `gotenberg`), GitHub Actions,
  runtime Node.js (última LTS) e PostgreSQL (última major estável). Versão beta, rc, canary ou nightly nunca entra.
- **R2. Prazos.** O componente alcança a última versão estável nestes prazos, contados da publicação:
  - patch e minor: até 7 dias;
  - major: até 30 dias;
  - correção de segurança: o prazo de vulnerabilidade de SEG-VUL-03 (72 horas, 7 dias ou 30 dias), se for menor.

  O prazo conta da publicação da primeira versão estável mais nova que a em uso: para patch e minor, a primeira versão
  mais nova dentro da mesma major; para major, a primeira versão estável da major nova. Para o Node.js, a major conta da
  data em que a linha entrou em LTS.
- **R3. Pedidos de integração.** O Renovate abre PR para patch, minor e major automaticamente. Não há
  `dependencyDashboardApproval` para major. O PR de major leva o rótulo `major`. Todo PR roda a CI completa. O merge é
  sempre humano. Nenhum merge é automático (item 5, sem mudança).
- **R4. Quarentena.** Atualização comum espera 3 dias desde a publicação (`minimumReleaseAge` de 3 dias). Motivo:
  ataques de cadeia de suprimentos publicam versões maliciosas que costumam ser retiradas do registro em horas ou poucos
  dias; 3 dias cabem dentro do prazo de 7 dias de R2. Atualização que corrige vulnerabilidade conhecida
  (`vulnerabilityAlerts` do Renovate, com os dados do OSV) entra sem quarentena (`minimumReleaseAge` nulo) e passa pela
  mesma revisão humana do item 3.
- **R5. Registro de versões.** Major não exige ADR novo. O PR de major atualiza o registro de versões do sistema
  (`docs/especificacao/adr/registro-versoes.md`, identificador ADR-RV): um ADR vivo, com a tabela componente, versão,
  data e notas de migração. O modelo está em `docs/modelos/REGISTRO_VERSOES.md` do kit. Componente atrás da última
  versão estável depois do prazo de R2 é exceção: exige entrada no registro com motivo verificável (por exemplo, a
  ferramenta X ainda não suporta a major Y, com o link do issue) e condição de saída. Cada exceção é revisada no
  relatório semanal (SEG-VUL-07).
- **R6. Dependência nova.** Dependência nova (nome novo no `package.json`), troca de biblioteca, imagem nova (nome de
  imagem novo no Dockerfile ou no `docker-compose.yml`) e serviço novo continuam exigindo ADR e decisão humana (P-13).
  A P-13 trata só disso. Etiqueta nova de uma imagem que já está em uso é atualização (R3), não imagem nova.
- **R7. Relatório de atraso.** O agente de segurança diário (`seguranca-diaria.yml`) lista os componentes atrás da
  última versão estável, com os dias de atraso: `npm outdated` (pacotes npm); etiquetas das imagens do Dockerfile e do
  `docker-compose.yml` contra o registro de imagens; versões das actions contra os lançamentos de cada uma; pacotes do
  Python do oráculo no ambiente do job de paridade; runtime Node.js contra o calendário de LTS; PostgreSQL gerenciado
  pela versão anotada no registro de versões. Quando um prazo de R2 vence, abre issue com o rótulo `versao-atrasada`,
  uma por componente e versão-alvo, citando a exceção do registro se houver. O relatório não aplica nada.
- **R8. Versões citadas no pacote.** Toda versão citada nos documentos do pacote é fotografia datada, não regra. A
  fonte da versão em uso é o registro de versões. Fotografia de 01/11/2026: Next.js 16.x, Prisma 7.x, Node.js 26 LTS,
  PostgreSQL 18, ESLint 10, Vitest 5.
- **R9. Exercício do D11.** O branch `exercicio/cve-2025-29927` continua com o Next.js numa versão anterior à correção,
  de propósito. Ele fica fora dos prazos de R2 e do relatório de R7, que olham só o `main`.

Configuração de referência: `renovate.json` do kit de desenvolvimento.

### Alternativas consideradas na revisão

- **Manter major como exceção (painel com aprovação e ADR por major).** Rejeitada pela decisão de 01/11/2026: mantém o
  sistema em linha antiga e transforma correção de segurança em migração urgente.
- **Merge automático de patch e minor para cumprir o prazo de 7 dias.** Rejeitada: tira o humano da decisão (item 5).
- **Sem quarentena, para alcançar a última versão mais cedo.** Rejeitada: expõe à versão maliciosa ainda não retirada
  do registro. A quarentena de 3 dias cabe no prazo de 7 dias.
- **Aceitar versão rc de major para chegar antes.** Rejeitada: pré-lançamento não é versão estável (R1).

### Consequências da revisão

- Positivas: o sistema fica na linha que recebe correção; cada migração de major é pequena e rotineira; o atraso fica
  visível todos os dias.
- Negativas: mais PRs de major para revisar; risco de quebra por mudança incompatível, contido pela CI completa e pelo
  merge humano; ferramenta que demora a suportar a major nova vira exceção registrada, com revisão semanal.
- O que passa a ser verificado: SEG-SUP-02 (quarentena e dispensa), SEG-SUP-03 (PR de major com o registro de versões),
  SEG-SUP-09 (prazos e relatório de atraso), SEG-VUL-05 (correção em qualquer major pelo Renovate) e SEG-VUL-07
  (exceções do registro no relatório semanal).
