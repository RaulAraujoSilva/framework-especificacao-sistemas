# Instruções para a IA de desenvolvimento do {{Nome do sistema}}

<!-- COMO PREENCHER: este arquivo deriva da arquitetura (05), dos testes (12), do backlog (13), do glossário (01) e das
decisões pendentes (08). Siga o capítulo 03 da metodologia, §3.14. Ele é copiado como AGENTS.md (e, se a ferramenta
pedir, como CLAUDE.md) na raiz do repositório do sistema, e a IA de desenvolvimento o lê antes de cada tarefa. Escreva
ordens curtas e verificáveis, sempre apontando o documento do pacote que manda. Pronto quando: o glossário, as camadas,
os pontos de reuso, as proibições, os portões com os comandos, a regra de commit, a definição de pronto e a lista do
que perguntar a um humano estão preenchidos com os nomes deste sistema. O arquivo equivalente do caso resolvido
(exemplo/reajusta/especificacao/AGENTS_DESENVOLVIMENTO.md) serve só de referência de formato e de nível de detalhe:
não copie termo, função, proibição nem frase dele. -->

Este arquivo vale para toda tarefa no repositório do {{Nome do sistema}}. Leia tudo antes de começar e volte a ele
quando tiver dúvida. A especificação fica em `docs/especificacao/`; os caminhos abaixo são relativos a essa pasta.

O {{Nome do sistema}} {{Uma frase: o que o sistema faz, para qual processo e para quem}}. **Ele não {{Atos que ficam com
as pessoas, por exemplo assinar, decidir ou publicar}}** (RNF-01).

## 1. Antes de cada tarefa

1. Leia a história no [`13_BACKLOG.md`](13_BACKLOG.md) e abra cada identificador que ela cita (RF, RNF, UC, RN, TL,
   AT) no documento dono: [`03_REQUISITOS.md`](03_REQUISITOS.md), [`04_CASOS_DE_USO.md`](04_CASOS_DE_USO.md),
   [`08_REGRAS_NEGOCIO.md`](08_REGRAS_NEGOCIO.md), [`11_TELAS.md`](11_TELAS.md), [`12_TESTES.md`](12_TESTES.md).
2. Veja no [`05_ARQUITETURA.md`](05_ARQUITETURA.md) a camada, a pasta e a porta de cada parte do trabalho, e no
   [`06_MODELO_DADOS.md`](06_MODELO_DADOS.md) as entidades e as regras de integridade envolvidas.
3. Procure o que já existe (§4). Escreva só o que falta.
4. Se a tarefa pede algo que a especificação não diz, pare e pergunte (§10). Não preencha a lacuna por conta própria.

## 2. Linguagem do domínio

Os nomes do código (entidades, funções, variáveis, arquivos, rotas, textos de tela) usam os termos do glossário do
[`01_VISAO_ESCOPO.md`](01_VISAO_ESCOPO.md), em {{Idioma do código: português sem acento ou outro}}, sem tradução e sem
sinônimo.

<!-- Uma linha por termo do glossário que aparece no código. A coluna "Não use" lista os sinônimos e as traduções que a
IA tende a escolher sozinha. -->

| Termo do glossário | No código | Não use |
|---|---|---|
| {{Termo}} | `{{Nome no código}}` | {{Sinônimos e traduções}} |

Convenções de nome:

| Item | Convenção | Exemplo |
|---|---|---|
| Tipos, entidades e componentes de tela | {{Convenção da linguagem}} | `{{Exemplo}}` |
| Funções e variáveis | {{Convenção}}; função começa por verbo | `{{Exemplo}}` |
| Parâmetro com fonte | constante com a origem em comentário | `{{NOME_DO_PARAMETRO}}` com a RN ao lado |
| Arquivos e pastas | {{Convenção}} | `{{Exemplo}}` |
| Identificadores da especificação | iguais aos do pacote, em testes e comentários | `RF-{{SIG}}-01`, `AT-01` |

## 3. Camadas e dependências

A dependência só aponta para dentro. A tabela completa e a configuração da ferramenta estão no `05_ARQUITETURA.md` §5 e
§6.

| Camada | Pasta | Pode depender de | Nunca depende de |
|---|---|---|---|
| contratos | `{{Pasta}}` | biblioteca de esquema | outra camada |
| domínio | `{{Pasta}}` | contratos, domínio, bibliotecas puras | framework, banco, rede, arquivo, relógio do sistema, variável de ambiente |
| portas | `{{Pasta}}` | tipos do domínio, contratos | implementação |
| aplicação | `{{Pasta}}` | domínio, portas, contratos | adaptadores, interface, infraestrutura |
| adaptadores | `{{Pasta}}` | portas, tipos do domínio, contratos | aplicação, interface, outro adaptador |
| composição | `{{Pasta}}` | todas, exceto interface | — |
| interface | `{{Pasta}}` | aplicação pela composição, contratos, tipos do domínio | banco, adaptadores, funções de regra |

Entre módulos do domínio vale a matriz do `05_ARQUITETURA.md` §4.3, sempre pelo ponto de entrada do módulo. Import
proibido derruba o portão G-03. A saída é mover o código para a camada certa; afrouxar a regra nunca é saída.

## 4. Reuso: onde procurar antes de escrever

Duplicar regra ou componente é defeito, mesmo que o teste passe.

**Interface.** As telas usam só os componentes do inventário do [`10_UX_UI.md`](10_UX_UI.md) (CMP-01 e seguintes), em
`{{Pasta dos componentes}}`, e só os tokens de cor, espaço e tipografia definidos lá. Os textos vêm do guia de
mensagens do 10, em `{{Pasta das mensagens}}`. Componente que falta no inventário é pedido (§10), não improviso.

**Domínio.** As funções abaixo são a única casa de cada regra (05 §9). Chame-as; não refaça a conta na tela, no
adaptador nem no teste de outra camada.

<!-- Uma linha por necessidade comum: datas e prazos, números decimais, resultado de falha esperada, parâmetros com
origem, permissão, e as regras centrais de cada módulo. -->

| Precisa de | Use | Onde |
|---|---|---|
| Data civil, dias úteis, vencimento de prazo | `{{Funções de calendário}}` | `{{Arquivo no domínio comum}}` |
| Número decimal e arredondamento | `{{Funções numéricas}}` | `{{Arquivo no domínio comum}}` |
| Falha esperada | `{{Tipo de resultado}}` | `{{Arquivo no domínio comum}}` |
| Parâmetro com origem | `{{Constantes ou leitura de parâmetro vigente}}` | `{{Arquivo no domínio comum}}` |
| Permissão | `{{Função de permissão}}` | `{{Pasta do módulo no domínio}}` |
| {{Regra central do módulo}} | `{{Função}}` | `{{Pasta do módulo no domínio}}` |

Não crie pastas genéricas de utilidades. Função nova vai para o módulo certo, com teste, exportada pelo ponto de
entrada dele.

## 5. Proibições

<!-- As linhas abaixo valem para quase todo sistema. Acrescente as do seu domínio (por exemplo, dado com licença
restrita que não pode sair do sistema). -->

| ID | Proibido | Faça assim |
|---|---|---|
| P-01 | Regra de negócio em tela, rota, rotina agendada ou adaptador | regra no domínio, orquestração na aplicação |
| P-02 | Número de negócio escrito no código (prazo, limite, percentual, casas decimais) | parâmetro com fonte (05 §9) ou parâmetro vigente no banco (06 §4); número sem fonte é pergunta (§10) |
| P-03 | Acesso ao mundo de fora fora de adaptador (rede, banco, arquivo, correio, serviço externo) | porta, adaptador e ligação na composição |
| P-04 | Relógio do sistema ou número aleatório no domínio e na aplicação | porta `Relogio`; valor recebido como parâmetro |
| P-05 | Ponto flutuante binário para valor com casas decimais significativas | tipo decimal (06 MD-05) |
| P-06 | Dado pessoal em log, mensagem de erro, endereço ou token | só o identificador do usuário (05 §13) |
| P-07 | Segredo no código, no repositório ou no log; leitura de variável de ambiente fora da composição | configuração validada (05 §14) |
| P-08 | Alterar ou apagar registro que é prova (dado recebido, resultado, trilha, versão de parâmetro usada) | registro novo que aponta o anterior (06 §7) |
| P-09 | Executar ato reservado a pessoa ({{Assinar, decidir, publicar}}) | o sistema prepara; a pessoa confirma |
| P-10 | Tipagem frouxa ou supressão de erro do verificador de tipos sem justificativa escrita | tipos explícitos; validação na borda |
| P-11 | Fazer o portão passar desativando ou enfraquecendo um teste, uma regra de lint, a cobertura mínima ou a verificação de dependências | corrigir a causa |
| P-12 | Editar o esperado de um fixture para o teste passar | corrigir o sistema; se o fixture estiver errado, pedir decisão (§10) |
| P-13 | Dependência nova, troca de biblioteca, imagem ou serviço novo | pedir (§10); se aprovado, ADR novo (15, SEG-SUP-04) |
| P-14 | Funcionalidade fora do escopo do 01 | não fazer; perguntar |
| P-15 | Nome de pessoa real ou caminho de máquina em código, fixture, carga inicial ou mensagem | dado sintético e caminho relativo ao repositório |

## 6. Testes antes do código, com os fixtures

1. **Ache o caso de aceitação.** Os testes AT-01 e seguintes do [`12_TESTES.md`](12_TESTES.md) têm o resultado
   esperado tirado de casos reais. Os fixtures ficam em `docs/especificacao/fixtures/`: leia de lá, não copie.
2. **Escreva o teste primeiro e veja-o falhar.**
3. **Implemente de dentro para fora:** domínio até passar; depois porta e adaptador (com dublê ou banco de teste);
   depois o caso de uso (com as portas em memória); por último a tela, com os componentes do inventário.
4. **Cubra os casos negativos** que a especificação cita: dado ausente ou inválido, regra não atendida, sistema externo
   fora do ar, perfil sem permissão, registro fora do escopo, transição de estado proibida.
5. Teste de tela usa só dados de fixture e usuários de teste. Nunca dado real de pessoa.

## 7. Portões

Uma tarefa só termina com todos os portões verdes. Rode `{{Comando que roda os portões locais}}` antes de cada commit.

| ID | Portão | Comando | Critério |
|---|---|---|---|
| G-01 | Tipos | `{{Comando}}` | zero erro |
| G-02 | Lint | `{{Comando}}` | zero erro e zero aviso |
| G-03 | Regra de dependência | `{{Comando}}` | zero violação (05 §6) |
| G-04 | Testes de unidade e de aplicação | `{{Comando}}` | todos passam |
| G-05 | Cobertura do domínio | `{{Comando}}` | pelo menos {{Percentual}} de linhas e ramos |
| G-06 | Esquema do banco | `{{Comando}}` | esquema válido; migração gerada e versionada |
| G-07 | Integração | `{{Comando}}` | adaptadores e regras de integridade verdes |
| G-08 | Ponta a ponta e acessibilidade | `{{Comando}}` | fluxos da release verdes; nenhuma violação WCAG 2.2 AA séria ou crítica |
| G-09 | Segurança | `{{Comando}}` | verificações de pedido de integração do 15 §16 verdes |
| G-10 | Build | `{{Comando}}` | sem erro |

{{Quais portões rodam a cada commit e quais só na integração contínua}}.

## 8. Commits

- Mensagem em português, com prefixo convencional (`feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `build`, `ci`)
  e o módulo como escopo, em minúsculas: `feat({{Sigla do módulo em minúsculas}}): ...`.
- Título no imperativo, com até 72 caracteres, dizendo o efeito.
- Corpo com o que mudou, por quê e os identificadores atendidos; rodapé `História: HIS-{{SIG}}-01`.
- Um commit por passo verde, com o teste e o código juntos. Nunca commit com portão vermelho.
- Migração do banco em commit próprio.
- Nunca commitar arquivo de ambiente, segredo, dependências instaladas, build ou dado com nome ou e-mail de terceiros.

## 9. Como pegar uma história e quando ela está pronta

1. Pegue a próxima história (HIS-{{SIG}}-01 e seguintes) do `13_BACKLOG.md`, na ordem das releases, que cumpra a
   Definition of Ready e não tenha dependência aberta.
2. Leia os identificadores que ela cita (§1) e escreva um plano curto: arquivos por camada, testes, portas.
3. Se uma parte depende de decisão pendente (§10), implemente o comportamento provisório e avise; não decida.
4. Avance em passos pequenos: teste, código, portões, commit.
5. A história está pronta quando cumpre a Definition of Done do 13. O mínimo verificável é:
   - [ ] cada critério Dado/Quando/Então da história tem teste automatizado;
   - [ ] todos os portões da §7 verdes;
   - [ ] nenhuma proibição da §5 na diferença inteira;
   - [ ] toda ação que muda dado grava a trilha de auditoria, com teste;
   - [ ] tela nova com os estados vazio, carregando, erro, sem permissão e sucesso (11), só com componentes do
     inventário e textos do guia;
   - [ ] documentação do pacote atualizada se a história mudou contrato, modelo de dados ou regra (07, 06, 08).
6. No relato final, liste o que mudou, quais identificadores a entrega cumpre, que testes entraram e o que continua
   pendente.

## 10. O que perguntar a um humano

Pare e pergunte, com as opções e a sua recomendação, sempre que a tarefa tocar um dos itens abaixo.

**Decisões pendentes.** Estão no [`08_REGRAS_NEGOCIO.md`](08_REGRAS_NEGOCIO.md) e no README do pacote. Implemente o
comportamento provisório e deixe a decisão em parâmetro ou configuração, nunca no código.

| DEC | Decisão | Quem decide | Comportamento até lá |
|---|---|---|---|
| DEC-01 | {{Decisão}} | {{Quem decide}} | {{Padrão provisório}} |

**Pergunte sempre antes de:**

- usar um número que não está nas fontes do pacote;
- acrescentar entidade, campo, enum, perfil, permissão, tela, rota ou regra que a especificação não tem;
- mudar o esquema de um dado que vem de fora (é contrato com quem envia);
- instalar dependência, trocar biblioteca, criar serviço ou mudar a stack;
- criar componente fora do inventário do 10;
- mudar o sentido de um texto que o usuário externo lê;
- tocar em dado de produção, fazer migração destrutiva ou mudar permissão do banco;
- {{Outro ponto em que este sistema exige decisão humana}}.

## 11. Segurança e privacidade

- Toda rota exige sessão, salvo a lista fechada do 15 (SEG-AUZ-01). Toda ação passa pela verificação de permissão no
  caso de uso; esconder o botão na tela não é controle.
- {{Regra de escopo: quem só vê os próprios registros}}. Toda leitura filtra pelo escopo da sessão, e há teste de
  acesso cruzado.
- Dado de fora é validado contra o esquema do 07 antes de gravar; arquivo tem tipo e tamanho conferidos e nome que
  nunca vira caminho (15 §5).
- Nada de dado real de pessoa em teste, fixture, carga inicial ou exemplo.
- Segredo só pela configuração (05 §14); nunca no código, no log ou na saída da integração contínua.
- Os requisitos completos e a forma de verificá-los estão no [`15_SEGURANCA.md`](15_SEGURANCA.md).

## Pronto quando

- [ ] Glossário da §2 com todos os termos que aparecem no código.
- [ ] Pastas, comandos e funções de reuso preenchidos com os nomes deste sistema.
- [ ] Proibições do domínio acrescentadas às da base.
- [ ] Portões com os comandos reais, iguais aos da integração contínua.
- [ ] Decisões pendentes da §10 iguais às do 08, com o comportamento provisório.
- [ ] Nenhum marcador `{{...}}` sobrou.
