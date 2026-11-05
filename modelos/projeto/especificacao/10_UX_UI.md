# 10. Guia de UX/UI

<!-- COMO PREENCHER: este guia deriva dos casos de uso que têm pessoa como ator (04), dos perfis e das jornadas (02) e
da lista de telas do 01. O passo a passo está no capítulo 03 da metodologia, §3.10
(docs/metodologia/03_PLANEJAMENTO_DA_ESPECIFICACAO.md); a convenção de identificadores, no §2 do mesmo capítulo.
Escreva os princípios primeiro, depois escolha o design system, meça o contraste dos tokens com script, monte o
inventário de componentes (CMP-01 em diante) olhando as telas do 11 e só então escreva as mensagens.
Pronto quando: todo componente usado nas telas do 11 está no inventário; todo par de cor usado em texto ou em
elemento de interface tem a razão de contraste medida e acima do mínimo; o guia de mensagens cobre erro, confirmação
e alerta de todo caso de uso com pessoa; as regras de acessibilidade citam o critério WCAG 2.2 ou eMAG 3.1.
Referência de formato: exemplo/reajusta/especificacao/10_UX_UI.md. Ele serve só para ver estrutura, seções e nível
de detalhe. Não copie frase, componente, mensagem, rótulo nem termo dele: o domínio do seu sistema é outro, e o
conferidor acusa termo e trecho copiados (C03 e C04). -->

Este guia mantém as telas de {{Nome do sistema}} coerentes entre si e com o design system adotado. Ele se aplica a toda
tela da lista do `01_VISAO_ESCOPO.md`; cada uma tem sua seção no documento 11 ([`11_TELAS.md`](11_TELAS.md)). Quem
usa cada tela, e em que ordem, está no documento 02 ([`02_PERFIS_E_JORNADAS.md`](02_PERFIS_E_JORNADAS.md)). Para ver
as telas funcionando em baixa fidelidade, abra [`prototipos/wireframes.html`](prototipos/wireframes.html).

Regras de uso deste guia, para quem desenvolve:

- Antes de criar um componente, procure no inventário da seção 5. Componente novo só entra com identificador novo,
  registrado aqui antes do primeiro uso.
- Cor, fonte, espaçamento, raio e sombra vêm só dos tokens da seção 3. Valor solto no código de uma tela é defeito.
- Todo texto de tela vem do guia de mensagens da seção 6 e do glossário de tela (seção 6.6).

## 1. Princípios

Cada princípio diz o que a tela faz, de forma verificável, e de onde ele vem (requisito, meta, norma ou dor de um
perfil). Princípio sem origem é gosto pessoal e não entra. Entre três e oito princípios costumam bastar.

| ID | Princípio | O que a tela faz | Origem |
|---|---|---|---|
| PRI-01 | {{Nome curto do princípio}} | {{Comportamento observável, por exemplo: toda ação que muda a situação do objeto do processo pede confirmação e mostra quem decide}} | {{RNF, meta, norma ou dor de um perfil que o justifica}} |
| PRI-02 | {{Nome curto do princípio}} | {{Comportamento observável}} | {{Origem}} |

Princípios que quase todo sistema de governo adota (mantenha, ajuste ou retire, dizendo por quê):

- **Situação nunca só por cor.** Toda situação aparece com cor, ícone e palavra (WCAG 1.4.1).
- **A pessoa decide; o sistema prepara.** A tela não anuncia como decidido o que depende de ato humano: diz "pronto
  para revisão", "aguarda decisão de {{Perfil}}".
- **Resumo antes do detalhe.** A tela abre com o que a pessoa precisa para agir; a lista e o detalhe vêm abaixo.
- **Dado de exemplo nunca parece dado real.** Protótipo e ambiente de treinamento marcam o dado ilustrativo como
  "exemplo".

## 2. Base: design system adotado

| Item | Escolha | Observação |
|---|---|---|
| Design system | {{Padrão Digital de Governo (gov.br/ds) ou o padrão do órgão}} | No governo federal, o padrão gov.br é a referência. Órgão estadual ou municipal usa o próprio, ou o gov.br nos fundamentos com a marca do órgão. |
| Versão consultada | {{Versão do pacote ou da documentação, com a data da consulta}} | Os valores da seção 3 são conferidos nesta versão. |
| Forma de uso | {{Pacote oficial de CSS e componentes, ou tokens reproduzidos na biblioteca de interface da stack}} | Diga o que se usa do pacote e o que se reimplementa. |
| Marca no cabeçalho | {{Marca do órgão e nome do sistema, ou marca gov.br}} | Siga a regra de identidade visual do órgão. |
| Ícones | {{Biblioteca de ícones}} | Ícone que comunica situação tem texto ao lado; ícone decorativo leva `aria-hidden="true"`. |
| Fontes | {{Família tipográfica e forma de servir os arquivos}} | Prefira servir a fonte pelo próprio sistema, sem depender de rede externa em produção. |
| Decisão registrada em | {{Número do ADR que registra a escolha do design system}} | A escolha tem alternativa real, por isso vira ADR (capítulo 03, §3.7). |

Marque cada valor da seção 3 como **confirmado** (lido na documentação ou no pacote do design system, na versão
acima) ou **a conferir** (extensão do sistema ou valor não achado no design system).

## 3. Tokens

### 3.1 Valores

As telas usam só nomes semânticos (`texto`, `fundo`, `interativo`, `erro-texto`...). O valor de cada nome vem daqui.

| Grupo | Token semântico | Token do design system | Valor | Uso | Situação |
|---|---|---|---|---|---|
| Cor de texto | `texto` | {{Token de origem}} | {{Cor em hexadecimal}} | texto principal | {{Confirmado ou a conferir}} |
| Cor de texto | `texto-2` | {{Token de origem}} | {{Cor em hexadecimal}} | texto secundário, metadado | {{Confirmado ou a conferir}} |
| Fundo | `fundo`, `superficie` | {{Token de origem}} | {{Cor em hexadecimal}} | fundo da página e dos cartões | {{Confirmado ou a conferir}} |
| Interação | `interativo` | {{Token de origem}} | {{Cor em hexadecimal}} | link, botão primário, item de menu atual | {{Confirmado ou a conferir}} |
| Foco | `foco` | {{Token de origem}} | {{Cor em hexadecimal; estilo, largura e afastamento do contorno}} | contorno de todo elemento focável | {{Confirmado ou a conferir}} |
| Borda | `borda` | {{Token de origem}} | {{Cor em hexadecimal}} | borda de campo e de componente | {{Confirmado ou a conferir}} |
| Situação | `ok-*`, `aviso-*`, `erro-*`, `info-*` | {{Tokens de origem}} | {{Valores de fundo, texto e borda de cada situação}} | chip, faixa e mensagem | {{Confirmado ou a conferir}} |
| Tipografia | `fonte`, escala | {{Tokens de origem}} | {{Família e tamanhos da escala, em rem}} | todo texto | {{Confirmado ou a conferir}} |
| Espaço | escala de espaçamento | {{Tokens de origem}} | {{Passo da escala, por exemplo múltiplos de 4 px}} | margem e espaçamento | {{Confirmado ou a conferir}} |
| Superfície | raio, sombra | {{Tokens de origem}} | {{Valores}} | campo, cartão, diálogo | {{Confirmado ou a conferir}} |
| Controle | altura de botão e campo | {{Tokens de origem}} | {{Alturas pequena, média e grande}} | botões e campos | {{Confirmado ou a conferir}} |
| Grade | quebras de layout | {{Tokens de origem}} | {{Larguras de quebra em px}} | responsividade (seção 8) | {{Confirmado ou a conferir}} |
| Tema escuro | {{Se houver: os mesmos tokens com valores do tema escuro}} | {{Tokens de origem}} | {{Valores}} | tema escuro | {{Confirmado ou a conferir}} |

Coloque abaixo o bloco de tokens pronto para a stack (por exemplo, as variáveis CSS ou o tema da biblioteca de
interface), com os mesmos nomes desta tabela:

```css
/* {{Bloco de tokens na sintaxe da stack escolhida no 05}} */
:root {
  --texto: #000000;      /* troque pelos valores da tabela 3.1 */
  --fundo: #ffffff;
}
```

### 3.2 Contraste medido (WCAG 2.2, critérios 1.4.3 e 1.4.11)

Mínimos que cada par tem de atingir:

| O que | Mínimo | Critério |
|---|---|---|
| Texto normal | 4,5:1 | 1.4.3 (AA) |
| Texto grande (a partir de 24 px, ou 18,66 px em negrito) | 3:1 | 1.4.3 (AA) |
| Componente de interface e estado (borda de campo, contorno de foco, ícone que informa, marca de seleção) | 3:1 contra as cores vizinhas | 1.4.11 (AA) |
| Texto de elemento desabilitado e logotipo | sem mínimo | 1.4.3 (exceções) |

Uma linha por par realmente usado nas telas, em cada tema. A razão é **medida por script**, nunca estimada a olho:

| Par (frente sobre fundo) | Razão medida | Mínimo | Critério | Uso |
|---|---|---|---|---|
| {{Cor da frente sobre cor do fundo, em hexadecimal}} | {{Razão com duas casas}} | {{Mínimo: 4,5 ou 3}} | {{Critério: 1.4.3 ou 1.4.11}} | {{Onde o par aparece}} |
| {{Cor da frente sobre cor do fundo, em hexadecimal}} | {{Razão com duas casas}} | {{Mínimo: 4,5 ou 3}} | {{Critério: 1.4.3 ou 1.4.11}} | {{Onde o par aparece}} |

Combinações proibidas (abaixo do mínimo, mas tentadoras): {{Lista dos pares que não podem ser usados, com a razão}}.

Como medir (fórmula de luminância relativa da WCAG 2.2):

```python
def luminancia(hexa: str) -> float:
    canais = [int(hexa.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

def contraste(frente: str, fundo: str) -> float:
    claro, escuro = sorted((luminancia(frente), luminancia(fundo)), reverse=True)
    return round((claro + 0.05) / (escuro + 0.05), 2)

print(contraste("#595959", "#ffffff"))  # 7.0
```

## 4. Layout das páginas

Desenhe a moldura comum a todas as telas e dê uma regra a cada região.

```
┌────────────────────────────────────────────────────────────────────┐
│ Barra de acessibilidade: ir para o conteúdo · menu · rodapé         │
├────────────────────────────────────────────────────────────────────┤
│ CABEÇALHO: {{Marca}} · {{Nome do sistema}}   [busca]   [perfil]     │
├───────────────┬────────────────────────────────────────────────────┤
│ MENU LATERAL  │ Trilha de navegação: Início › {{Seção}} › {{Tela}}   │
│ {{Item 1}}    │ Título da tela (h1)                 [ação principal] │
│ {{Item 2}}    │ Resumo                                              │
│ {{Item 3}}    │ ─────────────────────────────────────────────────── │
│               │ ÁREA DE TRABALHO: lista, formulário ou detalhe      │
├───────────────┴────────────────────────────────────────────────────┤
│ RODAPÉ: {{Órgão}} · versão · acessibilidade · privacidade           │
└────────────────────────────────────────────────────────────────────┘
```

| ID | Região | Regra |
|---|---|---|
| LAY-01 | Barra de acessibilidade | Primeiro elemento focável. Saltos para conteúdo, menu e rodapé, com os atalhos do eMAG; {{Recursos extras, como alto contraste e tema}}. |
| LAY-02 | Cabeçalho (`<header>`) | {{Altura, marca, busca, menu do usuário com perfil atual e saída}} |
| LAY-03 | Menu lateral (`<nav aria-label="Menu principal">`) | {{Largura; a partir de que largura fica fixo; abaixo dela vira gaveta}}. O menu lista apenas as telas permitidas ao perfil; a tela aberta fica marcada com `aria-current="page"`. |
| LAY-04 | Trilha de navegação (`<nav aria-label="Você está aqui">`) | Último item não é link e leva `aria-current="page"`. {{Forma compacta no celular}} |
| LAY-05 | Área de trabalho (`<main>`) | {{Largura máxima e margens}}. Ordem fixa: título, resumo, ações, detalhe. Uma só ação primária por tela. |
| LAY-06 | Rodapé (`<footer>`) | {{Versão do sistema, links de acessibilidade, privacidade e ajuda}} |
| LAY-07 | Título da página (`<title>`) | {{Padrão, por exemplo: tela · contexto · nome do sistema}} |

## 5. Inventário de componentes

Convenções do inventário:

- Um componente por linha, com identificador `CMP-nn` que nunca muda de número.
- **Propriedades** na linguagem da stack (por exemplo, a interface TypeScript) ou, antes da stack, em lista simples.
- **Estados** são os visuais que o componente precisa ter; cada um vira caso de teste de componente.
- **Telas** lista as TL que usam o componente; o inventário e o 11 têm de bater.
- Todo componente é testado com verificação automática de acessibilidade, sem violação.

Os componentes CMP-01 a CMP-10 são a base que quase todo sistema precisa, porque toda tela tem os cinco estados
(vazio, carregando, erro, sem permissão, sucesso). Ajuste as propriedades à stack e acrescente os componentes do seu
domínio a partir do CMP-11.

| ID | Componente | Propriedades | Estados | Quando usar | Telas |
|---|---|---|---|---|---|
| CMP-01 | Indicador de situação | situação, rótulo, tamanho, contagem opcional | {{Situações do seu domínio, por exemplo: em dia, atenção, pendente, concluído}} | Toda indicação de situação. Cor, ícone e palavra, sempre juntos. | TL-01, TL-02 |
| CMP-02 | Tabela de dados | colunas, linhas, legenda, ordenação, paginação, conteúdo do vazio | normal, ordenada, paginada, vazia, carregando | Toda lista tabular. `<caption>`, `<th scope>`, `aria-sort`; números alinhados à direita. | TL-01 |
| CMP-03 | Resumo em cifras | itens (rótulo, valor, situação, destino do clique) | normal, carregando | Bloco de duas a seis cifras no topo da tela, em `<dl>`. | TL-01, TL-02 |
| CMP-04 | Campo de formulário | rótulo, instrução, valor, erro, obrigatório | normal, com foco, com erro, desabilitado, somente leitura | Todo campo. Rótulo visível; erro ligado ao campo. | TL-02 |
| CMP-05 | Indicador de prazo | data limite, unidade (dias úteis ou corridos), dias restantes, regra de origem | no prazo, perto do vencimento, vence hoje, vencido, cumprido | Todo prazo exibido. Texto completo, nunca só a cor ou um número solto. | TL-01, TL-02 |
| CMP-06 | Estado vazio | título, explicação, ação sugerida | — | Lista ou área sem dados: diz por que está vazia e o que fazer. | TL-01, TL-02 |
| CMP-07 | Carregando | rótulo, forma do esqueleto | — | Espera acima de {{Limite em milissegundos}}. `role="status"`. | TL-01, TL-02 |
| CMP-08 | Erro com ação | título, explicação, código de rastreio, ação principal | — | Falha de carga ou de ação: o que falhou, o que foi guardado, o que fazer. `role="alert"`. | TL-01, TL-02 |
| CMP-09 | Sem permissão | perfil atual, perfis que têm acesso, ação de retorno | — | Rota que o perfil não pode abrir. Nunca mostra o dado protegido por trás. | TL-01, TL-02 |
| CMP-10 | Confirmação de ação | título, consequência, quem decide, rótulo do botão, justificativa opcional | aberta, confirmando, com erro | Ação irreversível ou que muda a situação do objeto do processo. Diálogo modal; o botão diz o verbo. | TL-02 |
| CMP-11 | {{Componente do domínio}} | {{Propriedades}} | {{Estados}} | {{Quando usar, com o requisito ou a regra que o motiva}} | {{Telas}} |

Componentes de moldura (cabeçalho, menu lateral, trilha de navegação, rodapé, mensagem passageira) também entram no
inventário quando a stack não os traz prontos: {{Liste com o próximo número livre, ou diga que vêm do design system}}.

## 6. Guia de mensagens

### 6.1 Tom de voz

| ID | Regra | Escreva | Evite |
|---|---|---|---|
| TOM-01 | Frases curtas, na voz ativa e no presente | "O documento foi anexado ao pedido." | "Informamos que foi realizada a anexação do documento." |
| TOM-02 | Diga o que aconteceu e o dado que motivou | "Falta o documento de identificação do requerente." | "Dados inválidos." |
| TOM-03 | Diga o que fazer e quem faz | "Anexe o comprovante e envie de novo." | "Verifique as informações." |
| TOM-04 | Sem termo técnico, código de erro ou língua estrangeira | "O arquivo está corrompido e não pôde ser lido." | "Erro 500: parse failure." |
| TOM-05 | O sistema não decide pela pessoa | "Pronto para a análise de {{Perfil}}." | "Pedido aprovado." (quando quem aprova é uma pessoa) |
| TOM-06 | O botão diz a ação | "Enviar pedido", "Registrar parecer" | "OK", "Confirmar" sem objeto |
| TOM-07 | Números, datas e unidades em português do Brasil | "1.250,40", "05/03/2026", "3 dias úteis" | "1250.40", "2026-03-05", "3d" |
| TOM-08 | Trate o público externo com formalidade neutra, sem culpa | "O pedido tem uma pendência. Corrija e envie de novo." | "Você errou o preenchimento." |

### 6.2 Mensagens de erro

| ID | Situação | Mensagem | Ação oferecida |
|---|---|---|---|
| ERR-01 | Falha ao carregar dados | {{Texto: o que não carregou e a garantia de que os dados continuam intactos}} | {{Nova tentativa}} |
| ERR-02 | Erro ao gravar | {{Texto: o que não foi gravado e que o que a pessoa digitou continua na tela}} | {{Nova tentativa}} |
| ERR-03 | Sessão expirada | {{Texto}} | {{Entrar de novo}} |
| ERR-04 | Sem permissão | {{Texto: que perfis abrem a tela e qual é o perfil atual}} | {{Voltar ao início}} |
| ERR-05 | Registro não encontrado | {{Texto}} | {{Ação}} |
| ERR-06 | Integração fora do ar (INT-01) | {{Texto: o que ficou pendente e quando será refeito}} | {{Ação ou contingência manual}} |
| ERR-07 | {{Erro de regra de negócio: cite a regra RN do 08 que não foi atendida}} | {{Texto com o dado e a regra}} | {{Ação}} |

Erro de validação de campo: a mensagem fica junto do campo e num resumo no topo do formulário, com link para cada
campo. {{Mensagens por regra de validação, se houver muitas: uma tabela regra × situação × mensagem × o que fazer}}.

### 6.3 Confirmações

| ID | Ação | Caso de uso | Título do diálogo | Consequência (texto do diálogo) | Botão |
|---|---|---|---|---|---|
| CNF-01 | {{Ação que muda a situação}} | UC-01 | {{Pergunta direta, por exemplo: Enviar o pedido para análise?}} | {{O que muda, quem é avisado, o que não poderá ser desfeito}} | {{Verbo da ação}} |
| CNF-02 | {{Ação}} | UC-02 | {{Título}} | {{Consequência}} | {{Verbo}} |

Retorno depois da ação confirmada (mensagem passageira): {{Texto curto do retorno de cada confirmação}}.

### 6.4 Alertas

| ID | Momento | Texto (na tela e no aviso enviado) | Destinatário | Requisito |
|---|---|---|---|---|
| ALR-01 | {{Antes do vencimento, com o limiar}} | {{Texto com o ato, o objeto, os dias que faltam e a regra do prazo}} | {{Perfil}} | {{RF-SIG-nn que gera o alerta}} |
| ALR-02 | {{No vencimento ou depois dele}} | {{Texto}} | {{Perfil}} | {{RF-SIG-nn}} |

Quando a tela explica um prazo, ela mostra a base. Uma linha por prazo do processo:

| Prazo | Valor | Unidade | Base (norma ou regra) |
|---|---|---|---|
| {{Nome do prazo}} | {{Quantidade}} | {{Dias úteis ou dias corridos}} | {{RN-SIG-nn, com a norma e o dispositivo}} |

### 6.5 Mensagens de sucesso

| Situação | Texto |
|---|---|
| {{Ação concluída}} | {{Texto que diz o que foi feito e o próximo passo}} |

### 6.6 Glossário de tela

Rótulos que as telas usam, tirados do glossário do 01. A coluna "Evite" lista sinônimos que tendem a aparecer no
código e na tela e que confundem quem usa.

| Rótulo de tela | Significado | Evite |
|---|---|---|
| {{Rótulo}} | {{Significado no processo, conforme o glossário do 01}} | {{Sinônimos a evitar}} |
| {{Rótulo}} | {{Significado}} | {{Sinônimos a evitar}} |

Pontos em aberto deste guia: {{Lista do que falta decidir, com DEC-01 quando for decisão do órgão, ou "nenhum"}}.

## 7. Acessibilidade: WCAG 2.2 nível AA e eMAG 3.1

### 7.1 Regras para todas as telas

| ID | Regra | Critério de referência |
|---|---|---|
| ACE-01 | Idioma da página declarado (`lang="pt-BR"`) e título único por tela (LAY-07) | WCAG 3.1.1, 2.4.2; eMAG 3.1 |
| ACE-02 | Regiões marcadas (`header`, `nav` com rótulos distintos, `main`, `footer`); um `h1` por tela; títulos sem saltar nível | WCAG 2.4.6, 1.3.1; eMAG 1.3 |
| ACE-03 | Saltos para conteúdo, menu e rodapé no início da página, com atalhos; página de acessibilidade no rodapé | WCAG 2.4.1; eMAG 1.5 |
| ACE-04 | Tudo operável pelo teclado, na ordem visual, sem armadilha de foco | WCAG 2.1.1, 2.1.2, 2.4.3 |
| ACE-05 | Foco sempre visível e não encoberto por cabeçalho fixo ou camada sobreposta | WCAG 2.4.7, 2.4.11 |
| ACE-06 | Contraste dentro dos mínimos da seção 3.2, em todos os temas | WCAG 1.4.3, 1.4.11 |
| ACE-07 | Informação nunca só pela cor | WCAG 1.4.1 |
| ACE-08 | Conteúdo se reorganiza a 320 px de largura sem rolagem horizontal da página | WCAG 1.4.10 |
| ACE-09 | Texto ampliado a 200% e espaçamento de texto ajustado sem perda de conteúdo | WCAG 1.4.4, 1.4.12 |
| ACE-10 | Área de toque de pelo menos 24 × 24 px ({{Tamanho adotado pelo sistema}}) | WCAG 2.5.8 |
| ACE-11 | Campo com rótulo visível, instrução antes do campo, erro ligado ao campo (`aria-describedby`, `aria-invalid`) e resumo dos erros | WCAG 3.3.1, 3.3.2, 3.3.3, 1.3.1; eMAG 6.2 |
| ACE-12 | Mensagem de situação anunciada ao leitor de tela sem mover o foco (`role="status"`; erro com `role="alert"`) | WCAG 4.1.3 |
| ACE-13 | Entrada no sistema sem teste cognitivo; colar senha e gerenciador de senhas permitidos | WCAG 3.3.8 |
| ACE-14 | Dado já informado no mesmo fluxo não é pedido de novo | WCAG 3.3.7 |
| ACE-15 | Ajuda no mesmo lugar em todas as telas | WCAG 3.2.6 |
| ACE-16 | Sessão que expira avisa antes e permite estender | WCAG 2.2.1 |
| ACE-17 | Nenhum recurso só por arrastar; há alternativa por clique | WCAG 2.5.7 |
| ACE-18 | Verificação automática em todas as telas e estados, a cada integração; teste manual com leitor de tela e teclado a cada release ({{Leitor de tela e navegador usados}}) | eMAG 3.1, recomendações de avaliação |

### 7.2 Regras por componente

| Componente | Uso pelo teclado | O que o leitor de tela anuncia | Critérios |
|---|---|---|---|
| CMP-01 Indicador de situação | não focável | lê a palavra da situação; ícone oculto do leitor | 1.4.1, 1.4.3 |
| CMP-02 Tabela de dados | cabeçalho ordenável é botão; contêiner rolável focável | `<caption>`, `th` com `scope`, `aria-sort` | 1.3.1, 1.4.10 |
| CMP-04 Campo de formulário | ordem de tabulação igual à visual | rótulo, instrução e erro ligados ao campo | 1.3.1, 3.3.1, 3.3.2 |
| CMP-05 Indicador de prazo | não focável | texto completo ("vence em 3 dias úteis, em 12/03/2026") | 1.4.1 |
| CMP-07 Carregando | — | `role="status"`; região com `aria-busy="true"` | 4.1.3 |
| CMP-08 Erro com ação | se a tela inteira falhou ao abrir, o foco vai para o título do erro | anunciado como alerta (`role="alert"`) | 4.1.3, 3.3.1 |
| CMP-10 Confirmação de ação | foco no primeiro controle; Tab circula no diálogo; Esc cancela e devolve o foco | diálogo modal (`aria-modal="true"`) cujo título e descrição são ligados por `aria-labelledby` e `aria-describedby` | 4.1.2, 2.4.3 |
| {{CMP-nn do domínio}} | {{Comportamento de teclado}} | {{O que o leitor de tela anuncia}} | {{Critérios}} |

## 8. Responsividade

| Faixa | Largura | Layout |
|---|---|---|
| Celular | {{Até a primeira quebra}} (projeto a partir de 320 px) | {{Uma coluna; menu em gaveta; tabelas com rolagem interna ou em cartões}} |
| Tablet | {{Faixa}} | {{Layout}} |
| Desktop | {{Faixa}} | {{Menu lateral fixo; área de trabalho}} |
| Desktop largo | {{A partir de}} | {{Layout}} |

Telas que precisam funcionar bem no celular, porque alguém as usa fora da mesa de trabalho:
{{Lista de TL com o perfil e o motivo, ou "nenhuma"}}. As demais abrem e são legíveis no celular, sem rolagem
horizontal da página.

## Pronto quando

- [ ] Todo princípio tem comportamento verificável e origem.
- [ ] O design system adotado está escolhido, com versão consultada e ADR.
- [ ] Todo token está marcado como confirmado ou a conferir.
- [ ] Todo par de cor usado em texto ou componente tem razão de contraste medida por script e acima do mínimo, em
      cada tema.
- [ ] Todo componente usado nas telas do 11 está no inventário, com estados e telas.
- [ ] Todo caso de uso com pessoa tem suas mensagens de erro, confirmação e sucesso; todo prazo tem alerta e base.
- [ ] O glossário de tela usa os termos do glossário do 01.
- [ ] As regras de acessibilidade citam o critério e há regra de teclado e de leitor de tela para cada componente
      interativo.
- [ ] Nenhum marcador `{{...}}` sobrou.
