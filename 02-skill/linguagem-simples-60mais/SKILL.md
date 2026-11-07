---
name: linguagem-simples-60mais
description: Transforma notícias, comunicados de bancos, Procons ou polícias e descrições de golpes digitais (falsa central, falso parente, voz clonada por IA, falso INSS, boleto falso, Pix, QR code, anúncio de empréstimo) em alertas curtos em linguagem simples para pessoas com 60 anos ou mais e para quem cuida delas, com um golpe, um sinal, uma ação e uma frase para lembrar, mais uma versão para WhatsApp. Também revisa alertas já escritos contra as técnicas do art. 5º da Lei 15.263/2025 (Política Nacional de Linguagem Simples). Use sempre que alguém pedir para explicar, resumir, traduzir ou divulgar um golpe para idosos, pais, avós ou o grupo da família, mesmo sem dizer "linguagem simples".
---

# Linguagem simples 60+

Esta skill escreve e revisa alertas de golpe digital para pessoas com 60 anos ou mais.
A meta: a pessoa lê uma vez, reconhece o golpe e sabe o que fazer, sozinha.

**Por que ela existe.** Pessoas 60+ não caem em mais golpes do que os jovens, mas caem em golpes
diferentes: imitação de banco, de cartão, do INSS e de parentes. Também são alvo deliberado de anúncios
fraudulentos segmentados. Os avisos que já existem costumam ser longos, institucionais e cheios de termos
técnicos. A skill fecha essa distância com um padrão fixo e verificável.

## Quando usar

- Transformar notícia, comunicado ou descrição de golpe em alerta.
- Revisar um alerta já escrito.
- Gerar o card de WhatsApp de um alerta pronto.

Não é para atender uma vítima específica, analisar estatísticas de golpes nem fazer campanha publicitária.
Esses casos estão em "Quando parar".

## O que pedir antes de escrever

1. **O material de origem**: texto, link ou descrição do golpe.
2. **Pelo menos duas fontes independentes**, com nome e link. Um alerta errado causa dano real: assusta sem
   motivo ou ensina a ação errada. Duas fontes concordando é o mínimo para publicar.
3. **A data ou a semana de referência.**

Se faltar fonte, não complete por conta própria. Siga "Quando parar".

## Fluxo

1. **Extraia cinco coisas** do material de origem:
   - o nome popular do golpe;
   - por onde ele chega (ligação, WhatsApp, mensagem de texto, anúncio, carta, visita);
   - o que o golpista pede;
   - o sinal que denuncia o golpe;
   - a ação de proteção.

   Se o material traz várias ações, escolha a que interrompe o golpe mais cedo. Em geral é parar,
   desligar, não clicar ou confirmar por outro caminho. As outras ficam de fora: ninguém lembra de uma lista
   de dez cuidados na hora do susto.
2. **Confira as fontes.** Duas fontes independentes precisam descrever o mesmo golpe. Se divergirem num
   detalhe que muda a ação, pare.
3. **Escreva** no formato da seção "Formato da saída", aplicando as regras abaixo. Troque termos técnicos
   pelo "Glossário essencial".
4. **Verifique.** Se a pasta da skill tiver `scripts/checar_alerta.py`, rode
   `python scripts/checar_alerta.py <arquivo.md>` e corrija tudo que aparecer como ERRO; AVISO pede
   julgamento. Sem o script, aplique à mão a "Lista de verificação" no fim deste arquivo.
5. **Releia como quem vai receber**: alguém de 70 anos, no celular, com pressa e com medo. Essa pessoa
   entende o que fazer na primeira leitura? Se não, reescreva.
6. **Entregue** no formato da seção "Formato da saída".

## Regras de escrita

A base é o art. 5º da Lei 15.263/2025 (detalhado em `references/lei-15263-art5.md`) e a ISO 24495-1:2023.
Cada regra tem um motivo; entenda o motivo e aplique o espírito, não só a letra.

- **O mais importante primeiro.** O título já diz o golpe e a ação. Muita gente só lê o título.
- **Frases curtas, em ordem direta e voz ativa.** Mire em até 15 palavras; o verificador aceita até 20.
  Frase longa obriga a guardar o começo na memória até chegar ao fim.
- **Uma ideia por frase**, sem intercalações entre vírgulas.
- **Palavras do dia a dia.** Termo técnico vira palavra comum. Se for preciso manter o termo, explique logo
  em seguida.
- **Sigla só depois do nome completo**: "Instituto Nacional do Seguro Social (INSS)". Pix e CPF são exceções:
  Pix é nome próprio e CPF é de uso corrente.
- **Uma única ação** no campo "O que fazer". Na hora do golpe a pessoa só lembra de uma coisa.
- **Fale com um adulto capaz.** Use "você". Nada de "vovô", "velhinho", diminutivos ou tom de bronca.
- **Sem alarmismo.** Sem CAIXA ALTA, sem "URGENTE", sem "!!!". O golpe já usa pressa e medo; o alerta usa
  calma e clareza.
- **Sem culpa.** Nunca sugira que quem cai é ingênuo. Golpes são feitos por profissionais e enganam qualquer
  pessoa.
- **Sem emoji.** Leitores de tela falam o nome de cada emoji em voz alta, e o card fica poluído.
- **Não acuse marcas.** Banco e órgão público aparecem como quem a pessoa deve procurar. Se o golpe imita uma
  empresa, escreva "mensagem que imita o banco", sem sugerir que a empresa participa.
- **Números em algarismos**: 3 dias, R$ 50.

## Glossário essencial

| Evitar | Usar |
| --- | --- |
| phishing | mensagem falsa |
| spoofing, número mascarado | número falsificado (parece do banco, mas não é) |
| engenharia social | conversa feita para enganar você |
| deepfake, clonagem de voz | vídeo ou voz falsos feitos no computador |
| link malicioso | link falso |
| app | aplicativo |
| token | código de segurança |
| QR code | código QR (o quadradinho que a câmera lê) |
| credenciais, dados sensíveis | senha, número do cartão e códigos |
| transação | pagamento ou transferência |
| beneficiário | quem vai receber o dinheiro |
| estelionato, fraude | golpe |
| central de atendimento | telefone do banco |
| empréstimo consignado | empréstimo descontado direto da aposentadoria |
| efetuar, realizar, solicitar, contatar | fazer, pedir, ligar para |

Nunca use: vovô, vovó, velhinho, idosinho, ingênuo, "cair como um patinho".

Siglas na primeira vez: Instituto Nacional do Seguro Social (INSS); mensagem de texto (SMS); Fundo de
Garantia do Tempo de Serviço (FGTS); boletim de ocorrência (BO). Pix e CPF dispensam o nome completo.

## Arquivos de apoio, quando a pasta completa estiver presente

| Arquivo | Quando ler |
| --- | --- |
| `references/lei-15263-art5.md` | Ao revisar: as 18 técnicas da lei e como cada uma é verificada |
| `references/glossario.md` | Ao escrever: o glossário completo |
| `references/exemplos.md` | Na primeira vez: dois pares antes/depois comentados |
| `scripts/checar_alerta.py` | Sempre, antes de entregar |
| `scripts/gerar_imagem.py` e `assets/imagem/` | Quando o alerta for publicado e precisar da imagem para WhatsApp |

## Imagem do alerta

Um alerta aprovado pode virar uma imagem de 1080 x 1350 pixels, para mandar no WhatsApp ou pôr no status. A
imagem repete quatro campos do alerta, sem acrescentar nada: título, sinal de golpe, o que fazer e a frase para
lembrar, com a data de publicação. Gere com `python scripts/gerar_imagem.py --alerta <alerta.json> --saida
<imagem.png>`; só publique com status APROVADO.

- **Pouco texto.** Até 12 palavras no título, 20 no sinal, 22 na ação, 10 na frase para lembrar e 60 no total.
- **Nada que vire golpe.** Sem link, endereço de site, perfil de rede social, QR code, emoji ou telefone pessoal.
  Número só o do canal oficial que está nas fontes.
- **Letra grande.** Fonte Atkinson Hyperlegible, criada pelo Braille Institute para leitores com baixa visão.
  Corpo de 56 pixels na imagem: perto de 20 pixels de tela quando a imagem ocupa a largura do celular.
- **Urgência calma.** Duas cores sobre o branco: grafite, para o tom sério, e laranja, para a atenção. Vermelho,
  "URGENTE" e contagem regressiva ficam de fora: são a estética do próprio golpe. Verde com amarelo também fica de
  fora, para o alerta não ser lido como bandeira ou campanha.
- **Contraste alto.** Todo texto principal com contraste de 7:1 ou mais (nível AAA da WCAG). A visão de cores
  muda com a idade, sobretudo entre azuis e amarelos claros, por isso a imagem separa as partes pela claridade
  e pelos rótulos escritos, não só pela cor.
- **Texto alternativo.** O gerador devolve a descrição da imagem para leitores de tela. Mande também o texto do
  card: a imagem complementa, não substitui.
- **Data visível.** Imagem encaminhada circula por anos. A data mostra se o aviso é antigo.

## Critérios de boa entrega

- Os cinco campos estão preenchidos e cada um cabe em uma ou duas frases.
- O corpo do alerta tem até 120 palavras, sem contar as fontes.
- "Para lembrar" tem até 10 palavras e está no imperativo.
- Há duas fontes ou mais, com link.
- A verificação não aponta erro.
- O card de WhatsApp tem até 500 caracteres.

## Formato da saída

Use sempre esta estrutura. O verificador lê exatamente estes rótulos.

```markdown
# [Nome do golpe]: [ação em poucas palavras]

**Como chega:** [canal e situação, em uma frase]
**O que pedem:** [o que o golpista quer]
**Sinal de golpe:** [o que denuncia o golpe]
**O que fazer:** [uma única ação]
**Para lembrar:** "[frase curta no imperativo]"

Fontes:
1. [Nome da fonte](link)
2. [Nome da fonte](link)

## Card para WhatsApp

*[Nome do golpe]*
[3 ou 4 linhas curtas: como chega, sinal, o que fazer]
*[Frase para lembrar]*
```

No card: o WhatsApp usa `*asterisco*` para negrito; não ponha link (o hábito de não clicar em link de
mensagem vale também para o nosso alerta); termine com a frase para lembrar.

**Ao revisar um alerta existente**, devolva o alerta reescrito no mesmo formato e, depois, uma seção
`## O que mudou` com 3 a 5 itens curtos.

## O que não fazer

- Não invente golpe, número, valor, órgão ou instrução que não esteja nas fontes.
- Não acrescente dicas genéricas de segurança sem relação com o golpe da vez. Elas diluem a ação principal.
- Não peça senha, código ou dado pessoal, nem como exemplo.
- Não prometa devolução de dinheiro nem resultado de denúncia.

## Quando parar e pedir validação humana

Pare e não entregue alerta pronto quando:

- houver menos de duas fontes independentes, ou elas divergirem sobre a ação;
- o material tratar de uma pessoa específica que caiu num golpe (a necessidade é atendimento: banco e
  delegacia, não alerta público);
- a orientação depender de conselho jurídico, médico ou financeiro individual;
- o pedido for acusar uma empresa ou pessoa pelo nome.

Nesses casos, entregue no máximo um rascunho com a primeira linha `RASCUNHO — NÃO PUBLICAR`, seguida do
motivo e do que falta para publicar.

## Lista de verificação

Use quando `scripts/checar_alerta.py` não estiver disponível. Cada item é um erro que impede a entrega.

- [ ] Título no formato "Nome do golpe: ação", sem sigla antes do nome completo.
- [ ] Os cinco campos presentes, com os rótulos exatos do formato.
- [ ] Nenhuma frase com mais de 20 palavras (ideal: até 15).
- [ ] Corpo com até 120 palavras; "Para lembrar" com até 10 palavras, entre aspas.
- [ ] "O que fazer" com no máximo duas frases e uma única ação.
- [ ] Nenhum termo da coluna "Evitar" do glossário sem explicação entre parênteses.
- [ ] Toda sigla depois do nome completo, salvo Pix e CPF.
- [ ] Sem caixa alta (fora siglas), sem "urgente", sem "!!", sem emoji.
- [ ] Nenhum termo pejorativo ou infantilizante.
- [ ] Duas fontes ou mais, com link.
- [ ] Card de WhatsApp presente, sem link, com até 500 caracteres, nome do golpe e frase final em `*negrito*`.
