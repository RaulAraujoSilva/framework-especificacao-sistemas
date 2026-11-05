# 05. Uso do caso resolvido sem contaminar a sua especificação

[`exemplo/reajusta/`](../../exemplo/reajusta/) é um caso resolvido de ponta a ponta: a especificação de um sistema
de reajuste tarifário de uma agência reguladora estadual, com o levantamento, o pacote técnico completo e os
documentos para avaliação. Ele existe para mostrar **como fica** cada artefato quando está pronto.

Ele não é ponto de partida. O seu sistema é de outro processo, outro órgão, outras regras. O risco é um só: conteúdo
do exemplo **vazar** para a sua especificação. Uma regra de cálculo, um perfil, um módulo, uma tela, um prazo ou uma
frase inteira que parecem razoáveis e não têm nada a ver com o seu processo. Vazamento é pior que lacuna, porque
parece trabalho feito e passa pela revisão.

## 1. O que se aproveita e o que não

| Pode olhar e imitar | Nunca copie |
|---|---|
| A estrutura de seções de cada documento | Nomes de módulos, perfis, telas, entidades, regras, integrações |
| O nível de detalhe (quantos passos num caso de uso, o que um critério de aceite contém) | Regras de negócio, fórmulas, prazos, parâmetros |
| O formato de uma tabela de rastreio, de uma ficha de integração, de uma máquina de estados | Números (metas, linhas de base, quantidades, percentuais) |
| Como uma decisão pendente é registrada | Decisões pendentes e seus donos |
| Como os documentos para avaliação ficam (abra os PDFs) | Frases do texto, mesmo as que parecem genéricas |
| A lógica de segurança e operação, como lista do que considerar | Escolhas de tecnologia e de hospedagem sem ADR próprio |

Na dúvida, a pergunta é: **isto vem do meu TO-BE, das minhas normas ou dos meus casos?** Se a resposta é "veio do
exemplo", sai.

## 2. Como as barreiras funcionam

1. **O projeto nasce dos modelos.** `scripts/iniciar_projeto.py` copia `modelos/projeto/`, que é neutro de domínio
   e tem testes que garantem que nenhum termo nem trecho do exemplo está nos modelos. Não comece copiando a pasta
   do exemplo.
2. **O exemplo se declara exemplo.** O `documentos.json` do caso resolvido tem `"exemplo": true`. O seu não tem, e por
   isso o conferidor aplica a ele as barreiras abaixo.
3. **Termos do exemplo são erro (C03).** O conferidor procura na sua especificação os nomes, os termos de domínio e os
   identificadores próprios do caso resolvido (lista em `scripts/termos_do_exemplo.json`). Cada ocorrência é erro e
   impede gerar os documentos.
4. **Trecho copiado é aviso (C04).** Doze palavras seguidas iguais às do exemplo são marcadas, mesmo sem termo de
   domínio. Reescreva com o seu conteúdo; se for texto realmente genérico (uma regra de acessibilidade, por exemplo),
   escreva com as suas palavras e a sua fonte.
5. **Termo legítimo do seu domínio.** Se o seu processo também usa uma palavra da lista (um órgão que também trata de
   "tarifa", por exemplo), declare em `termos_permitidos` do seu `documentos.json`, com a justificativa:

   ```json
   "termos_permitidos": {"tarifa": "o processo trata da tarifa de embarque cobrada pelo terminal (Lei estadual nº ...)"}
   ```

   Termo permitido sem justificativa também é erro.

## 3. Instruções para a IA

Quem trabalha com uma IA (Claude Code, Codex ou equivalente) deve garantir que ela:

- leia o [`AGENTS.md`](../../AGENTS.md) da raiz deste repositório antes de começar;
- abra um arquivo do exemplo **só depois** de ter escrito a primeira versão do documento equivalente a partir dos
  insumos do aluno, e só para comparar forma e completude;
- nunca escreva dentro de `exemplo/`;
- rode o conferidor depois de cada documento e trate todo C03 e C04 antes de seguir.

## 4. Pronto quando

- [ ] O projeto foi criado por `iniciar_projeto.py`, não por cópia do exemplo.
- [ ] O conferidor não acusa C03.
- [ ] Cada C04 foi reescrito ou justificado.
- [ ] Cada termo permitido tem justificativa ligada ao seu domínio.
