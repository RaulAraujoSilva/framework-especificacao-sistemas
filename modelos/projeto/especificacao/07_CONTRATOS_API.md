# 07. Contratos de dados e API

<!-- COMO PREENCHER: este documento deriva dos passos dos casos de uso (04) em que dado entra ou sai do sistema e das
entidades do 06. Siga o capítulo 03 da metodologia, §3.8 (contratos e API) e §2 (identificadores). Pronto quando: toda
operação aponta caso de uso e perfil; todo dado que vem de fora tem esquema (JSON Schema 2020-12) com tipos,
obrigatoriedade, casas decimais e exemplo real; todos os erros seguem um formato só (RFC 9457). O arquivo equivalente do
caso resolvido (exemplo/reajusta/especificacao/07_CONTRATOS_API.md) serve só de referência de formato e de nível de
detalhe: não copie caminho, campo, código de erro nem frase dele. -->

Os contratos abaixo são a fonte da verdade da implementação: tipos, validadores e testes de contrato são gerados deles,
e nenhum campo existe fora deles. Os identificadores (UC, RF, PER, TL) são os do [01](01_VISAO_ESCOPO.md); as regras
citadas estão no [08](08_REGRAS_NEGOCIO.md); as entidades, no [06](06_MODELO_DADOS.md).

## 1. Arquivos de contrato

<!-- Os arquivos ficam em contratos/ dentro deste pacote. Todo esquema tem um exemplo real (anonimizado) que passa nele
e, quando ajuda, um exemplo inválido que tem de ser recusado. -->

| Arquivo | O que é | Quem produz | Quem consome | Validado contra |
|---|---|---|---|---|
| `contratos/openapi.yaml` | OpenAPI 3.1 com as operações da §3 | — | rotas da API, cliente das telas, testes de contrato | validador oficial do OpenAPI; toda operação com UC e perfil |
| `contratos/{{Nome do dado}}.schema.json` | {{Dado que vem de fora: formulário, arquivo, mensagem de integração}} | {{Quem envia}} | {{Módulo que recebe}} | {{Exemplo real que passa; exemplo inválido que é recusado}} |

## 2. Convenções

### 2.1 Nomes

- Caminho de recurso: substantivo no plural, em português sem acento e em letra minúscula, com hífen entre as
  palavras (`/{{Recursos}}/{id}/{{Sub-recursos}}`).
- Ação que não é criar, ler, alterar ou apagar vira um recurso com nome de substantivo: `/{{Recursos}}/{id}/{{Ação}}`
  (por exemplo, `/pedidos/{id}/cancelamento` em vez de `/pedidos/{id}/cancelar`).
- Campos JSON em `snake_case`, sem acento, com os termos do glossário do 01.
- Valores enumerados em minúsculas com sublinhado; são os mesmos do 06 §2, convertidos só na borda.
- Identificador de registro: {{Uuid ou outro}}. Identificador que já existe no mundo de fora (número de processo,
  protocolo, documento) mantém o formato de origem, validado por expressão regular.

### 2.2 Datas e fusos

- Data civil: `AAAA-MM-DD` (`format: date`). Instante: ISO 8601 com deslocamento de fuso
  (`2026-03-02T14:30:00-03:00`).
- O banco guarda instantes em UTC; a tela mostra no fuso `{{Fuso horário do órgão}}`.
- Prazo é contado sobre datas civis, pela regra de calendário do 08 ({{RN de calendário}}).

### 2.3 Números

- Ponto decimal, sem separador de milhar, no JSON e nos arquivos trocados. A tela mostra no formato brasileiro.
- Valor com casas decimais significativas (moeda, percentual, quantidade medida) é lido sem perda: {{Como o servidor
  preserva as casas, por exemplo lendo o número como texto ou com analisador decimal}}.
- Percentual: {{Em pontos percentuais ou em fração; diga qual e dê um exemplo}}.

### 2.4 Erros (RFC 9457)

Todo erro HTTP responde `application/problem+json` com `type`, `title`, `status`, `detail` e `instance`, mais as
extensões `codigo` (estável, usado pela tela para escolher a mensagem do guia do 10), `regra` (a RN contrariada, quando
houver), `erros[]` (campo em JSON Pointer e motivo) e `correlacao_id`. O `type` é uma referência estável:
`/problemas/<codigo>`.

<!-- A tabela abaixo é uma base. Acrescente códigos do seu domínio; nunca use dois códigos para a mesma situação. A
mensagem técnica (pilha, SQL) nunca vai no corpo. -->

| Status | `codigo` | Quando |
|---|---|---|
| 400 | `entrada-malformada` | corpo que não é JSON válido, parâmetro com tipo errado |
| 401 | `nao-autenticado` | requisição sem credencial, ou com credencial vencida ou revogada |
| 403 | `sem-permissao` | o perfil da sessão não tem a operação (matriz do 14 §1) |
| 404 | `nao-encontrado` | o recurso não existe **ou** está fora do escopo do usuário; a resposta é a mesma, para não revelar existência |
| 409 | `conflito` | o estado atual não permite a operação (transição inválida da máquina do 04) |
| 409 | `chave-reutilizada` | `Idempotency-Key` repetida com corpo diferente (§2.6) |
| 412 | `versao-desatualizada` | `If-Match` diferente do `ETag` atual |
| 413 | `conteudo-grande-demais` | corpo ou arquivo acima do limite (15, SEG-ENT) |
| 415 | `formato-nao-aceito` | tipo de conteúdo diferente do previsto |
| 422 | `fora-do-esquema` | o dado de fora não passa no esquema; nada é gravado |
| 422 | `regra-negocio` | a operação contraria uma regra; `regra` traz o identificador |
| 429 | `limite-excedido` | limite de requisições; cabeçalho `Retry-After` |
| 503 | `externo-indisponivel` | sistema externo fora do ar e sem contingência para esta operação (09) |
| 500 | `erro-interno` | falha não prevista; o corpo leva só `codigo` e `correlacao_id` |

Exemplo:

```json
{
  "type": "/problemas/regra-negocio",
  "title": "Operação não permitida pela regra",
  "status": 422,
  "detail": "{{Explicação para a pessoa, sem dado pessoal}}",
  "instance": "/api/v1/{{Recursos}}/{{Identificador}}/{{Ação}}",
  "codigo": "regra-negocio",
  "regra": "RN-{{SIG}}-01",
  "erros": [{"campo": "/{{Campo}}", "motivo": "{{Motivo}}"}],
  "correlacao_id": "{{Identificador de correlação}}"
}
```

Resultado de conferência de negócio (pendência encontrada num documento recebido, por exemplo) **não é erro HTTP**: o
registro é aceito e a resposta traz as pendências como dado. {{Diga quais operações do seu sistema funcionam assim}}.

### 2.5 Paginação, filtro e ordenação

- Lista que pode crescer recebe `pagina` (a partir de 1) e `por_pagina` (padrão 20, máximo 100 (proposto)) e
  responde `{itens, pagina, por_pagina, total}`.
- Para filtrar, o cliente usa parâmetros de consulta que repetem o nome do campo; para ordenar, `ordenar`, que aceita
  só uma lista conhecida de valores.
- Lista pequena e limitada por natureza (os documentos de um único objeto do processo, por exemplo) volta inteira.

### 2.6 Idempotência e concorrência

- Toda operação de criação que pode ser repetida pela rede (envio de dado de fora, por exemplo) exige o cabeçalho
  `Idempotency-Key`, gerado pelo cliente a cada envio: {{Operações que exigem}}.
- O servidor guarda a chave, o hash do corpo e a resposta por {{Prazo de guarda}} (proposto). Mesma chave e mesmo
  corpo devolvem a resposta original; mesma chave e corpo diferente devolvem `409 chave-reutilizada`.
- Alteração de recurso editável exige `If-Match` com o `ETag` da última leitura; diferença devolve `412`.

### 2.7 Versionamento

- **API:** versão maior no caminho (`/api/v1`). Mudança incompatível cria `/api/v2`; a anterior continua ativa por
  {{Prazo de convivência}} (proposto).
- **Esquema do dado de fora:** o campo `versao_esquema` e o `$id` identificam a versão. Versão nova é arquivo novo; o
  servidor aceita as versões vigentes e o registro guarda qual foi usada.
- **Regras:** o resultado de uma conferência guarda a versão das regras que a produziu. Mudança de regra vale para
  conferências novas; as antigas não são refeitas sem pedido.

### 2.8 Autenticação e escopo

- Telas: sessão em cookie `httpOnly` (14 §2). Chamada de sistema externo: {{Token de serviço, certificado ou outro}},
  nunca a credencial de uma pessoa.
- Cada operação do OpenAPI declara os perfis que a usam (extensão `x-perfis`), iguais aos da matriz do 14 §1.
- Além do perfil, vale o escopo: {{Quem só alcança os registros a que está vinculado, por exemplo o usuário externo só
  vê os próprios pedidos}}. Pedido fora do escopo responde 404.
- Toda operação que muda dado grava a trilha de auditoria (06 §5).

### 2.9 Operações assíncronas

- Operação que pode passar de {{Tempo máximo síncrono, em segundos}} s (proposto) responde `202` com um recurso
  `Tarefa` e o cabeçalho `Location`; o cliente consulta `GET /tarefas/{tarefa_id}` até a situação final.
- {{Operações assíncronas deste sistema, por exemplo geração de documento ou consulta a sistema externo lento}}.

## 3. Operação × caso de uso × perfil

<!-- Uma linha por passo de caso de uso que cruza a fronteira do sistema (a tela chama o servidor, a parte externa
envia, o sistema publica). Todo caso de uso com ator humano tem ao menos uma operação; todo perfil citado está na
matriz do 14 §1. O OpenAPI é escrito a partir desta tabela. -->

Prefixo `/api/v1`. Esquemas e respostas de cada operação no `contratos/openapi.yaml`.

| Método | Caminho | UC | Perfis | Operação | Tela | Requisitos |
|---|---|---|---|---|---|---|
| GET | `/{{Recursos}}` | UC-01 | PER-{{SIG}} | {{Listar, com filtro e paginação}} | TL-01 | RF-{{SIG}}-01 |
| POST | `/{{Recursos}}` | UC-01 | PER-{{SIG}} | {{Criar ou receber}} | TL-01 | RF-{{SIG}}-01 |
| GET | `/{{Recursos}}/{id}` | UC-02 | PER-{{SIG}} | {{Detalhar}} | TL-02 | {{Requisitos}} |
| POST | `/{{Recursos}}/{id}/{{Ação}}` | UC-02 | PER-{{SIG}} | {{Ação que muda a situação}} | TL-02 | {{Requisitos}} |

Casos de uso sem ator humano (rotinas agendadas, 05 §11) e por onde são expostos: {{Lista ou "nenhum"}}.

## 4. Esquema do dado de fora

<!-- Um esquema por dado que entra vindo de terceiro (formulário externo, arquivo, mensagem de integração). Escreva
primeiro a tabela de campos com o exemplo real ao lado; depois o JSON Schema. Proíba propriedade desconhecida
(additionalProperties false): campo inesperado é recusado, não ignorado. Se o dado não pode conter dado pessoal, diga
aqui e recuse na entrada. -->

### 4.1 {{Nome do dado recebido}}

Quem envia: {{Perfil ou INT-01}}. Por onde: {{Operação da §3}}. Gravado em: {{Entidades do 06}} (06 §8).

| Campo | Tipo | Obrigatório | Formato ou casas | Exemplo real | Entidade.atributo |
|---|---|---|---|---|---|
| `versao_esquema` | texto | sim | constante | `0.1` | {{Entidade.versaoEsquema}} |
| `{{Campo}}` | {{Tipo}} | {{Sim ou não}} | {{Formato}} | {{Valor de um caso real anonimizado}} | {{Entidade.atributo}} |

Esboço do esquema (`contratos/{{Nome do dado}}.schema.json`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "{{Identificador do esquema}}/0.1",
  "title": "{{Nome do dado recebido}}",
  "type": "object",
  "additionalProperties": false,
  "required": ["versao_esquema", "{{Campo obrigatório}}"],
  "properties": {
    "versao_esquema": {"const": "0.1"},
    "{{Campo obrigatório}}": {
      "type": "string",
      "description": "{{O que é, de onde vem, regra que se aplica}}",
      "examples": ["{{Valor de um caso real anonimizado}}"]
    },
    "{{Campo de data}}": {"type": "string", "format": "date"},
    "{{Campo decimal}}": {
      "type": "string",
      "pattern": "^-?\\d+(\\.\\d{1,{{Casas decimais}}})?$",
      "description": "número como texto, para não perder casas"
    }
  }
}
```

## Pronto quando

- [ ] Todo passo de caso de uso que cruza a fronteira tem operação na §3, com UC, perfil, tela e requisito.
- [ ] Os perfis da §3 batem com a matriz do 14 §1 e com o `x-perfis` do OpenAPI.
- [ ] Todo dado que vem de fora tem esquema, tabela de campos e exemplo real que passa.
- [ ] Todos os erros usam o formato da §2.4, com `codigo` estável.
- [ ] Idempotência, versionamento e operações assíncronas estão decididos para as operações deste sistema.
- [ ] Nenhum marcador `{{...}}` sobrou.
