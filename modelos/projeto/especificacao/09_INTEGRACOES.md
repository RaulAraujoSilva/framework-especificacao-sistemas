# 09. Integrações

<!-- COMO PREENCHER: este documento deriva dos sistemas externos do contexto (lista de integrações do 01 e diagrama
de contexto do 05) e das partes externas que só trocam dados, sem usar telas (02). Siga o capítulo 03 da metodologia,
§3.9 (integrações) e §2 (identificadores). Uma ficha "## INT-nn Sistema" por sistema externo. Pronto quando: toda
integração tem dado trocado, direção, frequência, formato, autenticação, conduta em falha, contingência, porta e dono
do outro lado; integração que depende de decisão de outro órgão ou da TI tem DEC e começa com contingência manual. O
arquivo equivalente do caso resolvido (exemplo/reajusta/especificacao/09_INTEGRACOES.md) serve só de referência de
formato e de nível de detalhe: não copie sistema, endereço, campo nem frase dele. -->

{{Uma frase: com quantos sistemas externos o sistema conversa e qual deles é o mais crítico para o processo}}. Os
identificadores INT nascem no [01](01_VISAO_ESCOPO.md); as portas e os adaptadores estão no
[05](05_ARQUITETURA.md) §8; as rotinas que chamam as integrações, no 05 §11.

## 1. Princípios comuns

<!-- Valem para todas as fichas. Ajuste a coluna "Origem" com os RNF do seu 03. -->

| Princípio | Regra | Origem |
|---|---|---|
| Só por porta | O domínio e a aplicação conhecem a interface (porta); o adaptador fica fora e pode ser trocado sem mexer em regra | 05 §5 e §8 |
| Falha não para o processo | Sem resposta, vale a contingência da ficha: dado em cache, marcação "a refazer", fila para reenvio ou operação manual registrada | {{RNF de disponibilidade}} |
| Cache com data | Dado guardado de fonte externa leva a fonte, a data da consulta e o hash da resposta; dado revisado pela fonte vira registro novo, sem apagar o que já foi usado | {{RNF de rastreabilidade}} |
| Rastro de toda troca | Cada envio e cada consulta deixam registro com instante, resultado e identificador de correlação | 06 §5 |
| Segredo fora do código | Credencial de integração só por variável de ambiente vinda do cofre (14 §5); nunca em log | 15, SEG-SEC |
| Dado de fora é não confiável | Resposta e arquivo recebidos são validados (esquema, tipos, tamanho) antes de gravar | 15, SEG-ENT |
| Teste sem rede | Toda integração tem dublê com respostas gravadas; nenhum teste automatizado depende do sistema real | 05 §15 |
| Credencial de sistema, não de pessoa | Integração autentica como o sistema, com o menor acesso possível do outro lado | 15, SEG-SEC |

### Portas usadas

| Porta | Integrações | Operações | Adaptadores | Rotinas |
|---|---|---|---|---|
| `{{NomeDaPorta}}` | INT-01 | `{{Operação}}` | `{{Nome do adaptador}}`, `{{Adaptador manual}}`, dublê nos testes | JOB-01 |

Todo adaptador devolve o dado com a data da consulta, ou uma falha tipada (`FalhaExterna` com o sistema e o tipo:
`{{TEMPO_ESGOTADO, INDISPONIVEL, RESPOSTA_INVALIDA}}`). A aplicação decide pela falha tipada, nunca pela exceção da
biblioteca, e nenhuma resposta bruta passa da porta.

### Quadro geral

| ID | Sistema | Sentido | Forma | Frequência | Situação |
|---|---|---|---|---|---|
| INT-01 | {{Sistema externo}} | {{Entrada, saída ou ida e volta}} | {{API, arquivo, troca manual}} | {{Frequência}} | {{Decidida e testada, decidida, em aberto (DEC-01)}} |

## INT-01 {{Sistema externo}}

<!-- Copie esta seção inteira para cada sistema externo (INT-02, INT-03...). Comece pela finalidade e pelo dado: o
detalhe técnico só faz sentido depois. Se o acesso já foi testado no levantamento, registre o que foi testado e o
resultado; se não foi, diga "não testado" e abra DEC. -->

**Finalidade:** {{Por que o processo precisa deste sistema, em uma frase, com o caso de uso que o usa (UC-01)}}.

**Dono do outro lado:** {{Órgão, unidade ou empresa responsável; contato institucional, sem nome de pessoa}}.

**O que se troca**

| Do sistema externo para o sistema | Do sistema para o sistema externo |
|---|---|
| {{Dado recebido e o requisito que o usa}} | {{Dado enviado e o requisito}} |

**Formato e exemplo**

<!-- Endereço, operação, formato da mensagem ou do arquivo, campos usados. Ponha um exemplo real (anonimizado) da
resposta ou do arquivo, e diga como cada campo vira atributo do 06 (06 §8). -->

```text
{{Endereço ou operação, por exemplo GET seguido do endereço do recurso}}
```

```json
{"{{Campo}}": "{{Valor de exemplo anonimizado}}"}
```

| Campo de origem | Uso | Entidade.atributo |
|---|---|---|
| `{{Campo}}` | {{Para que serve}} | {{Entidade.atributo}} |

**Contingência manual**

<!-- Como o processo segue se a integração não existir ainda ou cair: quem faz o quê na tela, e como o sistema
registra que foi manual. Integração que depende de decisão de outro órgão começa aqui. -->

1. {{Passo manual, com o perfil e a tela}}.
2. {{Como o sistema registra que o dado veio por via manual}}.

**Ficha**

| Item | Regra |
|---|---|
| Sentido | {{Entrada, saída ou ida e volta}} |
| Frequência | {{Sob demanda, a cada evento, diária pela rotina JOB-01}} |
| Formato | {{JSON, XML, CSV, arquivo, SOAP, troca manual}} |
| Autenticação | {{Sem autenticação, chave de API, certificado, conta de serviço}}; credencial no cofre |
| Tempo máximo e novas tentativas | {{Tempo máximo em segundos}} s (proposto); {{Número}} tentativas, só em leitura, com espera crescente |
| Cache | {{O que fica guardado, por quanto tempo, como é renovado; ou "não se aplica"}} |
| Falha e reprocesso | {{O que acontece com o caso quando a chamada falha, e quando é refeita}} |
| Contingência | {{Resumo do caminho manual acima}} |
| Segurança | {{HTTPS, lista de hosts permitidos, validação do que chega}} |
| Termos de uso e licença | {{Dado público, contrato, restrição de redistribuição}} |
| Porta e adaptador | `{{NomeDaPorta}}`, adaptador `{{Nome do adaptador}}`; configuração em `{{VARIAVEL_DE_ENDERECO}}` |
| Testado no levantamento | {{O que foi testado, com que resultado; ou "não testado"}} |
| Decidido | {{O que já está decidido}} |
| Em aberto | {{O que falta decidir e quem decide; registre como DEC-01 no 08}} |

## Pronto quando

- [ ] Todo sistema externo do contexto (05 §2) tem ficha `INT-nn`, e toda ficha está na lista do 01.
- [ ] Toda ficha diz o dado trocado, a direção, a frequência, o formato e a autenticação.
- [ ] Toda ficha diz o que acontece quando o sistema externo falha e qual é a contingência manual.
- [ ] Toda integração tem porta e adaptador no 05 §8 e dublê para os testes.
- [ ] Integração que depende de decisão de terceiros tem DEC, com dono e padrão provisório.
- [ ] Nenhum marcador `{{...}}` sobrou.
