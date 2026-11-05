# Especificação do sistema {{Nome do sistema}}

<!-- COMO PREENCHER: este README é a porta de entrada do pacote. Ele deriva de todos os outros documentos e é o
último a fechar. Regras: capítulo 03 da metodologia (docs/metodologia/03_PLANEJAMENTO_DA_ESPECIFICACAO.md), §1 (ordem
dos documentos) e §3.5 (decisões pendentes). Pronto quando: a ordem de leitura aponta os 15 documentos e o
AGENTS_DESENVOLVIMENTO; toda decisão pendente do 08 está na tabela "Decisões pendentes" com quem decide e o padrão
provisório; os limites dizem o que ainda é hipótese. O equivalente do caso resolvido é
exemplo/reajusta/especificacao/README.md. Ele serve só de referência de formato e de nível de detalhe: não copie
nenhuma frase, nome ou termo dele. -->

{{Uma ou duas frases: o que o sistema faz, para qual processo do órgão e qual onda do TO-BE este pacote cobre}}

Este pacote sai do mapeamento do processo e do levantamento de casos reais e de regras. Nada nele é invenção: cada
requisito, regra e teste indica de onde veio, seja uma melhoria do TO-BE, uma norma, uma cláusula ou um caso com
resultado conhecido.

## Ordem de leitura

<!-- Mantenha a ordem e os nomes de arquivo. Acrescente na coluna "Para quê" o que for próprio do seu sistema
(por exemplo, as pastas adr/, contratos/, fixtures/ e prototipos/ quando existirem). -->

| # | Documento | Para quê |
|---|---|---|
| 01 | [Visão, escopo e identificadores](01_VISAO_ESCOPO.md) | O ponto de partida: problema, metas com linha de base, quadro de escopo, ondas e a lista de todos os identificadores |
| 02 | [Perfis e jornadas](02_PERFIS_E_JORNADAS.md) | As pessoas que usam o sistema, as dores medidas, o caminho de ponta a ponta e a navegação entre telas |
| 03 | [Requisitos](03_REQUISITOS.md) | O que o sistema deve fazer, funcional e não funcional, cada item com origem e critério de aceite |
| 04 | [Casos de uso](04_CASOS_DE_USO.md) | Objetivos de cada ator, diagramas de sequência e a máquina de estados do objeto do processo |
| 05 | [Arquitetura](05_ARQUITETURA.md) e [decisões registradas](adr/) | Contexto, contêineres, componentes por módulo, camadas e decisões de arquitetura |
| 06 | [Modelo de dados](06_MODELO_DADOS.md) | Entidades, atributos com origem do dado, relacionamentos e integridade |
| 07 | [Contratos e API](07_CONTRATOS_API.md) | Operações da API, esquemas do dado que vem de fora e convenções de erro |
| 08 | [Regras de negócio](08_REGRAS_NEGOCIO.md) | Regras com trecho literal da fonte e exemplo de caso real; decisões pendentes |
| 09 | [Integrações](09_INTEGRACOES.md) | Uma ficha por sistema externo, com o que fazer quando ele falha |
| 10 | [Experiência e interface](10_UX_UI.md) | Princípios de interface, componentes reutilizáveis, mensagens e acessibilidade |
| 11 | [Telas](11_TELAS.md) | Cada tela com dados, ações, estados e critérios de aceite |
| 12 | [Testes de aceitação](12_TESTES.md) | Testes tirados de casos reais e a matriz de rastreabilidade |
| 13 | [Backlog e entregas](13_BACKLOG.md) | Épicos, histórias, releases e as definições de pronto |
| 14 | [Operação](14_OPERACAO.md) | Permissões, auditoria, dados pessoais, ambientes e implantação |
| 15 | [Segurança](15_SEGURANCA.md) | Requisitos de segurança, nível de verificação adotado e resposta a incidente |
| — | [Regras para quem desenvolve](AGENTS_DESENVOLVIMENTO.md) | Camadas, proibições, portões e definição de pronto para a IA de desenvolvimento |

## Versões de leitura para avaliação

As áreas do órgão não leem estes arquivos em Markdown. Elas avaliam por PDFs e por uma planilha de parecer, gerados a
partir deste pacote pelo comando `python scripts/gerar_documentos.py --projeto {{Pasta do projeto}}`, rodado na raiz
do repositório-framework. Os arquivos vão para `saida/documentos_para_avaliacao/`.

[documentos.json](documentos.json) define o que vira documento, para qual público e com que nome. Antes de gerar, o
script roda o conferidor e para se houver erro. O método está no capítulo 04 da metodologia.

## Como a IA de desenvolvimento usa o pacote

1. No repositório do sistema, o `AGENTS_DESENVOLVIMENTO.md` vira `AGENTS.md` na raiz, e este pacote vai para
   `docs/especificacao/`.
2. A IA pega uma história do [backlog](13_BACKLOG.md) de cada vez, seguindo a ordem das releases. Antes de escrever
   código, lê os requisitos, casos de uso, regras e telas que a história cita.
3. O teste de aceitação vem primeiro, com o fixture do caso real. Depois vem a regra no domínio, então a porta e o
   adaptador, e por fim a tela, montada com os componentes do inventário do 10.
4. A história só é dada como pronta quando cumpre a definição de pronto do backlog.
5. Dúvida de regra não se resolve no código. Ela vira uma decisão pendente no 08 e uma linha na tabela abaixo.

## Decisões pendentes

<!-- A primeira tabela desta seção é lida pelo gerador da planilha de avaliação: não mude o título da seção nem os
nomes das colunas, e não ponha subtítulo antes da tabela. Uma linha por decisão em aberto: as de negócio (DEC-nn,
detalhadas no 08), as de TI (onde o sistema roda, integrações, provedores) e os bloqueios de teste. Na terceira
coluna, diga o que o sistema faz enquanto ninguém decide e onde isso está escrito. -->

| Decisão | Quem decide | Situação hoje (padrão adotado até a decisão) |
|---|---|---|
| DEC-01 {{O que precisa ser decidido, numa frase}} | {{Unidade ou cargo que decide}} | {{Padrão provisório que o sistema adota e a regra ou o requisito onde ele está}} |
| {{Decisão de TI, por exemplo onde o sistema vai rodar}} | {{Unidade de TI do órgão}} | {{Proposta registrada em ADR-0001, válida até a avaliação da TI}} |

## Limites

<!-- Diga com franqueza o que ainda não foi conferido. Quem avalia precisa saber o que é fato e o que é hipótese. -->

- Todo número de horas ou de custo é estimativa e só vale depois de conferido com quem executa o processo.
- {{O que ainda não foi validado com a área de negócio, por exemplo uma regra ou um caso real}}
- {{Dado ou insumo que falta e o que muda quando ele chegar}}

## Pronto quando

- [ ] A ordem de leitura aponta os 15 documentos e o AGENTS_DESENVOLVIMENTO, todos existentes.
- [ ] Toda decisão pendente do 08 aparece na tabela acima, com quem decide e o padrão provisório.
- [ ] As decisões de TI e os bloqueios de teste também estão na tabela.
- [ ] Os limites dizem o que é hipótese e o que ainda não foi validado.
- [ ] Nenhum marcador de preenchimento ficou no texto.
