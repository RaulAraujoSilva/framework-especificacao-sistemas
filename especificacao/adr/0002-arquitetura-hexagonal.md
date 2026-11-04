# ADR-0002: Arquitetura hexagonal e regra de dependência verificável

- **Situação:** aceita
- **Data:** 2026-10-31
- **Origem:** RNF-12 (domínio sem dependência de framework); RNF-06 (fonte externa fora do ar não bloqueia o fluxo);
  lacuna "Fronteiras do código" de `../docs/metodologia/01_ESPECIFICACAO_SISTEMA.md` §8.

## Contexto

As regras V01 a V12, o recálculo, os prazos e a verificação de citação são o valor do sistema. Elas mudam por aditivo,
por deliberação ou por decisão da CAPET e da Procuradoria. As fontes (IPEADATA, IBGE SIDRA, ANEEL, SEI, modelo de
linguagem) mudam por outro motivo e caem sem aviso. Se a regra ficar dentro da tela, da rota ou do adaptador, a IA de
desenvolvimento duplica a regra a cada tela nova e o teste passa a depender de rede.

## Decisão

Cinco camadas, mais a raiz de composição. A dependência só aponta para dentro.

| Camada | Pasta | Pode importar |
|---|---|---|
| `contratos` (núcleo compartilhado) | `src/contratos` | só `zod` e os arquivos JSON Schema |
| `dominio` | `src/dominio` | `contratos`, o próprio `dominio`, `decimal.js`, `ajv`, `ajv-formats` |
| `portas` | `src/portas` | `dominio` (tipos), `contratos` |
| `aplicacao` | `src/aplicacao` | `dominio`, `portas`, `contratos` |
| `adaptadores` | `src/adaptadores` | `portas`, `dominio` (tipos), `contratos`, bibliotecas de infraestrutura |
| `composicao` | `src/composicao` | todas, menos `interface`, `app` e `jobs` |
| `interface` | `src/app`, `src/components`, `src/interface`, `src/jobs` | `aplicacao`, `contratos`, `composicao` (só o contêiner) e tipos do `dominio` |

A regra é verificada por máquina, em dois portões que rodam a cada commit e no CI:

1. **dependency-cruiser** (`.dependency-cruiser.cjs`): proíbe import fora da tabela, ciclo entre módulos e import de
   outro módulo que não seja pelo `index.ts` dele. A configuração está em `05_ARQUITETURA.md` §6.
2. **ESLint** (`no-restricted-imports`, `no-restricted-globals`, `boundaries` opcional): proíbe `next`, `react`,
   `@prisma/client`, `node:*` e `fetch` no domínio e na aplicação.

Sem framework de injeção de dependência. Cada caso de uso é uma função fábrica que recebe as portas
(`criarValidarPleito({ pleitos, series, baseEspecialista, relogio, auditoria })`). A raiz de composição
(`src/composicao/container.ts`) liga portas a adaptadores a partir da configuração.

## Alternativas consideradas

- **Camadas tradicionais do Next.js (componentes, `lib/`, `services/`).** Sem fronteira verificável, a regra migra
  para a rota. Rejeitada.
- **Pastas por funcionalidade sem camadas.** Fácil de navegar, mas não impede o componente de chamar o Prisma.
  Rejeitada; os módulos MOD-* existem dentro de cada camada.
- **Contêiner de injeção (tsyringe, inversify).** Decoradores e metadados em tempo de execução para um grafo pequeno.
  Rejeitada: funções fábrica bastam e são tipadas.
- **eslint-plugin-boundaries sozinho.** Cobre as camadas, mas não a regra de "só pelo `index.ts`" nem a matriz entre
  módulos do domínio. Fica como reforço opcional.

## Consequências

- Positivas: domínio testável sem banco nem rede, com cobertura de 90% (RNF-12); troca de fonte ou de provedor de
  modelo de linguagem sem mexer em regra; o oráculo em Python compara com funções puras (ADR-0003).
- Negativas: mais arquivos por funcionalidade (porta, adaptador, fake de teste). O custo é aceito porque cada um é
  pequeno e a IA gera a partir do padrão.
- Um import proibido derruba o portão. A correção é mover o código para a camada certa, nunca relaxar a regra.
