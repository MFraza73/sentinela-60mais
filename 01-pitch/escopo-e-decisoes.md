# Sentinela 60+ — Escopo e decisões (N2 Vibe Coding)

Atualizado em 06/11/2026.

## Identificação
- FAAP — Tecnologia em Inteligência Artificial
- Disciplina: Vibe Coding & Arquitetura de Produtos com IA (PDCP) — Profª Drª Eliana Loureiro
- Trabalho individual — N2, entrega 27/11/2026

## Tema
Sentinela 60+ (nome provisório): alertas semanais sobre golpes digitais, em linguagem simples, para pessoas com 60+ e quem cuida delas.

Pitch editável: https://claude.ai/artifact/Ar6XfmaFShFphuWGdWwcKB

## Decisões
- Entrega "aberta" = repositório público no GitHub (skill) + link publicado (produto).
- Automação roda dentro do Claude (tarefa agendada), sem n8n.
- Varredura diária (7h40) com publicação semanal (segunda): decidido em 06/11, no lugar de publicar todo dia. Publicar diariamente baixaria a régua de confirmação, cansaria o público (habituação a avisos) e transformaria o repasse no WhatsApp em corrente. Golpe muito grave, com fonte oficial e noticiado nas últimas 48 horas, pode virar alerta extra, no máximo um por semana.
- Trava de uma execução por dia e por modo (idempotência), criada depois que o disparo de teste rodou duas vezes e publicou dois alertas a mais. Os dois voltaram para a fila.
- SabedorIA / Coletivo Bairro com Vida = apenas inspiração. Nenhum material, dado ou entrega reutilizado; o Coletivo não participa da entrega.
- Sem teste de compreensão com público nesta entrega; a hipótese de eficácia do formato fica declarada como fora do escopo.
- Embasamento do tema por fontes jornalísticas e oficiais públicas.
- Enquadramento da dor (ajustado após checagem): os dados não mostram que pessoas 60+ caiam em mais golpes (DataSenado: 16% das vítimas têm 60+, contra 27% entre 16 e 29 anos). O argumento é de tipo e de mira: pessoas 60+ sofrem sobretudo fraudes que imitam bancos e cartões e são alvo de anúncios segmentados (aposentadoria, benefício, INSS).

- Estado do agente (histórico de alertas e de execuções) fica em `dados.json`, publicado junto da página do produto: cada disparo da automação abre uma sessão nova, sem memória da anterior. O banco de dados das páginas do Claude foi descartado porque só entrega dados a quem está conectado ao Claude; visitantes sem conta veriam a página vazia.
- Produto publicado em 06/11: https://claude.ai/artifact/FXPh194Ln6RmBsnkLAU7m2 (privado até ser compartilhado por link público no menu Compartilhar).
- Regras do agente aprendidas na execução de 06/11: veículos do mesmo grupo contam como uma fonte; fonte com interesse comercial no tema não conta; sem orientação de proteção confirmada, não há alerta.
- Mapa de fontes (06/11), validado com as próprias ferramentas do agente: três papéis (sinal, confirmação, apoio); um dos dois confirmadores tem de ser primário (órgão público, polícia, Procon ou Febraban); agências de checagem só indicam; cada fonte leva o campo `origem` e cada candidato registra `indicado_por`. Busca por pacotes de até 7 domínios, com rodízio regional diário. A validação mostrou que Estadão, UOL, BBC e globo.com são recusados pela ferramenta de busca, que g1, O Globo e Folha não devolvem resultado, e que 11 das 27 polícias civis bloqueiam a abertura de página. Detalhes em `03-agente/fontes.md`.


## Arquitetura
1. Automação: tarefa agendada no Claude, todo dia às 7h40, dispara o agente.
2. Agente: de terça a domingo, varre órgãos públicos, Febraban, imprensa, agências de checagem e um pacote regional de polícias e Procons, e guarda numa fila os golpes novos, confirmados em 2 fontes (uma delas primária) e relevantes para 60+, já escritos e aprovados no verificador; na segunda, publica o mais relevante da fila.
3. Skill `linguagem-simples-60mais`: art. 5º da Lei 15.263/2025 + ISO 24495-1:2023 + regras próprias (um golpe, um sinal, uma ação, uma frase para lembrar; tom de autonomia, não de medo).
4. Produto: página pública com alerta da semana, arquivo, fila, histórico de execuções e card para WhatsApp (repassado por pessoa de confiança; sem disparo automático a pessoas idosas).

## Critérios de sucesso
- Skill: 10 casos de teste aprovados no checklist do art. 5º (pares antes/depois no repositório).
- Agente: todo alerta com 2 fontes citadas ou mais, uma delas primária, cada uma com a sua `origem`.
- Automação: execuções diárias reais, com ao menos duas publicações de segunda (9, 16 ou 23/11) antes de 27/11.
- Produto: página pública legível no celular, fonte grande, contraste nível AA da WCAG.

## Cronograma
- até 09/11: escopo fechado
- 10 a 14/11: skill v1 + 10 casos antes/depois (adiantado: v1 pronta em 06/11)
- 15 a 19/11: agente + página v1 (adiantado: agente v1 testado e página publicada em 06/11)
- 20 a 23/11: automação ligada, 2 execuções reais ou mais (adiantado: tarefa criada e testada em 06/11; varredura diária a partir de 07/11; publicações em 9, 16 e 23/11)
- 24 a 26/11: repositório aberto, revisão final, roteiro da apresentação
- 27/11: entrega N2 (13/11 sem aula)

## Pendências
- Nome final do produto ("Sentinela" conota vigilância; alternativas: "Antes de Clicar", "Confere?").
- Recorte nacional de estelionato digital por faixa etária: não encontrado nas fontes consultadas.
- Skill v2: definir "uma ação" como um comportamento num mesmo momento; rodar comparação com e sem a skill.
- Criar o link público da página do produto (menu Compartilhar), para a professora abrir sem convite.

## Fontes-chave
- Lei 15.263/2025 (Câmara): https://www2.camara.leg.br/legin/fed/lei/2025/lei-15263-14-novembro-2025-798293-publicacaooriginal-177011-pl.html
- DataSenado via Agência Senado: https://www12.senado.leg.br/noticias/infomaterias/2025/04/golpes-virtuais-aumentam-e-nao-fazem-distincao-de-idade
- Agência Pública (coluna de Natalia Viana): https://apublica.org/2026/05/depois-do-eca-esta-na-hora-de-um-estatuto-do-idoso-digital/
