# 01. Insumos do processo: o que trazer do TO-BE

A especificação deriva do processo. Antes de escrever qualquer requisito, reúna em `insumos/` o que o mapeamento
produziu. Cada item abaixo é citado pela especificação por um identificador. Por isso, insumo sem identificador
precisa ganhar um antes de começar.

Se o seu mapeamento seguiu o repositório
[mapeamento-processos-sei](https://github.com/RaulAraujoSilva/mapeamento-processos-sei), os arquivos já existem com
esses nomes. Se não seguiu, monte o **mínimo** da seção 2 à mão, com o mesmo cuidado de origem.

## 1. Insumos e uso de cada um

| Insumo | O que traz | Identificador que a especificação cita | Onde é usado |
|---|---|---|---|
| Modelo do TO-BE (BPMN) | Atividades, raias, decisões, eventos de tempo e de mensagem, gatilhos e saídas de cada atividade | Atividade (`t1`, `t2`...), decisão (`g1`), evento (`e1`) | Quadro de escopo, casos de uso, estados, jornadas |
| Melhorias do TO-BE | O que muda em relação ao AS-IS, e por quê | `M-<processo>-nn` | Origem dos requisitos funcionais |
| Fatos do diagnóstico | Tempos, esperas, volumes, retrabalho, caminhos mais frequentes, com a origem do número | Chave do fato | Problema, metas e linha de base |
| Normas e requisitos legais | Leis, decretos, resoluções, contratos, com o trecho literal | `N-<processo>-nn`, `R-<processo>-nn` | Regras de negócio, prazos, exigências a terceiros |
| Indicadores e controles | Indicador, linha de base, meta, controle de qualidade | `I-<processo>-nn`, `Q-<processo>-nn` | Requisitos de indicadores, metas do sistema, testes |
| Casos reais | Linha do tempo de casos concluídos: marcos, documentos, resultado | Número do processo ou do caso | Jornadas, testes de aceitação, conferência da máquina de estados |
| Avaliação AS-IS | Gargalo, desperdícios, potencial de automação por atividade | Atividade | Ordem das ondas |
| Priorização da automação | Por que este processo e esta função vêm primeiro | — | Escopo da primeira onda |

## 2. O mínimo para começar

Sem estes cinco itens, a especificação vira opinião:

1. **O TO-BE desenhado**, com raias e decisões, e a lista de atividades com identificador.
2. **A lista de melhorias**, cada uma com identificador e a atividade que muda.
3. **As normas** que regem o processo, com artigo e trecho literal.
4. **Três a dez casos reais concluídos**, com os documentos e o resultado. São eles que viram teste.
5. **A linha de base** de pelo menos um indicador (por exemplo, tempo total do caso, da abertura ao encerramento).

## 3. Cuidados

- **Sem nome de pessoa.** Troque nomes por função (analista, chefe da unidade, requerente) antes de copiar para
  `insumos/`. Dado pessoal fica em `dados/`, fora do git.
- **Número com origem.** Cada número do diagnóstico diz de onde veio (consulta, planilha, script). A especificação
  cita a chave do fato, não o número solto.
- **Uma versão do TO-BE.** Se o TO-BE mudou depois do mapeamento, atualize o modelo em `insumos/` antes de derivar os
  casos de uso. A especificação de um TO-BE que ninguém aprovou não serve.

## 4. Pronto quando

- [ ] `insumos/LEIA-ME.md` lista cada arquivo e diz se está presente.
- [ ] Toda atividade, melhoria, norma e indicador tem identificador.
- [ ] Há casos reais com resultado conhecido.
- [ ] Nenhum arquivo de `insumos/` tem nome de pessoa.
