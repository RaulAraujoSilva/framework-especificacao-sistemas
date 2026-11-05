# 08. Regras de negócio

<!-- COMO PREENCHER: este documento deriva das normas e contratos (com trecho literal) e dos casos reais com resultado
conhecido do levantamento. Regras: capítulo 03 da metodologia, §3.5 (regras de negócio e decisões pendentes). Separe
regra de requisito: o requisito diz o que o sistema faz ("contar o prazo"); a regra diz a lei do negócio ("o prazo
conta em dias úteis a partir da ciência"), que existe mesmo sem sistema. Escreva primeiro as convenções transversais,
depois as regras por módulo. Lacuna (a norma não diz, os casos divergem, falta dado) vira decisão pendente, nunca
escolha em silêncio. Pronto quando: toda regra tem fonte com trecho literal e exemplo de caso real; toda regra é
citada por requisito, caso de uso, tela ou teste; toda lacuna tem DEC com dono e padrão provisório. O equivalente do
caso resolvido é exemplo/reajusta/especificacao/08_REGRAS_NEGOCIO.md. Ele serve só de referência de formato e de
nível de detalhe: não copie nenhuma frase, nome ou termo dele. -->

Regras do {{Nome do sistema}}, cada uma com identificador, enunciado, fonte com trecho literal, parâmetros e um
exemplo calculado com caso real. Os requisitos que aplicam as regras estão no [03_REQUISITOS.md](03_REQUISITOS.md); os
testes que as exercitam, no [12_TESTES.md](12_TESTES.md).

Fontes: {{Arquivos do levantamento e do mapeamento de onde saem as normas, os trechos e os casos reais}}.

{{Se houver uma implementação de referência (planilha ou script que já reproduz os casos reais), diga qual é e que,
em caso de divergência nos casos de teste, ela prevalece até prova em contrário}}.

## Sumário

| Grupo | Regras | Módulo |
|---|---|---|
| 1. Convenções | arredondamento, calendário, datas | todos |
| 2. MOD-{{SIG}} {{Nome do módulo}} | RN-{{SIG}}-01 | MOD-{{SIG}} |
| 3. Tabelas de decisão | {{Regras que viram tabela}} | {{Módulos}} |
| 4. Decisões pendentes | DEC-01 | — |

## 1. Convenções

<!-- Valem para todas as regras e todos os módulos. Quando a norma não fixa a convenção, registre a escolha como
decisão pendente (seção 4) e diga aqui o padrão provisório. Se uma convenção precisar ser citada por testes, dê a
ela um identificador RN próprio. -->

### 1.1 Números e arredondamento

- **Casas decimais:** {{Quantas casas cada tipo de número guarda e exibe, por exemplo valores, percentuais e quantidades}}.
- **Arredondamento:** {{Modo (por exemplo meio para cima ou meio para o par), em que ponto se arredonda e a fonte}}.
  Arredonda-se uma vez, no ponto que a regra manda, nunca em resultado intermediário.
- **Aritmética:** {{Tipo numérico usado no cálculo, por exemplo decimal exato, sem ponto flutuante binário}}.
- **Exemplo:** {{Número de um caso real antes e depois do arredondamento}}.

### 1.2 Calendário e contagem de prazos

- **Dia útil:** {{Dias da semana com expediente, e o calendário de feriados adotado (nacional, estadual, municipal)}}.
- **Feriados e pontos facultativos:** {{Fonte da lista e quem a mantém no sistema}}.
- **Contagem:** {{Se o dia do início entra ou não, se o do vencimento entra, e o que acontece quando o vencimento cai em dia sem expediente}}.
- **Fonte:** {{Norma que fixa a contagem, com artigo}}: "{{Trecho literal da norma}}".
- **Exemplo:** {{Data de início de um caso real + prazo = data de vencimento, com os dias que não contaram}}.

### 1.3 Datas, horas e fuso

- **Fuso:** {{Fuso horário do órgão}}. Datas sem hora são guardadas como data civil, sem conversão de fuso.
- **Exibição:** {{Formato de data, hora e número na tela e nos documentos}}.

## 2. MOD-{{SIG}} {{Nome do módulo}}

<!-- Uma seção por módulo, um bloco por regra. Enunciado declarativo, sem falar do sistema. A fonte traz o trecho
copiado letra por letra da norma, do contrato ou da decisão, com o artigo ou a cláusula. Os parâmetros têm valor,
unidade e vigência: valor que muda no tempo guarda a data em que passou a valer. O exemplo usa um caso real, com a
conta feita e o resultado conferido com os autos; caso em que os autos têm erro também serve, desde que se diga o
erro. -->

### RN-{{SIG}}-01 {{Nome da regra}}

- **Enunciado:** {{A regra numa frase declarativa, por exemplo "a solicitação sem o documento X não é analisada"}}
- **Fonte:** {{Norma, artigo, cláusula ou decisão}}: "{{Trecho literal da fonte}}"
- **Parâmetros:** {{Nome, valor, unidade e vigência de cada parâmetro}}
- **Exemplo com caso real:** {{Caso anonimizado: entrada, conta passo a passo e resultado, com o documento de origem}}
- **Exceções:** {{Situações em que a regra não se aplica, ou "nenhuma"}}
- **Citada por:** RF-{{SIG}}-01, UC-01, AT-01

## 3. Tabelas de decisão

<!-- Regra com muitas combinações vira tabela: uma coluna por condição, uma por resultado, uma linha por combinação.
Cada linha vira um teste direto no 12. Use "—" para condição que não importa naquela linha. -->

### 3.1 {{Nome da decisão, por exemplo situação da solicitação após a conferência}}

| {{Condição 1}} | {{Condição 2}} | Resultado | Ação do sistema | Regra |
|---|---|---|---|---|
| sim | sim | {{Resultado}} | {{O que o sistema faz}} | RN-{{SIG}}-01 |
| sim | não | {{Resultado}} | {{O que o sistema faz}} | RN-{{SIG}}-01 |
| não | — | {{Resultado}} | {{O que o sistema faz}} | RN-{{SIG}}-01 |

## 4. Decisões pendentes

<!-- Abra uma linha quando a norma não diz, os casos divergem ou falta dado. O padrão provisório é o que o sistema
faz até a decisão, e precisa estar escrito também na regra afetada. Copie cada linha para a seção "Decisões
pendentes" do README do pacote, que é lida pela planilha de avaliação. -->

| ID | O que decidir | Quem decide | Padrão provisório até a decisão | Impacto | Prazo para decidir |
|---|---|---|---|---|---|
| DEC-01 | {{A pergunta em aberto, numa frase}} | {{Unidade ou cargo}} | {{O que o sistema faz enquanto isso, citando a regra}} | {{Regras, requisitos e testes que mudam com a decisão}} | {{Data ou release}} |

## Pronto quando

- [ ] As convenções de arredondamento, calendário e datas estão escritas, com fonte ou com decisão pendente.
- [ ] Toda regra tem enunciado, fonte com trecho literal, parâmetros e exemplo de caso real.
- [ ] Toda regra com muitas combinações virou tabela de decisão.
- [ ] Toda regra é citada por requisito, caso de uso, tela ou teste.
- [ ] Toda lacuna virou decisão pendente, com quem decide, padrão provisório e prazo.
- [ ] Toda decisão pendente está também no README do pacote.
