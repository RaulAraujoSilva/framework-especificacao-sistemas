# Pasta de saída

Índice gerado por `gerar_documentos.py`. Não edite à mão: rode o script de novo.

Pacote de especificação versão 1.0 (minuta para avaliação), gerado em 05/11/2026.

Impressão digital da fonte: `6fd45c1d875a7be8`. Se a fonte mudar e os documentos não forem gerados de novo, `conferir_especificacao.py --documentos` acusa documento desatualizado (C17).

| Pasta | O que tem | Quem produz |
|---|---|---|
| `levantamento/` | Dados que sustentam a especificação: casos reais com resultado conhecido, regras e parâmetros com origem, conferências refeitas por script | extração (com a fonte de cada valor) + scripts |
| `documentos_para_avaliacao/` | Versões de leitura para as áreas avaliarem: guia, cadernos por público, planilha de parecer, especificação completa, protótipo e um PDF por capítulo | `gerar_documentos.py` |
| `pareceres/` | `recebidos/`: planilhas de avaliação devolvidas pelas áreas; `00_Consolidado_dos_pareceres.xlsx`: todos os pareceres item por item | áreas avaliadoras + `consolidar_pareceres.py` |

## documentos_para_avaliacao/

Comece pelo `00_Guia_de_avaliacao.pdf`.

| Arquivo | O que é | Para quem | Leitura |
|---|---|---|---|
| `00_Guia_de_avaliacao.pdf` | Quem avalia o quê, como registrar o parecer, decisões pendentes | Todos | 10 min |
| `01_Caderno_Gestao.pdf` | Caderno da gestão (capítulos 01, 02, 13) | Conselho-Diretor e gestor do processo | 1 h 30 min |
| `02_Caderno_Area_Tecnica.pdf` | Caderno da área técnica (capítulos 03, 04, 08, 11, 12, 16, 17) | Área técnica responsável pelo cálculo e pela análise do pleito | 4 h 40 min |
| `03_Caderno_Procuradoria.pdf` | Caderno da Procuradoria (capítulos 01, 08, 14, 17) | Procuradoria e área jurídica | 1 h 45 min |
| `04_Caderno_TI.pdf` | Caderno da TI (capítulos 05, 06, 07, 09, 10, 14, 15) | Tecnologia da informação e segurança | 5 h 35 min |
| `05_Planilha_de_avaliacao.xlsx` | Planilha de parecer: 334 itens e 11 decisões pendentes, com lista de parecer | Todos os avaliadores |  |
| `06_Especificacao_completa.pdf` | Especificação completa (capítulos 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17) | Todos os avaliadores e a equipe de desenvolvimento | 11 h 45 min |
| `07_Prototipo_de_telas.pdf` | Protótipo de baixa fidelidade: 17 telas, em páginas paisagem | Área técnica, gestão e TI |  |
| `capitulos/01_Visao_e_escopo.pdf` | Capítulo 01: Visão, escopo e identificadores | Conselho-Diretor e gestor do processo; Procuradoria e área jurídica | 20 min |
| `capitulos/02_Perfis_e_jornadas.pdf` | Capítulo 02: Perfis de usuário e jornadas | Conselho-Diretor e gestor do processo | 30 min |
| `capitulos/03_Requisitos.pdf` | Capítulo 03: Requisitos | Área técnica responsável pelo cálculo e pela análise do pleito | 55 min |
| `capitulos/04_Casos_de_uso.pdf` | Capítulo 04: Casos de uso | Área técnica responsável pelo cálculo e pela análise do pleito | 1 h |
| `capitulos/05_Arquitetura_e_decisoes.pdf` | Capítulo 05: Arquitetura e decisões registradas | Tecnologia da informação e segurança | 1 h 55 min |
| `capitulos/06_Modelo_de_dados.pdf` | Capítulo 06: Modelo de dados | Tecnologia da informação e segurança | 45 min |
| `capitulos/07_Contratos_e_API.pdf` | Capítulo 07: Contratos de dados e API | Tecnologia da informação e segurança | 25 min |
| `capitulos/08_Regras_de_negocio.pdf` | Capítulo 08: Regras de negócio | Área técnica responsável pelo cálculo e pela análise do pleito; Procuradoria e área jurídica | 55 min |
| `capitulos/09_Integracoes.pdf` | Capítulo 09: Integrações | Tecnologia da informação e segurança | 20 min |
| `capitulos/10_Experiencia_e_interface.pdf` | Capítulo 10: Experiência do usuário e interface | Tecnologia da informação e segurança | 1 h |
| `capitulos/11_Telas.pdf` | Capítulo 11: Telas | Área técnica responsável pelo cálculo e pela análise do pleito | 1 h |
| `capitulos/12_Testes_de_aceitacao.pdf` | Capítulo 12: Testes de aceitação | Área técnica responsável pelo cálculo e pela análise do pleito | 30 min |
| `capitulos/13_Backlog_e_entregas.pdf` | Capítulo 13: Backlog e entregas | Conselho-Diretor e gestor do processo | 40 min |
| `capitulos/14_Operacao.pdf` | Capítulo 14: Operação, acesso e LGPD | Procuradoria e área jurídica; Tecnologia da informação e segurança | 20 min |
| `capitulos/15_Seguranca.pdf` | Capítulo 15: Segurança | Tecnologia da informação e segurança | 55 min |
| `capitulos/16_Levantamento_dos_calculos.pdf` | Capítulo 16: Levantamento dos cálculos da coorte | Área técnica responsável pelo cálculo e pela análise do pleito | 10 min |
| `capitulos/17_Layout_e_validacao_do_pleito.pdf` | Capítulo 17: Layout e validação do pleito | Área técnica responsável pelo cálculo e pela análise do pleito; Procuradoria e área jurídica | 10 min |

## levantamento/

| Arquivo | O que é | Para quem |
|---|---|---|
| `levantamento/calculo/componentes.csv` | Fonte de cada componente da fórmula e se o número-índice foi achado na série pública | Área técnica e TI |
| `levantamento/calculo/extracao_SEI-220007_001126_2023.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-220007_004053_2022.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-220007_004205_2022.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-220007_004207_2022.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_000036_2023.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_000037_2023.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_001912_2024.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_001913_2024.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_001914_2024.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_007635_2024.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_007637_2024.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_007639_2024.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_009058_2025.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_009594_2025.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_009822_2025.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_009837_2025.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_009940_2024.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/extracao_SEI-480002_009982_2025.json` | Fórmula, pesos e números de cada apuração, copiados das peças do processo (sem cálculo) | Área técnica |
| `levantamento/calculo/recalculo.csv` | Recálculo de cada apuração pelos números-índice e pelas variações escritas | Área técnica |
| `levantamento/calculo/resumo.json` | Contagens do levantamento (cálculos que conferem, índices achados) | Todos |
| `levantamento/contratos/paraty_008_2014.json` | Cadastro de parâmetros do contrato-piloto, cada um com o trecho literal do contrato | Área técnica e Procuradoria |
| `levantamento/pleito/exemplo_paraty_2026.json` | Pleito real escrito no layout | Área técnica e TI |
| `levantamento/pleito/exemplo_paraty_2026.validacao.json` | Resultado das regras V01 a V12 no pleito real | Área técnica |
| `levantamento/pleito/pleito_reajuste.schema.json` | Layout do pleito (JSON Schema) | TI e área técnica |
