# Roteiro: especificar o sistema do piloto e levar à aprovação

Passo a passo para a IA do aluno (e para o aluno) replicar a especificação no próprio órgão. Cada etapa tem ação,
comando, aceite e o artefato que fica na pasta certa. **PARADA** é ponto em que a IA para e espera a pessoa indicada.
Antes de cada etapa, leia o capítulo citado.

Pré-requisito: o mapeamento do órgão foi até a priorização (PARADA 10 do repositório
[mapeamento-processos-sei](https://github.com/RaulAraujoSilva/mapeamento-processos-sei)) e o tipo-piloto está escolhido.

## Etapa E0: preparação

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E0.1 | Instalar dependências | `pip install -r requirements.txt` e `python -m playwright install chromium` | `python -m pytest tests` passa no caso de referência | — |
| E0.2 | Trazer os insumos do mapeamento do tipo-piloto | copiar os arquivos de [00_VISAO_GERAL.md](00_VISAO_GERAL.md) §2 | Um arquivo por linha da tabela, com o código do processo no nome | `insumos/mapeamento/` |
| E0.3 | Ajustar o perfil do órgão (feriados, fontes de índice, séries públicas) | editar `perfis/<orgao>.py`; `PERFIL=<orgao>` | `python -c "import sys; sys.path.insert(0,'scripts'); import comum"` sem erro | `perfis/<orgao>.py` |

## Etapa E1: levantamento dos casos

Capítulo: [01_ESPECIFICACAO_SISTEMA.md](01_ESPECIFICACAO_SISTEMA.md) §2 a §4.

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E1.1 | Escolher a função da onda 1 | — | Regra mais fechada e dado mais disponível, pela avaliação AS-IS | registro no capítulo 01 do pacote |
| E1.2 | Extrair as apurações de cada processo da coorte (agente) | agente, um arquivo por processo | Valores literais com documento de origem; nenhuma conta; nenhum nome de pessoa | `saida/levantamento/calculo/extracao_<processo>.json` |
| E1.3 | Recalcular e classificar as fontes | `python scripts/recalcular_reajuste.py` (sem `--offline`, que zera a busca nas séries) | Cada divergência com causa classificada (erro no texto, arredondamento, regra diferente) | `recalculo.csv`, `componentes.csv`, `resumo.json` |

## Etapa E2: regras com origem

Capítulo: [01_ESPECIFICACAO_SISTEMA.md](01_ESPECIFICACAO_SISTEMA.md) §5 e §6.

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E2.1 | Cadastro do contrato-piloto (agente) | agente | Todo parâmetro com documento e trecho literal; uma versão por aditivo que muda o reajuste | `saida/levantamento/contratos/<contrato>.json` |
| E2.2 | Layout do pleito e pleito real no layout | — | JSON Schema válido; pleito real escrito sem perda de casas decimais | `saida/levantamento/pleito/` |
| E2.3 | Validar o pleito real | `python scripts/validar_pleito.py <pleito> <cadastro>` | Recálculo e total conferem; cada erro e aviso explicado | `<pleito>.validacao.json` |

## Etapa E3: pacote técnico

Capítulo: [01_ESPECIFICACAO_SISTEMA.md](01_ESPECIFICACAO_SISTEMA.md) §7 e §8. Modelo: o pacote do caso de referência
em [`especificacao/`](../../especificacao/README.md).

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E3.1 | Visão, escopo e identificadores (o documento-base) | — | Todo identificador usado nos outros documentos nasce aqui | `especificacao/01_VISAO_ESCOPO.md` |
| E3.2 | Documentos 02 a 15, ADRs, contratos, Prisma, protótipo | — | Requisito com origem e critério de aceite; lacunas do §8 do capítulo fechadas | `especificacao/` |
| E3.3 | Fixtures de aceite a partir do levantamento | `python especificacao/ferramentas/gerar_fixtures.py` | `--conferir` dá "confere" em todos | `especificacao/fixtures/` |
| E3.4 | Regras de código para a IA de desenvolvimento | — | Camadas, portões, proibições e Definition of Done escritos | `especificacao/AGENTS_DESENVOLVIMENTO.md` |

## Etapa E4: documentos para avaliação

Capítulo: [02_DOCUMENTOS_E_PASTA_DE_SAIDA.md](02_DOCUMENTOS_E_PASTA_DE_SAIDA.md).

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E4.1 | Configurar capítulos, cadernos por público, itens avaliáveis e versão | editar `especificacao/documentos.json` | Todo capítulo em pelo menos um caderno; todo prefixo de identificador com capítulo dono; versão 1.0, "Minuta para avaliação" | `especificacao/documentos.json` |
| E4.2 | Gerar | `python scripts/gerar_documentos.py` | Sem erro de portão; avisos lidos e tratados na fonte quando forem comentário sobre como o texto foi feito | `saida/documentos_para_avaliacao/`, `saida/LEIA-ME.md` |
| E4.3 | Conferir | `python -m pytest tests` | Todos passam (documentos atualizados, nomes no padrão, LEIA-ME completo, planilha íntegra) | — |
| E4.4 | Revisão humana das páginas | abrir os arquivos da lista do capítulo 02 §6 | Aluno revisou guia, uma página de cada caderno, protótipo e planilha | — |
| E4.5 | Registrar a versão | `git commit` | Commit com a versão gerada | — |

## PARADA 11: avaliação pelas áreas

Dono: gestão do processo, área técnica, Procuradoria e TI. A IA prepara e para.

| # | Ação | Quem | Aceite |
|---|---|---|---|
| P11.1 | Enviar a cada área o guia, o caderno dela e a planilha, com prazo | aluno | Envio registrado (e-mail ou processo no SEI) |
| P11.2 | Avaliar e devolver a planilha | cada área | Planilha devolvida em `saida/pareceres/recebidos/` |
| P11.3 | Decidir as decisões pendentes | quem a tabela de decisões indica | Decisão tomada, com responsável e data, na aba "Decisões pendentes" |

## Etapa E5: consolidar, corrigir e aprovar

| # | Ação | Comando | Aceite | Artefato |
|---|---|---|---|---|
| E5.1 | Consolidar os pareceres | `python scripts/consolidar_pareceres.py` | Toda planilha recebida lida; parecer fora da lista para com erro | `saida/pareceres/00_Consolidado_dos_pareceres.xlsx` |
| E5.2 | Cobrar os itens sem parecer | aba "Sem parecer" | Zero item sem parecer, ou dispensa registrada pelo dono do processo | — |
| E5.3 | Corrigir a fonte para cada "Não aprovado" e "Aprovado com ajustes" | editar `especificacao/` | Coluna "Tratamento" preenchida em cada item | `especificacao/`, consolidado |
| E5.4 | Nova versão | subir `versao` em `documentos.json`; `python scripts/gerar_documentos.py`; testes | Reenvio só do que mudou, com a lista de mudanças | `saida/documentos_para_avaliacao/` |
| E5.5 | Aprovar | `situacao` = "Versão aprovada em DD/MM/AAAA"; gerar | Nenhum "Não aprovado" aberto; decisões tomadas | versão aprovada; fim da especificação |

Depois da E5.5, o pacote vai para o desenvolvimento: copie `especificacao/AGENTS_DESENVOLVIMENTO.md` como `AGENTS.md`
na raiz do repositório do sistema e o pacote para `docs/especificacao/` (detalhe em
[`especificacao/README.md`](../../especificacao/README.md)).
