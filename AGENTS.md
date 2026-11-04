# Instruções para a IA que vai especificar o sistema

Você é a IA de um aluno do curso. Sua tarefa é **especificar o sistema do processo-piloto do órgão do aluno** e levar
a especificação à aprovação das áreas, com o mesmo rigor do caso de referência (Reajusta, AGENERSA/RJ). O passo a
passo está em [`docs/metodologia/ROTEIRO_ESPECIFICACAO.md`](docs/metodologia/ROTEIRO_ESPECIFICACAO.md).

## 1. Leia antes de agir, nesta ordem

1. [`docs/metodologia/00_VISAO_GERAL.md`](docs/metodologia/00_VISAO_GERAL.md): fluxo, insumos do mapeamento, tipos de etapa.
2. [`docs/metodologia/ROTEIRO_ESPECIFICACAO.md`](docs/metodologia/ROTEIRO_ESPECIFICACAO.md): o roteiro que você vai executar.
3. O capítulo de cada etapa, **antes** de começá-la: [01](docs/metodologia/01_ESPECIFICACAO_SISTEMA.md) para o
   levantamento e o pacote; [02](docs/metodologia/02_DOCUMENTOS_E_PASTA_DE_SAIDA.md) para os documentos de leitura e
   a pasta de saída.
4. O arquivo equivalente do caso de referência, como exemplo de formato e de nível de detalhe: `especificacao/`,
   `saida/levantamento/`, `saida/documentos_para_avaliacao/`.

Na primeira sessão, pergunte ao aluno o órgão, o processo-piloto escolhido no mapeamento e onde estão as saídas do
mapeamento desse processo. Não presuma.

## 2. Regras de trabalho

1. **Nenhum requisito sem origem.** Cada RF, RN e critério de aceite cita a melhoria, a norma, a cláusula ou o caso
   real de onde veio.
2. **Número só do código.** Não digite número na especificação: cite o fato (`insumos/mapeamento/fatos_<cod>.json`)
   ou a saída de script (`saida/levantamento/...`).
3. **Extraia sem calcular.** Na extração das peças, copie fórmula, pesos e números literalmente, com o documento de
   origem. Quem calcula é o script.
4. **Trecho de contrato é literal.** O validador confere palavra por palavra.
5. **Portão que falha para tudo.** Não contorne, não desative teste, não edite saída para passar. Corrija a causa.
6. **Hipótese explícita.** Horas, custos e prazos propostos levam "(proposto)" ou "hipótese, a calibrar".

## 3. Documentos para avaliação e pasta de saída

A especificação só termina quando as áreas a avaliam. Para isso:

1. **Fonte única.** Você escreve só em `especificacao/` (e nos relatórios de `docs/`). Os PDFs e a planilha saem de
   `python scripts/gerar_documentos.py`. **Nunca** crie ou edite arquivo à mão em `saida/documentos_para_avaliacao/`.
2. **Configure o conjunto** em `especificacao/documentos.json`: capítulos, cadernos por público (com as perguntas que
   cada público responde), prefixos de identificador avaliáveis, versão e situação. Todo capítulo novo entra num
   caderno; todo prefixo novo entra em `itens_avaliaveis`.
3. **Organize e nomeie a saída** pelo capítulo 02 §4: subpasta pelo conteúdo (nunca `fase5/`, `novos/`), documento
   para pessoas como `NN_Palavras_com_sublinhado.ext`, sem acento, espaço, versão, "final" ou data no nome; dado
   para máquina em subpasta própria. Todo arquivo de `saida/` tem linha no `LEIA-ME.md`, que é gerado, não escrito.
4. **Leia os avisos do gerador.** Menção a IA que é função do sistema fica; frase sobre como o documento foi feito
   sai da fonte. Nenhum caminho local da máquina em documento.
5. **Rode os testes** depois de gerar. "Documento desatualizado" quer dizer que a fonte mudou depois da geração.
6. **Mostre ao aluno** as páginas do capítulo 02 §6 e espere a revisão dele antes do envio às áreas.

## 4. PARADAs

Pare e espere o aluno:

- ao fim da etapa E2 (cadastro e layout prontos), para conferir com a área técnica;
- na **PARADA 11**, depois de gerar os documentos: o envio às áreas, a avaliação e as decisões são das pessoas;
- depois de duas falhas seguidas no mesmo portão.

## 5. Nunca

- Inventar regra de negócio, prazo ou parâmetro que não esteja na norma, no contrato ou nos autos. Lacuna vira
  decisão pendente (DEC-nn), com dono.
- Pôr nome de pessoa em extração, cadastro, especificação ou documento. Use a função (analista, conselheiro relator).
- Versionar `dados/`, `.env`, `saida/pareceres/` ou textos de contrato com assinaturas.
- Ler, imprimir ou gravar chave de API. Chave só por variável de ambiente.
- Escrever em entregável para o órgão que o texto foi produzido por IA, ou citar caminho local da máquina.
- Português sem acentuação correta.
