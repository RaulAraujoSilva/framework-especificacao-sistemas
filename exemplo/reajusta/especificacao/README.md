# Especificação do sistema Reajusta (reajuste tarifário anual, P01)

Pacote de especificação pronto para o desenvolvimento assistido por IA. É o ponto de parada da Aula 2 (PARADA 11 do
roteiro): daqui em diante começa o desenvolvimento.

O pacote nasce do mapeamento do SEI (aula 1) e do levantamento do piloto (fase 5). Cada requisito aponta a sua origem:
melhoria do TO-BE, requisito legal, cláusula de contrato ou caso real com resultado conhecido.

## Ordem de leitura

| # | Documento | Para quê |
|---|---|---|
| 01 | [01_VISAO_ESCOPO.md](01_VISAO_ESCOPO.md) | Problema, metas, escopo, stack e **todos os identificadores** (módulos, perfis, glossário, UC, RF, RNF, entidades, telas, integrações, releases) |
| 02 | [02_PERFIS_E_JORNADAS.md](02_PERFIS_E_JORNADAS.md) | Quem usa, o que dói hoje, a jornada de um ciclo e o mapa de navegação |
| 03 | [03_REQUISITOS.md](03_REQUISITOS.md) | Requisitos com origem, critério de aceite e rastreabilidade |
| 04 | [04_CASOS_DE_USO.md](04_CASOS_DE_USO.md) | Casos de uso, sequências e estados do ciclo |
| 05 | [05_ARQUITETURA.md](05_ARQUITETURA.md) e [adr/](adr/) | Camadas, portas e adaptadores, estrutura de pastas, decisões registradas (ADR-0001 a ADR-0013; 0012 cadeia de suprimentos, 0013 implantação no Railway) |
| 06 | [06_MODELO_DADOS.md](06_MODELO_DADOS.md) e [prisma/schema.prisma](prisma/schema.prisma) | Entidades, atributos, integridade |
| 07 | [07_CONTRATOS_API.md](07_CONTRATOS_API.md) e [contratos/](contratos/) | JSON Schemas e OpenAPI |
| 08 | [08_REGRAS_NEGOCIO.md](08_REGRAS_NEGOCIO.md) | Regras de cálculo, validação, prazos e encerramento, com exemplo real |
| 09 | [09_INTEGRACOES.md](09_INTEGRACOES.md) | SEI, IPEADATA, IBGE, ANEEL, base do Especialista, modelo de linguagem |
| 10 | [10_UX_UI.md](10_UX_UI.md) | Princípios, tokens gov.br sobre Tailwind, componentes reutilizáveis, mensagens, acessibilidade |
| 11 | [11_TELAS.md](11_TELAS.md) e [prototipos/wireframes.html](prototipos/wireframes.html) | Cada tela com dados, ações, estados e critérios de aceite; protótipo navegável |
| 12 | [12_TESTES.md](12_TESTES.md) e [fixtures/](fixtures/) | Testes de aceitação com o resultado esperado tirado dos autos |
| 13 | [13_BACKLOG.md](13_BACKLOG.md) | Épicos, histórias com critérios Dado/Quando/Então, releases, Definition of Ready e Done |
| 14 | [14_OPERACAO.md](14_OPERACAO.md) | Permissões, autenticação, auditoria, LGPD, ambientes, implantação |
| 15 | [15_SEGURANCA.md](15_SEGURANCA.md) | Requisitos de segurança SEG-* (ASVS 5.0 nível 2), cadeia de suprimentos, gestão de vulnerabilidades e matriz de verificações |
| — | [AGENTS_DESENVOLVIMENTO.md](AGENTS_DESENVOLVIMENTO.md) | Regras de código que a IA de desenvolvimento lê antes de cada tarefa |

## Versões de leitura para avaliação

As áreas da agência avaliam o pacote pelos PDFs e pela planilha de `saida/documentos_para_avaliacao/`, gerados deste
pacote por `python scripts/gerar_documentos.py`. O que vira documento, para qual público e com que nome está em
[documentos.json](documentos.json). Método no capítulo 04 da metodologia do repositório (documentos e pasta de saída).

## Como a IA de desenvolvimento usa o pacote

1. Copiar `AGENTS_DESENVOLVIMENTO.md` como `AGENTS.md` (e `CLAUDE.md`) na raiz do repositório do sistema, e este
   pacote para `docs/especificacao/`.
2. Trabalhar uma história do [backlog](13_BACKLOG.md) por vez, na ordem das releases. Antes de codar, ler os RF, UC,
   RN e TL que a história cita.
3. Escrever primeiro o teste com o fixture de aceite. Implementar no domínio, depois porta e adaptador, por último a
   tela com os componentes do inventário.
4. Fechar a história só com a Definition of Done do backlog cumprida.

A implementação em Python (`scripts/validar_pleito.py`, `scripts/recalcular_reajuste.py`) é a referência: em caso de
divergência entre o sistema e ela nos fixtures, o sistema está errado até prova em contrário.

## PARADA 11: o que precisa de decisão humana antes do desenvolvimento

| Decisão | Quem | Situação |
|---|---|---|
| Regra de composição da energia (distribuidora, TUSD + TE, tributos, bandeira, mês da resolução) | CAPET | aberta; o sistema exige o dado e marca erro (V11) até decidir |
| Interstício por mês de referência ou por dia | CAPET e Procuradoria | aberta; o sistema dá aviso |
| Instrumento que torna o layout do pleito obrigatório | Procuradoria e Conselho-Diretor | aberta |
| Integração com o SEI por webservice | TI | aberta; a release R1 funciona com troca manual |
| Onde o sistema roda (infraestrutura da agência ou nuvem) | TI | decidido para a aula 3: Railway ([ADR-0013](adr/0013-deploy-railway.md)); produção com dado real depende da TI |
| Provedor do modelo de linguagem e política de dados | TI e Procuradoria | provedor decidido: OpenRouter (adendo do ADR-0006); política de dados e transferência internacional ainda abertas (`15_SEGURANCA.md`) |
| Divergência do parecer de Paraty 2022 | CAPET | a confirmar pela planilha anexa |
| Decisões de negócio DEC-01 a DEC-08 (energia, interstício, instrumento, tabela nas faturas, marcos dos prazos, arredondamento, parcela fora do mês, Paraty 2022) | CAPET, Procuradoria | [08_REGRAS_NEGOCIO.md](08_REGRAS_NEGOCIO.md) §11, com o padrão adotado até a decisão |
| Divergências DIV-01 a DIV-07 entre o sistema e o oráculo Python (o sistema é mais estrito) | CAPET e quem aprova o aceite | [05_ARQUITETURA.md](05_ARQUITETURA.md) §16 |
| Decisões de TI DA-ARQ-01 a 03 (arquivos, exportação do SEI, exportação da base do Especialista) e valores de operação (sessão, backup, retenção) | TI | [05_ARQUITETURA.md](05_ARQUITETURA.md) §18 e [14_OPERACAO.md](14_OPERACAO.md) |
| Bloqueios de teste: AT-07 precisa do cadastro de Águas da Imperatriz; AT-08, do 1º e do 2º aditivos de Paraty | CAPET (gestor do cadastro) | [12_TESTES.md](12_TESTES.md) |

## Limites

- Horas, custos e metas de horas são hipótese até a calibração com servidores.
- A extração dos cálculos dos casos foi feita por IA e conferida pela aritmética, não por um segundo leitor.
- O cadastro de Paraty e o layout do pleito ainda não foram validados com a CAPET.
