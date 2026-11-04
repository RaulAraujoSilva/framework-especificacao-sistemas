# ADR-0006: Modelo de linguagem por adaptador, decisão humana obrigatória e citação verificada

- **Situação:** aceita; provedor e política de dados são decisão aberta da PARADA 11 (TI e Procuradoria).
- **Data:** 2026-10-31
- **Origem:** INT-06; RF-MIN-01 a RF-MIN-05; RNF-05, RNF-07, RNF-14; melhorias M-P01-15 a M-P01-18; controles Q-P01-01 a
  Q-P01-04 (`../insumos/mapeamento/controles_P01.json`).

## Contexto

As minutas de parecer técnico, parecer jurídico, relatório, voto e deliberação (MOD-MIN) usam modelo de linguagem. O
provedor ainda não foi escolhido e pode mudar. O modelo erra número e inventa citação. O controle Q-P01-01 exige
conferir 100% dos campos extraídos e das citações; o critério de aceite é parecer assinado sem número divergente e sem
citação que não confira com a fonte.

## Decisão

1. **Porta `ModeloLinguagem`** (`src/portas/externas/modelo-linguagem.ts`) com uma operação:
   `gerarEstruturado({ tarefa, versaoPrompt, entrada, esquemaSaida })`. Ela devolve um objeto validado contra o
   esquema Zod da saída, ou uma falha tipada. O domínio e a aplicação não conhecem provedor, URL nem SDK.
2. **Adaptadores:**
   - `desligado` (padrão): a minuta sai só do modelo de documento, sem texto gerado;
   - `openai-compativel`: qualquer API no formato de chat completions, inclusive servidor local;
   - `anthropic`.

   A escolha é por `LLM_PROVEDOR`. Nenhum provedor pago é obrigatório (RNF-14).
3. **Números não vêm do modelo.** Todo número da minuta (índices, IR, total, datas, prazos) vem da apuração e dos
   marcos, inserido pelo preenchimento do modelo (`dominio/doc`). O modelo redige o texto em volta e propõe citações.
4. **Verificação de citação** (RF-MIN-04) é função pura do domínio, `verificarCitacao` em `src/dominio/min`. Cada
   citação proposta tem referência e trecho. O trecho é procurado, com espaços normalizados como no oráculo
   (`norm()` de `../scripts/validar_pleito.py`), no texto da fonte trazido pela porta `BaseEspecialista` (INT-05).
   Sem o trecho, a citação fica `INVALIDA`; com a base fora do ar, fica `NAO_VERIFICADA`.
5. **Decisão humana obrigatória** (RNF-07):
   - minuta nasce `GERADA` e só passa a `REVISADA`, e a peça a `PRONTA_PARA_ASSINATURA`, por ação de uma pessoa com
     perfil para isso;
   - minuta com citação `INVALIDA` ou `NAO_VERIFICADA` não passa a `REVISADA` até o revisor corrigir a citação ou
     marcá-la como conferida na fonte (`CONFERIDA_PELO_REVISOR`, com autor e data);
   - a regra está no domínio e num `CHECK` do banco (`06_MODELO_DADOS.md` §5).
6. **Medição.** Cada edição do revisor é gravada (`EdicaoMinuta`) para a taxa de edição (RF-MIN-05, Q-P01-03). A minuta
   guarda provedor, modelo e `versaoPrompt`. Os prompts são arquivos versionados em `src/adaptadores/llm/prompts/`.
7. **Dados enviados ao modelo:** só peças e dados do processo, sem dado pessoal (RNF-05). O adaptador remove do envio
   os campos marcados como pessoais. Prompt e resposta não vão para log (`05_ARQUITETURA.md` §14).

## Alternativas consideradas

- **SDK de um provedor chamado direto no caso de uso.** Prende o sistema ao provedor e põe rede na aplicação.
  Rejeitada.
- **Vercel AI SDK como camada única.** Útil, mas é dependência a mais para uma operação só. Pode ser usado dentro de
  um adaptador, se a TI preferir, sem mudar a porta.
- **Deixar o modelo escrever os números.** O AS-IS tem 2 pareceres que não fecham com os próprios índices
  (`01_VISAO_ESCOPO.md` §1). Rejeitada.
- **Verificar citação com o próprio modelo.** Não é determinístico nem auditável. Rejeitada; a verificação é por
  texto literal.

## Consequências

- Positivas: o sistema funciona sem modelo de linguagem; trocar de provedor é configuração; Q-P01-01 a Q-P01-03 são
  medidos pelo próprio uso.
- Negativas: minuta sem modelo é mais seca (só o modelo de documento). A verificação literal recusa paráfrase: citação
  tem de trazer o trecho exato.
- A escolha do provedor e a política de dados ficam com a TI e a Procuradoria. Até lá, homologação usa `desligado` ou
  um servidor local.

## Adendo (31/10/2026)

Registra o OpenRouter como provedor padrão do adaptador, por decisão tomada no início da aula 3. A porta, as regras de
números, de citação e de decisão humana (itens 1 e 3 a 7 da decisão) não mudam.

1. **Novo adaptador `openrouter`**, escolhido por `LLM_PROVEDOR=openrouter`:
   - chama a API do OpenRouter no formato de chat completions;
   - usa `LLM_URL_BASE` com padrão `https://openrouter.ai/api/v1`;
   - lê a chave de `OPENROUTER_API_KEY`, no lugar de `LLM_CHAVE`, que segue valendo para os outros provedores.

   Os valores `desligado`, `openai-compativel` e `anthropic` continuam aceitos.
2. **Provedor padrão.** Quando a IA embarcada é ligada num ambiente, o provedor é `openrouter`.
   - `desligado` continua o valor em desenvolvimento, na CI (com MSW) e em todo ambiente enquanto o sistema não chama
     modelo.
   - A R1 não chama modelo de linguagem. O uso começa nas minutas da R3.
3. **Modelo.**
   - `LLM_MODELO` é configurável, com um modelo Claude por padrão.
   - O identificador exato é conferido em `https://openrouter.ai/api/v1/models` na hora de configurar e gravado no
     `AMBIENTES.md` do repositório do sistema.
   - A minuta continua guardando provedor e modelo (item 6).
4. **Dados.**
   - O adaptador pede ao OpenRouter só provedores que não retêm dados para treino (preferência de coleta de dados
     negada).
   - Continua removendo os campos pessoais antes do envio (item 7).
   - Não envia série paga (P-11, RNF-04).
5. **Chave.**
   - `OPENROUTER_API_KEY` é segredo selado no ambiente, com limite de crédito na chave, testada por `GET /api/v1/key`
     antes de virar segredo.
   - Nunca é impressa nem vai para log (`../15_SEGURANCA.md` SEG-SEC-02 e SEG-SEC-04).
6. **Triagem de vulnerabilidades.** O agente de segurança usa o mesmo provedor e o mesmo padrão de modelo. A chave dele
   é segredo do GitHub Actions, separado do segredo do Railway (`../15_SEGURANCA.md` SEG-VUL-02).
7. **O que continua em aberto.** O provedor e a política de dados para dado real seguem como decisão da TI e da
   Procuradoria (PARADA 11; `../14_OPERACAO.md` §4, relatório de impacto). Pelo OpenRouter, o pedido pode ser atendido
   fora do Brasil. RNF-14 continua atendido: nenhum provedor pago é obrigatório, porque `desligado` funciona.
