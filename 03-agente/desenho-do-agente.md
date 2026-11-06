# Desenho do agente Sentinela 60+

Atualizado em 06/11/2026.

## Por que é um agente, e não um roteiro

Um roteiro faz sempre os mesmos passos: busca, resume, publica. Um agente recebe um objetivo e decide o
caminho conforme o que encontra. A diferença aparece nos pontos de decisão. O Sentinela tem cinco:

| Ponto de decisão | O que o agente decide | Exemplo da execução de 06/11 |
| --- | --- | --- |
| O que buscar | Consultas, frentes e quando refinar | Refinou a busca para achar uma segunda fonte do caso do INSS |
| Em que fonte confiar | Papel (sinal ou confirmação), independência e interesse comercial | Descontou o blog de uma empresa de crédito consignado |
| Qual golpe vale um alerta | As 4 perguntas aplicadas a cada candidato | Escolheu 1 de 6 candidatos |
| Onde parar de pesquisar | Verificação em ordem de relevância | Não abriu fontes de candidatos que já perdiam em relevância |
| Se deve publicar | Na dúvida, não publica | Recusou o candidato mais grave por falta de orientação confirmada |

## O laço, nos termos da disciplina de agentes

O agente segue o padrão **ReAct** (*Reason + Act*): pensa, age com uma ferramenta, observa o resultado e
pensa de novo. Uma volta do laço, na execução de 06/11:

1. **Pensa:** "O caso da falsa consultoria do INSS é grave, mas só tenho uma fonte."
2. **Age:** busca o caso no site do Tribunal de Justiça de Minas Gerais.
3. **Observa:** o tribunal confirma o crime, mas não traz orientação ao público.
4. **Pensa de novo:** "O mecanismo está confirmado; a ação de proteção, não. Reprovo na pergunta 3."

O ambiente é **parcialmente observável**: o agente nunca vê todos os golpes em circulação, só o que a busca
devolve. Por isso a decisão se apoia em evidência mínima (duas fontes abertas) e não em cobertura total.
É o mesmo raciocínio dos modelos POMDP (*Partially Observable Markov Decision Process*) vistos em aula: o
agente age sobre uma crença do estado do mundo, não sobre o estado em si.

## Componentes

| Peça | Papel | Onde está |
| --- | --- | --- |
| Definição do agente | Objetivo, ferramentas, laço, regras de decisão e limites | `sentinela-60mais.md` |
| Mapa de fontes | Papéis das fontes, pacotes de busca, rodízio regional e situação de cada domínio | `fontes.md` |
| Skill | Como escrever: padrão de linguagem simples e verificador | `../02-skill/` |
| Ferramentas | Busca na web, leitura de páginas, republicação da página do produto | Do próprio Claude |
| Estado | Alertas, fila de golpes confirmados e histórico de execuções | `dados.json`, publicado junto da página (`../05-produto/`) |
| Gatilho | Tarefa agendada diária no Claude, às 7h40 | `../04-automacao/` |

## Dois ritmos: varredura diária, publicação semanal

O agente olha o noticiário todo dia, mas publica uma vez por semana. As duas frequências foram separadas de
propósito:

- **Varredura diária (terça a domingo).** Cada golpe que passa nas quatro perguntas é escrito, aprovado no
  verificador e guardado numa fila. Mais olhares por semana dão mais candidatos para escolher e mais tempo para
  as fontes amadurecerem.
- **Publicação semanal (segunda).** O golpe mais relevante da fila vira o alerta da semana. Publicar todo dia
  baixaria a régua de confirmação, cansaria quem recebe (avisos repetidos viram papel de parede, como mostram
  Anderson e colegas no *Journal of Management Information Systems*, 2016) e transformaria o repasse no
  WhatsApp em corrente.
- **Alerta extra.** Um golpe de relevância máxima, com fonte oficial e noticiado nas últimas 48 horas, pode sair
  antes da segunda, no máximo uma vez por semana.

## Onde o agente procura: sinal, confirmação e origem

A primeira versão mandava o agente buscar em "órgãos, imprensa e recorte de público", sem dizer onde. A segunda
separa as fontes por papel e fixa os endereços, num mapa testado com as próprias ferramentas do agente
(`fontes.md`):

- **Sinal.** Agências de checagem (Aos Fatos, Boatos.org, Projeto Comprova) e a busca aberta descobrem cedo que um
  golpe circula. Podem indicar um candidato, nunca confirmá-lo.
- **Confirmação.** Uma das duas fontes tem de ser primária: órgão público, polícia civil, Procon ou Febraban. São 14
  polícias civis e 11 Procons estaduais que a ferramenta encontra e abre, organizados em quatro pacotes regionais
  que se revezam ao longo da semana.
- **Origem.** Toda fonte guardada leva o campo `origem`, e todo candidato registra quem o indicou
  (`indicado_por`). Com algumas semanas de execução, o histórico mostra quais frentes de fato trazem os golpes que
  viram alerta.

A validação mudou a lista. Dos cinco grandes jornais da versão anterior, três são recusados pela ferramenta de
busca e dois não devolvem resultado; 11 das 27 polícias civis bloqueiam a abertura de página. O agente teria
gastado buscas em fontes que não pode citar. Com a regra da fonte primária, o agente também troca a notícia de
segunda mão pela nota original: o golpe do falso gerente, guardado na fila com dois sites regionais que
reproduziam a polícia, tem a página da própria Polícia Civil do Paraná, que abre e traz a orientação.

## Lição do primeiro disparo automático

No teste de 06/11, a mensagem que acompanhava o disparo foi lida como um segundo pedido, e o agente rodou duas
vezes, publicando dois alertas extras. Daí veio a trava de uma execução por dia e por modo: antes de
qualquer busca, o agente confere no `dados.json` se a execução do dia já aconteceu. Em sistemas que rodam
sozinhos, isso se chama idempotência: repetir o mesmo disparo não pode repetir o efeito.

**Por que o estado fica num arquivo publicado com a página:** cada disparo da automação abre uma sessão nova
do Claude, sem memória da anterior. O histórico precisa morar fora da conversa, num lugar que o agente leia
e grave e que a página mostre. Guardar no próprio produto evita duas fontes de verdade.

A primeira ideia era o banco de dados que as páginas do Claude oferecem. Foi descartada porque esse banco
só entrega dados a quem está conectado ao Claude: um visitante sem conta, como uma pessoa idosa que recebe o
link ou uma avaliadora sem login, veria a página vazia. Um arquivo publicado junto da página é lido por
qualquer visitante. O custo é que cada execução republica a página inteira, e não só uma linha.

## Riscos e defesas

| Risco | Defesa |
| --- | --- |
| Alerta com orientação errada | Duas fontes independentes que concordem na ação; na dúvida, não publica |
| Página da web com instrução escondida para o agente (*prompt injection*) | Conteúdo de página é dado, nunca instrução; a página suspeita é descartada e registrada |
| Fonte com interesse próprio | Fonte comercial no tema não conta como independente |
| Notícia de segunda mão | Uma das duas fontes tem de ser primária (órgão, polícia, Procon ou Febraban); checagem e site fora das listas nunca confirmam |
| Busca em fonte que o agente não consegue citar | Mapa de fontes testado: domínios que não abrem só servem de sinal; domínios recusados ficam fora do filtro |
| Mesma notícia contada duas vezes | Veículos do mesmo grupo contam como uma fonte |
| Texto difícil para o público | Skill + verificador; sem status APROVADO, não publica |
| Acusar uma empresa | Marca imitada aparece como "mensagem que imita"; nunca como culpada |
| Disparo repetido publicar duas vezes | Trava de uma execução por dia e por modo, conferida no `dados.json` |
| Excesso de alertas | No máximo um alerta normal e um extra por semana |

## Nível de capacidade na matriz da Gartner

Posição honesta do agente na matriz *Levels of agent capabilities* (aula 11, slide 21):

| Dimensão | Nível | Por quê | Como subir um nível |
| --- | --- | --- | --- |
| Perception | Intermediate — *Active* | Varre todo dia frentes fixas (órgãos, bancos, imprensa, checadores) e um pacote regional de polícias e Procons, e guarda o que confirma numa fila que atravessa os dias | Ser acionado por evento (um alerta oficial novo), e não só pelo relógio |
| Decisioning | Basic — *Analytical* | Aplica critérios explícitos com julgamento sobre evidência | Ponderar risco, alcance e recência num placar |
| Actioning | Basic — *Situational* | Escolhe entre guardar na fila, publicar, publicar alerta extra ou não fazer nada, conforme o caso | Coordenar subagentes: um pesquisa, outro verifica |
| Agency | Intermediate — *Autonomous* | Roda e publica sem humano, dentro de um escopo estreito e com regras de parada | Já é o teto desejável aqui: um alerta errado causa dano real |
| Adaptability | Emerging — *Contextual* | Responde ao noticiário da semana, mas as regras não mudam sozinhas | Ajustar critérios a partir do histórico de alertas e de erros |
| Knowledge | Emerging — *Specialized* | Conhece um domínio: golpes contra pessoas físicas e linguagem simples | Ampliar para outros públicos vulneráveis |

**Leitura:** é um agente de nível básico, com percepção e autonomia intermediárias. A combinação é
deliberada: autonomia alta só é aceitável porque o escopo é estreito e as regras de parada são
conservadoras. A percepção subiu de nível com a varredura diária, sem aumentar o volume de alertas.
