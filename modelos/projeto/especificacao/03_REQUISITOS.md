# 03. Requisitos

<!-- COMO PREENCHER: este documento deriva dos passos dos casos de uso do 04 que o sistema executa, das melhorias do
TO-BE, das metas e das normas. Regras: capítulo 03 da metodologia, §3.4 (requisitos). Percorra cada passo do sistema
nos fluxos dos casos de uso e escreva o que ele deve fazer; depois confira o caminho inverso: toda melhoria do TO-BE
gera ao menos um requisito. Um requisito por seção, sem "e também". Pronto quando: todo requisito tem origem e
critério de aceite; a lista do 01 e as seções deste documento batem; todo módulo tem requisito; todo requisito é
citado por teste (12) ou história (13). O equivalente do caso resolvido é
exemplo/reajusta/especificacao/03_REQUISITOS.md. Ele serve só de referência de formato e de nível de detalhe: não
copie nenhuma frase, nome ou termo dele. -->

Detalhamento dos requisitos funcionais (RF) e não funcionais (RNF) listados no
[01_VISAO_ESCOPO.md](01_VISAO_ESCOPO.md). Cada requisito diz o que o sistema deve fazer, de onde a exigência veio, como
se verifica que foi atendida e onde ele aparece (caso de uso, tela, release). As regras de negócio que os requisitos
aplicam estão no [08_REGRAS_NEGOCIO.md](08_REGRAS_NEGOCIO.md); os testes, no [12_TESTES.md](12_TESTES.md); as
histórias, no [13_BACKLOG.md](13_BACKLOG.md).

**Origens usadas.** {{Arquivos e códigos citados como origem: melhorias do TO-BE, normas e requisitos legais,
indicadores, atividades do BPMN e casos reais}}.

**Convenção.** "Deve" indica obrigação. Item marcado "(proposto)" ainda não tem origem nos insumos e depende de
confirmação da área de negócio.

## Sumário

| Módulo | Requisitos | Release |
|---|---|---|
| MOD-{{SIG}} {{Nome do módulo}} | RF-{{SIG}}-01 | R1 |
| Não funcionais | RNF-01 | todas |

## 1. MOD-{{SIG}} {{Nome do módulo}}

<!-- Uma seção por módulo, na ordem do fluxo. Dentro dela, um bloco por requisito, com os campos exatamente nesta
forma: o conferidor lê "Origem" e "Critério de aceite" dentro de cada seção RF. A descrição diz o comportamento
observável, não a solução de tela ("usar uma caixa de seleção" não é requisito). Cite a regra pelo identificador
(por exemplo RN-...) em vez de repeti-la. O critério de aceite é numerado, verificável e, de preferência, usa o dado de
um caso real: "o caso X, enviado sem o documento Y, volta com a pendência Z". Ele não repete a descrição. -->

### RF-{{SIG}}-01 {{Verbo + objeto}}

- **Descrição:** o sistema deve {{Comportamento observável, numa ou duas frases, citando a regra que aplica}}
- **Origem:** {{Origem: melhoria, norma com artigo, cláusula, atividade do BPMN ou caso real}}
- **Critério de aceite:**
  1. {{Situação concreta, com o dado de um caso real, e o resultado esperado}}
  2. {{Situação de erro ou de borda e o resultado esperado}}
- **UC:** UC-01 · **TL:** TL-01 · **Release:** R1

## 2. Requisitos não funcionais

<!-- Um por linha, cada um com número e forma de medir. Use as características da ISO/IEC 25010. Exigência legal
(acessibilidade, dados pessoais, guarda de documentos) e de operação (disponibilidade, cópia de segurança) também
entram aqui. -->

| ID | Característica (ISO/IEC 25010) | Requisito | Forma de medir | Origem | Release | Teste |
|---|---|---|---|---|---|---|
| RNF-01 | {{Característica}} | {{Requisito com número e unidade}} | {{Como e onde se mede}} | {{Meta, norma ou exigência de operação}} | R1 | AT-01 |

## 3. Melhorias do TO-BE e requisitos

<!-- Caminho inverso: toda melhoria do TO-BE tem ao menos um requisito, ou está no 01 como fora do escopo, com o
motivo. Uma linha por melhoria. -->

| Melhoria do TO-BE | Requisitos que a atendem | Situação |
|---|---|---|
| {{Código e nome curto da melhoria}} | RF-{{SIG}}-01 | {{Atendida, parcial ou fora do escopo (ver 01)}} |

## 4. Matriz de rastreabilidade

<!-- Uma linha por requisito funcional. Os testes e as histórias são os que citam o requisito no 12 e no 13. Ao fim,
diga quantos requisitos têm teste e quais ainda não têm. -->

| Requisito | Caso de uso | Tela | Teste de aceitação | História | Release |
|---|---|---|---|---|---|
| RF-{{SIG}}-01 | UC-01 | TL-01 | AT-01 | HIS-{{SIG}}-01 | R1 |

Cobertura: {{Quantos requisitos têm teste de aceitação e quais ainda não têm, com o motivo}}.

## Pronto quando

- [ ] Todo requisito funcional tem descrição, origem e critério de aceite numerado.
- [ ] A lista de requisitos do 01 e as seções deste documento batem, um a um.
- [ ] Todo módulo tem ao menos um requisito.
- [ ] Toda melhoria do TO-BE aparece na seção 3, atendida ou com o motivo de ficar fora.
- [ ] Todo requisito não funcional tem número e forma de medir.
- [ ] Todo requisito é citado por um teste de aceitação ou por uma história.
- [ ] Nenhum requisito descreve solução de tela nem junta duas obrigações.
