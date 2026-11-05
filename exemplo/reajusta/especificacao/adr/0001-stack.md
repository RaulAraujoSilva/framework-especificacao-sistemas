# ADR-0001: Stack do sistema

- **Situação:** aceita (stack principal); os complementos marcados "(proposto)" aguardam a validação da TI na PARADA 11.
  Política de versões revista em 01/11/2026 (ADR-0012, revisão de 01/11/2026): a stack fixa as bibliotecas, não as
  versões.
- **Data:** 2026-10-31; revisão das versões em 2026-11-01
- **Origem:** `01_VISAO_ESCOPO.md` §4; RNF-10, RNF-12, RNF-14; lacuna "Stack e onde roda" de
  `../../docs/COMO_FOI_FEITO.md` §8.

## Contexto

Uma IA de desenvolvimento vai construir o sistema em várias sessões. Sem a stack escrita, cada sessão escolhe outra
biblioteca para o mesmo problema. O sistema precisa subir com Docker e PostgreSQL, sem serviço pago obrigatório
(RNF-14), e ter domínio testável sem framework (RNF-12).

## Decisão

Stack fixa. Nenhuma biblioteca fora desta lista entra sem novo ADR. Cada biblioteca, runtime e serviço da lista fica na
última versão estável (SEG-SUP-09). As versões citadas abaixo são fotografia de 01/11/2026; a versão em uso é a do
registro de versões do sistema (`registro-versoes.md`, nesta pasta no repositório do sistema).

| Camada | Escolha | Situação |
|---|---|---|
| Linguagem | TypeScript em modo estrito (`strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`); `any` proibido por lint | decidida |
| Aplicação web | Next.js (última estável; 16.x em 01/11/2026) com App Router, React (última estável), route handlers como API | decidida |
| Validação de entrada | Zod nos route handlers e nos formulários | decidida |
| Banco e acesso | PostgreSQL com Prisma (última estável; 7.x em 01/11/2026) | decidida |
| Dados na tela | @tanstack/react-query e @tanstack/react-table | decidida |
| Formulários | react-hook-form com resolvedor Zod | decidida |
| Interface | Tailwind v4 (tokens em `@theme`), cn (clsx + tailwind-merge), cva, lucide-react, Recharts, next-themes; padrão do Design System gov.br (ADR-0010) | decidida |
| Autenticação | NextAuth com credenciais e sessão JWT (ADR-0009) | decidida |
| Testes | Vitest (última estável; 5.x em 01/11/2026), Testing Library, MSW, Playwright | decidida |
| Aritmética decimal no domínio | decimal.js (ADR-0003) | complemento (proposto) |
| Validação do layout do pleito (V01) | Ajv com o dialeto JSON Schema 2020-12 e ajv-formats, sobre o mesmo schema do layout | complemento (proposto) |
| Fila e agendamento | pg-boss, que guarda fila e agenda no próprio PostgreSQL | complemento (proposto) |
| Documento DOCX por modelo | docxtemplater com pizzip | complemento (proposto) |
| Conversão DOCX → PDF | Gotenberg (contêiner com LibreOffice), chamado por adaptador | complemento (proposto) |
| Logs | pino, em JSON, com redação de campos | complemento (proposto) |
| Hash de senha | argon2 (argon2id) | complemento (proposto) |
| Regra de dependência | dependency-cruiser e ESLint (última estável; 10.x em 01/11/2026) (ADR-0002) | complemento (proposto) |
| Testes de propriedade e diferencial | fast-check | complemento (proposto) |
| Acessibilidade automática | @axe-core/playwright | complemento (proposto) |
| Execução | Node.js (última LTS; 26 em 01/11/2026) em contêiner Docker; PostgreSQL (última major estável; 18 em 01/11/2026); npm com `package-lock.json` | complemento (proposto) |

Versões: o `package.json` fixa versão exata de cada dependência (sem `^` nem `~`), sempre a última estável, nos prazos de
SEG-SUP-09 (patch e minor em até 7 dias; major em até 30 dias). A atualização chega por PR do Renovate com os portões
verdes e merge humano (SEG-SUP-03). Major não pede ADR novo: o PR de major atualiza o registro de versões. Beta, rc,
canary e nightly nunca entram.

## Alternativas consideradas

- **Back-end separado (NestJS, FastAPI) e front-end em Next.js.** Dois serviços, duas linguagens ou dois deploys para
  um sistema de uma agência só. Rejeitada: a separação que importa é entre domínio e framework, e ela é garantida pela
  arquitetura hexagonal (ADR-0002), não por dois processos.
- **Manter o domínio em Python e chamar por API.** Ver ADR-0003.
- **Redis com BullMQ para a fila.** Mais um serviço para operar. Rejeitada: o volume é pequeno (cerca de 51 processos
  de reajuste por ano em toda a agência, `../docs/LEVANTAMENTO_MOTOR_CALCULO.md` §4) e o PostgreSQL já existe.
- **Biblioteca de componentes pronta (MUI, shadcn/ui sem adaptação).** Ver ADR-0010.

## Consequências

- Positivas: uma linguagem de ponta a ponta; um banco para dados e fila; tudo sobe com `docker compose up`, sem serviço
  pago (RNF-14).
- Negativas: o domínio deixa de ser o código de referência em Python e precisa de testes de paridade (ADR-0003). O
  Next.js obriga a separar com disciplina o que é rota e o que é regra (ADR-0002).
- A IA de desenvolvimento não instala biblioteca nova. Se precisar, para e pede (`AGENTS_DESENVOLVIMENTO.md` §10).
