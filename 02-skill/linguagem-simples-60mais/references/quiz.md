# É golpe ou não?

Um exercício curto: a pessoa vê uma mensagem como chegaria no celular e responde, para si mesma ou no grupo da
família, se é golpe. A resposta sai no dia seguinte. O objetivo é treinar o olho para o sinal, não assustar.

## Campos (JSON)

| Campo | O que é | Limite |
| --- | --- | --- |
| `canal` | `WhatsApp`, `mensagem de texto`, `ligação`, `e-mail` ou `rede social` | |
| `mensagem` | A mensagem como a pessoa receberia. Pode imitar o tom do golpe | 45 palavras |
| `resposta` | `golpe` ou `nao-golpe` | |
| `sinal` | O que denuncia o golpe, ou o que mostra que o aviso é verdadeiro | 25 palavras |
| `explicacao` | Por que é (ou não é) golpe e a única ação a tomar | 40 palavras |
| `para_lembrar` | Frase no imperativo, sem aspas | 10 palavras |
| `fontes` | Lista de `{nome, url, origem, data}`, com pelo menos uma fonte primária dos últimos 12 meses | |
| `card_pergunta` | Texto para o WhatsApp: a pergunta, sem a resposta | 500 caracteres |
| `card_resposta` | Texto para o WhatsApp: a primeira linha diz "É golpe" ou "Não é golpe" | 500 caracteres |
| `publicado_em`, `resposta_em` | Datas `AAAA-MM-DD`; a resposta sai no dia seguinte | |

## Regras

- **A mensagem vem de uma fonte.** Use o texto de uma mensagem falsa que a fonte reproduz ou descreve. Não
  invente golpe, valor nem órgão.
- **Nada que vire golpe.** Troque link por `[link]`, telefone por `[número]` e o nome do banco ou da loja por
  "seu banco" ou "a loja". Nunca copie link, telefone ou perfil de golpista.
- **A mensagem pode ter o tom do golpe** (pressa, ameaça, caixa alta), porque é assim que ela chega. O resto
  do quiz segue as regras do alerta: calma, frases curtas, palavras do dia a dia, sem culpa.
- **"Não é golpe" também ensina.** Um aviso verdadeiro, que a fonte primária confirma que o órgão manda, mostra
  que a saída é conferir por outro caminho, e não desconfiar de tudo. Use no máximo uma vez a cada 4 quizzes, e
  só quando a fonte disser como conferir.
- **Uma ação.** A explicação termina com a ação que interrompe o golpe, a mesma do alerta, se houver.
- **O card da pergunta não entrega a resposta.** Termine com "A resposta sai amanhã."

## Exemplo

```json
{
  "canal": "ligação",
  "mensagem": "Uma voz chorando: \"Mãe, me pegaram! Eles vão me machucar.\" Depois, um homem: \"Faz o Pix agora. Se desligar, ela morre. Qual o nome da sua filha?\"",
  "resposta": "golpe",
  "sinal": "Choro, ameaça e pressa para pagar, e ainda perguntam o nome da sua filha.",
  "explicacao": "É o golpe do falso sequestro. Quem liga não sabe quem é seu parente. Por isso pergunta o nome. Desligue e ligue para o parente no número que você já tem.",
  "para_lembrar": "Choro e pressa no telefone? Desligue e ligue você mesmo.",
  "card_pergunta": "*É golpe ou não?*\nVocê atende o telefone e ouve alguém chorando: \"Mãe, me pegaram!\"\nUm homem pede um Pix agora e pergunta o nome da sua filha.\nO que você acha? A resposta sai amanhã.",
  "card_resposta": "*É golpe: o falso sequestro.*\nQuem liga não sabe quem é seu parente. Por isso pergunta o nome.\nDesligue e ligue para o parente no número que você já tem.\n*Choro e pressa no telefone? Desligue e ligue você mesmo.*"
}
```

Verifique com `python3 scripts/checar_quiz.py <quiz.json>` antes de entregar.
