# Automação: a tarefa agendada semanal

A automação é uma tarefa agendada do próprio Claude. Toda segunda-feira, às 7h40 (horário de São Paulo),
ela abre uma sessão nova, sem ninguém apertar botão, e manda o agente trabalhar.

| Item | Valor |
| --- | --- |
| Onde roda | Tarefa agendada do Claude, na nuvem (não depende de nenhum computador ligado) |
| Quando | Segundas-feiras, 7h40, fuso America/Sao_Paulo |
| Expressão de agenda | `CRON_TZ=America/Sao_Paulo 40 7 * * 1` |
| O que dispara | O agente `03-agente/sentinela-60mais.md`, lido deste repositório a cada execução |
| Onde grava | `dados.json` da página do produto |
| Evidência | A seção "Cada vez que o agente trabalhou", na página do produto |
| Aprovações | Modo automático: as execuções não param para pedir aprovação |
| Criada em | 06/11/2026; primeira execução agendada em 09/11/2026 |

## Por que uma tarefa agendada, e não um clique

Um agente que só roda quando alguém pede é uma ferramenta. A automação transforma o agente num serviço: o
alerta da semana sai mesmo que ninguém se lembre dele. Cada disparo começa uma sessão nova, sem memória da
anterior. Por isso o agente lê o histórico de `dados.json` antes de decidir, e a tarefa lê a skill e o agente
direto deste repositório: a versão publicada aqui é sempre a que roda.

## O texto da tarefa

Cada disparo envia exatamente este texto ao Claude:

```text
Você é o agente Sentinela 60+, e esta é a execução semanal automática. Ninguém está acompanhando esta sessão: não faça perguntas, decida pelas regras. Escreva em português do Brasil.

1. Clone o repositório público do projeto:
   git clone https://github.com/MFraza73/sentinela-60mais.git
2. Leia sentinela-60mais/03-agente/sentinela-60mais.md e siga-o do começo ao fim. Ele define o objetivo, as ferramentas, o laço de trabalho, as quatro perguntas de decisão, os limites e o formato do relatório.
3. Para escrever o alerta, leia sentinela-60mais/02-skill/linguagem-simples-60mais/SKILL.md e os arquivos da pasta. Verifique o alerta com:
   python3 sentinela-60mais/02-skill/linguagem-simples-60mais/scripts/checar_alerta.py <arquivo do alerta>
4. A página do produto é https://claude.ai/artifact/FXPh194Ln6RmBsnkLAU7m2. O histórico fica no arquivo dados.json publicado com ela. Leia a página e o dados.json antes de decidir, e republique a página com o dados.json atualizado no fim, como o agente descreve.
5. Registre esta execução com "tipo": "automatica" e a data de hoje no formato AAAA-MM-DD.
6. Encerre com o relatório do contrato de saída do agente e envie-o ao usuário com SendUserMessage (carregue a ferramenta via ToolSearch, se necessário). Se algo impedir a publicação (ferramenta indisponível, erro ao republicar, repositório inacessível), não tente contornar: diga no relatório o que falhou e em qual passo.
```

## O que pode dar errado e como aparece

| Falha | Como aparece |
| --- | --- |
| Repositório inacessível | O relatório da execução diz em que passo parou; a página não muda |
| Nenhum golpe passa nas 4 perguntas | A página ganha uma execução "Sem alerta novo", com o motivo |
| Falha ao republicar a página | O relatório da execução registra o erro; a página continua na versão anterior |
| Alerta reprovado no verificador 3 vezes | Não publica; a execução registra o motivo |
