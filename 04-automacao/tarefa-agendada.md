# Automação: a tarefa agendada diária

A automação é uma tarefa agendada do próprio Claude. Todo dia, às 7h40 (horário de São Paulo), ela abre uma
sessão nova, sem ninguém apertar botão, e manda o agente trabalhar. De terça a domingo, o agente faz a
varredura e guarda os golpes confirmados numa fila. Na segunda, publica o melhor da fila como alerta da semana.

| Item | Valor |
| --- | --- |
| Onde roda | Tarefa agendada do Claude, na nuvem (não depende de nenhum computador ligado) |
| Quando | Todo dia, 7h40, fuso America/Sao_Paulo |
| Expressão de agenda | `CRON_TZ=America/Sao_Paulo 40 7 * * *` |
| O que dispara | O agente `03-agente/sentinela-60mais.md`, lido deste repositório a cada execução |
| Onde grava | `dados.json` da página do produto: alertas, fila e execuções |
| Evidência | As seções "Na fila para a próxima segunda" e "Cada vez que o agente trabalhou", na página do produto |
| Aprovações | Modo automático: as execuções não param para pedir aprovação |
| Histórico | Criada em 06/11/2026 como semanal; passou a diária no mesmo dia, com publicação mantida às segundas. Ainda em 06/11, o texto passou a mandar ler o mapa de fontes (`03-agente/fontes.md`). Em 07/11, passou a citar o gerador da imagem do alerta |

## Por que uma tarefa agendada, e não um clique

Um agente que só roda quando alguém pede é uma ferramenta. A automação transforma o agente num serviço: o
noticiário é varrido todo dia e o alerta da semana sai mesmo que ninguém se lembre dele. Cada disparo começa
uma sessão nova, sem memória da anterior. Por isso o agente lê o estado de `dados.json` antes de decidir, e a
tarefa lê a skill e o agente direto deste repositório: a versão publicada aqui é sempre a que roda.

## Por que varrer todo dia e publicar só na segunda

- Golpe novo, confirmado em duas fontes e relevante para quem tem 60+ não aparece todo dia. Publicar
  diariamente obrigaria a baixar a régua.
- Aviso repetido vira papel de parede, e um alerta por dia no WhatsApp da família vira corrente.
- Varrer todo dia, por outro lado, dá mais candidatos para escolher, reação mais rápida a um golpe grave
  (o alerta extra) e um histórico de decisões muito mais rico.

## O texto da tarefa

Cada disparo envia exatamente este texto ao Claude:

```text
Você é o agente Sentinela 60+, e esta é a execução diária automática. Ninguém está acompanhando esta sessão: não faça perguntas, decida pelas regras. Escreva em português do Brasil.

1. Clone o repositório público do projeto:
   git clone https://github.com/MFraza73/sentinela-60mais.git
2. Leia sentinela-60mais/03-agente/sentinela-60mais.md e siga-o do começo ao fim. Ele define os dois modos (varredura de terça a domingo; publicação na segunda, pelo horário de São Paulo), a trava de uma execução por dia, as ferramentas, as quatro perguntas de decisão, a fila, os limites e o formato do relatório. Leia também sentinela-60mais/03-agente/fontes.md: é o mapa de fontes, com os pacotes de domínios para o filtro allowed_domains da busca, o rodízio regional do dia e as regras de origem e de confirmação.
3. Para escrever alertas, leia sentinela-60mais/02-skill/linguagem-simples-60mais/SKILL.md e os arquivos da pasta. Verifique cada alerta com:
   python3 sentinela-60mais/02-skill/linguagem-simples-60mais/scripts/checar_alerta.py <arquivo do alerta>
   Para a imagem de cada alerta publicado, use sentinela-60mais/02-skill/linguagem-simples-60mais/scripts/gerar_imagem.py, como o agente descreve em "A imagem do alerta".
4. A página do produto é https://claude.ai/artifact/FXPh194Ln6RmBsnkLAU7m2. O estado (alertas, fila e execuções) fica no arquivo dados.json publicado com ela. Leia a página e o dados.json antes de decidir, e republique a página com o dados.json atualizado no fim, como o agente descreve.
5. Registre esta execução com "tipo": "automatica", o "modo" do dia e a data de hoje no formato AAAA-MM-DD.
6. Faça uma única execução completa. Encerre com o relatório do contrato de saída do agente e envie-o ao usuário com SendUserMessage (carregue a ferramenta via ToolSearch, se necessário). Se algo impedir a publicação (ferramenta indisponível, erro ao republicar, repositório inacessível), não tente contornar: diga no relatório o que falhou e em qual passo.
```

## O que pode dar errado e como aparece

| Falha | Como aparece |
| --- | --- |
| Repositório inacessível | O relatório da execução diz em que passo parou; a página não muda |
| Domínio da lista de fontes some, muda de endereço ou passa a bloquear | O agente anota na `observacao` da execução; a lista é revisada à mão |
| O mesmo disparo chega duas vezes | A trava de uma execução por dia faz a segunda parar sem gravar nada |
| Nenhum golpe passa nas 4 perguntas | A página ganha uma varredura "Nada novo confirmado" |
| Fila vazia na segunda | A página ganha uma publicação "Semana sem alerta" |
| Falha ao republicar a página | O relatório da execução registra o erro; a página continua na versão anterior |
| Alerta reprovado no verificador 3 vezes | Não entra na fila; a execução registra o motivo |
| Imagem reprovada no gerador 3 vezes | O alerta sai sem imagem; a execução registra o motivo |

## O disparo de teste de 06/11

O primeiro disparo, feito à mão durante a montagem, funcionou de ponta a ponta: clonou o repositório,
pesquisou, decidiu, escreveu, passou no verificador e republicou a página em cerca de 4 minutos. Revelou
também um defeito: a mensagem de teste anexada ao disparo foi lida como um segundo pedido, e o agente rodou
duas vezes. Os dois alertas extras voltaram para a fila, e o caso criou a trava de uma execução por dia.
