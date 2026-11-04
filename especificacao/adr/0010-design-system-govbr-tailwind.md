# ADR-0010: Design System gov.br sobre Tailwind v4

- **Situação:** aceita
- **Data:** 2026-10-31
- **Origem:** RNF-08 (WCAG 2.2 AA e eMAG), RNF-09; briefing (interface no padrão digital de governo); `10_UX_UI.md`
  (inventário de componentes e tokens).

## Contexto

O sistema é usado por servidores e por concessionárias e precisa seguir o padrão digital de governo. A stack usa
Tailwind v4 com tokens em `@theme` (ADR-0001). O Design System gov.br publica fundamentos (cores, tipografia,
espaçamento, grade, elevação) e componentes com CSS próprio. Misturar o CSS pronto com o Tailwind cria dois sistemas
de estilo que brigam pelo reset e pela especificidade.

## Decisão

1. **Fundamentos do gov.br viram tokens Tailwind.** Cores, tipografia, espaçamentos, raios, sombras e pontos de quebra
   do Design System gov.br são declarados no bloco `@theme` de `src/app/globals.css`, copiado de `10_UX_UI.md` §3.3.
   Os valores ficam só ali.
2. **Componentes próprios no padrão gov.br.** Cada componente do inventário de `10_UX_UI.md` §5 é implementado uma vez
   em `src/components/reajusta/`, com cva para as variantes e cn para compor classes. Ele segue a anatomia, os estados
   e o comportamento descritos pelo gov.br. Telas só usam componentes do inventário.
3. **Não importar o CSS do pacote do gov.br** (`@govbr-ds/core`). Ele fica como referência visual e de comportamento.
4. **Fonte** indicada pelo Design System gov.br, auto-hospedada em `public/fontes/`, sem CDN externo.
5. **Ícones** de lucide-react, com o mapeamento para os ícones do gov.br listado em `10_UX_UI.md`.
6. **Acessibilidade é critério de aceite**:
   - contraste dos tokens conferido;
   - foco visível;
   - navegação por teclado;
   - rótulos e mensagens associados aos campos;
   - teste automático com axe (Testing Library nos componentes, @axe-core/playwright nas telas dos fluxos e2e), sem
     violação WCAG 2.2 AA de impacto sério ou crítico (`12_TESTES.md` §1.1).
7. **Tema** claro como padrão; alto contraste por next-themes, se `10_UX_UI.md` o incluir.

## Alternativas consideradas

- **CSS do `@govbr-ds/core` direto.** Fiel ao padrão, mas conflita com o Tailwind e com React 19 (componentes em web
  components e JavaScript próprio). Rejeitada.
- **shadcn/ui ou MUI com tema.** Rápido, mas a aparência e o comportamento padrão não são os do gov.br, e o tema
  vira sobrescrita sem fim. Rejeitada; a técnica de cva + cn do shadcn é aproveitada, não a aparência.
- **Escrever estilo por tela.** Gera telas inconsistentes. Rejeitada.

## Consequências

- Positivas: um sistema de estilo só; telas consistentes entre si e com o serviço público.
- Negativas: os componentes são escritos e mantidos pela equipe. O inventário de `10_UX_UI.md` limita o trabalho ao
  que as telas TL-01 a TL-16 usam.
- A IA de desenvolvimento não cria componente fora do inventário. Se faltar um, ela para e pede
  (`AGENTS_DESENVOLVIMENTO.md` §4).
