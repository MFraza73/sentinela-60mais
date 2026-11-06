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
- Automação roda dentro do Claude (tarefa agendada semanal), sem n8n.
- SabedorIA / Coletivo Bairro com Vida = apenas inspiração. Nenhum material, dado ou entrega reutilizado; o Coletivo não participa da entrega.
- Sem teste de compreensão com público nesta entrega; a hipótese de eficácia do formato fica declarada como fora do escopo.
- Embasamento do tema por fontes jornalísticas e oficiais públicas.
- Enquadramento da dor (ajustado após checagem): os dados não mostram que pessoas 60+ caiam em mais golpes (DataSenado: 16% das vítimas têm 60+, contra 27% entre 16 e 29 anos). O argumento é de tipo e de mira: pessoas 60+ sofrem sobretudo fraudes que imitam bancos e cartões e são alvo de anúncios segmentados (aposentadoria, benefício, INSS).

- Estado do agente (histórico de alertas e de execuções) fica em `dados.json`, publicado junto da página do produto: cada disparo da automação abre uma sessão nova, sem memória da anterior. O banco de dados das páginas do Claude foi descartado porque só entrega dados a quem está conectado ao Claude; visitantes sem conta veriam a página vazia.
- Produto publicado em 06/11: https://claude.ai/artifact/FXPh194Ln6RmBsnkLAU7m2 (privado até ser compartilhado por link público no menu Compartilhar).
- Regras do agente aprendidas na execução de 06/11: veículos do mesmo grupo contam como uma fonte; fonte com interesse comercial no tema não conta; sem orientação de proteção confirmada, não há alerta.

## Arquitetura
1. Automação: tarefa agendada no Claude, semanal, dispara o agente.
2. Agente: pesquisa golpes da semana (bancos, Procons, polícias, imprensa), compara com o histórico e só segue com golpe novo e confirmado em 2 fontes.
3. Skill `linguagem-simples-60mais`: art. 5º da Lei 15.263/2025 + ISO 24495-1:2023 + regras próprias (um golpe, um sinal, uma ação, uma frase para lembrar; tom de autonomia, não de medo).
4. Produto: página pública com alerta da semana, arquivo, histórico de execuções e card para WhatsApp (repassado por pessoa de confiança; sem disparo automático a pessoas idosas).

## Critérios de sucesso
- Skill: 10 casos de teste aprovados no checklist do art. 5º (pares antes/depois no repositório).
- Agente: todo alerta com 2 fontes citadas ou mais.
- Automação: 2 execuções semanais reais ou mais, registradas antes de 27/11.
- Produto: página pública legível no celular, fonte grande, contraste nível AA da WCAG.

## Cronograma
- até 09/11: escopo fechado
- 10 a 14/11: skill v1 + 10 casos antes/depois (adiantado: v1 pronta em 06/11)
- 15 a 19/11: agente + página v1 (adiantado: agente v1 testado e página publicada em 06/11)
- 20 a 23/11: automação ligada, 2 execuções reais ou mais
- 24 a 26/11: repositório aberto, revisão final, roteiro da apresentação
- 27/11: entrega N2 (13/11 sem aula)

## Pendências
- Nome final do produto ("Sentinela" conota vigilância; alternativas: "Antes de Clicar", "Confere?").
- Recorte nacional de estelionato digital por faixa etária: não encontrado nas fontes consultadas.
- Skill v2: definir "uma ação" como um comportamento num mesmo momento; rodar comparação com e sem a skill.

## Fontes-chave
- Lei 15.263/2025 (Câmara): https://www2.camara.leg.br/legin/fed/lei/2025/lei-15263-14-novembro-2025-798293-publicacaooriginal-177011-pl.html
- DataSenado via Agência Senado: https://www12.senado.leg.br/noticias/infomaterias/2025/04/golpes-virtuais-aumentam-e-nao-fazem-distincao-de-idade
- Agência Pública (coluna de Natalia Viana): https://apublica.org/2026/05/depois-do-eca-esta-na-hora-de-um-estatuto-do-idoso-digital/
