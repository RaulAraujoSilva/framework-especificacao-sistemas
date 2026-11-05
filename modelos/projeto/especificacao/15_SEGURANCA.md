# 15. Segurança

<!-- COMO PREENCHER: este documento deriva da matriz de permissões, da autenticação, da trilha e do inventário de dados
pessoais do 14, das entradas de dado de fora (07 e 09) e da arquitetura (05). Siga o capítulo 03 da metodologia, §3.13
(operação e segurança) e §2 (identificadores: requisito de segurança é SEG-SIG-nn, definido como linha de tabela).
Pronto quando: o nível do OWASP ASVS 5.0 está escolhido e cada capítulo dele diz se aplica; todo requisito tem origem,
critério de aceite verificável, release e forma de verificar; os prazos de correção de vulnerabilidade estão
aprovados; toda exceção tem risco, mitigação, dono e prazo; a matriz diz quando cada verificação roda e se bloqueia.

As tabelas abaixo trazem uma linha de base genérica para sistema web público. Revise cada linha: mantenha, ajuste ou
retire com o motivo. Os valores "(proposto)" são pontos de partida; os marcadores {{...}} são onde o órgão decide. O
arquivo equivalente do caso resolvido (exemplo/reajusta/especificacao/15_SEGURANCA.md) serve só de referência de
formato e de nível de detalhe: não copie requisito, valor nem frase dele. -->

Requisitos de segurança do {{Nome do sistema}}. Cada linha diz de onde vem, como se aceita e que teste ou ferramenta
confirma.

- **Referência:** OWASP ASVS 5.0, nível {{Nível do ASVS adotado: 1, 2 ou 3}}. A coluna "Origem" cita o capítulo do
  ASVS (V1 a V17) e a seção do pacote que pede a mesma coisa.
- **Complementa o 14.** Matriz de permissões, autenticação, trilha, LGPD, segredos e implantação estão no
  [14](14_OPERACAO.md); aqui fica o requisito verificável de cada um e o que faltava.
- **Valores "(proposto)"** são parâmetros de partida, a confirmar com a TI; mudar o valor não muda o requisito.
- **Quem verifica.** {{Quem faz a auditoria de segurança antes de cada release}}. Quem audita não é quem construiu.
- **Onde bloqueia.** O que impede o merge ou a implantação é a integração contínua (§16); verificação local só avisa.

Colunas: **ID**, **Requisito**, **Origem**, **Critério de aceite** (verificável por teste ou inspeção), **Release** (as
do [01](01_VISAO_ESCOPO.md)) e **Verificação** (teste ou ferramenta).

## 1. Alcance pelo ASVS 5.0

<!-- Para cada capítulo, diga se aplica e, se não aplica, por quê (por exemplo: "o sistema não usa WebRTC"). Capítulo
que aplica aponta a seção deste documento que o cobre. -->

| Capítulo do ASVS 5.0 | Seção deste documento | Situação |
|---|---|---|
| V1 Codificação e higienização da saída | §5 | {{Aplica ou não aplica, com o motivo}} |
| V2 Validação e lógica de negócio | §5, §7 | {{Aplica ou não aplica, com o motivo}} |
| V3 Segurança do front-end web | §3, §6 | {{Aplica ou não aplica, com o motivo}} |
| V4 API e serviços web | §5, §6 | {{Aplica ou não aplica, com o motivo}} |
| V5 Tratamento de arquivos | §5 | {{Aplica ou não aplica, com o motivo}} |
| V6 Autenticação | §2 | {{Aplica ou não aplica, com o motivo}} |
| V7 Gestão de sessão | §3 | {{Aplica ou não aplica, com o motivo}} |
| V8 Autorização | §4 | {{Aplica ou não aplica, com o motivo}} |
| V9 Tokens autocontidos | §3 | {{Aplica ou não aplica, com o motivo}} |
| V10 OAuth e OIDC | §2 | {{Aplica se houver login único ou provedor de identidade}} |
| V11 Criptografia | §2, §10 | {{Aplica ou não aplica, com o motivo}} |
| V12 Comunicação segura | §6, §10 | {{Aplica ou não aplica, com o motivo}} |
| V13 Configuração | §8 | {{Aplica ou não aplica, com o motivo}} |
| V14 Proteção de dados | §10 | {{Aplica ou não aplica, com o motivo}} |
| V15 Codificação segura e arquitetura | §11, §12 | {{Aplica ou não aplica, com o motivo}} |
| V16 Registro de segurança e tratamento de erro | §9 | {{Aplica ou não aplica, com o motivo}} |
| V17 WebRTC | — | {{Aplica ou não aplica, com o motivo}} |

## 2. Autenticação

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-AUT-01 | Com autenticação própria, a senha é guardada só como hash de algoritmo feito para senha (Argon2id, scrypt ou bcrypt), com parâmetros de custo registrados. Aceita de {{Mínimo}} a pelo menos 64 caracteres (proposto), qualquer caractere, sem regra de composição e sem troca periódica forçada; senha que consta de lista de senhas vazadas ou comuns é recusada | ASVS V6, V11; 14 §2 | Senha abaixo do mínimo e senha da lista são recusadas; o valor gravado identifica o algoritmo e os parâmetros, e estes não ficam abaixo do mínimo | {{Release}} | teste de unidade da política de senha |
| SEG-AUT-02 | A falha de entrada dá a mesma resposta, no mesmo tempo aproximado, para usuário inexistente, senha errada e conta bloqueada ou desativada | ASVS V6 | As três situações devolvem resposta idêntica; o caminho do usuário inexistente também executa o cálculo do hash | {{Release}} | teste de integração |
| SEG-AUT-03 | Depois de {{Número}} falhas seguidas, a conta fica bloqueada por {{Minutos}} minutos (proposto); falha e bloqueio vão para a trilha, sem a senha digitada | ASVS V6; 14 §2, §3 | Durante o bloqueio, até a senha correta é recusada; a trilha tem um registro por falha | {{Release}} | teste de integração |
| SEG-AUT-04 | Primeiro acesso e recuperação usam credencial provisória de uso único, válida por {{Horas}} horas (proposto); com ela, o sistema só permite a troca de senha; a troca pede a senha atual e revoga as sessões abertas | ASVS V6; 14 §2 | Credencial provisória usada duas vezes, ou vencida, é recusada | {{Release}} | teste de integração |
| SEG-AUT-05 | Segundo fator para {{Perfis}}, a partir de {{Release ou data}} | ASVS V6 | {{Critério, ou "ver exceção EXC-SEG-01"}} | {{Release}} | {{Verificação}} |
| SEG-AUT-06 | Com login único ou provedor de identidade ({{Provedor}}), o sistema valida emissor, público, assinatura e validade do token recebido e liga a identidade externa a um usuário cadastrado; identidade sem cadastro não entra | ASVS V10; 14 §2 | Token de outro emissor, vencido ou com assinatura inválida é recusado | {{Release}} | teste de integração com token forjado |
| SEG-AUT-07 | Nenhuma credencial de usuário de teste no repositório; a carga de usuários de teste não roda em produção | ASVS V13; 14 §5 | Varredura de segredos sem achado; carga de teste com ambiente de produção termina em erro sem criar nada | {{Release}} | SEG-TST-03; teste da carga inicial |

## 3. Sessão

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-SES-01 | O cookie de sessão tem `HttpOnly`, `Secure`, `SameSite` e prefixo `__Host-`; nenhum token fica em armazenamento do navegador acessível por script | ASVS V3, V7; 14 §2 | O cookie lido no teste de navegador tem os atributos; nenhum token em `localStorage` ou `sessionStorage` | {{Release}} | teste ponta a ponta; regra de SAST |
| SEG-SES-02 | A sessão expira por inatividade e por tempo total (14 §2), conferidos no servidor a cada requisição | ASVS V7; 14 §2 | Requisição depois do limite responde 401 e leva à tela de entrada | {{Release}} | teste com relógio fixo (porta `Relogio`) |
| SEG-SES-03 | Sair, trocar a senha, desativar o usuário ou mudar seus perfis invalida as sessões abertas dele | ASVS V7 | A requisição com a sessão antiga, depois da troca, responde 401 | {{Release}} | teste de integração |
| SEG-SES-04 | Token de sessão autocontido, se usado, leva só identificadores (usuário, perfis, vínculo, versão da sessão, instantes) e é assinado com segredo de pelo menos 32 bytes aleatórios; a partida recusa segredo menor | ASVS V9, V11; 14 §2 | O token decodificado não tem nome, e-mail nem CPF; segredo curto impede a partida | {{Release}} | teste de unidade; validação da configuração |
| SEG-SES-05 | Toda mutação autenticada por cookie confere a origem da requisição (cabeçalho `Origin` ou token anti-CSRF); origem ausente ou diferente responde 403 | ASVS V3 | Mutação com cookie válido vinda de outra origem é recusada | {{Release}} | teste de integração |

## 4. Autorização

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-AUZ-01 | Negar por padrão: toda rota exige sessão, salvo uma lista fechada de rotas públicas ({{Entrada, saúde, arquivos estáticos}}) mantida num só arquivo | ASVS V8 | Percorrendo o OpenAPI, toda operação sem sessão responde 401 | {{Release}} | teste gerado do `contratos/openapi.yaml` |
| SEG-AUZ-02 | Todo caso de uso confere a permissão no servidor antes de agir. A matriz do 14 §1 é a fonte única: um teste compara a matriz com a função de permissão e com o `x-perfis` de cada operação | ASVS V8; 14 §1 | Nenhuma diferença entre matriz, código e OpenAPI; perfil fora da operação responde 403 | {{Release}} | teste gerado da matriz |
| SEG-AUZ-03 | Escopo por titularidade: {{Regra de escopo do 14 §1}}. O filtro fica na aplicação e na consulta ao banco, nunca só na tela; recurso fora do escopo responde 404 e a tentativa vai para a trilha | ASVS V8; 14 §1 | Para cada operação que recebe o identificador de um registro, inclusive a de baixar arquivo, um teste tenta alcançar registro de outro titular e recebe 404 | {{Release}} | teste de integração; teste ponta a ponta |
| SEG-AUZ-04 | Arquivo só é entregue por rota que confere a permissão sobre o registro dono; nada é servido direto do armazenamento | ASVS V5, V8 | Pedir um arquivo de outro titular pelo identificador correto responde 404 | {{Release}} | teste de integração |
| SEG-AUZ-05 | Segregação de funções do 14 §1: {{Pares de ações proibidos para a mesma pessoa}} | ASVS V2, V8; 14 §1 | A mesma pessoa nas duas ações recebe 422 `regra-negocio`, com registro na trilha | {{Release}} | teste de unidade do domínio |

## 5. Validação de entrada e arquivos

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-ENT-01 | Toda entrada é validada na borda contra o esquema do 07 (corpo, consulta, caminho e cabeçalhos usados); propriedade desconhecida é recusada e nada é gravado | ASVS V2, V4; 07 §4 | Dado de fora com um campo a mais responde 422 `fora-do-esquema`, sem linha nova no banco nem arquivo novo | {{Release}} | teste de integração |
| SEG-ENT-02 | Tamanho máximo: corpo {{MiB}} MiB, cada arquivo {{MiB}} MiB, até {{Número}} arquivos por envio (proposto); acima do limite, 413 antes de ler o corpo inteiro, e a leitura conta os bytes mesmo com tamanho declarado falso | ASVS V4, V5 | Corpo acima do limite recusado sem pico de memória do tamanho do corpo | {{Release}} | teste de integração |
| SEG-ENT-03 | O tipo do arquivo é conferido pelo conteúdo (assinatura do formato), não pela extensão nem pelo tipo declarado; aceitos só {{Formatos aceitos}} | ASVS V5 | Arquivo de outro tipo renomeado com extensão aceita é recusado com 415 | {{Release}} | teste de integração |
| SEG-ENT-04 | Nome de arquivo nunca vira caminho: a chave de armazenamento é gerada pelo sistema; o nome original é guardado só como texto, sem separadores de pasta nem caracteres de controle; o download vai como anexo, com `X-Content-Type-Options: nosniff` | ASVS V5 | Arquivo chamado `../../x` é guardado sob chave gerada, dentro da pasta de arquivos | {{Release}} | teste de integração |
| SEG-ENT-05 | Arquivo recebido não é executado, e só é aberto ou convertido no servidor quando o caso de uso exige, com limite de tamanho, de páginas ou de linhas e de tempo (proposto) | ASVS V5 | Arquivo acima dos limites é recusado sem derrubar o processo | {{Release}} | teste de integração |
| SEG-ENT-06 | Dado pessoal que o processo não precisa é recusado na entrada ({{Quais campos e quais padrões}}); a mensagem aponta o campo sem repetir o valor | ASVS V14; 14 §4 | Nem a resposta, nem o log, nem a trilha repetem o valor recusado | {{Release}} | teste de integração |
| SEG-ENT-07 | Saída sempre codificada para o contexto: a tela não injeta HTML vindo de dado; consultas ao banco só parametrizadas; planilha exportada neutraliza célula de texto que começa com `=`, `+`, `-` ou `@` | ASVS V1 | SAST sem achado; célula `=1+1` exportada sai como texto | {{Release}} | SEG-TST-01; teste de unidade da exportação |
| SEG-ENT-08 | Endereço de saída nunca vem do usuário: os endereços das integrações vêm da configuração, só por HTTPS e de uma lista de hosts permitidos; endereço interno ou de metadados de nuvem é recusado | ASVS V12, V13; 09 §1 | Configurar um host fora da lista ou um endereço interno é recusado e registrado | {{Release}} | teste de unidade da configuração |

## 6. Cabeçalhos HTTP e política de conteúdo (CSP)

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-CAB-01 | CSP restritiva com nonce por requisição: origem própria por padrão, `object-src 'none'`, `base-uri 'self'`, `frame-ancestors 'none'`, `form-action 'self'`; sem `'unsafe-inline'` nem `'unsafe-eval'` em `script-src` fora do desenvolvimento. {{Exceções necessárias, com o motivo}} | ASVS V3 | Toda página tem o cabeçalho, com nonce diferente a cada requisição; nenhuma violação de CSP no teste ponta a ponta | {{Release}} | teste de integração; teste ponta a ponta |
| SEG-CAB-02 | Só HTTPS, com `Strict-Transport-Security` de pelo menos um ano (proposto); HTTP é redirecionado na borda | ASVS V12 | Resposta de homologação com o cabeçalho; pedido em HTTP redirecionado | {{Release}} | conferência na implantação |
| SEG-CAB-03 | Em toda resposta: `X-Content-Type-Options: nosniff`, `Referrer-Policy` restritiva, `Permissions-Policy` negando recursos não usados, proteção contra enquadramento e isolamento de origem; sem cabeçalho que revele tecnologia ou versão do servidor | ASVS V3, V13 | Os cabeçalhos presentes em página, API, download e respostas de erro | {{Release}} | teste de integração |
| SEG-CAB-04 | Resposta autenticada e da API com `Cache-Control: no-store`; só os arquivos estáticos versionados têm cache longo | ASVS V14 | Resposta de uma operação autenticada traz `no-store` | {{Release}} | teste de integração |
| SEG-CAB-05 | CORS fechado: {{Nenhuma origem externa, ou lista fechada de origens}} | ASVS V3, V4 | Pré-verificação vinda de origem não listada não recebe permissão | {{Release}} | teste de integração |

## 7. Limite de requisições

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-LIM-01 | Entrada (login): no máximo {{Número}} tentativas a cada {{Minutos}} minutos por endereço de origem (proposto), além do bloqueio por conta (SEG-AUT-03); acima, 429 com `Retry-After` | ASVS V2, V6 | A tentativa acima do limite responde 429 com `Retry-After` | {{Release}} | teste de integração |
| SEG-LIM-02 | Operações caras ({{Envio de arquivo, geração de documento, consulta a sistema externo}}): no máximo {{Número}} por hora por usuário (proposto) | ASVS V2 | Acima do limite, 429; reenvio com a mesma chave de idempotência não conta | {{Release}} | teste de integração |
| SEG-LIM-03 | O endereço de origem contado é o informado pela borda confiável; o sistema desconsidera o cabeçalho de encaminhamento que vem do próprio cliente. Se houver várias instâncias, a contagem passa a um armazenamento que todas compartilham | ASVS V2 | Cabeçalho de encaminhamento forjado não muda o endereço contado | {{Release}} | teste de integração |

## 8. Segredos e configuração

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-SEC-01 | Nenhum segredo no repositório, na imagem, no log ou na saída da integração contínua; só a composição lê variável de ambiente (05 §14) | ASVS V13; 14 §5 | Varredura de segredos sem achado na diferença, no histórico e na imagem | {{Release}} | SEG-TST-03 |
| SEG-SEC-02 | Inventário de segredos com dono, data da última troca e da próxima (14 §5); troca imediata em incidente ou saída de pessoa com acesso | ASVS V13; 14 §5 | Inventário existe e nenhum segredo está com a troca vencida | {{Release}} | relatório periódico (SEG-VUL-05) |
| SEG-SEC-03 | Menor privilégio: credencial de implantação restrita a um ambiente; permissões mínimas em cada fluxo da integração contínua; papel do banco da aplicação sem permissão de esquema | ASVS V13, V8 | Nenhum fluxo com permissão de escrita ampla; o papel da aplicação não cria tabela | {{Release}} | revisão na auditoria (SEG-TST-07) |
| SEG-SEC-04 | A configuração falha fechada: valor ausente, mal formado ou igual ao do arquivo de exemplo, em homologação ou produção, encerra a partida | ASVS V13; 05 §14 | Partida com segredo de exemplo em produção termina em erro | {{Release}} | teste de unidade da configuração |

## 9. Registro e erro

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-LOG-01 | Eventos de segurança na trilha (14 §3): entrada, saída, falha de autenticação, bloqueio, negação de permissão, tentativa fora do escopo, troca de senha e de perfil, exportação; cada um com identificador de correlação | ASVS V16; 14 §3 | Cada evento da lista gera um registro no teste, sem senha nem token | {{Release}} | teste de integração |
| SEG-LOG-02 | Log técnico sem dado pessoal, segredo ou conteúdo de documento (05 §13) | ASVS V16; 14 §7.2 | Teste percorre as rotas com esses campos e falha se algum aparecer no log | {{Release}} | teste de integração |
| SEG-LOG-03 | Resposta de erro sem detalhe técnico (pilha, SQL, caminho, versão); erro interno leva só `codigo` e `correlacao_id` (07 §2.4) | ASVS V16, V13 | Falha forçada num adaptador responde 500 só com os dois campos | {{Release}} | teste de integração; SEG-TST-04 |
| SEG-LOG-04 | Alerta de segurança para {{Perfil ou equipe}} quando houver {{Número}} falhas de entrada em {{Minutos}} minutos (proposto), tentativa fora do escopo ou falha das verificações periódicas | ASVS V16; 14 §7.4 | A simulação acima do limiar gera um alerta | {{Release}} | teste de integração |
| SEG-LOG-05 | Instantes em UTC na trilha e no log; retenção da trilha e dos logs registrada (14 §3) | ASVS V16 | Registro com instante em UTC; retenção configurada conforme o 14 | {{Release}} | inspeção na auditoria |

## 10. Proteção de dados

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-DAD-01 | Minimização do 14 §4; teste, fixture, carga inicial e exemplo nunca têm dado real de pessoa | ASVS V14; 14 §4 | Regra de SAST para CPF e e-mail literais sem achado em testes e fixtures | {{Release}} | SEG-TST-01 |
| SEG-DAD-02 | Em trânsito: HTTPS entre navegador e borda; banco e serviços internos só em rede privada; integrações por HTTPS ({{Exceções registradas}}) | ASVS V12 | Nenhuma porta pública além da aplicação web | {{Release}} | conferência na implantação |
| SEG-DAD-03 | Em repouso: {{Cifra do disco ou do banco}}; cópias de segurança cifradas e guardadas fora do ambiente de origem (14 §7.1) | ASVS V14, V11 | Cópia independente existe e foi restaurada no último teste | {{Release}} | registro do teste de restauração |
| SEG-DAD-04 | Localização do dado registrada; dado guardado fora do Brasil só com a decisão da área jurídica (Lei 13.709/2018, art. 33) | ASVS V14; 14 §4 | Região registrada antes da carga de dado real | {{Release}} | inspeção na auditoria |
| SEG-DAD-05 | No navegador, nada sensível em armazenamento local; nenhum dado pessoal em endereço ou parâmetro de consulta | ASVS V14, V3 | Regras de SAST correspondentes sem achado | {{Release}} | SEG-TST-01 |

## 11. Dependências e cadeia de suprimentos

<!-- Registre a política num ADR de cadeia de suprimentos. Os prazos e a quarentena são propostos; a TI ajusta. -->

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-SUP-01 | Arquivo de travamento de versões versionado; instalação reprodutível na integração contínua e na imagem; um só registro de pacotes | ASVS V15 | Instalação falha com o arquivo de travamento fora de sincronia | {{Release}} | integração contínua |
| SEG-SUP-02 | Versão recém-publicada de dependência, imagem base ou ação da integração contínua só entra depois de {{Dias}} dias (proposto); correção de vulnerabilidade conhecida entra sem espera, sempre com revisão humana | ASVS V15 | Nenhuma atualização com versão mais nova que a quarentena, salvo as de segurança | {{Release}} | configuração da ferramenta de atualização |
| SEG-SUP-03 | Atualização chega por pedido de integração automático, com a integração contínua completa e merge humano; nada entra por merge automático | ASVS V15 | Ferramenta de atualização sem merge automático | {{Release}} | inspeção na auditoria |
| SEG-SUP-04 | Dependência nova, troca de biblioteca, imagem nova ou serviço novo exige ADR e decisão humana; a integração contínua falha o pedido que acrescenta dependência sem ADR no mesmo pedido | ASVS V15; AGENTS_DESENVOLVIMENTO | Pedido que acrescenta pacote sem ADR fica vermelho | {{Release}} | integração contínua |
| SEG-SUP-05 | Inventário de componentes (SBOM, formato {{CycloneDX ou SPDX}}) a cada build, da aplicação e da imagem, guardado com a versão | ASVS V15 | Cada build publica os dois inventários | {{Release}} | integração contínua |
| SEG-SUP-06 | Proveniência: ações da integração contínua fixadas por hash de commit; imagens base por digest; a imagem promovida a produção é a mesma (mesmo digest) aprovada em homologação | ASVS V15 | Nenhuma ação referida por etiqueta móvel; digests iguais nos dois ambientes | {{Release}} | integração contínua; implantação |
| SEG-SUP-07 | Componentes em versão suportada pelo fornecedor; versão de pré-lançamento (beta, rc, nightly) não entra; atraso além de {{Prazo}} (proposto) vira registro para tratamento | ASVS V15 | Relatório periódico lista os componentes atrasados e os de pré-lançamento | {{Release}} | relatório periódico |

## 12. Gestão de vulnerabilidades

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-VUL-01 | Varredura periódica do inventário de componentes contra bases públicas de vulnerabilidades ({{Bases consultadas, por exemplo OSV, GitHub Advisory e o catálogo CISA KEV}}); fonte fora do ar aparece como falha, não como zero achado | ASVS V15 | O resumo de cada execução lista cada fonte, a data e o número de achados | {{Release}} | rotina periódica |
| SEG-VUL-02 | Cada achado é triado: a versão afetada está em uso? o código alcança a parte vulnerável? há exploração ativa? A triagem propõe; baixar a severidade ou fechar o achado exige decisão humana registrada | ASVS V15 | Todo achado fechado tem quem decidiu e a evidência | {{Release}} | registro de vulnerabilidades |
| SEG-VUL-03 | Prazos de correção, contados da detecção, pela severidade final: **crítica, ou com exploração ativa conhecida: {{Horas}} horas; alta: {{Dias}} dias; média: {{Dias}} dias; baixa: até a próxima release** (proposto: 72 h, 7, 30 e 90 dias). Severidade de partida pela escala CVSS da fonte | ASVS V15 | Relatório mostra, para cada achado aberto, o prazo e se venceu | {{Release}} | relatório periódico |
| SEG-VUL-04 | Registro de cada vulnerabilidade com identificador próprio, componente e versão, fonte, severidade, alcance, prazo, situação (aberta, em correção, corrigida, não afeta, risco aceito) e a correção; nada é apagado. Risco aceito só com dono, motivo, mitigação e validade de até {{Dias}} dias (proposto) | ASVS V15 | Toda vulnerabilidade aberta tem registro; risco aceito vencido volta a falhar a varredura | {{Release}} | inspeção na auditoria |
| SEG-VUL-05 | Relatório periódico ({{Periodicidade}}) com o que entrou, o que foi corrigido, o que venceu, riscos aceitos a vencer, segredos com troca vencida e componentes atrasados; canal privado para comunicar vulnerabilidade publicado no repositório | ASVS V15 | Primeiro relatório publicado e revisado pela TI | {{Release}} | inspeção na auditoria |

## 13. Testes de segurança

<!-- Escolha as ferramentas no ADR de cadeia de suprimentos ou de stack. Exemplos comuns, só como referência: Semgrep
ou CodeQL (SAST), OSV-Scanner ou o auditor de pacotes da linguagem (dependências), gitleaks (segredos), OWASP ZAP
(DAST). -->

| ID | Teste | Ferramenta | Onde roda | Bloqueia quando |
|---|---|---|---|---|
| SEG-TST-01 | Análise estática (SAST), com regras próprias para os padrões proibidos no `AGENTS_DESENVOLVIMENTO.md` | {{Ferramenta de SAST}} | todo pedido de integração e periodicamente | achado de severidade alta |
| SEG-TST-02 | Dependências vulneráveis no arquivo de travamento e na imagem | {{Ferramenta de varredura de dependências}} | pedido de integração, build e periodicamente | vulnerabilidade alta ou crítica fora das exceções vigentes |
| SEG-TST-03 | Segredos na diferença, no histórico e na imagem | {{Ferramenta de varredura de segredos}} | pedido de integração, periodicamente e no build | qualquer achado não justificado |
| SEG-TST-04 | Análise dinâmica (DAST) contra a homologação | {{Ferramenta de DAST}} | depois de cada implantação em homologação | alerta de risco alto |
| SEG-TST-05 | Autorização, gerada da matriz do 14 §1 e do OpenAPI (SEG-AUZ) | ferramentas de teste do 05 §15 | todo pedido de integração | qualquer diferença ou acesso fora do escopo |
| SEG-TST-06 | Cabeçalhos, CSP, entrada e limites (SEG-CAB, SEG-ENT, SEG-LIM) | ferramentas de teste do 05 §15 | todo pedido de integração | qualquer teste vermelho |
| SEG-TST-07 | Revisão independente com este documento como lista de verificação | {{Quem revisa}} | antes de cada release | achado crítico ou alto aberto |

## 14. Resposta a incidente

| ID | Requisito | Origem | Critério de aceite | Release | Verificação |
|---|---|---|---|---|---|
| SEG-INC-01 | Todo incidente de segurança tem registro com identificador, dono, linha do tempo, dados afetados e ações | ASVS V16; 14 §4 | Registro aberto no dia da detecção | {{Release}} | inspeção na auditoria |
| SEG-INC-02 | Conter: revogar sessões, trocar os segredos expostos, tirar o serviço do ar se preciso e preservar log e trilha antes de restaurar | ASVS V16, V13 | Roteiro de contenção escrito, com os comandos do ambiente | {{Release}} | exercício simulado |
| SEG-INC-03 | Avisar: a TI e a gestão sempre; o encarregado, no dia da detecção, se houver dado pessoal envolvido, para decidir sobre a comunicação à ANPD (Lei 13.709/2018, art. 48) | 14 §4 | Contatos institucionais no roteiro | {{Release}} | exercício simulado |
| SEG-INC-04 | Recuperar e aprender: restaurar pelo 14 §7.1 e escrever relatório pós-incidente em até {{Dias úteis}} dias úteis (proposto), explicando a causa e qual teste ou regra nova teria detectado o problema | ASVS V16 | Relatório cita o teste novo | {{Release}} | inspeção na auditoria |

## 15. Exceções registradas

<!-- Requisito do nível escolhido que não será cumprido na primeira release vira exceção, nunca silêncio. Cada exceção
tem mitigação até ser resolvida e uma condição ou data para acabar. -->

| ID | Exceção | Risco | Mitigação até lá | Dono | Até quando |
|---|---|---|---|---|---|
| EXC-SEG-01 | {{Requisito não cumprido e por quê}} | {{O que pode acontecer}} | {{Controles que reduzem o risco}} | {{Unidade}} | {{Data ou condição}} |

## 16. Matriz de verificações

<!-- Quando cada verificação roda e se a falha impede o merge, a implantação ou a promoção. O que não bloqueia abre um
registro para tratamento. -->

| Verificação | IDs | Ferramenta | Pedido de integração | Periódica | Implantação | Bloqueia |
|---|---|---|---|---|---|---|
| Autorização pela matriz e pelo OpenAPI | SEG-AUZ, SEG-TST-05 | {{Ferramenta}} | sim | — | — | sim (merge) |
| Autenticação e sessão | SEG-AUT, SEG-SES | {{Ferramenta}} | sim | — | — | sim (merge) |
| Entrada, cabeçalhos e limites | SEG-ENT, SEG-CAB, SEG-LIM, SEG-TST-06 | {{Ferramenta}} | sim | — | — | sim (merge) |
| Registro e erro sem detalhe | SEG-LOG-02, SEG-LOG-03 | {{Ferramenta}} | sim | — | — | sim (merge) |
| SAST | SEG-TST-01 | {{Ferramenta de SAST}} | sim | sim | — | sim (merge) |
| Dependências | SEG-TST-02, SEG-VUL | {{Ferramenta}} | sim | sim | sim | sim no pedido e na implantação; registro na periódica |
| Segredos | SEG-SEC-01, SEG-TST-03 | {{Ferramenta}} | sim | sim | sim | sim |
| Cadeia de suprimentos | SEG-SUP | {{Ferramenta}} | sim | sim | sim | sim (merge e implantação) |
| DAST | SEG-TST-04 | {{Ferramenta de DAST}} | — | {{Sim ou não}} | sim (homologação) | sim (promoção), para alerta alto |
| Revisão independente | SEG-TST-07 | — | — | — | antes da produção | sim |

## Pronto quando

- [ ] O nível do ASVS 5.0 está escolhido e cada capítulo diz se aplica, com o motivo quando não aplica.
- [ ] Cada linha da linha de base foi mantida, ajustada ou retirada com o motivo.
- [ ] Todo requisito tem origem, critério de aceite verificável, release e verificação.
- [ ] Os prazos de correção de vulnerabilidade foram aprovados pela TI.
- [ ] Toda exceção tem risco, mitigação, dono e prazo.
- [ ] A matriz de verificações diz quando cada uma roda e se bloqueia.
- [ ] Nenhum marcador `{{...}}` sobrou.
