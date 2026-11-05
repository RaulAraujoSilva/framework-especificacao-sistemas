# ADR-0013: Implantação no Railway, com homologação e produção, por etiqueta de versão

- **Situação:** aceita como padrão provisório de aula. "Onde o sistema roda" continua decisão aberta da TI na PARADA 11
  (`../README.md`). Produção só com a PARADA 15. Dado real da agência só depois da decisão da TI e da Procuradoria sobre
  a hospedagem (`../15_SEGURANCA.md` SEG-DAD-05).
- **Data:** 2026-10-31
- **Origem:** `../14_OPERACAO.md` §5, §6 e §7; `../05_ARQUITETURA.md` §3 e §15; RNF-10, RNF-11, RNF-14; ADR-0012;
  SEG-INF-01 a 05 (`../15_SEGURANCA.md` §11); plano da aula 3 (etapa D10).

## Contexto

O pacote supõe Docker e PostgreSQL e descreve o arranjo num `docker-compose.yml`: `web`, `worker`, `db`, `gotenberg` e
o volume `arquivos` (05 §3, 14 §6). A aula 3 precisa pôr o sistema no ar sem a infraestrutura da agência, com dois
ambientes, deploy por etiqueta e volta à versão anterior.

O Railway roda contêineres a partir de imagem, tem PostgreSQL próprio, volumes, rede privada entre serviços, variáveis
por ambiente e token de projeto restrito a um ambiente. Ele também tem limites que mudam o arranjo do compose:

- cada serviço tem no máximo um volume, e o volume é montado num serviço só;
- serviço com volume não tem réplica, e a reimplantação dele tem uma janela curta fora do ar;
- o volume é montado como root;
- o volume não está montado no comando de pré-implantação;
- a verificação de saúde só roda na implantação, não depois;
- não há sistema de arquivos somente leitura garantido;
- não há bloqueio de saída para a internet por serviço;
- imagem de registro privado exige o plano Pro.

## Decisão

### 1. O que continua valendo

[14_OPERACAO.md](../14_OPERACAO.md) §6 continua valendo:

- **imagem:** uma imagem do app, em múltiplos estágios, sem root, com etiqueta da versão;
- **migração separada:** `prisma migrate deploy` num passo próprio, com o papel de migração, nunca na partida do app;
- **saúde:** rota de saúde que confere o banco e devolve 200 ou 503;
- **rollback:** volta à versão anterior pela etiqueta;
- **ordem:** homologação primeiro; produção só com o aceite da release registrado.

Este ADR diz como cada item acontece no Railway e o que muda.

### 2. Projeto, ambientes e serviços

Um projeto `reajusta` com os ambientes `homologacao` e `producao`. Os ambientes de PR do Railway ficam desligados:
nenhum ambiente nasce sozinho com segredo.

| Serviço no compose (05 §3, 14 §6) | Serviço no Railway | Origem | O que muda |
|---|---|---|---|
| `web` | `web` | imagem `ghcr.io/<organização>/reajusta`, pelo digest da etiqueta | único serviço com domínio público. TLS na borda do Railway, no lugar do proxy reverso da agência. Verificação de saúde da implantação na rota de saúde. O volume `arquivos` é montado aqui. Uma instância só, porque serviço com volume não tem réplica. A reimplantação tem uma janela curta fora do ar |
| `worker` | `worker` | a mesma imagem e o mesmo digest, com outro comando de partida | sem domínio e sem volume (item 4). Política de reinício em falha. Uma instância, como pede o pg-boss com `singletonKey` (05 §3) |
| `db` | `postgres` | modelo oficial de PostgreSQL do Railway, na última versão maior estável (18 em 01/11/2026; SEG-SUP-09), anotada no registro de versões | papéis separados (item 6). Sem proxy TCP público. Cópias do Railway e recuperação a ponto no tempo, que exige a etiqueta da versão maior (por isso não se fixa por digest, ADR-0012) |
| `gotenberg` | `gotenberg` | imagem oficial do Gotenberg, fixada por digest | sem domínio, só na rede privada. Busca de URL remota e webhooks desligados. O "sem internet" de 05 §3 não é garantido: EXC-SEG-05 |
| volume `arquivos` | volume `arquivos`, ligado ao `web` | — | `ARQUIVOS_DIR` aponta o caminho de montagem. Cópia de segurança do volume pelo Railway, mais uma cópia independente antes de dado real (item 11) |
| passo de migração (14 §6) | `migracao` | a mesma imagem e o mesmo digest; o comando de partida roda `prisma migrate deploy`; reinício desligado | é o único serviço com `DATABASE_URL_MIGRACAO`. Roda a cada implantação, antes do `web` e do `worker` (item 8) |

### 3. Rede e superfície

- Só o `web` tem domínio. `worker`, `gotenberg`, `migracao` e `postgres` falam pela rede privada do projeto
  (`*.railway.internal`).
- O proxy TCP público que o modelo de PostgreSQL pode criar é removido nos dois ambientes. Se a TI precisar de acesso
  pontual, cria o proxy, usa, remove e registra no `RUNBOOK_DEPLOY.md`.
- O `deploy.yml` confere a lista de domínios e de proxies do ambiente depois de cada implantação (SEG-INF-01).

### 4. Volume e arquivos

O volume é montado num serviço só. Ele fica no `web`, que recebe o pacote do pleito, gera a peça a pedido da pessoa
(TL-09, HIS-DOC-01) e entrega os arquivos.

**Regra da R1 (proposto):**

- só o `web` lê e grava arquivos;
- o `worker` trabalha só com o banco: as séries (JOB-01) e a validação (JOB-04) leem os dados do pleito já gravados nas
  tabelas (06, `Pleito`, `ComponentePleito`, `ValorMensal`);
- a proposta de ofício que o JOB-04 prepara (UC-04) é gravada como dados, e o DOCX e o PDF são gerados no `web` quando a
  pessoa abre ou exporta a peça.

**A partir da R2,** os jobs que geram peça sozinhos (JOB-02: reiteração, certidão) precisam de armazenamento que os dois
serviços alcancem. Antes da R2, a DA-ARQ-01 (05 §18) é decidida. A opção prevista é o adaptador `s3` da porta
`ArmazenamentoArquivos`, com armazenamento compatível com S3. É dependência nova: ADR próprio pela P-13.

**Dono dos arquivos.** O volume é montado como root. Então:

- só o `web` usa `RAILWAY_RUN_UID=0`;
- a entrada da imagem, como root, só ajusta o dono de `ARQUIVOS_DIR`;
- em seguida passa a execução ao usuário sem privilégio da imagem;
- nenhum processo da aplicação roda como root (SEG-INF-02).

### 5. Sistema de arquivos e usuário

- O Railway não garante sistema de arquivos somente leitura. A compensação está na imagem:
  - os arquivos do app pertencem ao root e não podem ser gravados pelo usuário do processo;
  - o processo só grava em `/tmp` e em `ARQUIVOS_DIR`.
- A CI confere na imagem que `id -u` é diferente de 0 e que a escrita em `/app` falha.
- O runbook confere o usuário do processo no `web` em execução, por `railway ssh`.

### 6. PostgreSQL e papéis

O PostgreSQL do Railway dá um superusuário. Com ele, a TI cria uma vez, por script versionado no repositório e rodado à
mão, os papéis de 05 §3 e 14 §5:

| Papel | Uso | Onde fica a credencial |
|---|---|---|
| superusuário do modelo | criar papéis, manutenção | só no serviço `postgres` e com a TI; nenhum serviço da aplicação o referencia |
| `reajusta_dono` | dono do esquema; `prisma migrate deploy` | `DATABASE_URL_MIGRACAO`, só no serviço `migracao` |
| `reajusta_app` | aplicação; sem `UPDATE` nem `DELETE` na trilha; sem DDL | `DATABASE_URL`, no `web` e no `worker` |

- As URLs dos papéis são montadas com o host privado do banco (variável de referência do domínio privado do serviço
  `postgres`) e a senha selada.
- A `DATABASE_URL` que o modelo do Railway expõe é a do superusuário. Ela não é referenciada.
- A migração fica num serviço próprio. O comando de pré-implantação do `web` poria a credencial do dono do esquema no
  único serviço exposto à internet, e esse papel pode desligar o gatilho que protege a trilha (RNF-11).

### 7. Variáveis por ambiente

As variáveis de 05 §15 são definidas por ambiente. Os segredos ficam como variáveis seladas. Variável compartilhada só
para o que não é segredo.

| Variável | `homologacao` | `producao` | Serviços |
|---|---|---|---|
| `APP_AMBIENTE` | `homologacao` | `producao` | `web`, `worker`, `migracao` |
| `DATABASE_URL` | papel `reajusta_app` (selada) | idem | `web`, `worker` |
| `DATABASE_URL_MIGRACAO` | papel `reajusta_dono` (selada) | idem | `migracao` |
| `NEXTAUTH_URL` | domínio de homologação | domínio de produção | `web` |
| `NEXTAUTH_SECRET` | próprio do ambiente (selada) | próprio do ambiente (selada) | `web` |
| `ARQUIVOS_DIR` | caminho de montagem do volume | idem | `web` |
| `GOTENBERG_URL` | endereço privado do `gotenberg` | idem | `web`, `worker` |
| `LLM_PROVEDOR` | `desligado` na R1 | `desligado` na R1 | `web`, `worker` |
| `SEI_MODO` | `manual` | `manual` | `web`, `worker` |
| `SMTP_*` | endereços internos de teste (14 §5) | institucional | `worker` |
| senhas dos usuários de teste do seed | seladas | não existem (SEG-AUT-06) | passo de seed |

- Segredo nunca é igual entre os ambientes.
- `OPENROUTER_API_KEY` não entra no Railway enquanto o sistema não chama modelo de linguagem (SEG-SEC-04).

### 8. Implantação por etiqueta (GitHub Actions)

O `deploy.yml` roda quando uma etiqueta `vX.Y.Z` é criada no repositório do sistema:

1. Constrói a imagem uma vez, gera os SBOM (ADR-0012), varre a imagem e publica no GHCR privado com a etiqueta. Guarda
   o digest.
2. Implanta em `homologacao`, pela API do Railway com o token de projeto do ambiente (`RAILWAY_TOKEN`, segredo do
   ambiente `homologacao` no GitHub):
   - aponta `migracao`, `web` e `worker` para o digest;
   - roda o `migracao` e só segue se ele terminar com sucesso;
   - implanta `web` e `worker`; o `web` só recebe tráfego quando a rota de saúde responde 200.
3. Na homologação, roda o smoke em Playwright (pleito de Paraty 2026: 10 ok, 5 avisos e 1 erro), o AT-26 com o papel
   `reajusta_app`, a conferência de cabeçalhos e de superfície e o ZAP baseline (`../15_SEGURANCA.md` §18).
4. Promove para `producao` o mesmo digest, só com a aprovação da PARADA 15. O token é o do ambiente `producao`, outro
   segredo. Onde o plano do GitHub tiver revisores obrigatórios de ambiente, a aprovação é a do ambiente. Senão, a
   promoção é disparada à mão, por quem a PARADA 15 autorizou, e registrada no `RUNBOOK_DEPLOY.md`.

O GHCR privado exige o plano Pro do Railway, por causa das credenciais de registro. Sem ele, o Railway constrói a
partir do commit da etiqueta. Nesse caso, a imagem implantada não é a que recebeu o SBOM e a varredura, e a lacuna fica
registrada no `AMBIENTES.md`.

### 9. Saúde e monitoramento

A verificação de saúde do Railway só roda na implantação. O "orquestrador reinicia o contêiner que falha" de 14 §6 vira:

- política de reinício em falha para os processos que caem;
- monitor externo da rota de saúde, escolhido pela TI e registrado no `AMBIENTES.md`;
- avisos do Railway de implantação falha e de queda, para a TI.

Os alertas de 14 §7.4 continuam valendo.

### 10. Volta à versão anterior

- **Como:** o mesmo `deploy.yml`, disparado à mão com a etiqueta anterior. Ele aponta `web` e `worker` para o digest
  daquela versão e não roda migração para trás.
- **Regra:** cada migração é compatível com a versão anterior do app (expandir antes, contrair numa versão seguinte).
- **Exceção:** migração que não puder ser compatível é marcada no CHANGELOG. A volta, então, exige restaurar o banco
  (recuperação a ponto no tempo), com decisão da TI.
- **Alternativa:** a volta pelo painel do Railway (implantação anterior) é aceita em emergência e registrada.

### 11. Cópias de segurança

14 §7.1 continua valendo:

- **banco:** cópias agendadas e recuperação a ponto no tempo do Railway;
- **volume:** cópias agendadas do Railway;
- **cópia independente:** apagar o volume apaga as cópias dele. Por isso, antes de dado real, há uma cópia cifrada fora
  do projeto do Railway (SEG-DAD-06);
- **restauração mensal em homologação:** continua.

## Alternativas consideradas

- **Infraestrutura da agência com o `docker-compose.yml`.** É o destino previsto pelo pacote, mas depende da TI e não
  está disponível na aula. Continua sendo a opção da PARADA 11. O mesmo arranjo de imagem, migração, saúde e etiqueta
  vale nela.
- **Migração no comando de pré-implantação do `web`.** É o caminho mais simples no Railway, mas expõe a credencial do
  dono do esquema no serviço público. Rejeitada como padrão (item 6).
- **Um volume só, montado no `web` e no `worker`.** O Railway não permite. Substituída pela regra do item 4.
- **Construção da imagem pelo Railway a partir do repositório.** Simples, mas a imagem que roda deixa de ser a que
  recebeu o SBOM e a varredura. Aceita só sem o plano Pro (item 8).

## Consequências

- Positivas:
  - homologação e produção iguais, separadas por token e por variáveis;
  - deploy e volta reproduzíveis pela etiqueta e pelo digest;
  - a credencial de migração fica fora do serviço público;
  - os dois ambientes custam poucas dezenas de dólares por mês, a confirmar no painel.
- Negativas:
  - o `web` não escala horizontalmente enquanto tiver o volume;
  - a reimplantação do `web` tem uma janela curta fora do ar;
  - o `worker` não grava arquivo na R1;
  - "sem root", "somente leitura" e "sem internet" dependem de compensações, não de garantia da plataforma.
- A hospedagem com dado real continua decisão da TI e da Procuradoria, inclusive a região e a transferência
  internacional de dados (SEG-DAD-05).
