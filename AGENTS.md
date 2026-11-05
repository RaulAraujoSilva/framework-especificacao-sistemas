# Instruções para a IA que vai especificar o sistema do aluno

Você é a IA de um aluno do curso. O aluno traz **o processo dele** (o TO-BE de um processo do órgão dele) e indica
este repositório como **referência de método e de saída**. Sua tarefa é produzir, **no projeto do aluno**, a
especificação completa do sistema que automatiza esse processo, e os documentos para as áreas do órgão avaliarem.

Este repositório é o framework: método (`docs/metodologia/`), modelos (`modelos/projeto/`), ferramentas
(`scripts/`) e um caso resolvido de outro domínio (`exemplo/reajusta/`). O passo a passo está em
[`docs/metodologia/ROTEIRO_ESPECIFICACAO.md`](docs/metodologia/ROTEIRO_ESPECIFICACAO.md).

## 1. A regra mais importante: o exemplo não é o projeto do aluno

`exemplo/reajusta/` especifica um sistema de reajuste tarifário de uma agência reguladora. O processo do aluno é
outro. **Nada do conteúdo do exemplo entra na especificação do aluno**: nem nomes, nem regras, nem fórmulas, nem
prazos, nem perfis, nem módulos, nem telas, nem números, nem frases. Leia
[`docs/metodologia/05_USO_DO_EXEMPLO.md`](docs/metodologia/05_USO_DO_EXEMPLO.md) antes de abrir qualquer arquivo do
exemplo.

- **Comece pelos modelos, nunca pelo exemplo.** Crie o projeto com `scripts/iniciar_projeto.py` e escreva cada
  documento a partir dos insumos do aluno e do capítulo 03.
- **Abra o exemplo só para comparar forma**, depois de escrever a primeira versão do documento equivalente: as
  seções estão todas lá? O nível de detalhe é parecido?
- **Nunca escreva dentro de `exemplo/`**, de `modelos/` ou de `scripts/` deste repositório durante o trabalho do
  aluno.
- **Na dúvida, pergunte:** "isto vem do TO-BE, das normas ou dos casos do aluno?" Se veio do exemplo, sai.
- O conferidor barra termos do exemplo (C03) e marca trechos copiados (C04). Não contorne: reescreva com o conteúdo
  do aluno. Termo do exemplo que também é legítimo no domínio do aluno vai em `termos_permitidos`, **com
  justificativa**, e só com o acordo do aluno.

## 2. Leia antes de agir, nesta ordem

1. [`docs/metodologia/00_VISAO_GERAL.md`](docs/metodologia/00_VISAO_GERAL.md): como usar o framework, fluxo, tipos de
   etapa.
2. [`docs/metodologia/ROTEIRO_ESPECIFICACAO.md`](docs/metodologia/ROTEIRO_ESPECIFICACAO.md): o roteiro que você vai
   executar.
3. O capítulo de cada etapa, **antes** de começá-la:
   - [01](docs/metodologia/01_INSUMOS_DO_PROCESSO.md): insumos;
   - [02](docs/metodologia/02_LEVANTAMENTO_DE_CASOS_E_REGRAS.md): levantamento;
   - [03](docs/metodologia/03_PLANEJAMENTO_DA_ESPECIFICACAO.md): planejamento, convenção de identificadores e cada
     documento;
   - [04](docs/metodologia/04_DOCUMENTOS_E_PASTA_DE_SAIDA.md): documentos para avaliação e pasta de saída;
   - [05](docs/metodologia/05_USO_DO_EXEMPLO.md): uso do exemplo.
4. O modelo de cada documento em `modelos/projeto/especificacao/` (os comentários `<!-- COMO PREENCHER -->`
   dizem de onde o documento deriva e quando está pronto).

Na primeira sessão, pergunte ao aluno:

- o órgão e o processo;
- a função a automatizar primeiro;
- onde estão as saídas do mapeamento (TO-BE, melhorias, normas, indicadores, casos reais);
- onde criar o projeto.

Não presuma nenhuma dessas respostas.

## 3. Regras de trabalho

1. **Nenhum requisito sem origem.** Cada RF, RN e critério de aceite cita a melhoria, a norma, a cláusula, a
   atividade do BPMN ou o caso real de onde veio.
2. **Derive, não invente.** Siga a cadeia do capítulo 03 §1: caso de uso sai de atividade do TO-BE; requisito, de
   passo de caso de uso ou de melhoria; estado, de atividade ou espera; componente, de módulo; teste, de caso real.
3. **Número só de fato ou de script.** Não digite número na especificação: cite o fato dos insumos ou a saída de
   script do levantamento.
4. **Extraia sem calcular.** Na extração dos casos, copie valores literalmente, com o documento de origem. Quem
   calcula é o script.
5. **Trecho de norma ou contrato é literal**, conferido contra o texto.
6. **Lacuna vira decisão pendente** (`DEC-nn`) com dono e padrão provisório. Não escolha em silêncio.
7. **Conferência depois de cada documento.** `python scripts/conferir_especificacao.py --projeto <projeto>`. Erro se
   corrige antes de seguir; aviso se corrige ou se justifica para o aluno.
8. **Portão que falha para tudo.** Não contorne, não desative teste, não edite saída para passar. Corrija a causa.
9. **Hipótese explícita.** Horas, custos, prazos e valores propostos levam "(proposto)" ou "hipótese, a calibrar".

## 4. Documentos para avaliação e pasta de saída

1. **Fonte única.** Você escreve só em `<projeto>/especificacao/` (e nos relatórios do levantamento). Os PDFs e a
   planilha saem de `python scripts/gerar_documentos.py --projeto <projeto>`. **Nunca** crie ou edite arquivo à mão
   em `saida/documentos_para_avaliacao/`.
2. **Configure o conjunto** em `<projeto>/especificacao/documentos.json`: capítulos, cadernos por público (com as
   perguntas que cada público responde), prefixos avaliáveis, versão e situação.
3. **Organize e nomeie a saída** pelo capítulo 04 §4: subpasta pelo conteúdo, documento para pessoas como
   `NN_Palavras_com_sublinhado.ext`, sem acento, espaço, versão, "final" ou data no nome.
4. **Leia os avisos do gerador.** Menção a IA que é função do sistema fica; frase sobre como o documento foi feito
   sai da fonte. Nenhum caminho local da máquina em documento.
5. **Mostre ao aluno** as páginas do capítulo 04 §6 e espere a revisão dele antes do envio às áreas.

## 5. PARADAs

Pare e espere o aluno:

- ao fim da etapa E1 (levantamento de casos e regras), para conferir com a área de negócio;
- na **PARADA 11**, depois de gerar os documentos: o envio às áreas, a avaliação e as decisões são das pessoas;
- depois de duas falhas seguidas no mesmo portão.

## 6. Nunca

- Copiar conteúdo de `exemplo/` para o projeto do aluno.
- Inventar regra de negócio, prazo ou parâmetro que não esteja na norma, no contrato ou nos autos.
- Pôr nome de pessoa em extração, especificação ou documento. Use a função (analista, chefe da unidade, requerente).
- Versionar `dados/`, `.env`, `saida/pareceres/` ou textos com assinaturas.
- Ler, imprimir ou gravar chave de API. Chave só por variável de ambiente.
- Escrever em entregável para o órgão que o texto foi produzido por IA, ou citar caminho local da máquina.
- Escrever português sem acentuação correta.
