# 01. Visão, escopo e identificadores

<!-- COMO PREENCHER: este é o documento-base. Ele deriva do TO-BE (atividades, raias, decisões, eventos), das
melhorias, das metas e da linha de base dos indicadores que vieram do mapeamento (pasta insumos/mapeamento/). Regras:
capítulo 03 da metodologia, §2 (convenção de identificadores) e §3.1 (escopo, metas e módulos). Todo identificador
nasce aqui, com título curto; o detalhe fica no documento dono. Se outro documento precisar de um item novo, ele entra
nesta lista antes. Pronto quando: toda atividade do TO-BE está no quadro de escopo; toda atividade "automatiza" ou
"apoia" aponta um módulo; toda meta cita a linha de base e o fato de origem; as listas de identificadores existem. O
equivalente do caso resolvido é exemplo/reajusta/especificacao/01_VISAO_ESCOPO.md. Ele serve só de referência de
formato e de nível de detalhe: não copie nenhuma frase, nome ou termo dele. -->

Este é o documento-base do pacote. Aqui nascem os identificadores de módulos, perfis, casos de uso, requisitos,
entidades, telas, integrações e releases. Os demais documentos usam só estes identificadores e estes nomes.

Sistema: **{{Nome do sistema}}**, para o processo **{{Nome e código do processo no catálogo do órgão}}**.

## 1. Problema

<!-- Use números do diagnóstico AS-IS, nunca impressões. Cada número cita o fato de origem (identificador do fato no
arquivo de fatos do mapeamento). Três a seis itens bastam: duração, esperas, retrabalho, gargalo, conformidade a
prazos legais, erros. -->

- **{{Dimensão do problema, por exemplo duração}}:** {{Fato com número e unidade}} ({{Identificador do fato}}).
- **{{Dimensão do problema, por exemplo retrabalho}}:** {{Fato com número e unidade}} ({{Identificador do fato}}).

Fontes: {{Arquivos do mapeamento de onde saíram os números, por exemplo insumos/mapeamento/fatos_<processo>.json}}.

## 2. Objetivo e metas

{{O que o processo passa a ser com o sistema, numa ou duas frases, deixando claro o que continua sendo decisão humana}}

<!-- Meta sem linha de base não é meta. A linha de base vem de um fato; a meta vem da simulação do TO-BE, de uma
norma ou de um benchmark, e diz em que fase ou release deve ser atingida. -->

| Indicador | Linha de base | Fato de origem | Meta | Quando |
|---|---|---|---|---|
| {{Código e nome do indicador}} | {{Valor e unidade hoje}} | {{Identificador do fato}} | {{Valor e unidade esperados}} | {{Fase do TO-BE ou release}} |

## 3. Quadro de escopo

<!-- Uma linha por atividade do TO-BE, sem pular nenhuma. Tratamentos: "automatiza" (o sistema executa sem pessoa),
"apoia" (a pessoa decide e o sistema prepara, calcula, sugere ou registra), "registra" (a atividade acontece fora e o
sistema guarda o marco e o prazo) e "fora" (o sistema não toca nela; diga por quê). Atividades afins formam um
módulo, agrupadas pelo objeto de trabalho, não pela unidade organizacional. -->

| Atividade do TO-BE | Raia | Tratamento | Módulo | Melhoria | Observação |
|---|---|---|---|---|---|
| {{Código e nome da atividade no BPMN}} | {{Raia}} | {{Automatiza, apoia, registra ou fora}} | MOD-{{SIG}} | {{Código da melhoria do TO-BE}} | {{Motivo, obrigatório quando o tratamento é fora}} |
| {{Código e nome da atividade no BPMN}} | {{Raia}} | {{Automatiza, apoia, registra ou fora}} | {{Módulo ou —}} | {{Código da melhoria ou —}} | {{Motivo}} |

**Fica fora deste sistema:**

- {{Parte do processo, tipo de caso ou decisão que o sistema não cobre, e o motivo}}

**Melhorias do TO-BE sem requisito:**

<!-- Toda melhoria do TO-BE gera ao menos um requisito no 03. A que não gerar precisa estar aqui, com o motivo. -->

| Melhoria | Por que não vira requisito agora |
|---|---|
| {{Código da melhoria}} | {{Motivo: descartada, depende de norma, fica para outra onda}} |

## 4. Ondas

<!-- Comece pela função de regra mais fechada e de dado mais disponível. Cada onda vira uma release do backlog. -->

| Onda | O que entra | Por que nesta ordem | Release |
|---|---|---|---|
| 1 | {{Funções da primeira onda}} | {{Regra fechada, dado disponível, volume ou risco}} | R1 |
| 2 | {{Funções da segunda onda}} | {{Motivo}} | R2 |

## 5. Stack (proposta)

<!-- Proposta de partida. Toda escolha com alternativa real vira ADR no 05, e o que depende da TI do órgão fica como
proposta até a avaliação. Fixe a versão de cada tecnologia na data da escrita. -->

| Camada | Tecnologia proposta | Motivo | Decisão |
|---|---|---|---|
| {{Interface, aplicação, banco de dados, autenticação ou hospedagem}} | {{Tecnologia e versão}} | {{Por que serve ao órgão}} | ADR-0001 |

A interface segue {{Design system adotado, por exemplo o padrão digital de governo}}. Esta stack é proposta até a
avaliação da TI do órgão.

## 6. Módulos

| ID | Módulo | O que faz | Atividades do TO-BE | Melhorias |
|---|---|---|---|---|
| MOD-{{SIG}} | {{Nome do módulo}} | {{Objeto de trabalho e responsabilidade do módulo}} | {{Códigos das atividades}} | {{Códigos das melhorias}} |

## 7. Perfis

<!-- Cada raia que usa o sistema vira um perfil, descrito pela função e nunca pelo nome de uma pessoa. Parte externa
que só envia ou recebe dados vira integração (seção 14), não perfil. O detalhe fica no 02. -->

| ID | Perfil | Raia ou parte do processo | O que faz no sistema |
|---|---|---|---|
| PER-{{SIG}} | {{Nome do perfil}} | {{Raia do BPMN}} | {{Ações principais}} |

## 8. Glossário

<!-- A linguagem do domínio. Estes termos aparecem nos nomes de entidade, função e tela, sem tradução. Um termo, um
significado: se a área usa duas palavras para a mesma coisa, escolha uma e registre a outra como sinônimo. -->

| Termo | Significado | Nome no código |
|---|---|---|
| {{Termo do processo}} | {{Definição curta, na linguagem da área}} | {{NomeNoCodigo}} |

## 9. Casos de uso

<!-- Cada atividade "automatiza" ou "apoia" gera um caso de uso, ou um passo de um caso maior. Evento de tempo gera
caso de uso do sistema, com ator "sistema (agendado)". Acrescente os que todo sistema precisa: administrar perfis e
acessos, manter parâmetros, consultar histórico. Nome no formato verbo + objeto. Descrição no 04. -->

| ID | Caso de uso | Ator principal | Módulo | Release |
|---|---|---|---|---|
| UC-01 | {{Verbo + objeto}} | PER-{{SIG}} | MOD-{{SIG}} | R1 |
| UC-02 | {{Verbo + objeto}} | {{Perfil, ou sistema (agendado) para evento de tempo}} | MOD-{{SIG}} | R1 |

## 10. Requisitos funcionais

<!-- Resumo de uma linha, começando pelo verbo. O identificador leva a sigla do módulo. Origem, critério de aceite e
rastreio ficam no 03; as duas listas têm de bater. -->

| ID | Requisito (resumo) | Módulo | Release |
|---|---|---|---|
| RF-{{SIG}}-01 | {{Verbo + objeto, numa linha}} | MOD-{{SIG}} | R1 |

## 11. Requisitos não funcionais

<!-- Cada um com número e forma de medir, pelas características da ISO/IEC 25010. "Rápido" não é requisito. -->

| ID | Característica (ISO/IEC 25010) | Requisito |
|---|---|---|
| RNF-01 | {{Desempenho, confiabilidade, segurança, usabilidade, manutenibilidade, portabilidade ou compatibilidade}} | {{Requisito com número e unidade}} |

## 12. Entidades principais

<!-- O que o sistema guarda e tem identidade. Atributos, relacionamentos e integridade ficam no 06. -->

| Entidade | O que guarda | Módulo |
|---|---|---|
| {{NomeDaEntidade}} | {{O que ela representa no processo}} | MOD-{{SIG}} |

## 13. Telas

<!-- Cada caso de uso com pessoa usa ao menos uma tela. Descrição no 11; as duas listas têm de bater. -->

| ID | Tela | Perfis | Casos de uso |
|---|---|---|---|
| TL-01 | {{Nome da tela}} | PER-{{SIG}} | UC-01 |
| TL-02 | {{Nome da tela}} | PER-{{SIG}} | UC-02 |

## 14. Integrações

| ID | Sistema externo | Dado trocado | Forma |
|---|---|---|---|
| INT-01 | {{Nome do sistema externo}} | {{O que entra ou sai}} | {{API, arquivo, troca manual na primeira release}} |

## 15. Releases

<!-- A primeira release é um esqueleto que anda: o fluxo principal de ponta a ponta, com o mínimo de cada camada.
Toda release tem uma prova de aceite verificável. -->

| Release | Conteúdo | Módulos | Prova de aceite |
|---|---|---|---|
| R1 | {{O que fica pronto}} | MOD-{{SIG}} | AT-01 |
| R2 | {{O que fica pronto}} | {{Módulos}} | {{Teste ou indicador que prova a entrega}} |

## Pronto quando

- [ ] Toda atividade do TO-BE está no quadro de escopo, com tratamento.
- [ ] Toda atividade "automatiza" ou "apoia" aponta um módulo.
- [ ] Toda atividade "fora" e toda melhoria sem requisito têm o motivo escrito.
- [ ] Toda meta tem linha de base com o fato de origem.
- [ ] As listas de módulos, perfis, glossário, casos de uso, requisitos, entidades, telas, integrações e releases existem.
- [ ] Todo módulo tem ao menos um requisito funcional.
- [ ] A stack está marcada como proposta e aponta o ADR.
