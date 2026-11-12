# Fontes do agente Sentinela 60+

Validado em 06/11/2026 com as mesmas ferramentas que o agente usa: busca na web filtrada por domínio
(`WebSearch` com `allowed_domains`) e abertura de página (`WebFetch`). Cada domínio desta lista passou por uma
busca filtrada e, quando a busca devolveu página, pela abertura de uma página real. Um domínio que a busca encontra
mas a ferramenta não abre só pode indicar golpes, nunca confirmá-los, porque trecho de busca não é fonte.

As regras deste arquivo também existem em código: `fontes.json` traz cada domínio com papel, origens aceitas e
grupo (a organização), e `scripts/checar_fontes.py` barra o candidato que não cumpre a regra de confirmação. Ao
mudar este arquivo, mude o `fontes.json` e rode `python3 testes/rodar_testes.py`.

## Papéis das fontes

| Papel | Quem | Indica candidato? | Confirma? |
| --- | --- | --- | --- |
| **Fonte primária** | Órgão público responsável pelo assunto, polícia, Procon, banco ou Federação Brasileira de Bancos (Febraban) | Sim | Sim; o setor bancário inteiro vale como uma fonte só |
| **Imprensa listada** | Veículos da tabela "Imprensa" abaixo | Sim | Sim, mas só como segunda fonte, ao lado de uma primária |
| **Sinal** | Agências de checagem, busca aberta, sites que a ferramenta encontra mas não abre | Sim | Nunca |
| **Apoio** | Cartilha do CERT.br, SaferNet | Não | Não. Serve para conferir a redação de "o que fazer" |
| **Ferramenta** | Serviços públicos e gratuitos de proteção: BC Protege+, Registrato, Proteção do CPF, Celular Seguro, Qual Empresa Me Ligou | Não | Não. Pode entrar em "o que fazer" quando uma das fontes que confirmam o golpe a recomenda |

**Golpe novo e golpe recorrente.** Um golpe novo precisa de notícia nos últimos 14 dias para entrar na fila, e
vale nela por 28 dias. Um golpe recorrente (falsa central, falso parente, falsa prova de vida) dispensa a notícia
recente, mas exige relevância máxima, orientação de fonte primária com data nos últimos 12 meses e 26 semanas
sem publicar o mesmo golpe. O recorrente só sai numa segunda sem golpe novo na fila. Os números estão em
`fontes.json`.

**Regra de confirmação.** Um golpe está confirmado quando duas fontes independentes, abertas pelo agente, descrevem
o mesmo mecanismo e a mesma ação de proteção, **e pelo menos uma delas é primária**.

**Independência.** Órgãos diferentes contam como fontes diferentes, mesmo dentro do mesmo governo (a Polícia Civil
e o Procon de um estado, por exemplo), desde que cada um publique a sua orientação. A agência de notícias de um
governo que só republica a nota de um órgão conta como o próprio órgão. Veículos do mesmo grupo contam como um.
Uma notícia que apenas reproduz a nota da outra fonte não soma.

**O setor bancário conta como uma fonte só.** A Febraban, qualquer banco e os materiais da Aliança Nacional de
Combate a Fraudes Bancárias Digitais (acordo entre o Ministério da Justiça e a Febraban) valem, juntos, como uma.
Um golpe confirmado só por bancos precisa de uma segunda fonte de fora do setor: órgão público, polícia, Procon ou
imprensa listada. Os bancos falam com autoridade sobre o que eles nunca fazem ("o banco não liga pedindo senha"),
mas têm dois vieses que o agente precisa compensar:

- **Toda página de banco testada promove recurso, seguro ou produto próprio**, menos a notícia da Caixa. A ação de
  proteção de um alerta precisa servir para cliente de qualquer banco: nunca recomende o recurso de um banco
  (modo protegido, alerta de golpe no aplicativo, proteção de chamadas), seguro ou produto pago.
- **O enquadramento é o do comportamento do cliente.** Nenhuma página testada menciona que o banco pode responder
  pelo prejuízo. A Súmula 479 do Superior Tribunal de Justiça diz que "as instituições financeiras respondem
  objetivamente pelos danos gerados por fortuito interno relativo a fraudes e delitos praticados por terceiros no
  âmbito de operações bancárias". Para orientar quem já caiu no golpe, prefira Procon, órgão público ou polícia.

## O campo `origem`

Toda fonte guardada pelo agente leva um campo `origem`, com um destes valores:

| `origem` | Quem | Primária? |
| --- | --- | --- |
| `orgao` | Órgão público dono do assunto: INSS, Secretaria Nacional do Consumidor (Senacon), Anatel, Receita, secretarias estaduais | Sim |
| `policia` | Polícia civil, secretaria de segurança, Polícia Federal | Sim |
| `procon` | Procon estadual ou municipal, inclusive os ligados ao Ministério Público | Sim |
| `banco` | Febraban e bancos (páginas de segurança, blogs e notícias dos próprios bancos) | Sim, mas o setor bancário inteiro vale como uma fonte |
| `imprensa` | Veículos da tabela "Imprensa" | Não |
| `checador` | Agências de checagem | Não; nunca confirma |
| `outro` | Site fora destas listas, achado na busca aberta (jornal regional, blog, portal) | Não; nunca confirma |
| `apoio` | CERT.br, SaferNet | Não; não conta como fonte |

Cada candidato também registra `indicado_por`: a primeira fonte em que o agente o encontrou, com `nome`, `url` e
`origem`. É o que mostra, ao longo das semanas, de onde vêm os golpes que viram alerta.

## Como buscar: regras aprendidas na validação

1. **Busque por pacotes de domínios**, com no máximo 7 domínios por busca. Num pacote grande, os sites que publicam
   muito ocupam todos os resultados: com 20 polícias juntas, a busca devolveu apenas 6 delas.
2. **Nunca inclua estes domínios no filtro:** `estadao.com.br`, `uol.com.br`, `globo.com`, `bbc.com`. A ferramenta
   recusa a busca inteira (erro HTTP 400), e o pacote todo se perde.
3. **Não gaste busca filtrada com** `g1.globo.com`, `oglobo.globo.com` e `folha.uol.com.br`: a ferramenta aceita o
   filtro, mas não devolve nenhum resultado, nem para a palavra "golpe" sozinha.
4. **"Golpe" também quer dizer golpe de Estado.** Combine sempre com o mecanismo: "golpe do falso...", "golpistas",
   "alerta", "como se proteger". A consulta "golpistas alerta como se proteger" trouxe resultados em todos os
   pacotes regionais.
5. **A busca não ordena por data.** Páginas de 2019 aparecem ao lado das de ontem. A data que vale é a da página
   aberta.
6. **Domínios amplos misturam órgãos.** Em `gov.br`, `ba.gov.br`, `goias.gov.br` e `pi.gov.br` aparecem também
   prefeituras, câmaras municipais e outras secretarias. Uma câmara municipal que republica nota do INSS não é
   fonte primária: confira quem publicou.
7. **Site que não abre só indica.** Se a polícia ou o Procon de um estado bloqueiam a ferramenta, procure a mesma
   orientação numa fonte que abra. A agência de notícias do governo estadual costuma republicar esses alertas
   (`agencia.ac.gov.br`, `parana.pr.gov.br`, `goias.gov.br`, `pi.gov.br`, `ba.gov.br`).
8. **Páginas longas do gov.br podem vir cortadas.** Leia o restante com `offset` antes de concluir que a página não
   traz orientação.
9. **O site do Banco Central não abre** (a página só carrega com JavaScript). Use a orientação do Banco Central
   quando ela estiver publicada em `gov.br` ou na Agência Brasil.

## Leitura direta: páginas de notícias

A busca não ordena por data, e nos primeiros cinco dias de varredura os pacotes regionais devolveram quase só
páginas de 2017 a 2025. A página de notícias de cada fonte traz o mais recente primeiro. A ferramenta só abre
endereço que tenha vindo de uma busca, por isso cada leitura começa por uma busca-ponte, que devolve o endereço da
página. Validado em 12/11/2026: cada linha abaixo passou pela busca-ponte e pela abertura.

| Fonte | Busca-ponte (`allowed_domains` e consulta) | Página de notícias | Quando | Observação |
| --- | --- | --- | --- | --- |
| Febraban | `["portal.febraban.org.br"]`, "Febraban notícias" | https://portal.febraban.org.br/ | Todo dia | Notícias com data; em 10/11 trazia dicas para a Black Friday |
| Procon de Santa Catarina | `["procon.sc.gov.br"]`, "notícias" | https://www.procon.sc.gov.br/ | Todo dia | Com data; em 11/11 trazia orientação para a Black Friday |
| Procon de São Paulo | `["procon.sp.gov.br"]`, "Procon-SP notícias" | https://www.procon.sp.gov.br/noticias/ | Todo dia | Vem a data e o título, sem o endereço: busque o título no mesmo domínio |
| Senacon | `["gov.br"]`, "Senacon notícias Ministério da Justiça últimas notícias" | https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/noticias-consumidor | Todo dia | Com data |
| Polícia Civil do Paraná | `["policiacivil.pr.gov.br"]`, "PCPR notícias" | https://www.policiacivil.pr.gov.br/noticias | Pacote `sul` | Com data e hora; muitas notícias por dia, quase todas de outros crimes |
| Polícia Civil de Santa Catarina | `["pc.sc.gov.br"]`, "notícias" | https://pc.sc.gov.br/?page_id=1258 | Pacote `sul` | Com data |
| Polícia Civil de Goiás | `["goias.gov.br"]`, "notícias" | https://goias.gov.br/policiacivil/ | Pacote `sudeste-centro-oeste` | Com data |
| Polícia Civil de Mato Grosso do Sul | `["pc.ms.gov.br"]`, "notícias" | https://www.pc.ms.gov.br/noticias/ | Pacote `sudeste-centro-oeste` | Com data |

**Não servem para leitura direta:** a página de últimas notícias do INSS pede login, e a lista em
`gov.br/inss/pt-br/assuntos/noticias` vem da mais antiga para a mais nova; a do Procon do Rio Grande do Sul está
parada desde abril de 2026; a da Polícia Civil do Rio Grande do Sul vem sem data confiável. Para essas fontes,
continue com a busca. Nos pacotes `nordeste` e `norte` nenhuma página foi validada ainda.

## Pacotes de busca

Ponha o mês e o ano na consulta ("golpe alerta novembro 2026"): no teste de 12/11, o pacote `sul` passou a
devolver notícias recentes da Polícia Civil do Paraná.

### Todos os dias

| Pacote | `allowed_domains` | Consulta testada |
| --- | --- | --- |
| `federal` | `["gov.br"]` | "INSS alerta golpe aposentados", "Senacon alerta golpe consumidor" |
| `bancos` | `["portal.febraban.org.br", "caixanoticias.caixa.gov.br", "feito.itau.com.br", "blog.nubank.com.br", "blog.bb.com.br", "blog.inter.co"]` | "golpe alerta como se proteger" |
| `imprensa` | `["agenciabrasil.ebc.com.br", "cnnbrasil.com.br", "correiobraziliense.com.br", "metropoles.com"]` | "golpe aposentados alerta", "golpe alerta" |
| `checadores` | `["aosfatos.org", "boatos.org", "projetocomprova.com.br", "e-farsas.com"]` | "golpe falso" |
| `recorte` | sem filtro | Termos do público: aposentado, INSS, parente, WhatsApp, ligação do banco |

### Um pacote regional por dia (fontes que confirmam)

| Pacote | `allowed_domains` |
| --- | --- |
| `sul` | `["pc.rs.gov.br", "procon.rs.gov.br", "pc.sc.gov.br", "procon.sc.gov.br", "policiacivil.pr.gov.br", "parana.pr.gov.br"]` |
| `sudeste-centro-oeste` | `["pc.es.gov.br", "procon.es.gov.br", "procon.sp.gov.br", "mpmg.mp.br", "goias.gov.br", "pc.ms.gov.br", "procon.ms.gov.br"]` |
| `nordeste` | `["policiacivil.ce.gov.br", "ba.gov.br", "policiacivil.ma.gov.br", "pi.gov.br", "procon.pe.gov.br"]` |
| `norte` | `["pc.ac.gov.br", "agencia.ac.gov.br", "policiacivil.am.gov.br", "rondonia.ro.gov.br", "policiacivil.rr.gov.br"]` |

Os quatro pacotes foram testados com a mesma consulta e devolveram páginas de pelo menos três domínios cada.

### Pacote de confirmação fora do rodízio

| Pacote | `allowed_domains` | Quando usar |
| --- | --- | --- |
| `bancos-orientacao` | `["seguranca.bradesco", "santander.com.br", "itau.com.br", "nubank.com.br", "inter.co"]` | Para confirmar o que o banco nunca faz num golpe que já é candidato. Páginas sem data: não servem para saber se o golpe é novo |

Testado com "golpe falsa central nunca liga pedindo senha": devolveu páginas dos cinco domínios.

### Pacotes de sinal (opcionais: indicam, não confirmam)

| Pacote | `allowed_domains` | Por que só sinal |
| --- | --- | --- |
| `sinal-sudeste-centro-oeste` | `["policiacivil.mg.gov.br", "ssp.sp.gov.br", "policiacivil.rj.gov.br", "pjc.mt.gov.br", "procon.mt.gov.br", "pcdf.df.gov.br", "procon.df.gov.br"]` | Bloqueiam a abertura pela ferramenta, ou a página vem sem texto |
| `sinal-nordeste` | `["policiacivil.pb.gov.br", "procon.pb.gov.br", "policiacivil.pe.gov.br", "sejuc.se.gov.br", "ssp.se.gov.br", "mppi.mp.br", "procon.al.gov.br"]` | Bloqueiam a abertura pela ferramenta |
| `sinal-norte` | `["policiacivil.ap.gov.br", "policiacivil.pa.gov.br", "procon.pa.gov.br", "procon.am.gov.br", "to.gov.br"]` | Bloqueiam a abertura pela ferramenta |

### Rodízio da semana

| Dia | Regional | Sinal (opcional) |
| --- | --- | --- |
| Segunda | `sudeste-centro-oeste` | `sinal-sudeste-centro-oeste` |
| Terça | `sul` | nenhum |
| Quarta | `nordeste` | `sinal-nordeste` |
| Quinta | `norte` | `sinal-norte` |
| Sexta | `sudeste-centro-oeste` | `sinal-sudeste-centro-oeste` |
| Sábado | `nordeste` | `sinal-nordeste` |
| Domingo | `sul` | `sinal-norte` |

São 6 buscas por dia, ou 7 com o pacote de sinal. Na hora de confirmar um candidato específico, o agente pode
buscar o nome do golpe em qualquer pacote de confirmação, de qualquer região, fora do rodízio.

## Polícias civis e Procons, estado por estado

"Confirma": a busca encontra e a página abre. "Só sinal": a busca encontra, mas a página não abre. "Lacuna": nenhum
endereço confiável encontrado.

| UF | Polícia Civil | Situação | Procon | Situação |
| --- | --- | --- | --- | --- |
| AC | `pc.ac.gov.br`, `agencia.ac.gov.br` | Confirma | `agencia.ac.gov.br` (o `procon.ac.gov.br` não aparece na busca) | Confirma |
| AL | `pc.al.gov.br` | Lacuna: a busca só traz páginas institucionais | `procon.al.gov.br` | Só sinal |
| AP | `policiacivil.ap.gov.br` | Só sinal | Não encontrado | Lacuna |
| AM | `policiacivil.am.gov.br` | Confirma | `procon.am.gov.br` | Só sinal |
| BA | `ba.gov.br` (`/policiacivil`, `/ssp`) | Confirma | Não encontrado | Lacuna |
| CE | `policiacivil.ce.gov.br` | Confirma | `mpce.mp.br` (Decon) | Só sinal: erro ao abrir |
| DF | `pcdf.df.gov.br` | Só sinal | `procon.df.gov.br` | Só sinal |
| ES | `pc.es.gov.br` | Confirma | `procon.es.gov.br` | Confirma |
| GO | `goias.gov.br` (`/policiacivil`, `/seguranca`); o antigo `policiacivil.go.gov.br` redireciona | Confirma | `goias.gov.br` (`/procon`); o antigo `procon.go.gov.br` redireciona | Confirma |
| MA | `policiacivil.ma.gov.br` | Confirma | Não encontrado | Lacuna |
| MT | `pjc.mt.gov.br` | Só sinal | `procon.mt.gov.br` | Só sinal |
| MS | `pc.ms.gov.br` | Confirma | `procon.ms.gov.br` | Confirma |
| MG | `policiacivil.mg.gov.br` | Só sinal | `mpmg.mp.br` (Procon-MG) | Confirma |
| PA | `policiacivil.pa.gov.br` | Só sinal | `procon.pa.gov.br` | Só sinal |
| PB | `policiacivil.pb.gov.br` | Só sinal | `procon.pb.gov.br` | Só sinal |
| PR | `policiacivil.pr.gov.br`, `parana.pr.gov.br` (`/aen`) | Confirma | `parana.pr.gov.br` (`/aen`); o `procon.pr.gov.br` dá erro ao abrir | Confirma |
| PE | `policiacivil.pe.gov.br`, `sds.pe.gov.br` | Só sinal | `procon.pe.gov.br` | Confirma; algumas páginas sem data, conferir |
| PI | `pi.gov.br`, `ssp.pi.gov.br` | Confirma | `mppi.mp.br` | Só sinal |
| RJ | `policiacivil.rj.gov.br` | Só sinal | Só Procons municipais (`*.rj.gov.br`) | Lacuna |
| RN | Não encontrado | Lacuna | `natal.rn.gov.br` (municipal) | Sinal; abertura não testada |
| RS | `pc.rs.gov.br` | Confirma | `procon.rs.gov.br` | Confirma |
| RO | `rondonia.ro.gov.br` | Confirma | `rondonia.ro.gov.br` | Confirma |
| RR | `policiacivil.rr.gov.br` | Confirma | `boavista.rr.gov.br` (municipal) | Só sinal |
| SC | `pc.sc.gov.br` | Confirma | `procon.sc.gov.br` | Confirma |
| SP | `ssp.sp.gov.br` | Só sinal: a página abre sem texto | `procon.sp.gov.br` | Confirma |
| SE | `ssp.se.gov.br` | Só sinal | `sejuc.se.gov.br` | Só sinal |
| TO | `to.gov.br` | Só sinal | `to.gov.br` (`/procon`) | Só sinal |

**Placar.** Polícias civis: 14 confirmam, 11 só sinalizam, 2 lacunas (AL, RN). Procons: 11 confirmam, 12 só
sinalizam, 4 lacunas (AP, BA, MA, RJ estadual).

## Fontes nacionais

| Fonte | Domínio | `origem` | Busca | Abre | Observação |
| --- | --- | --- | --- | --- | --- |
| INSS | `gov.br` (`/inss`) | `orgao` | Sim | Sim | Páginas longas podem vir cortadas |
| Senacon (Ministério da Justiça) | `gov.br` (`/mj`) | `orgao` | Sim | Sim | |
| Anatel | `gov.br` (`/anatel`) | `orgao` | Sim | Em parte | Uma página abriu, outra deu erro |
| Ministério das Comunicações, Planalto | `gov.br` (`/mcom`, `/planalto`) | `orgao` | Sim | Não testado | |
| Brasil contra Fake (Secom) | `gov.br` (`/secom`) | Não usar | Sim | Não | A página pede login |
| Banco Central | `bcb.gov.br` | Não usar | Só documentos técnicos | Não | A página só carrega com JavaScript |
| Febraban | `portal.febraban.org.br` | `banco` | Sim, série "Febraban alerta" | Sim | Tem uma lista dos golpes mais comuns contra pessoas idosas |
| Aliança Nacional de Combate a Fraudes Bancárias Digitais | `gov.br` (`/mj`) | `banco` | Sim | Em parte | Acordo entre o Ministério da Justiça e a Febraban: vale como setor bancário, não soma com a Febraban. Tem o material "Sofri um golpe, e agora?" |
| CERT.br | `cartilha.cert.br` | `apoio` | Sim | Sim | Fascículos "Golpes", entre eles "Caiu? Veja o que fazer". A página inicial `cert.br` é sobretudo técnica, para administradores de rede |
| SaferNet | `new.safernet.org.br` | `apoio` | Sim | Sim | |

## Bancos

| Banco | Onde buscar | Abre | Data nas páginas | Observação |
| --- | --- | --- | --- | --- |
| Caixa | `caixanoticias.caixa.gov.br` | Sim | Sim: alerta sobre golpes com o Bolsa Família, publicado em 17/09/2024 e atualizado em 28/10/2026 | Única página testada sem promoção de produto. O portal `caixa.gov.br/seguranca` bloqueia a ferramenta |
| Itaú | `feito.itau.com.br`; `itau.com.br/seguranca` | Sim | Sim no `feito` (24/09/2026); não na página de segurança | Promove recursos próprios do aplicativo e abertura de conta |
| Banco do Brasil | `blog.bb.com.br` | Sim | Sim (atualizado em 10/04/2026) | A página de golpes do portal `bb.com.br` vem sem o corpo do texto: use o blog |
| Nubank | `blog.nubank.com.br`; `nubank.com.br/ajuda-e-seguranca` | Sim | Sim no blog (atualizado em 17/08/2026); não na central | Promove recursos próprios do aplicativo |
| Inter | `blog.inter.co`; `inter.co/seguranca` | Sim | Sim no blog (13/08/2026); não na central | Promove recursos próprios; o mesmo site vende seguro contra golpe no Pix |
| Bradesco | `seguranca.bradesco` | Sim | Não | Promove seguros do banco. Só no pacote de confirmação |
| Santander | `santander.com.br` (blog e página de segurança) | Sim | Blog de 2023; página de segurança sem data | Promove curso e recursos próprios. Só no pacote de confirmação |

Os blogs com data (Itaú, Nubank, Banco do Brasil, Inter) e a Caixa às vezes noticiam golpes novos, por isso entram
no pacote diário `bancos`. Bradesco e Santander têm páginas permanentes, sem data, e só servem para confirmar.

## Ferramentas oficiais de proteção

Não são fontes de golpes: são serviços públicos e gratuitos que podem ser a ação de proteção de um alerta. Uma
ferramenta entra em "o que fazer" só quando uma das fontes que confirmam o golpe a recomenda. Use o link da página
do gov.br desta tabela, que abre; os sites próprios do Meu BC e do Celular Seguro carregam vazios para a ferramenta.

| Ferramenta | O que faz, em linguagem simples | Página validada | Conta gov.br |
| --- | --- | --- | --- |
| BC Protege+ (Banco Central) | Impede que abram conta de banco no seu nome | https://www.gov.br/pt-br/servicos/proteger-se-com-o-bc-protege (atualizada em 27/01/2026) | Prata ou ouro, com verificação em duas etapas |
| Registrato (Banco Central) | Mostra os empréstimos e as chaves Pix ligados ao seu CPF | https://www.gov.br/pt-br/servicos/obter-relatorio-do-sistema-de-informacoes-de-credito-scr (atualizada em 27/01/2026) | Prata ou ouro, com verificação em duas etapas |
| Proteção do CPF (Receita Federal e Redesim) | Impede que coloquem seu CPF como sócio de uma empresa | https://www.gov.br/pt-br/servicos/impedir-permitir-participacao-do-meu-cpf-no-cadastro-nacional-de-pessoas-juridicas-cnpj (atualizada em 08/09/2026) | Bronze para bloquear; prata ou ouro para desbloquear |
| Celular Seguro (Ministério da Justiça) | Bloqueia de uma vez o celular roubado, a linha e os aplicativos de banco | https://www.gov.br/pt-br/servicos/comunicar-roubo-furto-de-aparelho-pelo-aplicativo-celular-seguro (atualizada em 19/12/2025) | Qualquer nível. O celular precisa estar cadastrado antes do roubo |
| Qual Empresa Me Ligou (ABR Telecom, por determinação da Anatel) | Mostra de qual empresa é o número que ligou | https://www.qualempresameligou.com.br | Não precisa |

As cinco são gratuitas, segundo as próprias páginas. A exigência de conta gov.br prata ou ouro pode ser uma barreira
para quem tem 60+: quando a ferramenta exigir, o alerta diz que é preciso entrar com a conta gov.br.

**Fora do mapa:**

| Serviço | Por quê |
| --- | --- |
| Serasa AntiFraude | Serviço de empresa privada vendido em planos. O alerta não manda o público a produto pago |
| Detector de Site Confiável (Reclame AQUI e Axur) | Ferramenta de empresas privadas; a página não diz se é gratuita. Só entra se uma fonte oficial a recomendar |
| Meu BC (`bcb.gov.br/meubc`) e `celularseguro.mj.gov.br` | Carregam vazios para a ferramenta. Use as páginas do gov.br acima |

## Imprensa

| Veículo | Domínio | Busca | Abre | Observação |
| --- | --- | --- | --- | --- |
| Agência Brasil | `agenciabrasil.ebc.com.br` | Sim, com notícias recentes | Sim | Agência Brasil, Radioagência Nacional e TV Brasil são da EBC: contam como uma fonte |
| CNN Brasil | `cnnbrasil.com.br` | Sim | Sim | |
| Correio Braziliense | `correiobraziliense.com.br` | Sim | Sim | |
| Metrópoles | `metropoles.com` | Sim | Sim | |
| g1, O Globo | `g1.globo.com`, `oglobo.globo.com` | Sem resultado | Não testado | Fora dos pacotes |
| Folha | `folha.uol.com.br` | Sem resultado | Não testado | Fora dos pacotes |
| Estadão, UOL, BBC | `estadao.com.br`, `uol.com.br`, `bbc.com` | Recusado | Não testado | Nunca no filtro: derruba a busca |

## Agências de checagem (sinal)

| Agência | Domínio | Busca | Abre | Observação |
| --- | --- | --- | --- | --- |
| Aos Fatos | `aosfatos.org` | Sim | Sim | |
| Boatos.org | `boatos.org` | Sim, com checagens recentes | Sim | |
| Projeto Comprova | `projetocomprova.com.br` | Sim | Sim | Coalizão de veículos: conta como uma fonte |
| E-farsas | `e-farsas.com` | Sim, resultados antigos | Não testado | Prioridade baixa |
| Agência Lupa | Não encontrado | Não | Não testado | A busca não devolve páginas da Lupa |
| AFP Checamos | `checamos.afp.com` | Sem resultado | Não testado | |
| Fato ou Fake (g1) | `g1.globo.com` | Sem resultado | Não testado | |
| Estadão Verifica, UOL Confere | `estadao.com.br`, `uol.com.br` | Recusado | Não testado | |

Por que checagem não confirma: a checagem costuma verificar uma peça viral e, muitas vezes, cita a orientação da
empresa imitada. O agente usa a checagem para saber cedo que um golpe circula e vai à fonte primária buscar a
orientação.

## O que a validação mudou

- A lista antiga de imprensa (g1, Folha, Estadão, O Globo, UOL) era quase toda invisível para o agente: três domínios
  são recusados pela ferramenta e três não devolvem resultado. Só a Agência Brasil e a CNN Brasil funcionavam.
- Das 27 polícias civis, 11 bloqueiam a abertura de página pela ferramenta. Sem esta lista, o agente gastaria buscas
  em fontes que não pode citar.
- Os alertas guardados até 06/11 citavam sites regionais que reproduziam a polícia. A fonte primária existia e abre:
  a Polícia Civil do Paraná publicou em 16/10/2026 "PCPR alerta: recebeu uma ligação do banco pedindo Pix? Pode ser
  golpe" (`policiacivil.pr.gov.br`), com a orientação de que o banco "nunca orienta o cliente a fazer Pix para
  proteger dinheiro". Com a regra nova, a revisão de segunda-feira troca a fonte de segunda mão pela primária ou
  descarta o item.

- Sete bancos de varejo e a Febraban entraram no mapa, mas com papel limitado: o setor bancário vale como uma fonte
  só, e a ação de proteção nunca é um recurso ou produto de um banco. Os blogs com data entram no pacote diário; as
  páginas permanentes, só na hora de confirmar.

## Manutenção

Endereços de governo mudam (Goiás migrou polícia e Procon para `goias.gov.br`). Quando um domínio da lista falhar
três execuções seguidas, o agente registra o fato na `observacao` da execução, e a lista é revisada à mão. O agente
não altera este arquivo.
