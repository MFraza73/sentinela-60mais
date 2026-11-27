# Como executar o agente

O agente roda todo dia pela tarefa agendada (veja [`04-automacao/`](../04-automacao/)). Esta página mostra como
qualquer pessoa pode rodá-lo uma vez, em modo de demonstração: ele pesquisa, decide e escreve, mas não publica
nada.

## O que muda no modo de demonstração

| | Execução diária | Demonstração |
| --- | --- | --- |
| De onde lê o estado | `dados.json` da página no Claude | `05-produto/dados.json` do repositório clonado |
| Trava de uma execução por dia | Vale | Não vale: nada é gravado |
| Página do produto | Republicada | Não é tocada |
| Repositório e site público | Recebem os dados | Não recebem nada |
| Imagem do alerta | Gerada | Não é gerada |
| Saída | Página, site e relatório | Relatório na conversa, com o alerta em texto |

O resto é igual: as mesmas fontes, as mesmas quatro perguntas, a mesma skill e os mesmos verificadores.

## Do que você precisa

- Uma conta do Claude num ambiente que pesquise na web e rode comandos (o Claude Code, por exemplo).
- Nada do autor: nenhuma senha, chave ou acesso à conta dele. O repositório é público.

## O texto

Cole este texto numa conversa nova:

```text
Você vai executar o agente Sentinela 60+ em modo de demonstração. Nada pode ser publicado, gravado fora desta sessão ou enviado a ninguém. Escreva em português do Brasil.

1. Clone o repositório público:
   git clone https://github.com/MFraza73/sentinela-60mais.git
2. Leia sentinela-60mais/03-agente/sentinela-60mais.md e sentinela-60mais/03-agente/fontes.md. Siga o agente no modo do dia pelo horário de São Paulo (publicação na segunda, na quarta e na sexta; varredura nos outros dias), com estas quatro diferenças:
   a. Estado: leia sentinela-60mais/05-produto/dados.json no lugar da página do Claude. Não use a ferramenta Artifact.
   b. Trava: ignore a regra de uma execução por dia. Ela protege a página, e esta execução não grava nela.
   c. Não republique a página, não altere nenhum arquivo do repositório e não faça git commit nem git push. Guarde os arquivos de trabalho fora da pasta clonada.
   d. Faça no máximo 12 buscas e não gere imagem, para a demonstração caber em poucos minutos.
3. Para escrever um alerta, leia sentinela-60mais/02-skill/linguagem-simples-60mais/SKILL.md e verifique o texto com:
   python3 sentinela-60mais/02-skill/linguagem-simples-60mais/scripts/checar_alerta.py <arquivo do alerta>
   Confira as fontes de cada candidato com:
   python3 sentinela-60mais/03-agente/scripts/checar_fontes.py --item <candidato.json> --dados sentinela-60mais/05-produto/dados.json
   Se o ambiente não rodar os scripts, aplique à mão a lista de verificação do fim do SKILL.md e as regras de sentinela-60mais/03-agente/fontes.json, e diga isso no relatório.
4. Termine com um relatório na conversa: as buscas feitas; cada golpe avaliado, com a resposta às quatro perguntas e o motivo da decisão; o que entraria na fila ou seria publicado hoje; e, se houver alerta, o texto com o resultado dos verificadores. Diga também o que você não conseguiu abrir.
```

## O que esperar

- A execução leva de 5 a 10 minutos.
- O resultado mais comum é "nada novo confirmado". De cada 19 golpes avaliados nas execuções reais, 1 virou
  alerta. A recusa é o agente funcionando.
- O resultado não será idêntico ao da execução automática do mesmo dia. A busca devolve páginas diferentes a
  cada vez, e o limite de 12 buscas cobre menos fontes. O que deve se repetir é o critério: nenhum golpe
  aprovado sem duas fontes independentes, uma delas primária.

## Para conferir os verificadores sem rodar o agente

```bash
git clone https://github.com/MFraza73/sentinela-60mais.git && cd sentinela-60mais
python3 02-skill/linguagem-simples-60mais/scripts/checar_alerta.py 03-agente/execucoes/2026-11-06-teste/alerta.md
python3 03-agente/scripts/checar_fontes.py --dados 05-produto/dados.json --golpe falso-parente
python3 testes/rodar_testes.py --sem-imagem
```

O primeiro comando aprova o alerta da primeira execução. O segundo confere as fontes de um golpe que aguarda
na fila (em 27/11, o falso parente). Depois que esse golpe for publicado, o script responde que não o achou:
troque pelo nome de um golpe da seção "Na fila para os próximos alertas", no site. O terceiro roda os testes
de regressão.

## Limite desta página

O modo de demonstração foi conferido nos comandos e nas regras que cita. Uma execução completa por outra
conta, do começo ao fim, não foi registrada aqui.
