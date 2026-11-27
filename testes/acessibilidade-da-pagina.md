# Acessibilidade da página do produto: medição de 27/11/2026

O critério de sucesso do produto é "página pública legível no celular, com fonte grande e contraste nível AA da
WCAG". Até 26/11, a evidência citada era a da imagem do alerta (contraste de 7:1), não a da página. Esta medição
é da página.

## Como foi medido

`python3 testes/checar_pagina.py` abre `docs/index.html` (o mesmo arquivo que o site público serve) num
navegador sem janela, com o `dados.json` de 27/11, abre os blocos recolhidos e mede cada trecho de texto
visível, em três larguras de tela: 320, 360 e 390 pixels.

## Resultado

| O que foi medido | Resultado | Referência |
| --- | --- | --- |
| Trechos de texto medidos | 783, em 17 combinações de cor de letra e de fundo | |
| Menor contraste | 7,06:1 | AA pede 4,5:1 (3:1 em texto grande); AAA pede 7:1 (4,5:1 em texto grande) |
| Trechos reprovados no nível AA | 0 | WCAG 2.2, critério 1.4.3 |
| Trechos abaixo do nível AAA | 0 | WCAG 2.2, critério 1.4.6 |
| Menor tamanho de letra | 17 px; nenhum trecho abaixo de 16 px | |
| Cabe na tela, sem rolagem lateral | Sim a 360 e a 390 px; sim a partir de 340 px | |
| Cabe na tela a 320 px | Não: o conteúdo passa 3 px da borda | WCAG 2.2, critério 1.4.10 |
| Imagens sem texto alternativo | 0 de 1 | |

As duas combinações de menor contraste, ambas com 7,06:1: o rótulo "Sinal de golpe" (marrom `#8A3A00` sobre
`#FFF1E5`) e os links das fontes (azul `#0A58A8` sobre branco).

## Leitura do resultado

- **Contraste e tamanho de letra: cumprido, com folga.** Todo o texto passa no nível AA e também no AAA.
- **Legível no celular: cumprido para as telas em uso, com uma ressalva.** A página cabe na tela a partir de
  340 px de largura. A 320 px, largura que a WCAG usa como referência e que só aparelhos antigos têm, sobra uma
  rolagem lateral de 3 px, causada por uma lista com um item que não quebra a linha. O defeito está declarado
  e não foi corrigido nesta entrega: mexer na página no dia da entrega era um risco maior do que os 3 px.

## O que não foi medido

- Leitor de tela, navegação por teclado e ordem de foco.
- Ampliação a 200% e o botão "Letra maior".
- Aparelhos reais. A medição é de um navegador de computador com a largura de um celular.
- A largura exata com a fonte Atkinson Hyperlegible. O ambiente de medição não baixou a folha de estilo da
  fonte, e as larguras foram medidas com a fonte reserva. As cores e os contrastes não dependem disso; o ponto
  em que a página passa a caber na tela pode variar em poucos pixels.
