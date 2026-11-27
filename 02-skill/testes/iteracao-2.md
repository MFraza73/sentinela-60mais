# Testes da skill: iteração 2

Rodada de 27/11/2026, na versão atual da skill. A iteração 1 é de 06/11, antes de a skill ganhar a imagem do
alerta e o "É golpe ou não?". Esta rodada refaz os mesmos 10 casos para o resultado valer para a skill entregue.

## Como foi feito

1. A skill foi carregada pelo Claude a partir da conta do autor, na versão completa (o `SKILL.md`, as
   referências e os scripts), a mesma do pacote `linguagem-simples-60mais.skill`.
2. Para cada caso de [`evals/`](../linguagem-simples-60mais/evals/), o Claude recebeu o pedido do arquivo
   `prompt.md` e escreveu a resposta seguindo o fluxo da skill.
3. Cada resposta passou pelo `scripts/checar_alerta.py`. Onde ele apontou aviso, a frase foi revista, como o
   passo 4 da skill manda.
4. Cada resposta foi conferida contra os três critérios do caso (pasta `graders/`). Os critérios que dá para
   checar por programa (termo ausente, sigla depois do nome, número de itens, primeira linha) foram checados por
   programa; os outros citam o trecho do alerta que os atende.

## Resultado

| Caso | Verificador | Critérios | Observação |
| --- | --- | --- | --- |
| Anúncio de empréstimo com taxa | APROVADO | 3 de 3 | Frase de 16 palavras encurtada depois do aviso |
| Boleto falso | APROVADO | 3 de 3 | Sem aviso |
| Falsa central, a partir de comunicado de banco | APROVADO | 3 de 3 | Frase de 16 palavras encurtada depois do aviso |
| Falso entregador | APROVADO | 3 de 3 | Frase de 17 palavras encurtada depois do aviso |
| Falso aviso do INSS, com siglas | APROVADO | 3 de 3 | Frase de 16 palavras dividida em duas depois do aviso |
| Falso parente, a partir de notícia | APROVADO | 3 de 3 | Sem aviso |
| Fonte única: não publicar | RASCUNHO | 3 de 3 | O verificador reconhece o rascunho e não o trata como alerta |
| Código QR em adesivo | APROVADO | 3 de 3 | 1 aviso mantido: a explicação de "código QR" entre parênteses leva a frase a 17 palavras |
| Revisão de alerta alarmista | APROVADO | 3 de 3 | Sem aviso |
| Voz copiada, a partir de texto técnico | APROVADO | 3 de 3 | Sem aviso |

- 9 alertas com status APROVADO e 0 erro. O décimo caso pede que a skill não publique, e ela devolve o rascunho.
- 30 de 30 critérios atendidos.
- Na primeira passagem, antes de qualquer revisão, os 9 alertas já estavam aprovados; 5 tinham 1 aviso de frase
  com 16 ou 17 palavras (o ideal da skill é até 15). Quatro foram encurtadas. Uma foi mantida.

As respostas e as avaliações estão em [`iteracao-2/`](iteracao-2/). Para ver tudo de uma vez, com a resposta
da iteração 1 ao lado, baixe e abra `revisao-iteracao-2.html` no navegador.

## O que este teste mostra e o que não mostra

- **Mostra** que a skill atual produz, para os 10 pedidos, alertas que passam no verificador e atendem aos
  critérios definidos antes da rodada.
- **Não é uma avaliação independente.** A mesma sessão do Claude escreveu e conferiu as respostas, e já
  conhecia o projeto. O que não depende do Claude é o verificador em código e os critérios checados por
  programa. A sessão tinha lido a resposta da iteração 1 de um caso (boleto falso), para conhecer o formato.
- **Não compara com e sem a skill.** Não se mediu quanto o Claude erraria os mesmos pedidos sem ela.
- **Não cobre a imagem nem o "É golpe ou não?".** As regras dos dois são exercitadas pelos casos de
  [`testes/imagem/`](../../testes/imagem/) e [`testes/quiz/`](../../testes/quiz/), que testam os verificadores,
  não a escrita.
- **As fontes dos casos são fictícias** (`exemplo.org`). O teste mede a escrita, não a checagem de fontes, que é
  trabalho do agente.
