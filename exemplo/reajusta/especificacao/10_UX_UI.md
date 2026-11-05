# 10. Guia de UX/UI

Guia para a IA de desenvolvimento manter as telas do Reajusta consistentes entre si e com o padrão digital de
governo. Vale para todas as telas TL-01 a TL-16 (`01_VISAO_ESCOPO.md`, seção 12). As telas estão especificadas em
[`11_TELAS.md`](11_TELAS.md); os perfis e as jornadas, em [`02_PERFIS_E_JORNADAS.md`](02_PERFIS_E_JORNADAS.md). O
protótipo navegável de baixa fidelidade está em [`prototipos/wireframes.html`](prototipos/wireframes.html).

Como usar este guia:
- Antes de criar uma tela, procure o componente no inventário da seção 5. Não crie componente novo se um CMP-*
  resolve. Se precisar de um, acrescente-o aqui com ID novo antes de usá-lo.
- Cores, fontes, espaços, raios e sombras saem só dos tokens da seção 3. Nenhuma cor em hexadecimal fora do
  `globals.css`. A paleta padrão do Tailwind é desligada.
- Textos de tela saem do guia de mensagens da seção 6. Nenhum texto em inglês na interface.

## 1. Princípios

| ID | Princípio | O que a tela faz | Origem |
|---|---|---|---|
| UX-PRI-01 | **Decisão humana visível** | Toda ação que muda o ciclo (devolver, emitir peça, registrar deliberação, certificar, encerrar) é um botão explícito, com confirmação e com o nome do perfil e da unidade que decide. A tela nunca diz "aprovado" ou "homologado" por conta própria: diz "pronto para revisão", "minuta gerada", "aguarda decisão de…". Minuta tem selo permanente "Minuta — requer revisão" até ser exportada por quem revisou. | RNF-07; seção 3 do documento-base (decisão do Conselho-Diretor fora do escopo) |
| UX-PRI-02 | **Origem de todo número a um clique** | Todo número de domínio (índice, peso, valor de série, percentual, prazo, tarifa) é envolvido por CMP-05 `OrigemDoNumero`. Um clique, ou Enter, abre a origem: pleito e anexo, série com fonte e data da consulta, trecho do contrato, regra do motor. | RNF-02, RF-CAL-05 |
| UX-PRI-03 | **Situação sempre por cor e texto** | ok, aviso, erro e a refazer aparecem sempre com cor, ícone **e** palavra (CMP-01). Nenhuma informação depende só da cor. | WCAG 1.4.1; RF-PLE-03, RF-SER-04 |
| UX-PRI-04 | **Linguagem de quem analisa** | Mensagens no vocabulário do reajuste (mês o, mês i, interstício, realinhamento, IR, total), com o número e a regra que falhou, sem código de erro técnico, sem inglês, sem termo de programação. | RNF-09; seção 7 do documento-base |
| UX-PRI-05 | **Resumo antes do detalhe** | Cada tela abre com o resumo (CMP-10 `ResumoCifras`: quantos ok, avisos, erros; situação; dono; próximo prazo) e só abaixo a lista, a tabela ou o texto. O resultado da validação cabe numa tela de desktop (1280 × 800) sem rolar o resumo. | RNF-09 |
| UX-PRI-06 | **Unidade e data sempre explícitas** | Prazo diz "dias úteis" ou "dias corridos" por extenso na primeira ocorrência da tela e "du"/"dc" depois. Datas em dd/mm/aaaa; meses de referência em "out/2024". Números em pt-BR (vírgula decimal, ponto de milhar), com as casas que vieram da fonte. | RF-PRZ-01; R-P01-05 (dias corridos) × RF-PRZ-01 (dias úteis) |
| UX-PRI-07 | **Dono e próximo passo sempre na tela** | Todo ciclo mostra a unidade responsável (CMP-08) e o próximo ato com prazo (CMP-07). Ciclo sem dono é mostrado como erro, nunca como vazio. | RF-PRZ-02; AS-IS: 41 du sem unidade (mediana) |
| UX-PRI-08 | **Exemplo nunca se passa por dado real** | Dado ilustrativo (protótipo, ambiente de treinamento) tem a marca "exemplo". Hora estimada tem a marca "hipótese até a calibração". | Regras do briefing; I-P01-02 |

## 2. Base: Design System gov.br sobre Tailwind v4

- O Reajusta segue o **Padrão Digital de Governo** (Design System gov.br, https://www.gov.br/ds) nos fundamentos
  (cor, tipografia, espaço, superfície, foco, estados de interação) e nos padrões de cabeçalho, menu, breadcrumb,
  mensagem, tag, tabela, botão e campo.
- Não usa o CSS do pacote `@govbr-ds/core`. Reproduz os tokens em Tailwind v4 (`@theme`) e implementa os componentes
  em React (CMP-*), com `cva` para variantes e `cn` para classes.
- Os valores marcados "confirmado" foram lidos do arquivo `dist/core-tokens.css` e do `dist/core.min.css` do pacote
  `@govbr-ds/core` 3.7.0, a versão publicada mais recente da linha 3. Os marcados "(a conferir)" são extensão do
  Reajusta ou não foram confirmados no DS.
- A AGENERSA é órgão estadual. O cabeçalho usa a marca da agência e o nome do sistema, não o logotipo gov.br.
- Ícones: `lucide-react` no lugar do Font Awesome usado pelo DS. Todo ícone que transmite situação tem texto ao
  lado; ícone decorativo leva `aria-hidden="true"`.

## 3. Tokens

### 3.1 Valores do DS gov.br usados

| Grupo | Token gov.br | Valor | Uso no Reajusta | Situação |
|---|---|---|---|---|
| Interação | `--interactive-light` = `blue-warm-vivid-70` | `#1351B4` | links, botão primário, foco de seleção (tema claro) | confirmado |
| Interação | `--interactive-dark` = `blue-warm-20` | `#C5D4EB` | links e botão no tema escuro | confirmado |
| Fundo | `--background-light` = `pure-0` | `#FFFFFF` | fundo da área de trabalho | confirmado |
| Fundo | `--background-alternative` = `gray-5` | `#F0F0F0` | fundo da página e das faixas | confirmado |
| Fundo | `--background-dark` = `blue-warm-vivid-90` | `#071D41` | fundo do tema escuro, rodapé | confirmado |
| Texto | `--color-light` = `gray-80` | `#333333` | texto principal no tema claro | confirmado |
| Texto | `--color-dark` = `pure-0` | `#FFFFFF` | texto no tema escuro | confirmado |
| Estado | `--success` = `green-cool-vivid-50` | `#168821` | borda e ícone de ok | confirmado |
| Estado | `--danger` = `red-vivid-50` | `#E52207` | borda e ícone de erro | confirmado |
| Estado | `--warning` = `yellow-vivid-20` | `#FFCD07` | borda de aviso (nunca como cor de texto sobre branco) | confirmado |
| Estado | `--info` = `blue-warm-vivid-60` | `#155BCB` | informação | confirmado |
| Foco | `--focus-color-light` = `gold-vivid-40` | `#C2850C` | contorno de foco no tema claro | confirmado |
| Foco | `--focus-color-dark` = `gold-vivid-20` | `#FFBE2E` | contorno de foco no tema escuro | confirmado |
| Foco | `--focus-style`, `--focus-width`, `--focus-offset` | `dashed`, `4px`, `4px` | `outline` de todo elemento focável | confirmado |
| Interação | `--hover-light`, `--hover-dark` | opacidade 0,16 e 0,30 | sobreposição no passar do mouse | confirmado |
| Interação | `--pressed-light`, `--pressed-dark` | opacidade 0,45 e 0,65 | sobreposição ao pressionar | confirmado |
| Interação | `--disabled` | opacidade 0,45 | elemento desabilitado | confirmado |
| Tipografia | `--font-family-base` | `Rawline, Raleway, sans-serif` | todo texto | confirmado |
| Tipografia | `--font-size-scale-base` | `14px` | texto de tabela e de formulário | confirmado |
| Tipografia | escala `down-01` a `up-05` (razão 1,2) | 11,662 · 14 · 16,8 · 20,16 · 24,192 · 29,036 · 34,832 px | títulos e texto corrido | confirmado |
| Tipografia | pesos | 300 · 400 · 500 · 600 · 700 · 800 | regular 400, semi-bold 600 em botão e rótulo, bold 700 em cifras | confirmado |
| Tipografia | `--font-line-height-low/medium/high` | 1,15 · 1,45 · 1,85 | títulos · interface · texto corrido de minuta | confirmado |
| Espaço | `--spacing-scale-half`, `base`, `baseh`, `2x` … `10x` | 4 · 8 · 12 · 16 · 20 · 24 … 80 px | todo espaçamento (múltiplos de 4 px) | confirmado |
| Superfície | `--surface-rounder-sm/md/lg/pill` | 4 · 8 · 16 px · 999em | campo · cartão · diálogo · botão e tag | confirmado |
| Superfície | `--surface-width-sm/md/lg` | 1 · 2 · 4 px | bordas · borda de situação · foco | confirmado |
| Superfície | `--surface-shadow-sm/md/lg/xl` | `0 1px 6px`, `0 3px 6px`, `0 6px 6px`, `0 9px 6px`, preto a 16% | cartão · menu suspenso · diálogo · camada sobre camada | confirmado |
| Botão | `--button-small/medium/large` | 32 · 40 · 48 px de altura, raio 100em, semi-bold, 16,8 px | botões | confirmado |
| Campo | `--input-small/medium/large`, raio | 32 · 40 · 48 px, raio 4 px, borda 1 px | campos de formulário | confirmado |
| Grade | quebras de layout | 576 · 992 · 1280 · 1600 px | responsividade | confirmado (media queries do `core.min.css`) |
| Fundo de situação | pares claros (`green-cool-vivid-5`, `yellow-vivid-5`, `red-vivid-5`, `orange-vivid-5`, `blue-warm-vivid-5`) | `#E3F5E1`, `#FFF5C2`, `#FFF3F2`, `#FDF5E6`, `#EDF5FF` | fundo do CMP-01 e das mensagens | cores confirmadas; combinação é do Reajusta |
| Situação "a refazer" | `orange-vivid-50` / `orange-vivid-60` | `#C05600` / `#8C471C` | borda e texto de "a refazer" | cores confirmadas; uso é do Reajusta (a conferir com o DS, que não tem esse estado) |
| Tema escuro de página inteira | tokens `*-dark` aplicados à página toda | — | tema escuro do sistema | (a conferir): o DS define o modo escuro por componente (`.dark-mode`), não um tema de página |

### 3.2 Contraste medido (WCAG 2.2, 1.4.3 e 1.4.11)

| Par (texto sobre fundo) | Razão | Uso |
|---|---|---|
| `#333333` sobre `#FFFFFF` | 12,63 | texto principal |
| `#1351B4` sobre `#FFFFFF` | 7,33 | link, botão secundário |
| `#FFFFFF` sobre `#1351B4` | 7,33 | botão primário |
| `#636363` sobre `#FFFFFF` | 6,01 | texto secundário (menor tom de cinza permitido para texto) |
| `#216E1F` sobre `#E3F5E1` | 5,56 | chip ok |
| `#5F3617` sobre `#FFF5C2` | 9,42 | chip aviso |
| `#B50909` sobre `#FFF3F2` | 6,43 | chip erro |
| `#8C471C` sobre `#FDF5E6` | 6,39 | chip a refazer |
| `#1351B4` sobre `#EDF5FF` | 6,67 | chip informação |
| `#C2850C` sobre `#FFFFFF` | 3,16 | contorno de foco (elemento não textual, mínimo 3:1) |
| `#FFFFFF` sobre `#071D41` | 16,65 | texto no tema escuro |
| `#C5D4EB` sobre `#071D41` | 11,09 | link no tema escuro |
| `#B7F5BD`, `#FFCD07`, `#FDB8AE`, `#FFBC78` sobre `#071D41` | 13,33 · 11,09 · 10,03 · 10,08 | ok, aviso, erro, a refazer no tema escuro |
| `#FFBE2E` sobre `#071D41` | 10,04 | foco no tema escuro |

Proibido: `#FFCD07` (aviso) como cor de texto sobre fundo claro (1,5:1); `#888888` e mais claros como texto sobre
branco (3,54:1); `#E52207` em texto pequeno sobre fundo de situação (use `#B50909`).

### 3.3 Bloco `@theme` (copiar para `app/globals.css`)

```css
@import "tailwindcss";

/* next-themes grava a classe "dark" em <html>; o modo do sistema é o padrão */
@custom-variant dark (&:where(.dark, .dark *));

@theme {
  /* Desliga a paleta padrão do Tailwind: só valem os tokens abaixo */
  --color-*: initial;

  /* Paleta do DS gov.br (@govbr-ds/core 3.7.0, dist/core-tokens.css) */
  --color-branco: #ffffff;
  --color-preto: #000000;
  --color-cinza-2: #f8f8f8;
  --color-cinza-5: #f0f0f0;
  --color-cinza-10: #e6e6e6;
  --color-cinza-20: #cccccc;
  --color-cinza-30: #adadad;
  --color-cinza-40: #888888;
  --color-cinza-60: #636363;
  --color-cinza-80: #333333;
  --color-cinza-90: #1b1b1b;
  --color-azul-5: #edf5ff;          /* blue-warm-vivid-5 */
  --color-azul-10: #d4e5ff;         /* blue-warm-vivid-10 */
  --color-azul-20: #c5d4eb;         /* blue-warm-20 (interactive-dark) */
  --color-azul-30: #81aefc;         /* blue-warm-vivid-30 */
  --color-azul-60: #155bcb;         /* blue-warm-vivid-60 (info) */
  --color-azul-70: #1351b4;         /* blue-warm-vivid-70 (interactive-light) */
  --color-azul-80: #0c326f;         /* blue-warm-vivid-80 */
  --color-azul-90: #071d41;         /* blue-warm-vivid-90 (background-dark) */
  --color-azul-cinza-80: #252f3e;   /* blue-warm-80 */
  --color-verde-5: #e3f5e1;
  --color-verde-10: #b7f5bd;
  --color-verde-50: #168821;        /* success */
  --color-verde-60: #216e1f;
  --color-amarelo-5: #fff5c2;
  --color-amarelo-20: #ffcd07;      /* warning */
  --color-amarelo-50: #947100;
  --color-laranja-5: #fdf5e6;
  --color-laranja-20: #ffbc78;
  --color-laranja-50: #c05600;
  --color-laranja-60: #8c471c;
  --color-laranja-70: #5f3617;
  --color-vermelho-5: #fff3f2;
  --color-vermelho-20: #fdb8ae;
  --color-vermelho-50: #e52207;     /* danger */
  --color-vermelho-60: #b50909;
  --color-ouro-20: #ffbe2e;         /* focus-color-dark */
  --color-ouro-40: #c2850c;         /* focus-color-light */

  /* Tipografia: Rawline com fallback (Raleway e fonte do sistema) */
  --font-sans: Rawline, Raleway, ui-sans-serif, system-ui, "Segoe UI", Arial, sans-serif;
  --font-mono: ui-monospace, "Cascadia Mono", Consolas, monospace;
  /* Escala gov.br (base 14 px, razão 1,2), em rem sobre 16 px para respeitar o zoom do navegador */
  --text-xs: 0.729rem;    --text-xs--line-height: 1.45;   /* down-01 11,662 px: só metadado */
  --text-sm: 0.875rem;    --text-sm--line-height: 1.45;   /* base 14 px: tabela, formulário */
  --text-base: 1.05rem;   --text-base--line-height: 1.45; /* up-01 16,8 px: texto de interface, botão */
  --text-lg: 1.26rem;     --text-lg--line-height: 1.15;   /* up-02 20,16 px: título de seção */
  --text-xl: 1.512rem;    --text-xl--line-height: 1.15;   /* up-03 24,192 px: título de tela */
  --text-2xl: 1.815rem;   --text-2xl--line-height: 1.15;  /* up-04 29,036 px: cifra do resumo */
  --text-3xl: 2.177rem;   --text-3xl--line-height: 1.15;  /* up-05 34,832 px: cifra de painel */
  --leading-baixo: 1.15;
  --leading-medio: 1.45;
  --leading-alto: 1.85;   /* texto corrido de minuta */
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;

  /* Espaço: múltiplos de 4 px (spacing-scale-half). p-1 = 4 px, p-2 = 8 px (base), p-3 = 12 px, p-4 = 16 px (2x) */
  --spacing: 0.25rem;

  /* Superfície */
  --radius-sm: 4px;       /* surface-rounder-sm: campo, chip retangular */
  --radius-md: 8px;       /* surface-rounder-md: cartão */
  --radius-lg: 16px;      /* surface-rounder-lg: diálogo */
  --radius-pill: 999em;   /* surface-rounder-pill: botão, tag */
  --shadow-sm: 0 1px 6px rgb(0 0 0 / 0.16);
  --shadow-md: 0 3px 6px rgb(0 0 0 / 0.16);
  --shadow-lg: 0 6px 6px rgb(0 0 0 / 0.16);
  --shadow-xl: 0 9px 6px rgb(0 0 0 / 0.16);

  /* Quebras do DS gov.br */
  --breakpoint-sm: 36rem;   /* 576 px */
  --breakpoint-md: 62rem;   /* 992 px */
  --breakpoint-lg: 80rem;   /* 1280 px */
  --breakpoint-xl: 100rem;  /* 1600 px */

  /* Alturas de controle */
  --height-controle-p: 32px;
  --height-controle-m: 40px;
  --height-controle-g: 48px;
}

/* Tokens semânticos: as telas usam só estes nomes (bg-fundo, text-texto, border-ok…) */
:root {
  --fundo: #f0f0f0;            /* background-alternative */
  --superficie: #ffffff;       /* background-light */
  --superficie-2: #f8f8f8;
  --texto: #333333;            /* color-light */
  --texto-2: #636363;
  --borda: #cccccc;
  --interativo: #1351b4;       /* interactive-light */
  --interativo-texto: #ffffff;
  --foco: #c2850c;             /* focus-color-light */
  --sobreposicao-hover: 0.16;  /* hover-light */
  --sobreposicao-pressionado: 0.45;
  --ok-fundo: #e3f5e1;      --ok-texto: #216e1f;      --ok-borda: #168821;
  --aviso-fundo: #fff5c2;   --aviso-texto: #5f3617;   --aviso-borda: #ffcd07;  --aviso-icone: #947100;
  --erro-fundo: #fff3f2;    --erro-texto: #b50909;    --erro-borda: #e52207;
  --refazer-fundo: #fdf5e6; --refazer-texto: #8c471c; --refazer-borda: #c05600;
  --info-fundo: #edf5ff;    --info-texto: #1351b4;    --info-borda: #155bcb;
  --cabecalho: #ffffff;
  --rodape: #071d41;
}

.dark {
  --fundo: #071d41;            /* background-dark */
  --superficie: #0c326f;
  --superficie-2: #252f3e;
  --texto: #ffffff;            /* color-dark */
  --texto-2: #c5d4eb;
  --borda: #81aefc;
  --interativo: #c5d4eb;       /* interactive-dark */
  --interativo-texto: #071d41;
  --foco: #ffbe2e;             /* focus-color-dark */
  --sobreposicao-hover: 0.3;   /* hover-dark */
  --sobreposicao-pressionado: 0.65;
  --ok-fundo: #071d41;      --ok-texto: #b7f5bd;      --ok-borda: #00a91c;
  --aviso-fundo: #071d41;   --aviso-texto: #ffcd07;   --aviso-borda: #ffcd07;  --aviso-icone: #ffcd07;
  --erro-fundo: #071d41;    --erro-texto: #fdb8ae;    --erro-borda: #fb5a47;
  --refazer-fundo: #071d41; --refazer-texto: #ffbc78; --refazer-borda: #ff8c00;
  --info-fundo: #071d41;    --info-texto: #c5d4eb;    --info-borda: #81aefc;
  --cabecalho: #071d41;
  --rodape: #13171f;
}

@theme inline {
  --color-fundo: var(--fundo);
  --color-superficie: var(--superficie);
  --color-superficie-2: var(--superficie-2);
  --color-texto: var(--texto);
  --color-texto-2: var(--texto-2);
  --color-borda: var(--borda);
  --color-interativo: var(--interativo);
  --color-interativo-texto: var(--interativo-texto);
  --color-foco: var(--foco);
  --color-ok-fundo: var(--ok-fundo);         --color-ok-texto: var(--ok-texto);         --color-ok-borda: var(--ok-borda);
  --color-aviso-fundo: var(--aviso-fundo);   --color-aviso-texto: var(--aviso-texto);   --color-aviso-borda: var(--aviso-borda);
  --color-aviso-icone: var(--aviso-icone);
  --color-erro-fundo: var(--erro-fundo);     --color-erro-texto: var(--erro-texto);     --color-erro-borda: var(--erro-borda);
  --color-refazer-fundo: var(--refazer-fundo); --color-refazer-texto: var(--refazer-texto); --color-refazer-borda: var(--refazer-borda);
  --color-info-fundo: var(--info-fundo);     --color-info-texto: var(--info-texto);     --color-info-borda: var(--info-borda);
  --color-cabecalho: var(--cabecalho);
  --color-rodape: var(--rodape);
}

@layer base {
  html { font-family: var(--font-sans); color: var(--texto); background: var(--fundo); }
  body { font-size: var(--text-base); line-height: var(--leading-medio); }
  /* Foco do DS gov.br: tracejado de 4 px, afastado 4 px, nunca removido */
  :focus-visible { outline: 4px dashed var(--foco); outline-offset: 4px; }
  /* Cifras e tabelas de números com algarismos de largura fixa */
  .numeros, table td.num { font-variant-numeric: tabular-nums; }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
  }
}

/* Alto contraste (barra de acessibilidade, eMAG): classe "alto-contraste" em <html> */
.alto-contraste {
  --fundo: #000000; --superficie: #000000; --superficie-2: #000000;
  --texto: #ffffff; --texto-2: #ffffff; --borda: #ffffff;
  --interativo: #ffff00; --interativo-texto: #000000; --foco: #ffff00;
}
```

Regras de uso dos tokens:
- Texto de situação usa `text-ok-texto`, `text-aviso-texto`, `text-erro-texto`, `text-refazer-texto`; borda e ícone
  usam `*-borda` e `aviso-icone`.
- Fonte Rawline: servir os arquivos pelo próprio sistema com `next/font/local` (licença e arquivos a conferir com o
  DS); sem acesso, o fallback é Raleway (`next/font/google`, licença OFL) e depois a fonte do sistema. Nada de CDN em
  produção (RNF-14).
- O alto contraste é extensão do Reajusta para atender ao eMAG (a conferir com o DS).

## 4. Layout das páginas

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Barra de acessibilidade: Ir para o conteúdo [1] · Ir para o menu [2] ·      │
│ Ir para a busca [3] · Alto contraste · Tema claro/escuro                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ CABEÇALHO (CMP-19): [≡] AGENERSA · Reajusta  [Buscar ciclo]  [🔔 3] [Perfil] │
├──────────────┬──────────────────────────────────────────────────────────────┤
│ MENU LATERAL │ Breadcrumb (CMP-21): Início › Ciclos › Paraty 2026            │
│ (CMP-20)     │ Título da tela (h1)               [ação principal]            │
│ Ciclos       │ ResumoCifras (CMP-10)                                         │
│ Minha fila   │ ───────────────────────────────────────────────────────────── │
│ Pleitos      │ ÁREA DE TRABALHO (main)                                        │
│ Contratos    │ detalhe: tabelas, listas, linha do tempo, editor              │
│ Pauta        │                                                              │
│ Faturas      │                                                              │
│ Indicadores  │                                                              │
│ Séries       │                                                              │
│ Administração│                                                              │
├──────────────┴──────────────────────────────────────────────────────────────┤
│ RODAPÉ: AGENERSA · versão do sistema · Acessibilidade · Privacidade (LGPD)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

| ID | Região | Regra |
|---|---|---|
| UX-LAY-01 | Barra de acessibilidade | Primeira coisa focável da página. Links com atalho eMAG: `Alt+1` conteúdo, `Alt+2` menu, `Alt+3` busca, `Alt+4` rodapé. Botões de alto contraste e de tema. |
| UX-LAY-02 | Cabeçalho (`<header>`) | Altura de 56 px no desktop e 48 px no celular (a conferir com o padrão de cabeçalho compacto do DS). Marca da agência e nome do sistema à esquerda; busca de ciclo por número SEI ou contrato; sino de alertas com contador (CMP-07 resumido); menu do usuário com nome do perfil, unidade, troca de perfil (TL-16) e sair. |
| UX-LAY-03 | Menu lateral (`<nav aria-label="Menu principal">`) | 256 px fixo a partir de 992 px; abaixo disso, gaveta aberta pelo botão `≡` do cabeçalho, com foco preso enquanto aberta e `Esc` para fechar. Mostra só os itens que o perfil pode abrir. Item atual com `aria-current="page"` e barra de 4 px na cor `interativo`. |
| UX-LAY-04 | Breadcrumb (`<nav aria-label="Você está aqui">`) | Sempre presente, exceto em TL-16. Último item não é link e leva `aria-current="page"`. No celular, mostra só o nível anterior ("‹ Ciclos"). |
| UX-LAY-05 | Área de trabalho (`<main id="conteudo" tabindex="-1">`) | Largura máxima de 1280 px de conteúdo, margem lateral de 24 px no desktop e 16 px no celular. Ordem fixa: h1 → resumo → ações → detalhe. Uma única ação primária por tela (botão cheio); as demais são secundárias (contorno) ou terciárias (texto). |
| UX-LAY-06 | Rodapé (`<footer>`) | Fundo `rodape`. Versão do sistema, versão das regras e do layout em uso (RNF-03), links de acessibilidade e privacidade. |
| UX-LAY-07 | Detalhe lateral | Painel deslizante à direita (480 px) para OrigemDoNumero e TrechoCitado no desktop; no celular vira tela cheia com botão "Voltar". |
| UX-LAY-08 | Título da página | `<title>` = "{tela} · {contexto} · Reajusta" (ex.: "Resultado da validação · Águas de Paraty 2026 · Reajusta"). |

## 5. Inventário de componentes

Convenções:
- Pasta `components/reajusta/`; nome do arquivo igual ao do componente.
- Tipos de domínio vêm do pacote de domínio (`06_MODELO_DADOS.md`). Os tipos abaixo são de exibição e nunca usam `any`.
- Todo componente aceita `className?: string` e é testado com Testing Library e `axe` (sem violação).

Tipos de apoio usados pelos componentes:

```ts
export type Situacao = "ok" | "aviso" | "erro" | "a_refazer";
export type RegraValidacao = "V01" | "V02" | "V03" | "V04" | "V05" | "V06" | "V07" | "V08" | "V09" | "V10" | "V11" | "V12";
export type Unidade = "SCEXEC" | "CAPET" | "PROC" | "GABINETE" | "CODIR" | "CONCESSIONARIA";
export type UnidadePrazo = "du" | "dc"; // dias úteis | dias corridos

export type Origem =
  | { tipo: "pleito"; campo: string; arquivo: string; sha256: string; pagina?: number }
  | { tipo: "serie"; fonte: "IPEADATA" | "IBGE SIDRA" | "ANEEL" | "FGV"; codigo: string; mes: string; consultadoEm: string; paga: boolean }
  | { tipo: "contrato"; versao: string; parametro: string; documento: string; trecho: string; conferido: boolean }
  | { tipo: "regra"; regra: RegraValidacao | string; descricao: string; versaoRegras: string }
  | { tipo: "marco"; marco: string; data: string; registradoPor: string }
  | { tipo: "fato_asis"; fato: string; arquivo: string };

export interface NumeroComOrigem { valor: number; casas: number; unidade?: "%" | "p.p." | "du" | "dc" | "h" | "R$"; origem: Origem }
```

| ID | Componente | Propriedades (TypeScript) | Estados | Quando usar | Telas |
|---|---|---|---|---|---|
| CMP-01 | `SituacaoChip` | `{ situacao: Situacao; rotulo?: string; tamanho?: "p" \| "m"; contagem?: number }` | ok, aviso, erro, a refazer; com contagem ("5 avisos") | Toda indicação de situação de regra, conferência, série, prazo ou ciclo. Ícone: `CircleCheck`, `TriangleAlert`, `CircleX`, `RotateCcw`. O texto é obrigatório; o padrão é a palavra da situação. | TL-01 a TL-05, TL-07, TL-12 a TL-14 |
| CMP-02 | `LinhaRegraValidacao` | `{ regra: RegraValidacao; situacao: Situacao; mensagem: string; detalhe?: ReactNode; origens?: Origem[]; acao?: { rotulo: string; href: string } }` | recolhida, expandida; as quatro situações | Uma linha por item do `ResultadoValidacao`. Ordem: erros, a refazer, avisos, ok; dentro de cada grupo, por regra. Expande para mostrar os números e as origens. | TL-03 (prévia), TL-04 |
| CMP-03 | `TabelaMemoriaCalculo` | `{ termos: { sigla: string; peso: NumeroComOrigem; o: NumeroComOrigem; i: NumeroComOrigem; variacao: number; ponderada: number }[]; ir: { refeito: number; arredondado: NumeroComOrigem; declarado: number; casas: number }; outros: { nome: string; pct: NumeroComOrigem; parcela?: number }[]; total: { refeito: number; declarado: number; regra: "multiplicativa" \| "aditiva" }; mesO: string; mesI: string; tolerancia: number }` | conferida, divergente (linha do IR ou do total com CMP-01 erro), com série a refazer | Memória de cálculo de uma apuração. Variações sem arredondar (4 casas); IR arredondado só nas casas do contrato; linha de total com a regra de combinação escrita. Cada célula numérica é CMP-05. | TL-05; resumo em TL-02 e TL-08 |
| CMP-04 | `TrechoCitado` | `{ documento: string; dispositivo?: string; trecho: string; conferido: boolean; conferidoEm?: string; destaque?: string; versao?: string }` | conferido ("trecho achado no texto"), não achado (erro), não conferido (base indisponível: a refazer) | Mostrar a fonte literal de um parâmetro do cadastro ou de uma citação de minuta. Trecho entre aspas tipográficas, em `<blockquote cite>`, com o documento e o dispositivo. | TL-06, TL-08, painel de origem em TL-04 e TL-05 |
| CMP-05 | `OrigemDoNumero` | `{ numero: NumeroComOrigem; formato?: "numero" \| "percentual" \| "prazo"; children?: ReactNode }` | fechado, aberto (painel), origem indisponível | Envolver todo número de domínio. Renderiza o número como botão sem aparência de botão (sublinhado pontilhado); Enter ou clique abre o painel lateral (UX-LAY-07) com a origem. Série paga mostra "série paga: uso restrito ao processo" (RNF-04). | todas as telas com números |
| CMP-06 | `LinhaDoTempoMarcos` | `{ marcos: { id: string; nome: string; data?: string; situacao: "feito" \| "atual" \| "previsto" \| "atrasado"; dono: Unidade; peca?: { nome: string; href: string }; prazo?: { limite: string; unidade: UnidadePrazo; base: string } }[]; orientacao?: "vertical" \| "horizontal" }` | feito, atual, previsto, atrasado; marco sem data ("data não registrada") | Linha do tempo do ciclo, do protocolo ao encerramento. Lista ordenada (`<ol>`); o marco atual leva `aria-current="step"`. Horizontal só em ≥ 1280 px. | TL-02, TL-07 (resumo), TL-03 (visão da concessionária) |
| CMP-07 | `PrazoBadge` | `{ limite: string; unidade: UnidadePrazo; restante: number; base: string; regra?: string }` | no prazo (> 5 dias, info), perto (≤ 5 dias, aviso), vence hoje (aviso), vencido (erro), cumprido (ok) | Todo prazo. Texto: "vence em 3 du (12/12/2025)", "venceu há 2 du", "cumprido em 05/12/2025". `title` e painel dizem a base ("30 dias corridos do pleito, Lei 2.869/1997, art. 8º"). Limiares a confirmar com a regra de alerta de RF-PRZ-03. | TL-01, TL-02, TL-10, TL-11, TL-12 |
| CMP-08 | `DonoDaEtapa` | `{ unidade: Unidade \| null; pessoa?: string; desde: string; diasComDono: number }` | com dono, sem dono (erro: "sem unidade responsável") | Mostrar quem tem o ciclo agora e há quanto tempo. `unidade = null` nunca some: vira erro visível. O nome da pessoa só aparece para usuários internos. | TL-01, TL-02, TL-10 |
| CMP-09 | `FilaDeCiclos` | `{ ciclos: { id: string; contrato: string; concessionaria: string; vigencia: string; numeroSei?: string; situacao: string; dono: Unidade \| null; proximoPrazo?: PrazoBadgeProps; idade: number; erros: number; avisos: number }[]; filtros: FiltrosFila; aoFiltrar: (f: FiltrosFila) => void }` | lista, vazia, carregando, erro; filtrada | Lista de ciclos com situação, dono, prazo e idade. Usa CMP-13 por baixo, com colunas fixas. Ordem padrão: prazo mais próximo primeiro; vencidos no topo. | TL-01, TL-10 |
| CMP-10 | `ResumoCifras` | `{ itens: { rotulo: string; valor: number \| string; situacao?: Situacao; origem?: Origem; href?: string }[]; titulo?: string }` | normal, carregando (esqueleto) | Bloco de 2 a 6 cifras no topo da tela (UX-PRI-05). Cada cifra pode levar a um filtro do detalhe. Usa `<dl>`. | TL-01, TL-02, TL-04, TL-05, TL-12, TL-13, TL-14 |
| CMP-11 | `EditorMinuta` | `{ minuta: { id: string; peca: "parecer_tecnico" \| "parecer_juridico" \| "relatorio" \| "voto" \| "deliberacao"; versao: number; html: string }; citacoes: { id: string; documento: string; dispositivo: string; trecho: string; situacao: "verificada" \| "invalida" \| "nao_verificada" }[]; somenteLeitura: boolean; aoSalvar: (html: string) => Promise<void>; aoExportar: (formato: "docx" \| "pdf") => Promise<void> }` | edição, salvando, salvo, com citação inválida (exportar bloqueado até o revisor resolver), somente leitura | Revisão humana de minuta. Citação aparece como marca no texto (sublinhado + ícone + número), lista lateral de citações com CMP-04. Selo "Minuta — requer revisão". Registra cada edição (RF-MIN-05). Exportação em DOCX e PDF (RF-DOC-02). | TL-08 |
| CMP-12 | `UploadPacote` | `{ modo: "validacao_previa" \| "envio"; aceita: string[]; tamanhoMaximoMb: number; aoValidar: (arquivos: File[]) => Promise<ItemValidacaoExibicao[]>; aoEnviar: (arquivos: File[]) => Promise<{ recibo: string; sha256: Record<string, string> }> }` | vazio, arrastando, lendo, validado com erro, validado sem erro, enviando, enviado (recibo) | Envio do pacote do pleito ou da remessa de faturamento. Primeiro valida (mesmas regras, sem registro: RF-PLE-05) e mostra o resultado com CMP-02; "Enviar" só fica ativo depois da validação prévia. Mostra o SHA-256 calculado de cada arquivo (RF-PLE-01). Recusa arquivo com dado pessoal detectado (RNF-05). | TL-03, TL-12 |
| CMP-13 | `TabelaDados` | `{ colunas: ColumnDef<T>[]; dados: T[]; legenda: string; ordenacaoInicial?: SortingState; paginacao?: { tamanho: number }; vazio: ReactNode; carregando?: boolean }` (TanStack Table, genérico `T`) | normal, ordenada, paginada, vazia (CMP-15), carregando (CMP-16) | Toda tabela de dados. `<table>` com `<caption>`, `<th scope>`, `aria-sort`. Colunas numéricas alinhadas à direita com `tabular-nums`. No celular: rolagem horizontal **dentro** do contêiner com sombra indicativa, ou troca por lista de cartões quando a tabela tem até 4 colunas essenciais. | TL-01, TL-06, TL-07, TL-10 a TL-15 |
| CMP-14 | `GraficoIndicador` | `{ indicador: { id: string; nome: string; unidade: string }; serie: { periodo: string; valor: number }[]; linhaBase: { valor: number; origem: Origem }; metas: { fase: 1 \| 2 \| 3; valor: number }[]; tipo?: "linha" \| "barra" }` (Recharts) | com dados, sem medição ainda (só linha de base e metas), carregando | Indicadores I-P01. Linha de base e metas como linhas de referência rotuladas. Sempre acompanhado de tabela equivalente (botão "Ver como tabela") e de resumo em texto (`aria-describedby`). Cores só de tokens; série distinguida também por traço. | TL-13 |
| CMP-15 | `Vazio` | `{ titulo: string; descricao: string; acao?: { rotulo: string; href?: string; aoClicar?: () => void } }` | — | Lista ou área sem dados. Diz por que está vazio e o que fazer. Nunca "Nenhum registro". | todas |
| CMP-16 | `Carregando` | `{ rotulo: string; forma?: "esqueleto-tabela" \| "esqueleto-cartao" \| "linha" }` | — | Carregamento acima de 300 ms. Esqueleto com a forma do conteúdo; `role="status"` com o rótulo ("Carregando a fila de ciclos"). Validação longa (RNF-13: até 60 s) mostra a regra em curso. | todas |
| CMP-17 | `ErroComAcao` | `{ titulo: string; descricao: string; codigoRastreio?: string; acao: { rotulo: string; aoClicar: () => void }; acaoSecundaria?: { rotulo: string; href: string } }` | — | Falha de carga ou de ação. Diz o que falhou, o que já foi guardado e o que fazer ("Tentar de novo"). Mostra código de rastreio para o suporte, sem detalhe técnico. `role="alert"`. | todas |
| CMP-18 | `SemPermissao` | `{ perfilAtual: string; perfisComAcesso: string[]; acao?: { rotulo: string; href: string } }` | — | Rota que o perfil não pode abrir (HTTP 403). Diz que perfis abrem a tela e oferece voltar ao painel. Nunca mostra dado da tela por trás. | todas |
| CMP-19 | `CabecalhoSistema` | `{ usuario: { nome: string; perfil: string; unidade?: string }; alertas: number; aoAbrirMenu: () => void }` | desktop, celular (compacto), sem sessão (TL-16) | Cabeçalho de todas as telas (UX-LAY-02). | todas |
| CMP-20 | `MenuLateral` | `{ itens: { rotulo: string; href: string; icone: LucideIcon; tela: string; perfis: string[] }[]; atual: string; perfil: string }` | fixo, gaveta aberta, gaveta fechada | Navegação principal (UX-LAY-03). Itens filtrados pelo perfil. | todas, exceto TL-16 |
| CMP-21 | `Breadcrumb` | `{ itens: { rotulo: string; href?: string }[] }` | completo, compacto (celular) | UX-LAY-04. | todas, exceto TL-16 |
| CMP-22 | `ConfirmacaoAcao` | `{ titulo: string; consequencia: string; perfilQueDecide: string; rotuloConfirmar: string; exigeJustificativa?: boolean; aoConfirmar: (justificativa?: string) => Promise<void> }` | aberto, confirmando, erro | Toda ação irreversível ou que muda o ciclo (UX-PRI-01). Diálogo `role="dialog" aria-modal`, foco no primeiro campo, `Esc` cancela, botão de confirmar com o verbo da ação ("Devolver pleito", nunca "OK"). | TL-04, TL-08, TL-09, TL-11, TL-02 (encerrar) |
| CMP-23 | `Mensagem` | `{ tipo: "ok" \| "aviso" \| "erro" \| "info"; titulo: string; texto: ReactNode; fechavel?: boolean; persistente?: boolean }` | inline, toast | Retorno de ação (toast, 6 s, pausa no foco) e alerta inline na tela. Erro nunca some sozinho. Toast usa `role="status"`; erro usa `role="alert"`. Padrão "Mensagem" do DS. | todas |
| CMP-24 | `ListaVerificacao` | `{ itens: { id: string; texto: string; requisito?: string; situacao: Situacao; evidencia?: { rotulo: string; href: string } }[]; titulo: string }` | completa (todos ok), incompleta | Lista de verificação do encerramento (RF-PRZ-08) e checklist legal da minuta jurídica (RF-MIN-02). Item não ok bloqueia a ação ligada. | TL-02, TL-08, TL-09 |
| CMP-25 | `SeletorPerfil` | `{ perfis: { id: string; nome: string; unidade?: string }[]; aoEscolher: (id: string) => void }` | um perfil (pula a escolha), vários | Escolha de perfil depois da entrada, quando o usuário tem mais de um. | TL-16 |

## 6. Guia de mensagens

### 6.1 Tom e voz

| ID | Regra | Assim | Não assim |
|---|---|---|---|
| UX-MSG-01 | Frase curta, voz ativa, presente | "O índice refeito é 3,967%, igual ao declarado." | "Foi verificado que o índice encontra-se em conformidade." |
| UX-MSG-02 | Diga o número e a regra | "Meses informados o = out/2024, i = out/2025; a regra do contrato dá o = out/2024, i = out/2025." | "Período inválido." |
| UX-MSG-03 | Diga o que fazer e quem faz | "Informe a distribuidora, a regra de composição e a resolução da ANEEL usadas no IEE." | "Corrija os dados." |
| UX-MSG-04 | Trate a concessionária com formalidade neutra, sem culpa | "O pacote tem 1 pendência. Corrija e envie de novo." | "Você errou o pleito." |
| UX-MSG-05 | Sem jargão técnico nem inglês | "O arquivo não segue o layout 0.1: falta o campo vigência pretendida." | "Schema validation failed: 'vigencia_pretendida' is a required property." |
| UX-MSG-06 | O sistema não decide pelo humano | "Pronto para a decisão da CAPET." | "Pleito aprovado." |
| UX-MSG-07 | Verbo do botão = ação | "Devolver pleito", "Gerar ofício", "Exportar DOCX" | "OK", "Enviar" genérico, "Confirmar" sem objeto |
| UX-MSG-08 | Números em pt-BR com as casas da fonte | "1.222,36", "6,795%", "0,4925" | "1222.36", "6.795 %" |

### 6.2 Mensagens das regras V01 a V12

Partem das mensagens do validador de referência (`scripts/validar_pleito.py`) e do resultado do pleito de Paraty 2026
(`saida/levantamento/pleito/exemplo_paraty_2026.validacao.json`). A situação é a do oráculo; a tela só muda o texto
(formato pt-BR, mês por extenso abreviado, regra explicada). Campos entre chaves vêm do `ItemValidacao`.

| Regra | Situação | Mensagem de tela (modelo) | Exemplo real (Paraty 2026) | O que fazer (texto para a concessionária) |
|---|---|---|---|---|
| V01 | ok | Layout {versao} válido. | Layout 0.1 válido. | — |
| V01 | erro | Campo {campo}: {problema}. (uma linha por campo; tradução na tabela 6.3) | — | Corrija o campo no `pleito.json` e valide de novo. |
| V02 | ok | Todos os trechos do cadastro foram achados no contrato e nos aditivos. | idem | — |
| V02 | erro | A versão contratual {codigo} não está no cadastro do contrato {numero}. · Trechos não achados no texto: {versao}: {parametro}. | — | Use a versão contratual publicada no cadastro do contrato. (O trecho não achado é pendência do cadastro, não da concessionária: vai para PER-GCA.) |
| V02 | a refazer | Textos dos contratos indisponíveis: os trechos do cadastro não foram conferidos. A conferência será refeita quando a base voltar. | — | — (o oráculo dá "aviso"; ver ponto em aberto 6.7) |
| V03 | ok | {meses} meses de referência e {dias} dias entre {de} e {ate}. | — | — |
| V03 | aviso | {meses} meses de referência entre {de} e {ate}, mas só {dias} dias. A forma de contar o interstício (por mês de referência ou por dia) está em definição. | 12 meses de referência entre 12/01/2025 e 01/01/2026, mas só 354 dias. | Nada a corrigir agora; a agência decide a contagem. |
| V03 | erro | Só {meses} meses de referência entre {de} e {ate}; o contrato pede {n}. | — | Ajuste a vigência pretendida para respeitar o intervalo de {n} meses. |
| V04 | ok | Meses o = {o} e i = {i}, iguais aos da regra do contrato ({n}º mês anterior à vigência). | Meses o = out/2024 e i = out/2025, iguais aos da regra do 3º mês anterior. | — |
| V04 | erro | Meses informados o = {o}, i = {i}; a regra do contrato ({n} meses antes da vigência) dá o = {o_esp}, i = {i_esp}. | — | Use os meses de referência da regra do contrato. |
| V05 | ok | Componentes e códigos de série iguais aos do cadastro. | idem | — |
| V05 | erro | Componentes a mais ou a menos: {siglas}. Códigos de série diferentes do cadastro: {siglas}. | — | Use as siglas e os códigos publicados no cadastro do contrato. |
| V06 | ok | Séries mensais completas de {o} a {i}. | — | — |
| V06 | aviso | Séries só com as pontas, sem os meses intermediários: {siglas}. | Séries só com as pontas, sem os meses intermediários: IMO, IEE, IPA, IPQ, IPC, ICC. | Envie todos os meses de o até i no `series.csv`. |
| V06 | erro | {sigla}: faltam os meses o ou i na série. | — | Inclua os valores de {o} e {i} da série {sigla}. |
| V07 | ok | {sigla}: o = {o} e i = {i} achados em {serie} (consulta de {data}). | IPC: o = 761,643 e i = 789,092 achados em IPEADATA IGP12_IPC12. | — |
| V07 | aviso | {sigla}: valores achados em {serie}, mas {valores} vieram com menos de {casas} casas, arredondados em relação à série. | ICC: o = 1.149,17 e i = 1.222,36 achados em IPEADATA IGP12_INCC12, mas vieram com menos de 3 casas (a série publica 1.222,356). | Envie os valores como publicados pela fonte, sem arredondar. |
| V07 | erro | {sigla}: {valor} não foi achado em {serie} para {mes}. | — | Confira o valor na fonte e anexe a exportação da série. |
| V07 | a refazer | {fonte} indisponível em {data}: a conferência de {sigla} será refeita. Último cache: {data_cache}. | — | — |
| V08 | ok | {sigla} ({codigo}): {n} de 2 valores iguais aos de outros pleitos do mesmo mês. | IPA (1006819): 2 de 2 valores iguais aos de outros pleitos. | — |
| V08 | aviso | {sigla} ({codigo}): {n} de 2 valores iguais aos de outros pleitos; sem outro pleito do mesmo mês para comparar. | IMO (159401): 0 de 2 valores iguais; sem outro pleito do mesmo mês para comparar. | Anexe a exportação da série paga (evidência). |
| V09 | ok | Índice refeito {ir}% (arredondado {ir_r}%), igual ao declarado {decl}%. | Índice refeito 3,9669% (arredondado 3,967%), igual ao declarado 3,967%. | — |
| V09 | erro | Índice refeito {ir_r}% e declarado {decl}%: diferença de {dif} p.p., acima da tolerância de 0,01 p.p. | — | Refaça o índice com os pesos do cadastro e as casas do contrato. |
| V10 | ok | Total pela regra {regra}: {total}%; declarado {decl}%; parcela {n} do cronograma ({pct}%). | Total pela regra multiplicativa: 6,7949%; declarado 6,795%; parcela 2 do cronograma (2,72%). | — |
| V10 | erro | Realinhamento de {ref}: o cronograma dá {pct}%, o pleito declara {decl}. · Total pela regra {regra}: {total}%; declarado {decl}%. | — | Use a parcela do cronograma da versão contratual e a regra de combinação do contrato. |
| V11 | ok | Energia com distribuidora, composição e resoluções da ANEEL. | — | — |
| V11 | erro | Energia sem {lacunas}. | Energia sem distribuidora, sem regra de composição e sem resolução da ANEEL. | Informe no `energia.csv` a distribuidora, a regra de composição (TUSD, TE, bandeira, tributos) e a resolução da ANEEL de cada valor. |
| V11 | a refazer | Base da ANEEL indisponível em {data}: a conferência da energia será refeita. | — | — |
| V12 | ok | {n} tarifas fecham com vigente × (1 + total). | — | — |
| V12 | aviso | Pleito sem tabela tarifária vigente e proposta. | idem | Envie o `tabela_tarifaria.csv`. |
| V12 | erro | Tarifas que não fecham com vigente × (1 + total): {categorias}. | — | Refaça a tabela proposta com o total e as casas do pleito. |

Resumo do resultado (CMP-10 em TL-04):
- Com erro: "{n} conferências ok · {a} avisos · {e} erro(s): devolver para complementação." Paraty 2026: "10
  conferências ok · 5 avisos · 1 erro: devolver para complementação."
- Sem erro: "{n} conferências ok · {a} avisos: segue para a CAPET."
- Com "a refazer" e sem erro: "… · {r} a refazer: segue para a CAPET; a conferência será refeita quando a fonte voltar."

### 6.3 Tradução dos erros de layout (V01)

O validador de JSON Schema devolve mensagens em inglês. A tela traduz pela palavra-chave do erro; `{campo}` é o
caminho em linguagem de tela (ex.: `componentes/2/serie` → "componente IPA, série").

| Palavra-chave | Mensagem |
|---|---|
| `required` | Falta o campo {campo}. |
| `type` | O campo {campo} deve ser {tipo_esperado} (texto, número, lista). |
| `format` / `pattern` | O campo {campo} está fora do formato: use {formato} (ex.: data aaaa-mm-dd, mês aaaa-mm). |
| `enum` / `const` | O campo {campo} só aceita: {valores}. |
| `minItems` | O campo {campo} precisa de pelo menos {n} item(ns). |
| `additionalProperties` | O campo {campo} não faz parte do layout 0.1. |
| outra | O campo {campo} não segue o layout 0.1. (registrar a palavra-chave para tradução) |

### 6.4 Erros de sistema

| ID | Situação | Mensagem | Ação |
|---|---|---|---|
| MSG-ERR-01 | Falha ao carregar dados | Não foi possível carregar {o quê}. Nada foi perdido. | Tentar de novo |
| MSG-ERR-02 | Falha ao salvar | Não foi possível salvar {o quê}. Suas alterações continuam na tela. | Tentar de novo · Copiar texto |
| MSG-ERR-03 | Sessão expirada (RNF-10) | Sua sessão terminou por inatividade. Entre de novo para continuar; o rascunho foi guardado. | Entrar |
| MSG-ERR-04 | Sem permissão (HTTP 403) | Esta tela é dos perfis {perfis}. Seu perfil atual é {perfil}. | Voltar ao painel · Trocar perfil |
| MSG-ERR-05 | Ciclo não encontrado (HTTP 404) | Não achamos o ciclo {numero}. Confira o número SEI ou o contrato. | Buscar ciclo |
| MSG-ERR-06 | Conflito de edição (HTTP 409) | {perfil} alterou esta minuta às {hora}. Compare as versões antes de salvar. | Comparar versões |
| MSG-ERR-07 | Fonte externa fora do ar (RNF-06) | {fonte} não respondeu às {hora}. O sistema usou o cache de {data} e marcou a conferência como "a refazer". | Ver séries externas (TL-14) |
| MSG-ERR-08 | Arquivo com dado pessoal (RNF-05) | O arquivo {arquivo} parece ter dado pessoal ({tipo}: CPF, nome de usuário, endereço). O layout não aceita dado pessoal. O arquivo foi recusado e não foi guardado. | Escolher outro arquivo |
| MSG-ERR-09 | Arquivo fora do formato | O arquivo {arquivo} não é {formato}. O pacote aceita {lista}. | Escolher outro arquivo |
| MSG-ERR-10 | Arquivo grande demais | O arquivo {arquivo} tem {tamanho}; o limite é {limite}. | Escolher outro arquivo |
| MSG-ERR-11 | Exportação falhou | Não foi possível gerar o {formato} da peça. A minuta continua salva. | Tentar de novo |

### 6.5 Confirmações (CMP-22)

| ID | Ação | Título | Consequência (texto do diálogo) | Botão |
|---|---|---|---|---|
| MSG-CNF-01 | Devolver pleito (UC-04) | Devolver o pleito de {concessionaria} {ano}? | A concessionária recebe a lista de {n} pendência(s) e a minuta do ofício de complementação vai para assinatura no SEI. O ciclo fica "aguardando a concessionária". | Devolver pleito |
| MSG-CNF-02 | Enviar pleito (UC-01) | Enviar o pleito para a AGENERSA? | O pacote será registrado com os hashes abaixo e não poderá ser alterado; correções exigem novo envio. | Enviar pleito |
| MSG-CNF-03 | Exportar minuta para o SEI | Exportar a minuta revisada? | A versão {v} será exportada em {formato} para assinatura no SEI. O sistema não assina nem protocola. | Exportar {formato} |
| MSG-CNF-04 | Publicar nova versão contratual (UC-06) | Publicar a versão {codigo}? | Ciclos com vigência a partir de {data} passam a usar esta versão. Ciclos já apurados mantêm a versão que usaram. | Publicar versão |
| MSG-CNF-05 | Registrar marco | Registrar {marco} em {data}? | Os prazos ligados a este marco passam a contar desta data. | Registrar marco |
| MSG-CNF-06 | Encerrar ciclo (RF-PRZ-08) | Encerrar o ciclo {ciclo}? | A lista de verificação está completa. O termo de encerramento vai para assinatura no SEI; o arquivamento é feito no SEI. | Encerrar ciclo |
| MSG-CNF-07 | Incluir na pauta (UC-13) | Incluir {ciclo} na pauta de {data}? | O gabinete do relator e as partes são avisados da data da sessão. | Incluir na pauta |
| MSG-CNF-08 | Desativar usuário (UC-19) | Desativar {usuario}? | A pessoa perde o acesso agora. A trilha de auditoria mantém o que ela fez. | Desativar usuário |

Retorno depois da ação (CMP-23, toast): "Pleito devolvido. Ofício de complementação pronto para assinatura." · "Marco
registrado. Prazo da Procuradoria conta a partir de 05/12/2025."

### 6.6 Alertas de prazo (RF-PRZ-03)

| ID | Momento | Texto (tela e correio, INT-08) | Destinatário |
|---|---|---|---|
| MSG-PRZ-01 | Antes do vencimento (limiar a definir em RF-PRZ-03) | {ato} de {ciclo} vence em {n} {unidade} ({data}). Base: {regra}. | dono da etapa |
| MSG-PRZ-02 | No dia | {ato} de {ciclo} vence hoje. | dono da etapa e chefia |
| MSG-PRZ-03 | Vencido | {ato} de {ciclo} venceu há {n} {unidade}. {consequencia} | dono, chefia e PER-SEC |
| MSG-PRZ-04 | Diligência vencida (RF-PRZ-04) | A diligência a {destinatario} venceu em {data} sem resposta. A reiteração está pronta para assinatura. | PER-REL ou PER-SEC (quem diligenciou) |
| MSG-PRZ-05 | Razões finais vencidas (RF-PRZ-06) | O prazo de razões finais de {ciclo} venceu. O ciclo entrou na pauta de {data}. | PER-SEC, PER-REL |
| MSG-PRZ-06 | Prazo recursal vencido (RF-PRZ-07, RF-PRZ-08) | O prazo recursal de {ciclo} venceu sem recurso registrado. A certidão de ausência de recurso está pronta para conferência. | PER-SEC |
| MSG-PRZ-07 | Ciclo sem dono (RF-PRZ-02) | {ciclo} está sem unidade responsável desde {data}. Atribua um dono. | PER-SEC e gestão |
| MSG-PRZ-08 | Data-base próxima (RF-CAD-04) | A data-base de {contrato} é {data}. A instrução do reajuste deve começar até {data_inicio}. | PER-GCA, PER-ANA |

Prazos que a tela explica com a base legal (de `insumos/mapeamento/normas_P01.json`):

| Prazo | Valor | Base | Unidade |
|---|---|---|---|
| Pronunciamento sobre o pleito (R-P01-05) | 30 dias do recebimento | Lei estadual 2.869/1997, art. 8º, parágrafo único | dias corridos |
| Parecer da Procuradoria (R-P01-07, RF-PRZ-05) | 15 dias do parecer da CAPET | Regimento Interno, art. 17, VI | dias corridos |
| Razões finais (R-P01-04) | até 10 dias para manifestação | Regimento Interno, art. 49, § 2º; Lei 5.427/2009, art. 40 | dias, a confirmar (o requisito anota dias úteis) |
| Deliberação (R-P01-06) | até 40 dias do ofício de razões finais | Lei 5.427/2009, art. 45; Regimento, art. 49 | dias corridos |
| Início da conferência das faturas (R-P01-16) | até 90 dias da publicação | IN 31/2012, § 2º; IN 141/2025, § 4º | dias corridos |
| Vigência da nova tarifa (R-P01-09) | 30 dias depois de tornada pública | Lei federal 11.445/2007, art. 39 | dias corridos |
| Certidão antes do encerramento (R-P01-17) | ato obrigatório | Resolução CODIR 787/2022, art. 1º, parágrafo único | — |

### 6.7 Glossário de termos de tela

Use estes rótulos. A coluna "Evite" lista o que a IA de desenvolvimento tende a escrever.

| Rótulo de tela | Significado (seção 7 do documento-base) | Evite |
|---|---|---|
| Ciclo de reajuste, ciclo | Um reajuste anual de um contrato | processo (sem qualificar), caso, ticket |
| Pleito | Pedido da concessionária no layout | solicitação, requisição, submissão |
| Pacote | Conjunto de arquivos do pleito | upload, lote |
| Validação prévia | Conferência sem registro antes do envio (RF-PLE-05) | pré-checagem, teste |
| Resultado da validação | Lista V01 a V12 | relatório de erros, log |
| Situação | ok, aviso, erro, a refazer | status, estado |
| Pendência | Erro a corrigir pela concessionária | issue, bug |
| Devolver para complementação | UC-04 | rejeitar, reprovar |
| Versão contratual | Regras vigentes a partir de um ato | revisão, release |
| Parâmetro / fonte da regra / trecho | Valor do cadastro e o texto que o sustenta | config, setting |
| Mês o, mês i | Meses de referência | data inicial/final |
| Índice de reajuste (IR) | Resultado da fórmula | taxa, fator |
| Realinhamento | Parcela adicional do aditivo | ajuste, extra |
| Total | Percentual aplicado à tabela | resultado final |
| Apuração, memória de cálculo | Resultado do motor e sua demonstração | cálculo automático |
| Série, valor da série, consulta | Valores mensais de índice e quando foram lidos | dados, feed |
| Marco | Evento datado do ciclo | evento, milestone |
| Prazo, vence em, venceu há | Intervalo contado de um marco | deadline, SLA |
| Dono, unidade responsável | Quem tem a etapa | assignee, responsável genérico |
| Minha fila | Ciclos e prazos do meu perfil (TL-10) | inbox, tarefas |
| Peça | Documento do processo | arquivo, doc |
| Minuta — requer revisão | Peça gerada para revisão humana | rascunho automático, documento final |
| Citação verificada / citação inválida / não verificada | Situação da citação contra a fonte | referência OK |
| Remessa de faturamento | Arquivo periódico de faturas | carga, import |
| Divergência | Fatura que não fecha com a tabela homologada | erro de fatura |
| a refazer | Conferência pendente porque a fonte estava fora | erro, falha |
| exemplo | Dado ilustrativo | mock, fake, teste |
| hipótese até a calibração | Hora estimada não calibrada | estimativa precisa |

Pontos em aberto deste guia:
- V02 com a base de textos indisponível: o oráculo dá "aviso"; a tela propõe "a refazer" por coerência com RNF-06.
  Decidir com quem escreve as regras e os testes.
- Limiares de "perto do vencimento" (5 dias) e regra de alerta: confirmar em RF-PRZ-03.
- Unidade do prazo de razões finais (dias úteis ou corridos).

## 7. Acessibilidade (WCAG 2.2 AA e eMAG 3.1)

### 7.1 Regras gerais

| ID | Regra | Critério |
|---|---|---|
| UX-A11Y-01 | `lang="pt-BR"` no `<html>`; título único por página (UX-LAY-08) | 3.1.1, 2.4.2; eMAG 3.1, 1.1 |
| UX-A11Y-02 | Landmarks: `header`, `nav` (menu e breadcrumb com `aria-label` distintos), `main`, `footer`; um `h1` por tela, hierarquia sem saltos | 1.3.1, 2.4.6; eMAG 1.3 |
| UX-A11Y-03 | Barra de acessibilidade com saltos e atalhos `Alt+1` a `Alt+4`; página "Acessibilidade" no rodapé | 2.4.1; eMAG 1.5, 1.9 |
| UX-A11Y-04 | Tudo operável por teclado, na ordem visual; nenhum atalho de uma letra só | 2.1.1, 2.1.2, 2.1.4, 2.4.3 |
| UX-A11Y-05 | Foco sempre visível (tracejado 4 px `--foco`, afastado 4 px) e nunca encoberto pelo cabeçalho fixo (`scroll-padding-top` = altura do cabeçalho + 8 px) | 2.4.7, 2.4.11 |
| UX-A11Y-06 | Contraste de texto ≥ 4,5:1 (≥ 3:1 para texto ≥ 24 px ou 18,66 px bold); componentes e foco ≥ 3:1 (tabela 3.2) | 1.4.3, 1.4.11 |
| UX-A11Y-07 | Situação nunca só por cor (UX-PRI-03) | 1.4.1 |
| UX-A11Y-08 | Reflow a 320 px CSS (zoom de 400% em 1280 px) sem rolagem horizontal da página; tabelas rolam dentro do próprio contêiner | 1.4.10 |
| UX-A11Y-09 | Texto aumenta a 200% sem perda; espaçamento de texto ajustável sem corte | 1.4.4, 1.4.12 |
| UX-A11Y-10 | Alvo de toque ≥ 24 × 24 px (padrão do sistema: 40 px, botão médio do DS) | 2.5.8 |
| UX-A11Y-11 | Rótulo visível em todo campo (`<label for>`), instrução antes do campo, erro ligado ao campo por `aria-describedby` e `aria-invalid`, resumo de erros no topo do formulário com links para os campos | 1.3.1, 3.3.1, 3.3.2, 3.3.3; eMAG 6.2, 6.5 |
| UX-A11Y-12 | Mensagens de situação anunciadas (`role="status"`; erro com `role="alert"`), sem mover o foco | 4.1.3 |
| UX-A11Y-13 | Entrada sem teste cognitivo (sem CAPTCHA de texto); colar senha permitido; gerenciador de senhas funciona | 3.3.8 |
| UX-A11Y-14 | Dado já informado não é pedido de novo no mesmo fluxo (ex.: contrato e versão da validação prévia vão para o envio) | 3.3.7 |
| UX-A11Y-15 | Ajuda e contato no mesmo lugar em todas as telas (rodapé) | 3.2.6 |
| UX-A11Y-16 | Movimento reduzido respeitado; nenhum conteúdo pisca | 2.3.1, 2.3.3 (recomendado) |
| UX-A11Y-17 | Sessão expira com aviso 2 min antes e opção de estender; rascunho guardado | 2.2.1; RNF-10 |
| UX-A11Y-18 | Teste automático com `axe` (Vitest e Playwright) em todas as telas e estados; teste manual com NVDA + Firefox e teclado a cada release | eMAG 3.1 (avaliação) |

### 7.2 Por componente

| Componente | Teclado | Leitor de tela | Outros critérios |
|---|---|---|---|
| CMP-01 SituacaoChip | não focável (só texto) | lê "Situação: aviso" (texto visível; ícone `aria-hidden`) | 1.4.1, 1.4.3 |
| CMP-02 LinhaRegraValidacao | botão de expandir com `aria-expanded` e `aria-controls`; Enter/Espaço | lê "V11, erro, Energia sem distribuidora…"; detalhe numa região ligada | 1.3.1, 4.1.2 |
| CMP-03 TabelaMemoriaCalculo | Tab percorre os números com origem; setas não são capturadas | `<caption>` "Memória de cálculo, out/2024 a out/2025"; `<th scope="col/row">`; IR e total em `<tfoot>` | 1.3.1; números com `tabular-nums` |
| CMP-04 TrechoCitado | link do documento focável | `<blockquote cite>` com `<cite>`; situação da conferência em texto | 1.3.1 |
| CMP-05 OrigemDoNumero | é `<button>`; Enter abre o painel, foco vai para o título do painel, `Esc` fecha e devolve o foco ao número | `aria-haspopup="dialog"`; nome acessível "6,795%, ver origem" | 2.4.3, 4.1.2, 1.4.13 (painel não some com o mouse) |
| CMP-06 LinhaDoTempoMarcos | itens com link de peça focáveis | `<ol>`; marco atual com `aria-current="step"`; situação e data em texto | 1.3.1 |
| CMP-07 PrazoBadge | não focável; base do prazo também no painel do ciclo | texto completo ("vence em 3 dias úteis, em 12/12/2025") | 1.4.1; nunca só "3d" |
| CMP-08 DonoDaEtapa | — | "Dono: CAPET desde 03/12/2025 (2 du)" | — |
| CMP-09 FilaDeCiclos | filtros antes da tabela; linha inteira não é clicável: o nome do ciclo é o link | resultado do filtro anunciado ("12 ciclos") por `role="status"` | 2.4.4, 4.1.3 |
| CMP-10 ResumoCifras | cifras com link focáveis | `<dl>` com `<dt>` rótulo e `<dd>` valor | 1.3.1 |
| CMP-11 EditorMinuta | barra de ferramentas com `role="toolbar"` e setas; `Ctrl+S` salva; citação marcada focável, Enter abre o trecho; `F6` alterna texto e lista de citações | marcas de citação com `aria-describedby` para a situação; área de edição com rótulo "Texto da minuta do parecer técnico" | 2.1.1, 3.3.1, 4.1.2 |
| CMP-12 UploadPacote | área de soltar é também `<input type="file">` com rótulo; nenhum recurso só por arrastar | progresso com `role="progressbar"` e texto; resultado anunciado | 2.5.7 (alternativa ao arrastar), 4.1.3 |
| CMP-13 TabelaDados | cabeçalho ordenável é `<button>` com `aria-sort` no `<th>`; paginação com botões rotulados | `<caption>` obrigatório; contêiner rolável com `tabindex="0"`, `role="region"` e `aria-label` | 1.3.1, 1.4.10, 2.1.1 |
| CMP-14 GraficoIndicador | "Ver como tabela" focável antes do gráfico | gráfico com `role="img"` e resumo textual; tabela equivalente | 1.1.1, 1.4.1, 1.4.11 |
| CMP-15 Vazio | ação focável | título em `h2` | — |
| CMP-16 Carregando | — | `role="status"` com o rótulo; `aria-busy="true"` na região | 4.1.3 |
| CMP-17 ErroComAcao | foco vai para o título do erro quando a falha é da carga da tela | `role="alert"` | 3.3.1, 4.1.3 |
| CMP-18 SemPermissao | foco no `h1` | `h1` "Sem permissão para esta tela" | — |
| CMP-20 MenuLateral | gaveta com foco preso, `Esc` fecha, foco volta ao botão `≡` | `aria-expanded` no botão; `aria-current="page"` | 2.4.3, 2.1.2 |
| CMP-22 ConfirmacaoAcao | foco no primeiro elemento; Tab circula no diálogo; `Esc` cancela | `role="dialog"`, `aria-modal`, `aria-labelledby`, `aria-describedby` | 2.4.3, 4.1.2 |
| CMP-23 Mensagem | toast pausa com foco ou mouse; botão fechar rotulado | `role="status"`; erro `role="alert"` | 2.2.1, 4.1.3 |

## 8. Responsividade

| Faixa | Largura | Layout |
|---|---|---|
| Celular | < 576 px (projeto a partir de 320 px; teste em 375 px) | uma coluna; menu em gaveta; breadcrumb compacto; resumo em grade de 2 colunas; tabelas com rolagem interna ou cartões; ação primária fixa no rodapé da tela quando houver formulário |
| Celular grande e tablet | 576 a 991 px | uma coluna; menu em gaveta; resumo em 3 colunas |
| Desktop (principal) | 992 a 1279 px | menu lateral fixo; área de trabalho de uma coluna |
| Desktop largo | ≥ 1280 px | menu lateral fixo; detalhe em duas colunas quando a tela pede (ex.: texto da minuta + citações); linha do tempo horizontal |

Telas que **precisam** funcionar bem no celular (uso real fora do gabinete):
- TL-03 Envio do pleito e validação prévia e TL-04 Resultado da validação, para PER-CON;
- TL-12 Remessa de faturamento e divergências (visão PER-CON);
- TL-10 Prazos e alertas, para todos os internos, e o sino de alertas do cabeçalho;
- TL-16 Entrada.

As demais telas (TL-05, TL-06, TL-08, TL-11, TL-13, TL-15) devem abrir e ser legíveis no celular sem rolagem
horizontal da página, mas a edição (cadastro, minuta) é feita no desktop; no celular elas abrem em modo de leitura
com o aviso "Para editar, use um computador".
