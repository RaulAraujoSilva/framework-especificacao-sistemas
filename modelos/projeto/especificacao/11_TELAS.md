# 11. Telas

<!-- COMO PREENCHER: este documento deriva dos casos de uso com pessoa como ator (04), das jornadas e do mapa de
navegação (02), das entidades do modelo de dados (06) e da lista de telas do 01. O passo a passo está no capítulo 03
da metodologia, §3.10 (docs/metodologia/03_PLANEJAMENTO_DA_ESPECIFICACAO.md). Cada tela listada no 01 ganha uma
seção "## TL-nn Nome", com o mesmo número; copie o bloco da TL-01 para cada tela nova. Todo caso de uso com pessoa
usa ao menos uma tela; todo dado exibido diz de que entidade e atributo vem; toda ação diz o caso de uso que dispara.
Pronto quando: as telas do 01 e as seções deste documento batem (regra C08 do conferidor); toda tela tem os cinco
estados (vazio, carregando, erro, sem permissão, sucesso) e critérios de aceite CA-TLnn-nn; todo componente citado
está no inventário do 10; o protótipo tem uma seção por tela.
Referência de formato: exemplo/reajusta/especificacao/11_TELAS.md. Ele serve só para ver estrutura, seções e nível
de detalhe. Não copie frase, rótulo, dado nem termo dele: o domínio do seu sistema é outro, e o conferidor acusa termo
e trecho copiados (C03 e C04). -->

Uma seção por tela listada no `01_VISAO_ESCOPO.md`. O documento 10 ([`10_UX_UI.md`](10_UX_UI.md)) define o que as
telas compartilham: componentes CMP-nn, tokens de cor e tipografia, textos de mensagem e acessibilidade. Quem usa
cada tela e como se chega a ela vem do documento 02 ([`02_PERFIS_E_JORNADAS.md`](02_PERFIS_E_JORNADAS.md)). Cada
tela tem também sua seção no protótipo navegável, [`prototipos/wireframes.html`](prototipos/wireframes.html).

## Convenções

- **Dados exibidos:** cada linha diz a entidade e o atributo de `06_MODELO_DADOS.md` (`Entidade.atributo`) e de onde
  o valor vem (quem informa, integração, cálculo).
- **Ações:** cada ação diz quem pode executá-la e o caso de uso que dispara. Ação sem caso de uso ou é navegação
  (diga para qual tela) ou falta caso de uso no 04.
- **Rota:** endereço sugerido, marcado "(proposto)"; prevalece o que o `05_ARQUITETURA.md` definir.
- **Permissões:** a tabela separa quem só consulta ("ver") de quem executa as ações ("agir"). O servidor confere de
  novo a permissão; esconder o botão não basta. A matriz completa está em `14_OPERACAO.md`.
- **Estados:** toda tela descreve os cinco: vazio, carregando, erro, sem permissão e sucesso. O texto padrão vem do
  guia de mensagens do 10; a tela só descreve o que muda.
- **Critérios de aceite da tela:** `CA-TLnn-nn`, verificáveis por teste de componente ou de ponta a ponta. Toda tela
  cumpre também os critérios gerais:
  - CA-GERAL-01: em todos os cinco estados, a verificação automática de acessibilidade não acusa violação;
  - CA-GERAL-02: com 320 px de largura, a página não rola na horizontal;
  - CA-GERAL-03: toda situação tem texto, além da cor;
  - CA-GERAL-04: título da página no padrão do 10 (LAY-07);
  - CA-GERAL-05: tudo alcançável e operável pelo teclado, com foco visível;
  - CA-GERAL-06: {{Critério geral próprio do sistema, ou retire esta linha}}.
- **Dados de exemplo:** o protótipo e os desenhos usam {{Caso real anonimizado que serve de fio, com o código do caso
  no levantamento}}. O que não vem desse caso leva a marca "exemplo".

---

## TL-01 {{Nome da tela}}

- **Objetivo:** {{O que a pessoa consegue fazer nesta tela e por que isso importa no processo, citando a melhoria ou
  a meta (por exemplo: ver a fila de pedidos com prazo e responsável, para que nenhum fique parado sem dono)}}
- **Perfis:** PER-{{SIG}} {{E os demais perfis que usam a tela}}
- **Casos de uso:** UC-01 {{E outros que esta tela atende}}
- **Requisitos:** RF-{{SIG}}-01 {{E outros requisitos que a tela materializa}}
- **Rota (proposto):** `{{Endereço da tela, por exemplo /pedidos}}`

**Dados exibidos:**

| Dado | Entidade.atributo | Origem |
|---|---|---|
| {{Nome do dado na tela}} | `{{Entidade.atributo}}` | {{Quem informa, integração (INT-nn) ou cálculo (RN do 08)}} |
| {{Nome do dado na tela}} | `{{Entidade.atributo}}` | {{Origem}} |
| Resumo | {{Contagens ou totais do topo da tela}} | {{Cálculo sobre a lista}} |

**Ações:**

| Ação | Quem | Caso de uso | Requisito |
|---|---|---|---|
| {{Verbo + objeto, por exemplo: Filtrar por situação}} | PER-{{SIG}} | UC-01 | RF-{{SIG}}-01 |
| {{Abrir o item}} | {{Perfis}} | {{Navegação para TL-02}} | — |

**Componentes:** CMP-01, CMP-02, CMP-03, CMP-05, CMP-06, CMP-07, CMP-08, CMP-09 {{E os do domínio}}.

**Regras de exibição:**

- {{Ordem padrão da lista, por exemplo: prazo vencido primeiro, depois o mais próximo}}
- {{O que acontece com o item sem dado obrigatório: aparece como erro visível, nunca some}}
- {{Regra de negócio que a tela aplica ao exibir, citando RN-SIG-nn do 08}}

**Permissões:**

| Perfil | Pode |
|---|---|
| PER-{{SIG}} | {{Ver e agir: quais ações}} |
| {{Outro perfil}} | {{Só ver, ou sem acesso}} |

**Estados:**

| Estado | O que a tela mostra |
|---|---|
| Vazio | {{Mensagem que diz por que não há itens e o que fazer; com filtro aplicado, a mensagem e "Limpar filtros"}} |
| Carregando | {{Forma do esqueleto e rótulo anunciado, por exemplo: esqueleto de tabela com cinco linhas}} |
| Erro | {{Mensagem do 10 (ERR-nn) e ação de nova tentativa}} |
| Sem permissão | {{Perfis que abrem a tela e retorno oferecido (CMP-09)}} |
| Sucesso | {{O que a tela mostra depois de uma ação concluída: mensagem passageira e mudança visível na lista}} |

**Critérios de aceite:**

- CA-TL01-01: {{Comportamento verificável, com dado do caso de exemplo, por exemplo: o item sem responsável aparece
  na primeira linha com o texto "sem responsável"}}
- CA-TL01-02: {{Comportamento verificável}}
- CA-TL01-03: {{Perfil sem acesso recebe a tela de sem permissão na rota e o servidor recusa a chamada}}

**Desenho de baixa fidelidade:**

```
Início › {{Seção}}
{{Título da tela}}                                    [{{Ação principal}}]
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ {{Cifra 1}}  │ {{Cifra 2}}  │ {{Cifra 3}}  │ {{Cifra 4}}  │
└──────────────┴──────────────┴──────────────┴──────────────┘
Filtros: [{{Filtro 1}} ▾] [{{Filtro 2}} ▾]
┌──────────────────┬────────────┬──────────────┬──────────────┐
│ {{Coluna 1}}     │ {{Col. 2}} │ {{Situação}} │ {{Prazo}}    │
├──────────────────┼────────────┼──────────────┼──────────────┤
│ {{Item}}         │ {{Valor}}  │ [{{Chip}}]   │ {{Vence em}} │
└──────────────────┴────────────┴──────────────┴──────────────┘
```

---

## TL-02 {{Nome da tela}}

- **Objetivo:** {{O que a pessoa consegue fazer nesta tela, por exemplo: examinar um item e registrar a decisão sobre
  ele, com os documentos e os prazos à vista}}
- **Perfis:** PER-{{SIG}} {{E os demais perfis}}
- **Casos de uso:** UC-02 {{E outros}}
- **Requisitos:** RF-{{SIG}}-01 {{E outros}}
- **Rota (proposto):** `{{Endereço da tela, por exemplo /pedidos/[id]}}`

**Dados exibidos:**

| Dado | Entidade.atributo | Origem |
|---|---|---|
| {{Identificação do item}} | `{{Entidade.atributo}}` | {{Origem}} |
| {{Situação e responsável}} | `{{Entidade.atributo}}` | {{Máquina de estados do 04}} |
| {{Linha do tempo ou histórico}} | `{{Entidade.atributo}}` | {{Trilha de auditoria ou marcos registrados}} |
| {{Documentos ligados}} | `{{Entidade.atributo}}` | {{Origem}} |

**Ações:**

| Ação | Quem | Caso de uso | Requisito |
|---|---|---|---|
| {{Verbo + objeto, por exemplo: Registrar decisão}} | PER-{{SIG}} | UC-02 | RF-{{SIG}}-01 |
| {{Ação que muda a situação, com confirmação (CMP-10 e CNF-nn)}} | {{Perfil}} | {{UC}} | {{RF}} |
| {{Voltar à lista}} | {{Perfis}} | {{Navegação para TL-01}} | — |

**Componentes:** CMP-01, CMP-03, CMP-04, CMP-05, CMP-06, CMP-07, CMP-08, CMP-09, CMP-10 {{E os do domínio}}.

**Regras de exibição:**

- {{Campo ou ação que só aparece em certa situação do objeto, e por quê}}
- {{Botão desabilitado diz o que falta para habilitá-lo, em texto}}
- {{Regra de negócio que a tela aplica, citando RN-SIG-nn do 08}}

**Permissões:**

| Perfil | Pode |
|---|---|
| PER-{{SIG}} | {{Ver e agir: quais ações}} |
| {{Outro perfil}} | {{Só ver, ou sem acesso}} |

**Estados:**

| Estado | O que a tela mostra |
|---|---|
| Vazio | {{O que aparece quando o item ainda não tem os dados da seção, por exemplo: "Nenhum documento anexado"}} |
| Carregando | {{Forma do esqueleto e rótulo anunciado}} |
| Erro | {{Mensagem do 10, inclusive item não encontrado (ERR-nn), e o que foi preservado}} |
| Sem permissão | {{Perfis que abrem a tela e retorno oferecido (CMP-09)}} |
| Sucesso | {{Mensagem depois de registrar a ação, nova situação do item e próximo passo}} |

**Critérios de aceite:**

- CA-TL02-01: {{Comportamento verificável com o dado do caso de exemplo}}
- CA-TL02-02: {{A ação que muda a situação só conclui depois da confirmação, e a nova situação aparece sem recarregar}}
- CA-TL02-03: {{Erro de campo é anunciado e o foco vai para o resumo de erros}}

**Desenho de baixa fidelidade:**

```
Início › {{Seção}} › {{Item}}
{{Identificação do item}}                       [{{Chip de situação}}]
┌───────────────────┬───────────────────┬───────────────────┐
│ Responsável       │ Próximo prazo     │ {{Outra cifra}}   │
│ {{Perfil}}        │ {{Vence em}}      │ {{Valor}}         │
└───────────────────┴───────────────────┴───────────────────┘
Dados do item                         │ Histórico
 {{Campo}}: {{Valor}}                 │ ● {{Data}} {{Evento}}
 {{Campo}}: {{Valor}}                 │ ○ {{Próximo passo}}
Decisão: ( ) {{Opção 1}}  ( ) {{Opção 2}}
Justificativa [_____________________________]
[{{Verbo da ação}}]   [Cancelar]
```

---

## Itens "(proposto)" desta especificação de telas

Tudo o que este documento propõe e o documento-base ainda não fixou, para a área avaliar:

| Item | Proposta | Quem confirma |
|---|---|---|
| Rotas | {{As rotas marcadas "(proposto)" acima}} | {{TI}} |
| {{Rótulo, regra de exibição ou permissão proposta}} | {{Proposta}} | {{Área ou perfil}} |

## Pronto quando

- [ ] Toda tela listada no 01 tem seção `## TL-nn` neste documento, e nenhuma seção existe sem estar no 01 (C08).
- [ ] Todo caso de uso com pessoa como ator aparece em pelo menos uma tela.
- [ ] Todo dado exibido aponta entidade e atributo do 06 e a origem.
- [ ] Toda ação aponta o caso de uso que dispara, ou a tela para onde navega.
- [ ] Toda tela descreve os cinco estados: vazio, carregando, erro, sem permissão e sucesso.
- [ ] Toda tela tem critérios de aceite `CA-TLnn-nn` verificáveis.
- [ ] Todo componente citado está no inventário do 10.
- [ ] O protótipo tem uma seção `data-tela` por tela, com o mesmo número.
- [ ] Nenhum marcador `{{...}}` sobrou.
