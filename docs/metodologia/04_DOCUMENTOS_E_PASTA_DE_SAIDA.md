# 04. Documentos para avaliação e pasta de saída

O pacote de especificação (Markdown, JSON Schema, OpenAPI, modelo de dados) é feito para quem programa e para a IA de
desenvolvimento. Quem **aprova** a especificação é outro público: gestão, área de negócio, jurídico e TI. Essas
pessoas não leem Markdown num repositório. Elas precisam de documento paginado, com capa, sumário e versão, e de um
jeito simples de devolver o parecer. Sem isso, a PARADA de aprovação vira leitura por cima ou simplesmente não
acontece.

Este capítulo diz **o que entregar para leitura, como organizar e nomear a pasta de saída e como gerar tudo por
script**. Para ver o resultado pronto, abra os PDFs do caso resolvido em
[`exemplo/reajusta/saida/documentos_para_avaliacao/`](../../exemplo/reajusta/saida/documentos_para_avaliacao/) e o
índice em [`exemplo/reajusta/saida/LEIA-ME.md`](../../exemplo/reajusta/saida/LEIA-ME.md).

## 1. Princípios

| Princípio | O que significa na prática |
|---|---|
| **Fonte única** | Escreve-se só no pacote (`especificacao/`). PDF e planilha são gerados por `gerar_documentos.py`. Ninguém edita o PDF: a correção vai na fonte e gera nova versão |
| **Um documento por público** | O caderno junta os capítulos que aquele público avalia e abre com as perguntas que ele precisa responder. A área de negócio não precisa folhear a arquitetura; a TI não precisa ler as regras de prazo |
| **Parecer item a item** | Cada requisito, regra, caso de uso, tela, teste e decisão tem identificador estável (RF-SIG-01, RN-SIG-02, TL-04...). O parecer vai numa planilha, uma linha por identificador, com lista fechada (Aprovado, Aprovado com ajustes, Não aprovado, Não se aplica) |
| **Versão em toda página** | Capa e rodapé trazem versão, data e situação ("Minuta para avaliação: não é versão aprovada"). O nome do arquivo não leva versão |
| **Sem bastidor** | Nenhum caminho da máquina (`C:\Users\...`), nenhuma frase sobre como o texto foi produzido. IA só aparece quando é função do sistema |
| **Acessível** | PDF marcado (com estrutura para leitor de tela), marcadores de navegação, idioma pt-BR, texto real (nunca imagem de texto), diagramas em vetor e tabelas com cabeçalho repetido a cada página |
| **Reprodutível e conferido** | A geração só roda com a especificação conferida (capítulo 03, §4), e tem portões próprios: fonte inexistente, caminho local, diagrama que não desenhou e nome fora do padrão param a geração. A conferência acusa documento desatualizado em relação à fonte |

## 2. O conjunto de documentos

Tudo em `saida/documentos_para_avaliacao/`, na ordem em que o avaliador usa:

| Arquivo | Conteúdo | Para quem |
|---|---|---|
| `00_Guia_de_avaliacao.pdf` | Quem avalia o quê, como registrar o parecer, decisões pendentes, lista de arquivos e significado dos identificadores | Todos (é o primeiro a abrir) |
| `01_Caderno_Gestao.pdf` | Visão e escopo, perfis e jornadas, backlog e entregas | Dirigente e gestor do processo |
| `02_Caderno_Area_de_Negocio.pdf` | Requisitos, casos de uso e estados, regras de negócio, telas, testes de aceitação | Unidade que executa o processo |
| `03_Caderno_Juridico.pdf` | Visão e escopo, regras de negócio, operação e LGPD | Procuradoria ou assessoria jurídica |
| `04_Caderno_TI.pdf` | Arquitetura e ADRs, modelo de dados, contratos e API, integrações, interface, operação, segurança | TI e segurança |
| `05_Planilha_de_avaliacao.xlsx` | Um item avaliável por linha, com Parecer em lista, ajuste pedido, avaliador e data; aba de decisões pendentes | Todos os avaliadores |
| `06_Especificacao_completa.pdf` | Todos os capítulos em ordem, com sumário de dois níveis | Quem confere a coerência entre capítulos; equipe de desenvolvimento |
| `07_Prototipo_de_telas.pdf` | Cada tela do protótipo em página paisagem, com o identificador TL | Área de negócio, gestão e TI |
| `capitulos/NN_<Nome>.pdf` | Um PDF por capítulo, com o mesmo conteúdo dos cadernos | Quem quer um capítulo sozinho (enviar por e-mail, juntar ao processo) |

Quantos cadernos, com que nome e com que capítulos é decisão do órgão: está no `especificacao/documentos.json`
(seção 5). A regra é que **todo capítulo esteja em pelo menos um caderno** e que **todo item avaliável tenha um
público** na planilha.

Por que PDF e planilha, e não Word: o PDF preserva paginação, diagramas e numeração em qualquer computador e pode ser
juntado ao processo administrativo; a planilha recebe o parecer de forma estruturada, que se consolida por script
(seção 7). Se uma área insistir em comentar no Word, converta a fonte (por exemplo, com `pandoc capitulo.md -o
capitulo.docx`) só para ela, e traga os comentários para a planilha. A fonte continua sendo o Markdown.

## 3. Anatomia de cada documento

1. **Capa:** órgão, nome do pacote, título do documento, selo "Minuta para avaliação: não é versão aprovada" e uma
   ficha com sistema, versão, data, situação, para quem e leitura estimada. Logo abaixo, a caixa **O que avaliar**,
   com 2 a 4 perguntas fechadas para aquele público e a instrução de registrar o parecer na planilha.
2. **Sumário** com links internos. Nos cadernos, capítulos e seções; no capítulo avulso, as seções.
3. **Corpo:** cada capítulo começa em página nova, com título no formato `NN. Nome`, igual ao do nome do arquivo e ao
   do sumário. Links para outros capítulos viram link interno quando o capítulo está no mesmo documento e
   "(documento NN, Nome)" quando não está.
4. **Cabeçalho:** órgão e pacote à esquerda, título do documento à direita.
5. **Rodapé:** versão, data e situação à esquerda; "Página X de Y" à direita.
6. **Marcadores do PDF** (o painel lateral do leitor de PDF) com capítulos e seções.

A data é a do último commit que mexeu no pacote. A leitura estimada é calculada pelo número de palavras (150 por
minuto, texto técnico). Os comentários de orientação dos modelos (`<!-- ... -->`) não aparecem no PDF.

## 4. Pasta de saída: organização e nomes

```
saida/
├── LEIA-ME.md                     índice gerado: cada arquivo, o que é, para quem, quem produz
├── levantamento/                  dados que sustentam a especificação
│   ├── casos/                     um arquivo por caso real: valores copiados das peças, com a origem
│   ├── regras/                    parâmetros e regras com trecho literal e vigência
│   └── conferencias/              resultado refeito por script: o que confere e o que diverge, com a causa
├── documentos_para_avaliacao/     versões de leitura (geradas; não editar)
│   ├── 00_Guia_de_avaliacao.pdf
│   ├── 01_Caderno_Gestao.pdf … 04_Caderno_TI.pdf
│   ├── 05_Planilha_de_avaliacao.xlsx
│   ├── 06_Especificacao_completa.pdf
│   ├── 07_Prototipo_de_telas.pdf
│   └── capitulos/01_Visao_e_escopo.pdf … 15_Seguranca.pdf
└── pareceres/                     o retorno das áreas (fora do git: tem o nome dos avaliadores)
    ├── recebidos/                 planilhas devolvidas (Area_AAAA-MM-DD.xlsx)
    └── 00_Consolidado_dos_pareceres.xlsx
```

Regras:

1. **Toda pasta de saída tem um `LEIA-ME.md` gerado por script.** Ele lista cada arquivo, o que é, para quem e qual
   script o produz. Quem abre a pasta pela primeira vez entende tudo sem perguntar.
2. **Subpasta pelo que o conteúdo é, não pela fase do projeto.** `levantamento/` e `documentos_para_avaliacao/`
   dizem o que há dentro; `fase5/`, `etapa3/` e `novos/` não dizem nada a quem não acompanhou o projeto.
3. **Documento para pessoas: `NN_Palavras_com_sublinhado.ext`.** `NN` é a ordem de leitura, com dois dígitos. Sem
   acento, sem espaço, sem caractere especial: o nome sobrevive a e-mail, sistema de processo, zip e qualquer sistema
   operacional. A acentuação correta fica no título dentro do documento.
4. **Nada de versão, data, "final", "novo" ou "revisado" no nome.** A versão está na capa e no rodapé, e o histórico no
   git. `Especificacao_v2_final_revisada.pdf` é o sintoma que esta regra evita.
5. **O nome diz o conteúdo para quem não conhece o projeto.** `03_Caderno_Juridico.pdf`, e não `cad3.pdf` nem
   `spec_jur.pdf`. Sigla interna (MOD-SIG, código do processo) vai dentro do documento, não no nome.
6. **Dado para máquina pode ter nome de máquina**, como `caso_<numero-do-processo>.json`, porque é lido por script.
   Ele fica em subpasta própria e tem uma linha no `LEIA-ME.md` dizendo o que é (padrões em `descricao_saida`).
7. **Nada solto na raiz de `saida/`** além do `LEIA-ME.md`.
8. **Arquivo gerado não se edita.** O `LEIA-ME.md` diz qual script o produz. Correção vai na fonte ou no script.

| Ruim | Bom | Por quê |
|---|---|---|
| `saida/fase5/calculo/` | `saida/levantamento/conferencias/` | A pasta diz o conteúdo, não a fase |
| `Especificação Sistema v1.2 FINAL.pdf` | `06_Especificacao_completa.pdf` | Sem espaço, acento e versão; a versão está no rodapé |
| `doc_ti.pdf` | `04_Caderno_TI.pdf` | Ordem de leitura e público no nome |
| `planilha.xlsx` | `05_Planilha_de_avaliacao.xlsx` | O nome diz para que serve |
| PDF editado no leitor para corrigir um número | Correção no Markdown e nova geração | Fonte única: o PDF não pode divergir do pacote |

## 5. Como gerar

```bash
python -m playwright install chromium
```

```bash
python scripts/gerar_documentos.py --projeto <pasta do projeto>
```

O script primeiro roda a conferência (capítulo 03, §4) e para se houver erro. Depois gera tudo em cerca de um minuto
e precisa de rede, para a fonte tipográfica e a biblioteca que desenha os diagramas. `--rapido` gera só o guia, a
planilha e o `LEIA-ME.md`.

Tudo o que muda de um órgão para outro está em `especificacao/documentos.json`:

| Campo | Para quê |
|---|---|
| `sistema`, `titulo_pacote`, `subtitulo`, `orgao`, `versao`, `situacao` | Capa, cabeçalho e rodapé. Suba a `versao` a cada rodada de avaliação; troque `situacao` para "Versão aprovada" depois da PARADA |
| `capitulos` | Cada capítulo: número, fontes (aceita padrão, como `especificacao/adr/[0-9]*.md`, que vira anexo), nome do arquivo e título. Relatórios do levantamento podem entrar como capítulos 16 em diante |
| `cadernos` | Cada caderno: arquivo, título, público, perguntas da caixa "O que avaliar" e capítulos |
| `itens_avaliaveis` | Prefixo de identificador → capítulo dono. A planilha pega o item de lá (título `### RF-SIG-01 ...` ou primeira célula de tabela), uma vez só |
| `prefixos_extras` | Prefixos próprios do seu sistema, com o significado, para o guia |
| `decisoes_pendentes` | Arquivo e seção com a tabela de decisões (Decisão, Quem decide, Situação hoje) |
| `prototipo` | HTML do protótipo; cada `section[data-tela]` vira uma ou mais páginas paisagem |
| `termos_bloqueados` | Expressões que param a geração (por padrão, frases que dizem que o documento foi feito por IA) |
| `termos_permitidos` | Termos do caso resolvido que são legítimos no seu domínio, com justificativa ([capítulo 05](05_USO_DO_EXEMPLO.md)) |
| `descricao_saida` | Descrição dos arquivos de `saida/levantamento/` no `LEIA-ME.md` |

**Portões** (a geração para): erro na conferência; fonte inexistente; caminho local da máquina no texto; diagrama que
não desenhou; termo bloqueado; nome de arquivo fora do padrão. **Avisos** (a geração segue, a revisão é humana):
avisos da conferência e menções a IA, modelo de linguagem ou nome de ferramenta, listadas por capítulo. Se a menção é
função do sistema, fica; se comenta como o documento foi feito, sai da fonte.

**Atualização:** `python scripts/conferir_especificacao.py --projeto <pasta> --documentos` compara a impressão digital
da fonte gravada no `LEIA-ME.md` com a fonte atual (C17). Mudou a fonte, gere de novo.

## 6. Revisão humana antes de enviar

O script garante forma; a leitura garante conteúdo. Antes de mandar às áreas, abra e confira:

- [ ] O guia: a tabela "Quem avalia o quê" e as decisões pendentes estão certas?
- [ ] Uma página de cada caderno com tabela larga e uma com diagrama: legíveis?
- [ ] O protótipo: as telas estão inteiras e na ordem?
- [ ] A planilha: filtre por público; cada área tem os itens que de fato lhe cabem?
- [ ] Os avisos: cada menção a IA é função do sistema? Cada aviso da conferência foi tratado?

## 7. O ciclo de avaliação

1. **Gerar** a versão (por exemplo, 1.0, "Minuta para avaliação") e fazer o commit.
2. **Enviar** a cada área o guia, o caderno dela e a planilha, com prazo. Os PDFs podem ser juntados ao processo
   administrativo da especificação.
3. **Receber** as planilhas preenchidas em `saida/pareceres/recebidos/` (sugestão de nome: `Juridico_AAAA-MM-DD.xlsx`).
4. **Consolidar:** `python scripts/consolidar_pareceres.py --projeto <pasta>` gera
   `saida/pareceres/00_Consolidado_dos_pareceres.xlsx`. Ele traz um item por linha, com o parecer mais restritivo como
   situação consolidada (Não aprovado > Aprovado com ajustes > Aprovado > Não se aplica) e todos os comentários. A aba
   "Sem parecer" lista o que ninguém avaliou, para cobrar. A aba "Decisões" junta as decisões que as áreas
   registraram.
5. **Tratar:** para cada "Não aprovado" e "Aprovado com ajustes", corrija a fonte e registre na coluna "Tratamento" o
   que mudou. Decisão tomada vai para a fonte (o documento 08 e o README do pacote).
6. **Nova versão:** suba a `versao` (1.1), gere de novo e reenvie só o que mudou, com a lista de mudanças.
7. **Aprovar:** sem "Não aprovado" aberto e com as decisões tomadas, troque a `situacao` para "Versão aprovada em
   DD/MM/AAAA" e gere a versão final. Essa é a saída da PARADA 11.

## 8. Lista de verificação para a IA

Antes de dizer ao aluno que os documentos estão prontos:

- [ ] `python scripts/conferir_especificacao.py --projeto <pasta>` sem erro, e cada aviso tratado ou justificado.
- [ ] `python scripts/gerar_documentos.py --projeto <pasta>` rodou sem erro e os avisos foram lidos.
- [ ] Todo capítulo novo do pacote está em `documentos.json` e em pelo menos um caderno.
- [ ] Todo prefixo de identificador novo está em `itens_avaliaveis`.
- [ ] Nenhum arquivo foi criado à mão em `saida/documentos_para_avaliacao/`.
- [ ] O `LEIA-ME.md` de `saida/` foi gerado de novo e descreve cada arquivo.
- [ ] Versão e situação em `documentos.json` correspondem ao momento (minuta, revisão, aprovada).
- [ ] Mostrou ao aluno as páginas da seção 6 e esperou a revisão dele antes do envio às áreas.
