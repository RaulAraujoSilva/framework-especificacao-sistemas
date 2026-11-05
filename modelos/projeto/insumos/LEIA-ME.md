# Insumos do processo

Copie aqui as saídas do mapeamento do processo que o sistema vai atender. A especificação cita cada uma pelo
identificador (atividade do BPMN, melhoria, norma, indicador, caso). A lista completa, com o mínimo necessário quando
o mapeamento não seguiu o mesmo método, está no capítulo 01 da metodologia (`docs/metodologia/01_INSUMOS_DO_PROCESSO.md`
do repositório especificacao-sistema-sei).

| Arquivo | O que traz | Situação |
|---|---|---|
| `modelo_<processo>.json` ou `.bpmn` | Modelo do TO-BE: atividades, raias, decisões, eventos, gatilhos e saídas | {{presente ou ausente}} |
| `melhorias_<processo>.json` | Melhorias do TO-BE, com identificador | {{...}} |
| `fatos_<processo>.json` | Números do diagnóstico (tempos, volumes, esperas), com origem | {{...}} |
| `normas_<processo>.json` | Normas e requisitos legais com trecho literal | {{...}} |
| `controles_<processo>.json` | Indicadores com linha de base e meta | {{...}} |
| `casos_<processo>.json` | Linha do tempo dos casos reais | {{...}} |

Nenhum arquivo aqui leva nome de pessoa. Dado pessoal fica fora do git (`dados/`).
