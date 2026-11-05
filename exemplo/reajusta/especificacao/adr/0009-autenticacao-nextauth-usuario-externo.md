# ADR-0009: Autenticação com NextAuth e usuário externo da concessionária

- **Situação:** aceita; integração com o diretório da agência ou com o login gov.br fica para depois (decisão da TI).
- **Data:** 2026-10-31
- **Origem:** RF-ADM-01, RF-ADM-02; RNF-05, RNF-10, RNF-11; perfis PER-CON a PER-ADM (`01_VISAO_ESCOPO.md` §6); TL-16.

## Contexto

Há dois públicos. Servidores da agência (PER-ANA, PER-GCA, PER-PRO, PER-SEC, PER-REL, PER-GES, PER-ADM) e usuários
externos da concessionária (PER-CON), que enviam pleito e remessa e só podem ver o que é da sua concessionária. A
stack fixa NextAuth (ADR-0001). Não há, por ora, provedor de identidade da agência acessível ao sistema.

## Decisão

1. **NextAuth com provedor de credenciais** (e-mail e senha) e **sessão JWT**, cookie `httpOnly`, `secure` e
   `sameSite=lax`. A expiração da sessão vem de `SESSAO_MAX_MINUTOS` (RNF-10; valor em `14_OPERACAO.md`).
2. **Senha** guardada só como hash argon2id. Tentativas falhas contadas no usuário, com bloqueio temporário
   (parâmetros em `14_OPERACAO.md`). O sistema não guarda nem mostra senha em claro e não a escreve em log.
3. **Usuário externo** tem `externo = true` e `concessionariaId` obrigatório (`CHECK` no banco). Ele recebe só o perfil
   PER-CON. Toda consulta e todo caso de uso que lê dado de ciclo, pleito ou remessa filtra pela concessionária do
   usuário na aplicação, não na tela. O teste de autorização cobre o acesso cruzado entre concessionárias.
4. **Usuário interno** tem `unidadeId` obrigatório e um ou mais perfis. O token JWT leva só `id`, perfis, unidade e
   concessionária. Nome e e-mail não vão no token.
5. **Autorização** é a função pura `permite(perfis, acao, recurso)` de `src/dominio/adm`, com a matriz de permissões de
   `14_OPERACAO.md`. A rota chama o caso de uso; o caso de uso chama `permite` antes de agir. A tela só esconde o
   botão; ela não é a barreira.
6. **Escolha de perfil** (TL-16): quem tem mais de um perfil escolhe o perfil ativo da sessão; a trilha de auditoria
   grava o perfil ativo.
7. **Cadastro de usuário externo** é feito pelo PER-ADM, a pedido formal da concessionária. Não há autocadastro.
8. A configuração do NextAuth fica em `src/interface/autenticacao/`. O `authorize` do provedor chama o caso de uso
   `autenticar` da aplicação; não acessa o Prisma direto.

## Alternativas consideradas

- **Login gov.br.** Bom para usuário externo, mas exige credenciamento do órgão e não resolve o vínculo com a
  concessionária. Fica para depois, como outro provedor do NextAuth.
- **Diretório da agência (LDAP/AD).** Depende da TI. Fica para depois, como provedor adicional para os internos.
- **Sessão em banco.** O provedor de credenciais do NextAuth trabalha com JWT. Mantida a sessão JWT, com expiração
  curta.

## Consequências

- Positivas: R1 funciona sem integração de identidade; o isolamento entre concessionárias está na aplicação e é
  testado.
- Negativas: a agência administra senhas de usuários externos. O fluxo de troca e recuperação de senha está em
  `14_OPERACAO.md`. Revogar uma sessão JWT antes de expirar exige lista de bloqueio por usuário (campo de versão de
  sessão no usuário, conferido no callback do JWT).
