# Evidências da automação

A tarefa agendada vive na conta do autor no Claude e não pode ser aberta por outra pessoa. Este documento
reúne o que qualquer pessoa consegue conferir sem acesso à conta, e separa o que é declarado pelo próprio
projeto do que é registrado por terceiros.

## Três camadas

| Camada | O que é | Quem consegue ver |
| --- | --- | --- |
| Definição | O texto que cada disparo envia ao Claude | Todos: `04-automacao/tarefa-agendada.md`, no repositório público |
| Gatilho | A tarefa agendada em si, com o horário | Só o autor, na lista de tarefas agendadas do Claude |
| Rastro | O que cada execução deixou | Todos: commits diários, execuções do GitHub Actions e histórico na página do produto |

O gatilho é privado em qualquer agendador hospedado. O que dá para abrir é a definição e o rastro.

## Configuração da tarefa, lida da conta em 27/11/2026

| Item | Valor |
| --- | --- |
| Nome | Sentinela 60+ — varredura diária e alertas seg/qua/sex |
| Agenda | `CRON_TZ=America/Sao_Paulo 40 7 * * *` (todo dia, 7h40, horário de São Paulo) |
| Situação | Ativa |
| Aprovações | Modo automático: as execuções não param para pedir aprovação |
| Criada em | 06/11/2026, 19h35 |
| Última alteração | 15/11/2026, 15h49 (passagem para três publicações por semana) |
| Última execução | 27/11/2026: disparo às 7h40min55s, término às 7h47min01s, concluída com sucesso |
| Próxima execução | 28/11/2026, 7h40 |
| Texto do disparo | O mesmo publicado em `04-automacao/tarefa-agendada.md` |

Esta tabela é declarada pelo autor: quem lê não tem como conferi-la sem a conta. O que a sustenta é a seção
seguinte.

## Rastro público: 19 dias seguidos de commits

Cada execução termina com um envio do agente ao repositório ("Execução de AAAA-MM-DD"). Em seguida, o GitHub
Actions roda os testes, monta o site e registra outro commit, assinado por `github-actions[bot]`
("Site público atualizado a partir de ...").

| Data | Dia | Modo | Envio do agente | Montagem pelo GitHub | Resultado |
| --- | --- | --- | --- | --- | --- |
| 09/11 | segunda | publicação | 07h50 | 07h51 | Alerta publicado |
| 10/11 | terça | varredura | 07h44 | 07h45 | Golpe guardado na fila |
| 11/11 | quarta | varredura | 07h45 | 07h46 | Nada novo confirmado |
| 12/11 | quinta | varredura | 07h45 | 07h46 | Nada novo confirmado |
| 13/11 | sexta | varredura | 07h47 | 07h47 | Golpe guardado na fila |
| 14/11 | sábado | varredura | 07h46 | 07h47 | Golpe guardado na fila |
| 15/11 | domingo | varredura | 07h56 | 07h57 | Golpe guardado na fila |
| 16/11 | segunda | publicação | 07h45 | 07h45 | Alerta publicado |
| 17/11 | terça | varredura | 07h50 | 07h51 | Nada novo confirmado |
| 18/11 | quarta | publicação | 07h48 | 07h53 | Alerta publicado |
| 19/11 | quinta | varredura | 07h50 | 07h51 | Nada novo confirmado |
| 20/11 | sexta | publicação | 07h45 | 07h46 | Alerta publicado |
| 21/11 | sábado | varredura | 07h49 | 07h49 | Nada novo confirmado |
| 22/11 | domingo | varredura | 07h50 | 07h50 | Nada novo confirmado |
| 23/11 | segunda | publicação | 07h53 | 07h54 | Alerta publicado |
| 24/11 | terça | varredura | 07h44 | 07h45 | Nada novo confirmado |
| 25/11 | quarta | publicação | 07h50 | 07h50 | Alerta publicado |
| 26/11 | quinta | varredura | 07h45 | 07h46 | Golpe guardado na fila |
| 27/11 | sexta | publicação | 07h46 | 07h47 | Alerta publicado |

Horários de São Paulo. Em 19 dias, o envio do agente caiu sempre entre 7h44 e
7h56, de 4 a 16 minutos depois do disparo das 7h40, incluindo fins de semana e os feriados de 15 e 20/11.
Essa regularidade é a assinatura de um agendador, não de alguém apertando um botão.

## O que cada relógio prova

- **Horário do envio do agente.** É informado por quem faz o commit. Sozinho, não prova nada: poderia ser
  ajustado.
- **Horário da montagem pelo GitHub.** É registrado pelos servidores do GitHub, fora do controle do autor e do
  agente. A aba Actions do repositório guarda cada execução, com data, hora e resultado dos testes.
- **Histórico na página do produto.** É escrito pelo próprio agente em `dados.json`, com as buscas, os golpes
  avaliados e o motivo de cada decisão. É o registro mais rico e o menos independente.

Os três concordam nos 19 dias.

## Como conferir

1. Abra o repositório público (https://github.com/MFraza73/sentinela-60mais) e entre na lista de commits: há um
   "Execução de ..." por dia desde 09/11.
2. Na aba Actions, veja as execuções do fluxo de testes, com o horário registrado pelo GitHub.
3. No site (https://mfraza73.github.io/sentinela-60mais/), abra a seção "Cada vez que o agente trabalhou".

## Limites desta evidência

- As execuções de 07/11 e 08/11 não têm commit próprio: o envio automático ao repositório começou em 09/11. Elas
  constam só no histórico da página.
- O nome de quem assina os envios do agente varia ("Claude", "Sentinela 60+"), porque cada sessão nasce nova e
  configura a própria identidade. Os horários e o conteúdo não dependem disso.
- Os commits provam que algo rodou todo dia no mesmo horário e enviou dados. Que esse algo seja a tarefa
  agendada do Claude, e não outro agendador, só se vê na conta do autor ou numa demonstração ao vivo.
