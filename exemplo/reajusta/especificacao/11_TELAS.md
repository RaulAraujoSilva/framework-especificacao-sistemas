# 11. Telas

Uma seção por tela do documento-base (`01_VISAO_ESCOPO.md`, seção 12). Os componentes CMP-*, os tokens, as mensagens
e as regras de acessibilidade estão em [`10_UX_UI.md`](10_UX_UI.md). Os perfis, a jornada e o mapa de navegação
estão em [`02_PERFIS_E_JORNADAS.md`](02_PERFIS_E_JORNADAS.md). O protótipo navegável das 16 telas está em
[`prototipos/wireframes.html`](prototipos/wireframes.html).

## Convenções

- **Dados mostrados:** cada linha diz a entidade e o atributo (`06_MODELO_DADOS.md`) e a origem do número (RNF-02).
- **Rota:** sugestão de URL do App Router, marcada "(proposto)". Se `05_ARQUITETURA.md` fixar outra, vale a de lá.
- **Permissões:** "ver" é leitura; "agir" são as ações listadas. A API repete a checagem: esconder o botão não basta
  (RNF-10).
- **Estados comuns a todas as telas** (não repetidos abaixo, salvo quando a tela muda o texto):
  - carregando: CMP-16 com o rótulo da tela;
  - erro de carga: CMP-17 com MSG-ERR-01;
  - sem permissão: CMP-18 com MSG-ERR-04;
  - sessão expirada: MSG-ERR-03.
- **Critérios de aceite de UI:** CA-TLnn-xx, verificáveis por teste de componente (Testing Library + `axe`) ou de
  ponta a ponta (Playwright). Todas as telas cumprem também:
  - CA-GER-01: nenhuma violação do `axe` em nenhum estado;
  - CA-GER-02: sem rolagem horizontal da página a 375 px e a 320 px;
  - CA-GER-03: todo número de domínio abre a origem (CMP-05);
  - CA-GER-04: toda situação tem texto, além da cor;
  - CA-GER-05: título da página no padrão UX-LAY-08;
  - CA-GER-06: tudo alcançável e operável por teclado, com foco visível.
- **Dados reais:** o ciclo de Paraty 2026 é o do pleito real (`saida/levantamento/pleito/exemplo_paraty_2026.json`, resultado
  em `exemplo_paraty_2026.validacao.json`, cadastro em `saida/levantamento/contratos/paraty_008_2014.json`, extração em
  `saida/levantamento/calculo/extracao_SEI-480002_009982_2025.json`). Nos wireframes, o que não vem dessas fontes leva a marca
  "exemplo".

---

## TL-01 Painel do ciclo

**Objetivo:** mostrar a fila de ciclos de reajuste com situação, dono, próximo prazo e idade, para que nenhum ciclo
fique parado sem dono (RF-PRZ-09, RF-PRZ-02).

**Perfis:** todos os internos (PER-ANA, PER-GCA, PER-PRO, PER-SEC, PER-REL, PER-GES, PER-ADM). **Rota (proposto):**
`/ciclos`.

**Dados mostrados:**

| Dado | Entidade.atributo | Origem |
|---|---|---|
| Contrato e concessionária | `Contrato.numero`, `Concessionaria.nome` | cadastro (MOD-CAD) |
| Vigência pretendida | `Pleito.vigenciaPretendida` | pleito enviado |
| Número SEI | `CicloReajuste.numeroSei` | registrado por PER-SEC (INT-01) |
| Situação do ciclo | `CicloReajuste.situacao` | estado do ciclo (rótulos da seção "Situações do ciclo" abaixo) |
| Erros e avisos da última validação | contagem de `ItemValidacao` por situação | `ResultadoValidacao` mais recente |
| Dono e desde quando | `Prazo` ou etapa corrente: unidade e data | RF-PRZ-02 |
| Próximo prazo | `Prazo.limite`, unidade (du/dc), base legal | RF-PRZ-01 |
| Idade | dias úteis desde o marco de protocolo | `Marco` protocolo |
| Resumo | ciclos abertos; com prazo vencido; sem dono; devolvidos aguardando a concessionária | contagens sobre a fila |

**Ações:**
- Filtrar por situação, dono (unidade), contrato, vencimento e "só os meus".
- Ordenar por prazo, idade ou contrato.
- Abrir o ciclo (TL-02).
- Exportar a fila em CSV (somente dados internos, sem séries pagas: RNF-04).

**Componentes:** CMP-10, CMP-09 (com CMP-13), CMP-01, CMP-07, CMP-08, CMP-15.

**Regras de exibição:**
- Ordem padrão: prazo vencido primeiro, depois o prazo mais próximo.
- Ciclo sem dono aparece no topo com CMP-08 em erro ("sem unidade responsável") e conta no resumo (I-P01-06).
- Ciclo encerrado sai da fila padrão; filtro "encerrados" o traz de volta.
- A idade usa dias úteis com os feriados do estado (RF-PRZ-01).

**Permissões:**

| Perfil | Pode |
|---|---|
| PER-ANA, PER-PRO, PER-SEC, PER-REL | ver todos os ciclos; filtrar "só os meus" pela unidade |
| PER-GCA, PER-GES, PER-ADM | só ver |
| PER-CON | sem acesso (CMP-18) |

**Estados:**
- Vazio sem filtro: "Nenhum ciclo de reajuste aberto. Os ciclos aparecem aqui quando uma concessionária envia o
  pleito." (CMP-15).
- Vazio com filtro: "Nenhum ciclo com estes filtros." + "Limpar filtros".
- Carregando: esqueleto de tabela com 5 linhas.

**Critérios de aceite:**
- CA-TL01-01: ciclo com dono nulo aparece na primeira linha com o texto "sem unidade responsável".
- CA-TL01-02: o prazo mostra a unidade por extenso no `title` e a data limite em dd/mm/aaaa.
- CA-TL01-03: o filtro aplicado anuncia o número de ciclos por `role="status"`.
- CA-TL01-04: a 375 px a fila vira lista de cartões com contrato, situação, dono e prazo.
- CA-TL01-05: PER-CON recebe CMP-18 na rota e na API (HTTP 403).

**Wireframe:**

```
Início › Ciclos
Ciclos de reajuste                                          [Exportar CSV]
┌──────────────┬──────────────┬──────────────┬──────────────────────────┐
│ 3 abertos    │ 1 vencido    │ 0 sem dono   │ 1 aguarda concessionária │
└──────────────┴──────────────┴──────────────┴──────────────────────────┘
Filtros: [Situação ▾] [Dono ▾] [Contrato ▾] [ ] só os meus
┌────────────────────────┬──────────┬───────────────┬──────┬────────┬─────────────────┬──────┐
│ Contrato               │ Vigência │ Situação      │ Erros│ Avisos │ Dono · prazo    │ Idade│
├────────────────────────┼──────────┼───────────────┼──────┼────────┼─────────────────┼──────┤
│ Águas de Paraty 008/14 │01/01/2026│ [erro] devolv.│  1   │   5    │ CONCESS. · vence│  2 du│
│ Águas da Imperatriz    │ exemplo  │ em análise    │  0   │ exemplo│ CAPET · exemplo │exemplo│
│ Águas da Condessa      │ exemplo  │ recebido      │exemplo│exemplo│ SCEXEC · exemplo│exemplo│
└────────────────────────┴──────────┴───────────────┴──────┴────────┴─────────────────┴──────┘
```

### Situações do ciclo (rótulos de tela)

Rótulos de `CicloReajuste.situacao` (proposto). Se `06_MODELO_DADOS.md` fixar outra máquina de estados, valem os nomes
de lá.

| Rótulo | Quando | Dono padrão | Tarefa BPMN |
|---|---|---|---|
| recebido | pacote enviado, validação em curso | sistema | t1 |
| devolvido · aguarda a concessionária | validação com erro, devolução confirmada | concessionária | t4, t14 |
| em análise na CAPET | validação sem erro | CAPET | t2 |
| na Procuradoria | parecer técnico registrado | PROC | t3 |
| em diligência | ofício de diligência emitido | quem diligenciou | t4, t14, t5 |
| em razões finais | ofício de razões finais emitido | gabinete | t7 |
| pautado | incluído na pauta | CODIR | t8 |
| deliberado | marco de deliberação registrado | SCEXEC | t8 |
| em prazo recursal | publicação registrada | SCEXEC | t9 |
| em conferência de faturas | remessa recebida ou prazo de início aberto | CAPET | t10 |
| pronto para encerrar | lista de verificação completa | SCEXEC | t12 |
| encerrado | termo de encerramento registrado | — | t13 |

---

## TL-02 Detalhe do ciclo

**Objetivo:** reunir num lugar o que se sabe de um ciclo: linha do tempo de marcos, dono, prazos, peças, pendências e
apuração (UC-08).

**Perfis:** internos. **Rota (proposto):** `/ciclos/[id]`.

**Dados mostrados:**

| Dado | Entidade.atributo | Origem |
|---|---|---|
| Cabeçalho | contrato, concessionária, versão contratual, vigência, número SEI | `CicloReajuste`, `Pleito`, `VersaoContratual` |
| Resumo | situação, dono, próximo prazo, idade, resultado da validação, total apurado | CMP-10 |
| Linha do tempo | `Marco.tipo`, `Marco.data`, quem registrou, peça ligada | marcos registrados (RF-PRZ-01) |
| Prazos | `Prazo.limite`, base, dono, situação | RF-PRZ-01 a 08 |
| Peças | `Peca.tipo`, versão, situação (minuta, exportada) | MOD-DOC, MOD-MIN |
| Pendências | itens com erro do último `ResultadoValidacao` | MOD-PLE |
| Apuração | IR refeito, IR declarado, total, situação de V09 e V10 | `Apuracao` |
| Lista de verificação do encerramento | certidão, conferência de faturas, publicação | RF-PRZ-08 |

Dados reais de Paraty 2026 na linha do tempo (AS-IS, para comparação):
- 17/11/2025: Ofício nº 0320/2025 (pleito).
- Ofício CAPET nº 136/2025: pedido dos arquivos em Excel, prazo de 3 du (data não extraída).
- 30/11/2025: publicação da tabela no Diário do Vale (Ofício 0345/2025).
- 03/12/2025: Parecer Técnico CAPET nº 343/2025, assinado em 05/12/2025.
- 19ª Reunião Interna do Conselho Diretor (data não extraída).
- Deliberação nº 4.997: 6,795%, homologação definitiva.
- 01/01/2026: vigência pretendida.

**Ações:**

| Ação | Quem | UC / RF |
|---|---|---|
| Registrar marco (data, peça, número SEI da peça) | PER-SEC; PER-ANA (parecer técnico); PER-PRO (parecer jurídico); PER-REL (diligência, razões finais) | UC-08, RF-PRZ-01 |
| Vincular número SEI | PER-SEC | RF-PLE-06 |
| Atribuir ou trocar dono | PER-SEC | RF-PRZ-02 |
| Abrir pendências | todos os internos | TL-04 |
| Abrir memória | todos os internos | TL-05 |
| Abrir minuta | dono da peça | TL-08 |
| Gerar peça | PER-SEC, PER-REL | TL-09 |
| Encerrar ciclo, com lista completa | PER-SEC | UC-15, CMP-22 com MSG-CNF-06 |

**Componentes:** CMP-21, CMP-10, CMP-06, CMP-07, CMP-08, CMP-01, CMP-13, CMP-24, CMP-22, CMP-23, CMP-05.

**Regras de exibição:**
- Marco sem data aparece como "data não registrada", nunca some.
- Marco previsto mostra a data calculada pela regra e a base (ex.: "razões finais: 10 dias do ofício").
- O botão "Encerrar ciclo" só aparece habilitado com a lista de verificação toda ok. Desabilitado, diz o que falta
  ("falta a certidão de ausência de recurso", R-P01-17).
- A seção "Apuração" mostra o selo "Minuta — requer revisão" enquanto o parecer técnico não for exportado.

**Permissões:** ver: internos. Agir: conforme a tabela de ações. PER-GES e PER-ADM só veem.

**Estados:**
- Ciclo inexistente: MSG-ERR-05.
- Ciclo sem dono: faixa de erro no topo com MSG-PRZ-07 e botão "Atribuir dono" (PER-SEC).
- Ciclo encerrado: tudo em leitura, faixa "Encerrado em {data}" com o termo.
- Ciclo devolvido: faixa de aviso "Aguarda a concessionária desde {data}", com as pendências.

**Critérios de aceite:**
- CA-TL02-01: a linha do tempo é `<ol>`, com o marco atual em `aria-current="step"`.
- CA-TL02-02: o encerramento fica bloqueado sem a certidão e o motivo é lido pelo leitor de tela.
- CA-TL02-03: registrar um marco recalcula os prazos dependentes e mostra o toast com o novo limite.
- CA-TL02-04: a 375 px a linha do tempo é vertical e os prazos ficam acima das peças.

**Wireframe:**

```
Início › Ciclos › Águas de Paraty 2026
Águas de Paraty · 008/2014 · vigência 01/01/2026     SEI-480002/009982/2025
versão contratual 3TA-2024
┌────────────────┬────────────────────┬────────────────┬──────────────┐
│ Situação       │ Dono               │ Próximo prazo  │ Validação    │
│ [erro] devolv. │ CONCESSIONÁRIA     │ resposta:exemplo│ 10 ok·5 av·1 er│
└────────────────┴────────────────────┴────────────────┴──────────────┘
Linha do tempo                         │ Prazos
 ● 17/11/2025 Pleito (Of. 0320/2025)   │ Pronunciamento: 30 dc do pleito
 ● validação: 1 erro (V11)             │ [vencido] exemplo
 ◉ devolução · aguarda concessionária  │ Procuradoria: 15 dc do parecer
 ○ parecer técnico (previsto)          │
 ○ parecer jurídico · razões finais    │ Peças
 ○ pauta · deliberação · publicação    │ Ofício de complementação [minuta]
 ○ certidão · encerramento             │
Lista de verificação do encerramento: [ ] certidão [ ] faturas  [Encerrar ▒]
```

---

## TL-03 Envio do pleito e validação prévia

**Objetivo:** a concessionária monta o pacote, valida antes de enviar com as mesmas regras e envia com recibo
(UC-01, RF-PLE-01, RF-PLE-05).

**Perfis:** PER-CON. **Rota (proposto):** `/pleitos/novo` e `/pleitos/[id]/reenvio`.

**Dados mostrados:**

| Dado | Origem |
|---|---|
| Contrato e versão contratual vigente | cadastro publicado da própria concessionária (MOD-CAD) |
| Ciclo e vigência esperada | calendário de data-base (RF-CAD-04) |
| Lista do pacote: `pleito.json`, `series.csv`, `energia.csv`, `tabela_tarifaria.csv`, evidências, memória de cálculo, publicação | `docs/ESPECIFICACAO_DADOS_PLEITO.md`, seção 3 |
| Layout aceito: versão 0.1 | `pleito_reajuste.schema.json` |
| SHA-256 de cada arquivo | calculado no navegador e de novo no servidor |
| Resultado da validação prévia | mesmas regras V01 a V12, sem registro |
| Pendências da devolução anterior | `ResultadoValidacao` anterior, no reenvio |

**Ações:**
- Escolher ou arrastar os arquivos.
- "Validar antes de enviar" (RF-PLE-05).
- "Enviar pleito", habilitado só depois de uma validação prévia do mesmo conjunto de arquivos (CMP-22 com MSG-CNF-02).
- Baixar o modelo do layout e o cadastro publicado do contrato.

**Componentes:** CMP-12, CMP-02, CMP-10, CMP-22, CMP-23, CMP-06 (visão resumida dos marcos do próprio ciclo).

**Regras de exibição:**
- A validação prévia mostra o mesmo resultado de TL-04, com a marca "validação prévia: nada foi enviado".
- Pacote com erro pode ser enviado. O sistema avisa que ele será devolvido com as pendências: a decisão de devolver é
  da CAPET (UC-04).
- Arquivo com dado pessoal é recusado antes de qualquer registro (RNF-05, MSG-ERR-08).
- No reenvio, a tela mostra as pendências anteriores ao lado e marca as que foram resolvidas.
- Depois do envio: recibo com data e hora, número do recebimento e hashes, e o aviso "o ciclo será vinculado ao
  processo SEI pela Secretaria".

**Permissões:** só PER-CON, e só para os contratos da própria concessionária (RF-ADM-01).

**Estados:**
- Vazio: "Escolha os arquivos do pleito. O pacote mínimo é o pleito.json e o series.csv; a lista completa está
  abaixo."
- Lendo/validando: CMP-16 com a regra em curso ("Conferindo séries públicas (V07)…"). Limite de 60 s (RNF-13).
- Validado com erro: resumo em erro e lista CMP-02; "Enviar" habilitado com aviso.
- Validado sem erro: resumo ok; "Enviar" é a ação primária.
- Enviado: recibo; link para o resultado (TL-04).
- Fonte externa fora do ar: itens "a refazer"; o envio continua permitido (RNF-06).

**Critérios de aceite:**
- CA-TL03-01: o botão "Enviar pleito" fica desabilitado até haver validação prévia do conjunto atual; trocar um
  arquivo desabilita de novo.
- CA-TL03-02: o pacote de Paraty 2026 na validação prévia mostra "10 conferências ok · 5 avisos · 1 erro".
- CA-TL03-03: o seletor de arquivo funciona sem arrastar (teclado e leitor de tela).
- CA-TL03-04: a tela funciona a 375 px, com o botão de ação fixo no rodapé.
- CA-TL03-05: os hashes do recibo são iguais aos calculados no servidor.

**Wireframe:**

```
Início › Meus pleitos › Novo pleito
Enviar pleito de reajuste · Contrato 008/2014 · versão 3TA-2024
1 Arquivos ─── 2 Validação prévia ─── 3 Envio
┌───────────────────────────────────────────────────────────┐
│  Arraste os arquivos aqui ou [Escolher arquivos]           │
│  pleito.json ✓  series.csv ✓  energia.csv ✓  tabela… —     │
└───────────────────────────────────────────────────────────┘
pleito.json   sha256 0000…0000 (exemplo)
[Validar antes de enviar]
Resultado: 10 ok · 5 avisos · 1 erro (validação prévia: nada foi enviado)
 [erro] V11 Energia sem distribuidora, composição e resolução da ANEEL
 [aviso] V03 … [aviso] V06 … [ver tudo]
                                        [Enviar pleito]  (fixo no celular)
```

---

## TL-04 Resultado da validação (V01 a V12)

**Objetivo:** mostrar o resultado das regras V01 a V12 numa tela, na linguagem de quem analisa, e permitir à CAPET
devolver o pleito com as pendências (UC-02, UC-04, RNF-09).

**Perfis:** PER-CON (só os próprios pleitos) e PER-ANA. Outros internos leem (proposto). **Rota (proposto):**
`/ciclos/[id]/validacao`.

**Dados mostrados:**

| Dado | Entidade.atributo | Origem |
|---|---|---|
| Cabeçalho | concessionária, vigência, versão contratual, versão do layout, versão das regras, data e hora da validação | `ResultadoValidacao` (RNF-03) |
| Resumo | contagem de ok, aviso, erro, a refazer; conclusão ("devolver para complementação" ou "segue para a CAPET") | `ItemValidacao` |
| Itens | regra, situação, mensagem (guia 6.2), números e origens | `ItemValidacao` |
| Histórico | validações anteriores do mesmo ciclo, com a contagem | `ResultadoValidacao` |

Dados reais de Paraty 2026: 16 itens; 10 ok, 5 avisos, 1 erro. O erro é V11. Os avisos são:
- V03: 12 meses de referência, mas só 354 dias;
- V06: séries só com as pontas;
- V07 ICC: arredondado em relação à série;
- V08 IMO: sem outro pleito do mesmo mês;
- V12: sem tabela tarifária.

**Ações:**

| Ação | Quem | UC / RF |
|---|---|---|
| Expandir item (números e origens) | todos | — |
| Ver memória de cálculo | PER-ANA | TL-05 |
| Ver cadastro do contrato | PER-ANA | TL-06 |
| Devolver pleito | PER-ANA | UC-04, CMP-22 com MSG-CNF-01; gera a minuta do ofício de complementação em TL-09 (RF-PLE-04, RF-DOC-03) |
| Seguir para análise | PER-ANA, em pleito sem erro | registra o marco |
| Corrigir e reenviar | PER-CON | TL-03 |

**Componentes:** CMP-10, CMP-02, CMP-01, CMP-05, CMP-04 (no painel de origem), CMP-22, CMP-23.

**Regras de exibição:**
- Ordem: erro, a refazer, aviso, ok.
- O resumo e os itens com erro cabem na primeira dobra a 1280 × 800.
- Para PER-CON, cada item com erro ou aviso traz a coluna "O que fazer" (guia 6.2). Para PER-ANA, a coluna mostra a
  regra e a origem.
- "Devolver pleito" só aparece se houver erro. Sem erro, a ação primária é "Seguir para análise".
- Aviso de interstício (V03) traz a nota fixa "contagem em definição com a CAPET e a Procuradoria" enquanto a
  pendência 2 de `docs/ESPECIFICACAO_DADOS_PLEITO.md` estiver aberta.

**Permissões:** PER-CON vê só os próprios pleitos e não vê séries pagas de outros pleitos usadas em V08 (vê só
"igual" ou "diferente", RNF-04). PER-ANA vê e age.

**Estados:**
- Validação em curso: CMP-16 com a regra em curso.
- Sem validação ainda: "O pleito ainda não foi validado." (CMP-15).
- Com "a refazer": faixa "A conferência de {fonte} será refeita quando a fonte voltar" com link para TL-14 (PER-ANA).

**Critérios de aceite:**
- CA-TL04-01: com o pleito de Paraty 2026, o resumo mostra 10 ok, 5 avisos e 1 erro, e a conclusão "devolver para
  complementação".
- CA-TL04-02: os números aparecem em pt-BR ("3,967%", "1.222,36", "out/2024").
- CA-TL04-03: cada linha expandida tem `aria-expanded` correto e a mensagem é lida com a regra e a situação.
- CA-TL04-04: "Devolver pleito" abre o diálogo com o número de pendências e, ao confirmar, cria a minuta do ofício.
- CA-TL04-05: PER-CON de outra concessionária recebe HTTP 403.

**Wireframe:**

```
Início › Ciclos › Paraty 2026 › Validação
Validação · Águas de Paraty · vigência 01/01/2026
cadastro 3TA-2024 · layout 0.1 · regras (versão) · validado em (data e hora)
┌──────────────────┬──────────────┬──────────────────────────────────────┐
│ 10 conferências ok│ 5 avisos     │ 1 erro: devolver para complementação │
└──────────────────┴──────────────┴──────────────────────────────────────┘
[erro]  V11 Energia sem distribuidora, sem regra de composição e sem resolução da ANEEL ▸
[aviso] V03 12 meses de referência entre 12/01/2025 e 01/01/2026, mas só 354 dias ▸
[aviso] V06 Séries só com as pontas: IMO, IEE, IPA, IPQ, IPC, ICC ▸
[aviso] V07 ICC achado no IPEADATA, com menos casas que a série (1.222,356) ▸
[aviso] V08 IMO (159401): sem outro pleito do mesmo mês ▸
[aviso] V12 Pleito sem tabela tarifária vigente e proposta ▸
[ok]    V01 … V02 … V04 … V05 … V07 IPC … V08 IPA, IPQ, ICC … V09 … V10 …
[Devolver pleito]  [Ver memória de cálculo]  [Ver cadastro do contrato]
```

---

## TL-05 Memória de cálculo

**Objetivo:** mostrar cada termo da apuração com a origem de cada número, o IR refeito contra o declarado e o total
pela regra de combinação (RF-CAL-05, RNF-01, RNF-02).

**Perfis:** PER-ANA, PER-PRO, PER-REL; PER-GCA e PER-GES leem (proposto). **Rota (proposto):** `/ciclos/[id]/apuracao`.

**Dados mostrados (Paraty 2026, reais):**

| Índice | Peso | o (out/2024) | i (out/2025) | Variação | Ponderada |
|---|---|---|---|---|---|
| IMO | 0,1951 | 1.466,05 | 1.576,75 | 7,5509% | 1,4732% |
| IEE | 0,0974 | 511,75 | 471,91 | −7,7851% | −0,7583% |
| IPA | 0,1082 | 367,637 | 356,857 | −2,9322% | −0,3173% |
| IPQ | 0,0405 | 199,691 | 209,255 | 4,7894% | 0,1940% |
| IPC | 0,0662 | 761,643 | 789,092 | 3,6039% | 0,2386% |
| ICC | 0,4925 | 1.149,17 | 1.222,36 | 6,3689% | 3,1367% |

O resultado:
- IR refeito: 3,9669%, arredondado em 3 casas (cláusula 20) para 3,967%, igual ao declarado (V09 ok);
- total pela regra multiplicativa: (1 + 3,967%) × (1 + 2,72%) − 1 = 6,7949%, contra 6,795% declarado (V10 ok);
- os 2,72% são a parcela 2 do cronograma do 3º termo aditivo;
- a soma dos pesos é 0,9999, como escrita no Anexo X; o cálculo usa os pesos como escritos.

A ponderada é calculada sobre a variação sem arredondar; a coluna mostra 4 casas. A soma das ponderadas exibidas pode
diferir do IR refeito na última casa.

| Dado | Origem (CMP-05) |
|---|---|
| Peso | `Componente.peso` da versão contratual + trecho do Anexo X (`FonteRegra`) |
| o e i | `ValorMensal` do pleito, arquivo de evidência e SHA-256 |
| Valor da série pública (IPC, ICC) | `ValorSerieExterna`: IPEADATA IGP12_IPC12 e IGP12_INCC12, com data da consulta |
| Série paga (IMO, IPA, IPQ) | comparação com outros pleitos (V08); marca "série paga: uso restrito ao processo" |
| Energia (IEE) | pleito; composição pendente (V11) |
| Casas decimais | `Formula.casasDecimais` + trecho do contrato |
| Regra de combinação e parcela | `VersaoContratual.combinacao`, `ParcelaRealinhamento` + trecho do 3º termo aditivo |
| Versões usadas | cadastro, layout, regras, séries (RNF-03) |

**Ações:**
- Abrir a origem de qualquer número.
- Ver o cadastro na versão usada (TL-06).
- Ver as séries (TL-14).
- Emitir a minuta do parecer técnico (PER-ANA → TL-08, UC-05).
- Exportar a memória em PDF para juntada (RF-DOC-02).

**Componentes:** CMP-03, CMP-05, CMP-04, CMP-10, CMP-01.

**Regras de exibição:**
- Os valores de série aparecem com as casas da fonte. O IR aparece nas casas do contrato.
- Diferença acima de 0,01 p.p. (RNF-01) marca a linha do IR ou do total como erro, com os dois valores.
- Componente com série "a refazer" mostra CMP-01 a refazer na linha e não bloqueia a leitura.
- Componente com pendência de cadastro (IEE) mostra o aviso do cadastro na linha.
- Valor de série paga nunca aparece em painel público nem em exportação para fora do processo (RNF-04).

**Permissões:** ver: PER-ANA, PER-PRO, PER-REL (e leitura proposta). Agir (emitir minuta, exportar): PER-ANA.

**Estados:**
- Sem apuração: "A apuração aparece depois que o pleito passa pela validação." (CMP-15).
- Apuração incompleta (componente sem o ou i, V06 erro): tabela com a linha marcada e IR "não calculado".

**Critérios de aceite:**
- CA-TL05-01: os números de Paraty 2026 aparecem como na tabela acima.
- CA-TL05-02: o IR mostra o valor refeito com 4 casas e o arredondado com 3, lado a lado com o declarado.
- CA-TL05-03: clicar no peso 0,4925 abre o trecho do Anexo X com "trecho achado no texto".
- CA-TL05-04: a tabela tem `<caption>`, cabeçalhos com `scope` e IR e total em `<tfoot>`.
- CA-TL05-05: a 375 px a tabela rola dentro do contêiner, com rótulo acessível, e o resumo fica acima.

**Wireframe:**

```
Início › Ciclos › Paraty 2026 › Memória de cálculo
Memória de cálculo · out/2024 → out/2025 · versão 3TA-2024
┌────────────────┬───────────────┬────────────────┬──────────────┐
│ IR refeito     │ IR declarado  │ Total          │ Situação     │
│ 3,9669% → 3,967│ 3,967%        │ 6,7949% (6,795)│ [ok] V09 V10 │
└────────────────┴───────────────┴────────────────┴──────────────┘
Índice  Peso    o          i          Variação   Ponderada
IMO     0,1951  1.466,05   1.576,75    7,5509%    1,4732%
IEE     0,0974    511,75     471,91   −7,7851%   −0,7583%   [aviso] composição pendente
IPA     0,1082    367,637    356,857  −2,9322%   −0,3173%
IPQ     0,0405    199,691    209,255   4,7894%    0,1940%
IPC     0,0662    761,643    789,092   3,6039%    0,2386%
ICC     0,4925  1.149,17   1.222,36    6,3689%    3,1367%
IR (3 casas, cláusula 20)                                 3,967%
Total multiplicativo com a 2ª parcela (2,72%)             6,795%
[Emitir minuta do parecer técnico]  [Exportar PDF]
```

---

## TL-06 Cadastro do contrato: versões e parâmetros com trecho

**Objetivo:** manter o contrato, as versões contratuais com herança e cada parâmetro com o documento e o trecho
literal que o sustentam (UC-06, RF-CAD-01 a 04).

**Perfis:** PER-GCA; PER-ANA, PER-PRO, PER-REL e PER-GES leem (proposto). **Rota (proposto):** `/contratos/[id]/cadastro`.

**Dados mostrados (Paraty, reais):**

Contrato: Contrato de Concessão nº 008/2014, Águas de Paraty, saneamento. Situação: "rascunho para validação com a
CAPET".

Versões:

| Versão | Vigente desde | Ato | Herda de |
|---|---|---|---|
| contrato-2014 | — | Contrato de Concessão nº 008/2014, cláusula 20; Anexo X (Proposta Comercial) | — |
| 3TA-2024 | 16/12/2024 | 3º Termo Aditivo, cláusula quarta, em cumprimento à Deliberação AGENERSA nº 4.830/2024 | contrato-2014 |

Parâmetros:
- fórmula: índices ponderados, IR = Σ Pk × (Ik,i − Ik,o) / Ik,o;
- mês de referência: 3 meses antes da vigência; periodicidade de 12 meses; IR com 3 casas;
- seis componentes, com sigla, peso, fonte e código;
- combinação multiplicativa (3TA-2024);
- cronograma de realinhamento: parcela 1 de 6,30% em jan/2025 e parcelas 2 a 7 de 2,72%, de jan/2026 a jan/2031.

São 12 trechos, conferidos na base de textos. Exemplos reais:

| Parâmetro | Documento | Trecho |
|---|---|---|
| periodicidade | contrato | "serão reajustados a cada período de 12 (doze) meses" |
| mês de referência | contrato | "correspondente, quando do cálculo dos posteriores reajustes, ao terceiro mês anterior ao da data de início de vigência da tarifa em vigor" |
| ICC, código de série | contrato | "INCC — Índice Nacional de Preços da Construção Civil (160868)" |
| combinação | 3º termo aditivo | "que serão aplicados cumulativamente ao reajuste ordinário anual" |
| realinhamento, parcela 2 | 3º termo aditivo | "2º: a partir da referência janeiro de 2026 — 2,72%" |

Pendências do cadastro, reais:
- IEE: composição exata (TUSD + TE, tributos, bandeira) a confirmar com a CAPET. O pedido de alteração do IEE
  (SEI-480002/003110/2024) foi remetido à revisão ordinária.
- Os pesos somam 0,9999, como escritos.

**Ações (PER-GCA):**
- Criar versão por aditivo ou deliberação (a nova versão herda da anterior).
- Editar parâmetro: valor + documento + trecho obrigatório.
- Conferir o trecho na base (V02).
- Registrar pendência de parâmetro.
- Publicar a versão (CMP-22 com MSG-CNF-04).
- Manter o calendário de data-base.

**Componentes:** CMP-13, CMP-04, CMP-01, CMP-22, CMP-23, CMP-15.

**Regras de exibição:**
- Parâmetro herdado aparece com a marca "herdado de {versão}". Só os alterados aparecem em destaque.
- Parâmetro sem trecho, ou com trecho não achado, mostra CMP-01 erro e impede publicar a versão (RF-CAD-02).
- Com a base de textos fora, a conferência fica "a refazer" e a publicação fica permitida, com aviso.
- O formulário de parâmetro tem a ordem valor → documento → trecho e destaca no trecho o valor achado.

**Permissões:** agir: PER-GCA. Ver: PER-ANA, PER-PRO, PER-REL, PER-GES (proposto). PER-CON vê só o cadastro
**publicado** do próprio contrato, em TL-03, por download.

**Estados:**
- Contrato sem versão: "Este contrato ainda não tem regra de reajuste cadastrada." + "Criar versão".
- Edição não salva ao sair: diálogo "Há alterações não salvas".
- Trecho não achado: erro inline no campo, com "o texto procurado" e "o documento".

**Critérios de aceite:**
- CA-TL06-01: salvar parâmetro sem trecho é bloqueado com erro ligado ao campo (`aria-invalid`, `aria-describedby`).
- CA-TL06-02: a versão 3TA-2024 mostra a fórmula e os componentes com "herdado de contrato-2014".
- CA-TL06-03: os 12 trechos de Paraty aparecem com "trecho achado no texto".
- CA-TL06-04: a pendência do IEE aparece na linha do componente.
- CA-TL06-05: no celular a tela abre em leitura com o aviso "Para editar, use um computador".

**Wireframe:**

```
Início › Contratos › 008/2014 › Cadastro
Contrato de Concessão nº 008/2014 · Águas de Paraty      [Nova versão]
Versões: [contrato-2014] [3TA-2024 ● vigente desde 16/12/2024]
3TA-2024 · herda contrato-2014 · ato: 3º Termo Aditivo, cláusula quarta
┌──────────────────┬──────────────┬──────────────────────────────────┬────────────┐
│ Parâmetro        │ Valor        │ Fonte (trecho)                   │ Situação   │
├──────────────────┼──────────────┼──────────────────────────────────┼────────────┤
│ combinação       │ multiplicativa│"…aplicados cumulativamente ao…" │ [ok] achado│
│ realinhamento 2  │ 2,72% jan/26 │ "2º: a partir da referência…"    │ [ok] achado│
│ peso ICC (herd.) │ 0,4925       │ "…P6 = 0,4925 (zero vírgula…)"   │ [ok] achado│
│ IEE (herdado)    │ peso 0,0974  │ composição pendente              │ [aviso]    │
└──────────────────┴──────────────┴──────────────────────────────────┴────────────┘
[Publicar versão]
```

---

## TL-07 Histórico do contrato (ciclos encadeados)

**Objetivo:** mostrar os ciclos de um contrato em sequência: o mês i de um ciclo é o mês o do seguinte. Mostra também
a versão contratual usada, o IR, o total e se o recálculo confere (UC-07, RF-CAL-06).

**Perfis:** PER-ANA, PER-GES; PER-GCA, PER-PRO e PER-REL leem (proposto). **Rota (proposto):** `/contratos/[id]/historico`.

**Dados mostrados (Paraty, reais quando extraídos):**

| Ciclo (vigência) | Processo | Meses o → i | IR escrito | IR refeito | Total | Recálculo | Lead time |
|---|---|---|---|---|---|---|---|
| 01/01/2023 | SEI-220007/004053/2022 | out/2021 → out/2022 | 10,37% | 9,5601% pelos índices | 18,051% | [erro] não confere | 698 du (caso crítico) |
| 2024 | não extraído | out/2022 → out/2023 (pelo encadeamento) | não extraído | — | — | — | — |
| 12/01/2025 | não extraído | out/2023 → out/2024 (pelo encadeamento) | não extraído | — | parcela 1 de 6,30% | — | — |
| 01/01/2026 | SEI-480002/009982/2025 | out/2024 → out/2025 | 3,967% | 3,9669% | 6,795% | [ok] confere | em andamento no TO-BE |

Fontes:
- `saida/levantamento/calculo/recalculo.csv`;
- `fatos_P01.json` (`critico.lead`);
- cadastro (cronograma de realinhamento);
- tarifa em vigor desde 12/01/2025 pela Deliberação AGENERSA nº 4.857/2025 (pleito de 2026).

**Ações:**
- Abrir ciclo (TL-02).
- Abrir a versão contratual usada (TL-06).
- Comparar dois ciclos: mostra o que mudou na versão e nos índices.
- Exportar em CSV, sem séries pagas.

**Componentes:** CMP-13, CMP-01, CMP-05, CMP-06 (modo resumido: um ponto por ciclo), CMP-15.

**Regras de exibição:**
- Quebra de encadeamento (mês o de um ciclo ≠ mês i do anterior) mostra erro entre as duas linhas.
- Ciclo sem extração mostra "não extraído", nunca zero.
- Recálculo que não confere mostra os dois valores e a diferença em p.p.

**Permissões:** ver: conforme o perfil. Sem ações de escrita.

**Estados:**
- Contrato com um ciclo só: tabela com uma linha e o aviso "sem ciclo anterior para encadear".
- Vazio: "Nenhum ciclo deste contrato no sistema."

**Critérios de aceite:**
- CA-TL07-01: o ciclo de 2023 de Paraty aparece com "não confere" e os valores 10,37% e 9,5601%.
- CA-TL07-02: os meses o e i dos ciclos de 2024 e 2025, quando não registrados, aparecem como derivados do
  encadeamento, com a marca "pelo encadeamento".
- CA-TL07-03: a tabela é ordenável por vigência, com `aria-sort`.

**Wireframe:**

```
Início › Contratos › 008/2014 › Histórico
Histórico · Águas de Paraty · 4 ciclos
 2023 ──── 2024 ──── 2025 ──── 2026
 [erro]    não extr. não extr. [ok]
┌────────────┬──────────────┬─────────┬──────────┬────────┬─────────────┐
│ Vigência   │ Meses o → i  │ IR escr.│ IR refeito│ Total  │ Recálculo   │
│ 01/01/2023 │ 10/21→10/22  │ 10,37%  │ 9,5601%  │ 18,051%│ [erro] diverge│
│ 2024       │ 10/22→10/23* │ —       │ —        │ —      │ não extraído │
│ 12/01/2025 │ 10/23→10/24* │ —       │ —        │ +6,30% │ não extraído │
│ 01/01/2026 │ 10/24→10/25  │ 3,967%  │ 3,9669%  │ 6,795% │ [ok] confere │
└────────────┴──────────────┴─────────┴──────────┴────────┴─────────────┘
* pelo encadeamento (RF-CAL-06)
```

---

## TL-08 Editor de minuta com citações verificadas

**Objetivo:** revisar a minuta gerada (parecer técnico, parecer jurídico, relatório, voto, deliberação), conferir
cada citação contra a fonte e exportar a versão revisada para assinatura no SEI (UC-05, UC-11, UC-12, RF-MIN-01 a 05).

**Perfis:**
- PER-ANA: parecer técnico;
- PER-PRO: parecer jurídico;
- PER-REL: relatório, voto e deliberação.

**Rota (proposto):** `/ciclos/[id]/minutas/[peca]`.

**Dados mostrados:**

| Dado | Origem |
|---|---|
| Texto da minuta, versão e autor da última edição | `Minuta`, `EdicaoMinuta` |
| Citações: documento, dispositivo, trecho, situação (verificada, inválida, não verificada) | `Citacao` (RF-MIN-04), base de normas e deliberações (INT-05) |
| Números da minuta ligados à apuração | `Apuracao` (CMP-05) |
| Checklist legal (parecer jurídico) | requisitos R-P01 (`insumos/mapeamento/normas_P01.json`), CMP-24 |
| Taxa de edição | RF-MIN-05 (Q-P01-03) |

Citações reais para o parecer técnico de Paraty 2026:

| Citação | Trecho | Situação |
|---|---|---|
| Contrato 008/2014, cláusula 20 (periodicidade) | "serão reajustados a cada período de 12 (doze) meses" | verificada |
| Anexo X (pesos) | "… e P6 = 0,4925 (zero vírgula quatro nove dois cinco)" | verificada |
| 3º Termo Aditivo, cláusula quarta | "2º: a partir da referência janeiro de 2026 — 2,72%" | verificada |
| Lei estadual 2.869/1997, art. 8º, parágrafo único | "terá o prazo de 30 (trinta) dias para se manifestar sobre o pedido de reajuste" | verificada |
| Deliberação AGENERSA nº 4.830/2024, art. 18 | texto do artigo não está na base de textos usada pelo cadastro | não verificada (exemplo do estado) |

**Ações:**
- Editar o texto.
- Abrir uma citação, ver o trecho e trocar a citação.
- Marcar a citação inválida como resolvida (corrigir ou remover).
- Ver a diferença entre versões.
- Salvar (`Ctrl+S`).
- Exportar em DOCX ou PDF (CMP-22 com MSG-CNF-03; RF-DOC-02).
- Registrar o marco da peça depois da assinatura no SEI (TL-02).

**Componentes:** CMP-11, CMP-04, CMP-24 (checklist do parecer jurídico), CMP-05, CMP-22, CMP-23, CMP-01.

**Regras de exibição:**
- Selo fixo "Minuta — requer revisão" no topo e no rodapé do arquivo exportado até a exportação pela pessoa revisora.
- A exportação fica bloqueada enquanto houver citação "inválida". Citação "não verificada" exige confirmação
  explícita do revisor ("conferi na fonte").
- Os números ligados à apuração não são editáveis como texto livre. Para trocá-los, o revisor muda a apuração ou
  desliga o vínculo com justificativa, e isso entra na trilha (RF-ADM-02).
- A lista de citações fica ao lado do texto a partir de 1280 px e abaixo dele em telas menores.
- Os extensos (ex.: "seis inteiros e setecentos e noventa e cinco milésimos por cento") saem do motor, não da
  digitação. Isso evita o erro do Parecer CAPET nº 343/2025, que escreveu "sete inteiros, setecentos e noventa e
  cinco milésimos" para 6,795%.

**Permissões:** cada perfil edita só a peça da sua unidade; os demais internos com acesso ao ciclo veem em
somente leitura. PER-CON não tem acesso.

**Estados:**
- Minuta ainda não gerada: "A minuta do {peça} é gerada a partir da apuração." + "Gerar minuta" (dono).
- Gerando: CMP-16 "Gerando a minuta e verificando as citações".
- Modelo de linguagem indisponível (INT-06): "Não foi possível gerar a minuta agora. Você pode começar pelo modelo
  sem texto assistido." + "Usar modelo".
- Conflito de edição: MSG-ERR-06.
- Salvo: indicação discreta "Salvo às {hora}" (`role="status"`).

**Critérios de aceite:**
- CA-TL08-01: com uma citação inválida, "Exportar" fica desabilitado e o motivo é lido.
- CA-TL08-02: cada citação no texto é focável e abre o trecho com Enter.
- CA-TL08-03: cada salvamento cria uma `EdicaoMinuta` com autor, hora e diferença.
- CA-TL08-04: o arquivo DOCX exportado leva o selo e os números da apuração.
- CA-TL08-05: a barra de ferramentas tem `role="toolbar"` e navegação por setas.

**Wireframe:**

```
Início › Ciclos › Paraty 2026 › Minuta do parecer técnico
Minuta do parecer técnico · versão 3      [MINUTA — REQUER REVISÃO]
[B][I][Lista][Citação]                         Salvo às 10:42 (exemplo)
┌────────────────────────────────────────┬───────────────────────────┐
│ 1. A fórmula da cláusula 20 [1] aplica │ Citações (5)              │
│ os pesos do Anexo X [2] …              │ [1] Cl. 20   [ok] verif.  │
│ 2. O índice de reajuste é 3,967% …     │ [2] Anexo X  [ok] verif.  │
│ 3. A 2ª parcela do realinhamento [3],  │ [3] 3º TA    [ok] verif.  │
│ de 2,72%, combina-se por produto …     │ [4] Lei 2.869 [ok] verif. │
│ 4. … art. 18 da Deliberação 4.830 [5]  │ [5] Del. 4.830 [refazer]  │
│ Total: 6,795% (seis inteiros e …)      │   não verificada          │
└────────────────────────────────────────┴───────────────────────────┘
Taxa de edição desta minuta: exemplo        [Exportar DOCX] [Exportar PDF]
```

---

## TL-09 Emissão de documento por modelo

**Objetivo:** gerar peças de rotina por modelo versionado com os dados do ciclo, revisar e exportar para assinatura no
SEI (UC-09, RF-DOC-01 a 03).

**Perfis:** PER-SEC, PER-REL; PER-ANA para o ofício de complementação da devolução (proposto, UC-04). **Rota
(proposto):** `/ciclos/[id]/documentos/novo?modelo=…`.

**Modelos** (`ModeloDocumento`, MOD-DOC):
- ofício de recebimento (t1);
- ofício de complementação, com as pendências (RF-PLE-04);
- ofício único de diligência, com os quesitos (RF-DOC-03, t4/t14);
- reiteração de diligência (RF-PRZ-04, t5);
- ofício de razões finais com 10 dias (t7);
- ofício de acesso aos autos (t16);
- notificação da deliberação (t9);
- certidão de ausência de recurso (RF-PRZ-08, t12);
- termo de encerramento (t13).

**Dados mostrados:**

| Dado | Origem |
|---|---|
| Modelo e versão | `ModeloDocumento` (RF-ADM-03) |
| Campos preenchidos: contrato, concessionária, número SEI, vigência, marcos, prazo com base, pendências | `CicloReajuste`, `Marco`, `Prazo`, `ItemValidacao` |
| Prévia do documento | renderização do modelo |
| Campos que faltam | validação do modelo |

Exemplo real: o ofício de complementação de Paraty 2026 traz um quesito, a energia (V11). O texto pede a
distribuidora, a regra de composição (TUSD, TE, bandeira, tributos) e a resolução da ANEEL de cada valor usado:
511,75 em out/2024 e 471,91 em out/2025. O prazo da resposta vem da regra do modelo (exemplo).

**Ações:**
- Escolher o modelo.
- Completar os campos livres permitidos pelo modelo.
- Ver a prévia.
- Exportar em DOCX ou PDF (MSG-CNF-03).
- Registrar o marco com o número SEI da peça assinada.

**Componentes:** CMP-13 (lista de modelos), CMP-24 (campos obrigatórios), CMP-05 (dados do ciclo na prévia),
CMP-22, CMP-23.

**Regras de exibição:**
- Campo que vem do ciclo não é editável na peça. Para mudar, muda-se o dado no ciclo, com trilha.
- O prazo concedido no ofício de razões finais nunca fica abaixo de 10 dias (R-P01-04).
- A certidão só fica disponível depois do vencimento do prazo recursal sem recurso registrado.
- O termo de encerramento só fica disponível com a lista de verificação completa (R-P01-17, R-P01-18).

**Permissões:** PER-SEC: todos os modelos. PER-REL: diligência, reiteração, razões finais, acesso aos autos. PER-ANA:
ofício de complementação (proposto).

**Estados:**
- Sem modelo publicado: "Não há versão publicada do modelo {nome}. Peça ao administrador." (link TL-15 para PER-ADM).
- Campo obrigatório vazio: lista CMP-24 com o item não ok e a exportação bloqueada.

**Critérios de aceite:**
- CA-TL09-01: o ofício de complementação de Paraty lista exatamente as pendências com erro do resultado (V11).
- CA-TL09-02: a prévia é legível por leitor de tela (HTML semântico, não imagem).
- CA-TL09-03: o modelo de razões finais recusa prazo menor que 10 dias.
- CA-TL09-04: exportar registra modelo, versão e dados usados na trilha de auditoria.

**Wireframe:**

```
Início › Ciclos › Paraty 2026 › Novo documento
Emitir documento · modelo: [Ofício de complementação ▾] versão (exemplo)
┌──────────────────────────┬─────────────────────────────────────────┐
│ Dados do ciclo           │ Prévia                                  │
│ Contrato 008/2014        │ OFÍCIO Nº ___/2025 (numerado no SEI)    │
│ Vigência 01/01/2026      │ Assunto: complementação do pleito de    │
│ Pendências (1)           │ reajuste de 01/01/2026                  │
│  [erro] V11 energia      │ 1. Informar a distribuidora, a regra de │
│ Prazo: exemplo           │ composição e a resolução da ANEEL dos   │
│ [✓] campos completos     │ valores 511,75 (out/2024) e 471,91 …    │
└──────────────────────────┴─────────────────────────────────────────┘
[Exportar DOCX] [Exportar PDF] [Registrar marco]
```

---

## TL-10 Prazos e alertas (minha fila)

**Objetivo:** mostrar ao usuário os prazos e alertas da sua unidade, do mais urgente ao menos urgente, com o próximo
ato de cada ciclo (UC-08, RF-PRZ-03, RF-PRZ-09).

**Perfis:** internos. **Rota (proposto):** `/minha-fila`.

**Dados mostrados:**

| Dado | Origem |
|---|---|
| Prazo: ato, ciclo, limite, unidade (du/dc), base legal, situação | `Prazo`, `Alerta` |
| Alertas não lidos | `Alerta` (inclui os enviados por correio, INT-08) |
| Idade do ciclo na unidade | marcos e dono |
| Resumo: vencidos, vencem hoje, nos próximos 5 dias, sem dono | contagens |

Exemplos de linha (dados de exemplo, com as bases reais):
- Procuradoria: parecer jurídico em 15 dc do parecer técnico (R-P01-07);
- gabinete: diligência vencida, reiteração pronta (RF-PRZ-04);
- Secretaria: razões finais vencidas, incluir na pauta (RF-PRZ-06);
- Secretaria: prazo recursal vencido, conferir certidão (RF-PRZ-08);
- CAPET: conferência das faturas até 90 dc da publicação (R-P01-16).

**Ações:**
- Abrir o ciclo.
- Abrir a peça pronta (reiteração, certidão) em TL-09.
- Marcar alerta como lido.
- Filtrar por tipo de ato e por situação do prazo.

**Componentes:** CMP-10, CMP-09, CMP-07, CMP-08, CMP-23, CMP-15.

**Regras de exibição:**
- Ordem: vencidos, vence hoje, perto, no prazo.
- O sino do cabeçalho (CMP-19) mostra o número de alertas não lidos e abre esta tela.
- Cada linha diz o próximo ato com verbo ("Emitir reiteração", "Conferir certidão").

**Permissões:** cada perfil vê os prazos da sua unidade. PER-SEC vê também todos os ciclos sem dono. PER-GES vê
todos, só leitura.

**Estados:**
- Vazio: "Nenhum prazo da sua unidade nos próximos 30 dias." (CMP-15).
- Alerta enviado por correio com falha: aviso na linha "o alerta por correio não foi entregue" (INT-08).

**Critérios de aceite:**
- CA-TL10-01: a tela funciona a 375 px como lista de cartões, com o prazo e o próximo ato visíveis sem expandir.
- CA-TL10-02: o prazo vencido é anunciado como "venceu há {n} dias úteis".
- CA-TL10-03: a reiteração aparece na fila no dia útil seguinte ao vencimento da diligência.

**Wireframe:**

```
Início › Minha fila
Minha fila · Procuradoria (exemplo)
┌────────────┬──────────────┬────────────────┬───────────┐
│ 1 vencido  │ 0 vence hoje │ 2 em 5 dias    │ 0 sem dono│
└────────────┴──────────────┴────────────────┴───────────┘
[vencido] Parecer jurídico · Imperatriz (exemplo) · 15 dc do parecer técnico
          venceu há 2 du · próximo ato: emitir parecer jurídico   [Abrir]
[perto]   Parecer jurídico · Condessa (exemplo) · vence em 3 du   [Abrir]
```

---

## TL-11 Pauta do Conselho-Diretor

**Objetivo:** montar a pauta das sessões com os ciclos cujo prazo de razões finais venceu, e acompanhar o prazo de
deliberação (UC-13, RF-PRZ-06, M-P01-06).

**Perfis:** PER-SEC; PER-REL e PER-GES leem (proposto). **Rota (proposto):** `/pauta`.

**Dados mostrados:**

| Dado | Origem |
|---|---|
| Sessões: data, tipo | cadastro de sessões (exemplo) |
| Ciclos aptos: razões finais vencidas, relator, dias desde o ofício de razões finais | `Marco`, `Prazo` |
| Prazo de deliberação: 40 dias do ofício de razões finais | R-P01-06 |
| Vigência pretendida e antecedência de 30 dias para a publicação | `Pleito`, R-P01-09 |
| Minutas de relatório, voto e deliberação: situação | `Minuta` |

**Ações:**
- Incluir ciclo na pauta (MSG-CNF-07).
- Retirar da pauta, com justificativa.
- Registrar o resultado da sessão como marco: deliberado, pedido de vista, adiado.
- Exportar a pauta.

**Componentes:** CMP-13, CMP-07, CMP-01, CMP-22, CMP-23, CMP-15.

**Regras de exibição:**
- O ciclo apto entra sozinho na lista "a pautar" no vencimento das razões finais.
- O ciclo cujo prazo de 40 dias vence antes da próxima sessão aparece em aviso.
- O ciclo cuja vigência pretendida exige publicação antes da próxima sessão aparece em erro, com a data-limite.
  Esse caso alimenta, no AS-IS, as decisões em reunião interna (44% dos casos).
- O sistema não registra voto nem resultado sem a ação de PER-SEC (RNF-07).

**Permissões:** agir: PER-SEC. Ver: PER-REL, PER-GES (proposto).

**Estados:**
- Sem sessão marcada: "Não há sessão marcada. Cadastre a próxima sessão para pautar." (exemplo).
- Sem ciclo apto: "Nenhum ciclo com razões finais vencidas."

**Critérios de aceite:**
- CA-TL11-01: o ciclo aparece em "a pautar" no dia útil seguinte ao vencimento das razões finais.
- CA-TL11-02: o conflito com a vigência pretendida mostra a data-limite de publicação.
- CA-TL11-03: incluir na pauta pede confirmação e registra quem incluiu.

**Wireframe:**

```
Início › Pauta
Pauta do Conselho-Diretor
Próxima sessão: exemplo                                 [Exportar pauta]
A pautar (razões finais vencidas)
┌────────────────────────┬──────────────┬───────────────────┬────────────┐
│ Ciclo                  │ Razões finais│ Prazo de 40 dc    │ Minutas    │
│ Imperatriz (exemplo)   │ venceu (ex.) │ [aviso] vence ex. │ [ok] voto  │
└────────────────────────┴──────────────┴───────────────────┴────────────┘
[Incluir na pauta]
```

---

## TL-12 Remessa de faturamento e divergências

**Objetivo:**
- a concessionária envia a remessa periódica de faturamento, sem dados pessoais (UC-16, RF-FAT-01);
- a CAPET vê só as faturas que divergem da tabela homologada (UC-17, RF-FAT-02, M-P01-11).

**Perfis:** PER-CON (só a própria remessa), PER-ANA; PER-GES lê (proposto). **Rota (proposto):** `/faturas`.

**Dados mostrados:**

| Dado | Origem |
|---|---|
| Remessas: período, data de envio, faturas recebidas, conferidas, divergentes | `RemessaFaturamento`, `FaturaConferida` |
| Divergências: categoria, faixa, consumo, valor cobrado, valor pela tabela, diferença | `DivergenciaFatura` |
| Tabela homologada usada e deliberação | `Apuracao` do ciclo, `Peca` deliberação |
| Prazo de início da conferência: 90 dc da publicação | R-P01-16 |

Todos os números desta tela são **exemplo**: a coorte não tem remessa no layout.

**Ações:**
- PER-CON: enviar a remessa com validação prévia (CMP-12 em modo remessa) e ver o recibo.
- PER-ANA: abrir as divergências, marcar a divergência como "justificada" ou "a cobrar" com nota, e registrar o marco
  de início e de fim da conferência.

**Componentes:** CMP-12, CMP-10, CMP-13, CMP-01, CMP-07, CMP-23, CMP-15.

**Regras de exibição:**
- A tela lista só as divergências (RF-FAT-02). As faturas conferidas aparecem como contagem.
- Arquivo com dado pessoal é recusado (RNF-05, MSG-ERR-08).
- O prazo de 90 dias aparece no topo para a CAPET desde a publicação.

**Permissões:** PER-CON envia e vê o próprio resultado agregado (quantas divergências e por que categoria), sem a
anotação interna. PER-ANA vê e anota tudo.

**Estados:**
- Sem remessa: PER-CON: "Envie a primeira remessa do período {período}."; PER-ANA: "Nenhuma remessa recebida para
  o ciclo." com o prazo.
- Remessa sem divergência: estado ok "Todas as {n} faturas conferidas fecham com a tabela homologada."

**Critérios de aceite:**
- CA-TL12-01: a visão PER-CON funciona a 375 px, do envio ao recibo.
- CA-TL12-02: a tabela de divergências tem a diferença com sinal e unidade (R$).
- CA-TL12-03: o arquivo com coluna de CPF é recusado antes de ser guardado.

**Wireframe:**

```
Início › Faturas
Remessa de faturamento · Paraty (exemplo)     prazo de início: 90 dc da publicação
┌────────────────┬────────────────┬────────────────┐
│ 1.200 faturas  │ 1.188 fecham   │ 12 divergências│   (todos exemplo)
└────────────────┴────────────────┴────────────────┘
Categoria  Faixa    Consumo  Cobrado   Pela tabela  Diferença   Situação
Residen.   11–20 m³  15 m³   exemplo   exemplo      +exemplo    [erro] a cobrar
[Enviar remessa] (PER-CON)
```

---

## TL-13 Indicadores e auditoria contínua

**Objetivo:** acompanhar os indicadores I-P01-01 a 10 contra a linha de base e as metas do TO-BE, os testes contínuos
dos requisitos R-P01 e os controles de qualidade da IA Q-P01 (UC-18, RF-IND-01 a 03).

**Perfis:** PER-GES; PER-ANA, PER-SEC e PER-REL leem (proposto). **Rota (proposto):** `/indicadores`.

**Dados mostrados (linha de base e metas reais, de `insumos/mapeamento/controles_P01.json`):**

| Indicador | Linha de base | Metas |
|---|---|---|
| I-P01-01 Lead time do pleito ao encerramento (mediana) | 337,5 du | 155,8 · 149,3 · 145,5 du (fases 1 · 2 · 3, simulação) |
| I-P01-02 Horas por processo (teto, mediana) | 64,0 h, hipótese até a calibração | 63,4 · 60,0 · 52,3 h |
| I-P01-03 Conferência das faturas iniciada em até 90 dias | 50,0% | 100% (fase 1) |
| I-P01-04 Parecer jurídico em até 15 dias do parecer técnico | 58,8% | 76,5% (fase 1) |
| I-P01-05 Deliberação em até 40 dias das razões finais | 71,4% | 92,9% (fase 1) |
| I-P01-06 Dias sem nenhuma unidade com o processo aberto (mediana) | 41 du | 23 du (fase 1) · 5 du (fase 2) |
| I-P01-07 Pareceres de cálculo refeitos ou cancelados | 5 casos | 0 (fase 2) |
| I-P01-08 Deliberações que voltam ao Conselho depois da publicação | 16% | 16% |
| I-P01-09 Pronunciamento em até 30 dias do pleito | 17,6% | 17,6% (fase 3, simulação) |
| I-P01-10 Encerramento precedido da certidão | 25% | 100% (fase 1, norma) |

Auditoria contínua: conformidade de cada requisito R-P01 na coorte (`conformidade_P01.json`). Exemplos:
- R-P01-01 e R-P01-02: 100%;
- R-P01-04: 22,2%;
- R-P01-05: 17,6%;
- R-P01-07: 58,8%;
- R-P01-16: 50%;
- R-P01-17: 25%.

No sistema, o teste roda sobre cada ciclo (RF-IND-02).

Controles Q-P01-01 a 04: critério de aceite e amostragem de `controles_P01.json`. As medições são do sistema.

**Ações:**
- Escolher o período.
- Abrir o indicador (gráfico + tabela).
- Abrir os ciclos que falham num teste (TL-02).
- Exportar em CSV, sem séries pagas (RNF-04).

**Componentes:** CMP-10, CMP-14, CMP-13, CMP-01, CMP-05 (origem de cada valor: fato do AS-IS, simulação, norma ou
benchmark), CMP-15.

**Regras de exibição:**
- Cada valor diz a origem: fato do AS-IS (`fatos_P01.json`), simulação, norma ou benchmark.
- Indicador sem medição no sistema mostra só a linha de base e as metas, com "sem medição no período".
- Horas sempre com "hipótese até a calibração".
- O gráfico sempre tem a tabela equivalente.

**Permissões:** só leitura para todos com acesso.

**Estados:**
- Sem ciclo encerrado no período: "Ainda não há ciclos encerrados no período; os indicadores de duração aparecem com
  o primeiro encerramento."

**Critérios de aceite:**
- CA-TL13-01: as linhas de base e as metas são as da tabela acima, com a origem acessível.
- CA-TL13-02: cada gráfico tem "Ver como tabela" e resumo em texto.
- CA-TL13-03: o teste R-P01-17 lista os ciclos encerrados sem certidão, com link.

**Wireframe:**

```
Início › Indicadores
Indicadores e auditoria contínua · período: [últimos 12 meses ▾]
┌──────────────────┬──────────────────┬────────────────┬───────────────┐
│ Lead time        │ Sem dono         │ Refeitos       │ Certidão antes│
│ base 337,5 du    │ base 41 du       │ base 5 casos   │ base 25%      │
│ meta 155,8 (f1)  │ meta 23 (f1)     │ meta 0 (f2)    │ meta 100%     │
└──────────────────┴──────────────────┴────────────────┴───────────────┘
[gráfico I-P01-01: linha de base ── meta f1 ┄┄ medição ●]  [Ver como tabela]
Auditoria contínua (R-P01)       conformidade na coorte
R-P01-05 pronunciamento 30 dc    ███░░░░░░░ 17,6%
R-P01-17 certidão antes          █████░░░░░ 25,0%
```

---

## TL-14 Séries externas (situação do cache e consultas)

**Objetivo:** mostrar a situação das séries públicas e pagas, a data da última consulta, as conferências "a refazer"
e as integrações (UC-20, RF-SER-01 a 04, RNF-06).

**Perfis:** PER-ANA, PER-ADM. **Rota (proposto):** `/series`.

**Dados mostrados:**

| Série | Fonte | Código | Uso |
|---|---|---|---|
| IPC-Brasil | IPEADATA (INT-02) | IGP12_IPC12 | V07 (Paraty, IPC) |
| INCC | IPEADATA (INT-02) | IGP12_INCC12 | V07 (Paraty, ICC) |
| IPCA, IPCA-E | IBGE SIDRA (INT-03) | exemplo | V07 (contratos de índice único) |
| Tarifas e bandeiras | ANEEL dados abertos (INT-04) | exemplo | V11 |
| ICC-RJ mão de obra, IPA | FGV (INT-07, opcional) | 159401, 1006819, 1006820 | V08 (série paga) |

Os códigos das três primeiras linhas e da última são reais (cadastro de Paraty). As datas de consulta, a situação e
o tamanho do cache são exemplo.

**Ações:**
- Atualizar agora uma série (PER-ANA, PER-ADM).
- Ver os valores de uma série num mês, sem exportação de série paga.
- Reprocessar as conferências "a refazer" quando a fonte volta.
- Ver o registro de consultas.

**Componentes:** CMP-10, CMP-13, CMP-01, CMP-23, CMP-17.

**Regras de exibição:**
- Fonte fora do ar mostra "a refazer" e a data do último cache (MSG-ERR-07).
- Série paga mostra só metadados e a comparação entre pleitos, nunca a série inteira (RNF-04).
- Cada consulta registra data e hora (RF-SER-01).

**Permissões:** PER-ANA: ver e atualizar. PER-ADM: ver, atualizar, configurar a integração (em TL-15).

**Estados:**
- Nenhuma série em cache: "As séries são buscadas na primeira validação ou pela atualização agendada."
- Fonte indisponível: linha "a refazer" com "Tentar de novo".

**Critérios de aceite:**
- CA-TL14-01: com o IPEADATA simulado fora do ar (MSW), a linha mostra "a refazer" e a data do cache.
- CA-TL14-02: a série paga não tem botão de exportação.
- CA-TL14-03: "Reprocessar a refazer" mostra quantas conferências serão refeitas antes de confirmar.

**Wireframe:**

```
Início › Séries externas
Séries externas
┌────────────┬────────────┬──────────────┬────────────────┐
│ 4 fontes   │ 3 em dia   │ 1 a refazer  │ última: exemplo│
└────────────┴────────────┴──────────────┴────────────────┘
Série      Fonte      Código        Última consulta  Situação
IPC        IPEADATA   IGP12_IPC12   exemplo          [ok] em dia
INCC       IPEADATA   IGP12_INCC12  exemplo          [ok] em dia
Tarifas    ANEEL      exemplo       exemplo          [a refazer] fora do ar
ICC-RJ MO  FGV (paga) 159401        —                [aviso] sem licença: compara pleitos
[Atualizar agora] [Reprocessar a refazer]
```

---

## TL-15 Administração: usuários, perfis, modelos, integrações

**Objetivo:** gerir usuários e perfis, usuários externos vinculados à concessionária, modelos de documento com versão,
integrações e trilha de auditoria (UC-19, RF-ADM-01 a 03).

**Perfis:** PER-ADM. **Rota (proposto):** `/admin/usuarios`, `/admin/modelos`, `/admin/integracoes`, `/admin/auditoria`.

**Dados mostrados:**
- Usuários: nome, e-mail institucional, perfis, unidade, concessionária (externo), situação, último acesso.
- Modelos: nome, versão, publicada em, quem publicou.
- Integrações INT-01 a INT-08: situação, última execução, configuração (sem mostrar segredos: RNF-10).
- Trilha de auditoria: quem, o quê, quando, antes e depois (RF-ADM-02, RNF-11).

Todos os dados desta tela são **exemplo**.

**Ações:**
- Criar e editar usuário.
- Atribuir perfis.
- Vincular o externo à concessionária.
- Desativar usuário (MSG-CNF-08). Nunca excluir: a trilha mantém o histórico.
- Publicar nova versão de modelo.
- Testar a integração.
- Filtrar a trilha.

**Componentes:** CMP-13, CMP-01, CMP-22, CMP-23, CMP-15.

**Regras de exibição:**
- Segredo de integração aparece como "configurado" ou "não configurado", nunca o valor.
- A trilha é só leitura: sem botão de editar ou apagar.
- O usuário externo sem concessionária vinculada não pode ser salvo.

**Permissões:** só PER-ADM.

**Estados:**
- Integração com falha: linha em erro com a última mensagem do adaptador em linguagem de tela.
- Trilha vazia no filtro: "Nenhuma ação registrada com estes filtros."

**Critérios de aceite:**
- CA-TL15-01: o valor de um segredo não aparece no HTML nem na resposta da API.
- CA-TL15-02: desativar um usuário mantém os registros dele na trilha.
- CA-TL15-03: a publicação de modelo cria versão nova e mantém a anterior para os documentos já emitidos.

**Wireframe:**

```
Início › Administração › Usuários
Administração   [Usuários] [Modelos] [Integrações] [Trilha de auditoria]
┌──────────────────────┬────────────────┬───────────┬──────────┐
│ Usuário (exemplo)    │ Perfil         │ Unidade   │ Situação │
│ usuario.a            │ PER-ANA        │ CAPET     │ [ok] ativo│
│ externo.b            │ PER-CON        │ Paraty    │ [ok] ativo│
└──────────────────────┴────────────────┴───────────┴──────────┘
[Novo usuário]
```

---

## TL-16 Entrada (login) e escolha de perfil

**Objetivo:** autenticar o usuário interno ou externo e, se ele tiver mais de um perfil, escolher com qual vai
trabalhar (RF-ADM-01, RNF-10).

**Perfis:** todos. **Rota (proposto):** `/entrar` e `/entrar/perfil`.

**Dados mostrados:**
- Campos de usuário e senha (NextAuth, credenciais).
- Perfis do usuário com a unidade ou a concessionária.
- Aviso de privacidade (LGPD) e link de acessibilidade.

**Ações:**
- Entrar.
- Mostrar a senha.
- Esqueci a senha (fluxo do administrador; detalhe em `05_ARQUITETURA.md`).
- Escolher o perfil.
- Trocar de perfil depois, pelo menu do usuário.

**Componentes:** CMP-25, CMP-23, CMP-17. Formulário com rótulos visíveis e resumo de erros (UX-A11Y-11).

**Regras de exibição:**
- Com um só perfil, a escolha é pulada.
- Erro de credencial genérico: "Usuário ou senha não conferem." (não revela qual dos dois).
- Depois de 5 tentativas, aviso de bloqueio temporário (valor a definir em `05_ARQUITETURA.md`).
- Sem CAPTCHA de texto. Colar a senha e usar o gerenciador de senhas funcionam (WCAG 3.3.8).
- Destino depois da entrada: PER-CON vai para TL-03 (ou TL-04 se houver devolução aberta); PER-GES, para TL-13;
  PER-ADM, para TL-15; os demais, para TL-01.

**Permissões:** pública.

**Estados:**
- Sessão expirada: mensagem MSG-ERR-03 acima do formulário.
- Conta desativada: "Seu acesso foi desativado. Fale com a administração do sistema."

**Critérios de aceite:**
- CA-TL16-01: os campos têm `autocomplete="username"` e `autocomplete="current-password"`.
- CA-TL16-02: o erro é anunciado com `role="alert"` e o foco vai para o resumo de erros.
- CA-TL16-03: funciona a 375 px e com zoom de 200%.

**Wireframe:**

```
┌──────────────────────────────────────┐
│ AGENERSA · Reajusta                  │
│ Entrar                               │
│ Usuário   [______________________]   │
│ Senha     [______________] [mostrar] │
│ [Entrar]           Esqueci a senha   │
│ Acessibilidade · Privacidade         │
└──────────────────────────────────────┘
Escolha o perfil:
( ) Analista da CAPET · CAPET
( ) Gestor do cadastro · CAPET
[Continuar]
```

## Itens "(proposto)" desta especificação de telas

| Item | Proposta |
|---|---|
| Rotas | Todas as rotas `/…` acima |
| Rótulos de situação do ciclo | Tabela "Situações do ciclo" em TL-01 |
| Leitura ampliada | TL-04, TL-05, TL-06, TL-07, TL-11, TL-12, TL-13 abertas em leitura a perfis internos além dos listados no documento-base |
| PER-ANA em TL-09 | Emissão do ofício de complementação na devolução (UC-04) |
| Situação "a refazer" em V02 | Quando a base de textos está fora (o oráculo dá "aviso") |
