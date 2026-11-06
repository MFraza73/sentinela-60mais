#!/usr/bin/env python3
"""Verificador de alertas da skill linguagem-simples-60mais.

Lê um alerta em Markdown no formato de assets/modelo-alerta.md e aponta:
  ERRO  -> impede a publicação; corrija antes de entregar.
  AVISO -> pede julgamento; corrija se melhorar a leitura.

Cada achado indica a técnica do art. 5º da Lei 15.263/2025 a que se refere (art5-N),
ou uma regra própria da skill (skill-...).

Uso:
  python scripts/checar_alerta.py alerta.md          # relatório legível
  python scripts/checar_alerta.py alerta.md --json   # relatório em JSON

Código de saída: 0 = aprovado, 1 = reprovado (há ERRO), 2 = rascunho marcado como NÃO PUBLICAR.
Só usa a biblioteca padrão do Python.
"""

import json
import re
import sys
import unicodedata

CAMPOS = ["Como chega", "O que pedem", "Sinal de golpe", "O que fazer", "Para lembrar"]
LIMITE_PALAVRAS_CORPO = 120
LIMITE_FRASE_ERRO = 20
LIMITE_FRASE_AVISO = 15
LIMITE_PARA_LEMBRAR = 10
LIMITE_CARD = 500
MIN_FONTES = 2

# Termos técnicos e estrangeiros (art. 5º, técnicas 5 e 6). ERRO, salvo se explicados entre parênteses logo depois.
TERMOS_EVITAR = {
    r"phishing": "mensagem falsa",
    r"spoofing": "número falsificado",
    r"n[úu]mero mascarado": "número falsificado",
    r"engenharia social": "conversa feita para enganar você",
    r"deep\s?fakes?": "vídeo ou voz falsos feitos no computador",
    r"clonagem de voz": "voz copiada por computador",
    r"voz sint[ée]tica": "voz copiada por computador",
    r"links? malicios[oa]s?": "link falso",
    r"malware": "programa espião",
    r"apps?": "aplicativo",
    r"tokens?": "código de segurança",
    r"autentica[çc][ãa]o de dois fatores": "confirmação em duas etapas",
    r"qr\s?codes?": "código QR (o quadradinho que a câmera lê)",
    r"credenciais": "senha e dados de acesso",
    r"dados sens[íi]veis": "senha, número do cartão e códigos",
    r"transa[çc](?:[ãa]o|[õo]es)": "pagamento ou transferência",
    r"benefici[áa]rios?": "quem vai receber o dinheiro",
    r"estelionatos?": "golpe",
    r"fraudes?": "golpe",
    r"central de atendimento": "telefone do banco",
    r"consignados?": "empréstimo descontado direto da aposentadoria",
}

# Verbos e fórmulas de repartição pública (técnica 4). AVISO.
VERBOS_EVITAR = {
    r"efetu\w*": "fazer",
    r"realiz\w*": "fazer",
    r"solicit\w*": "pedir",
    r"utiliz\w*": "usar",
    r"contat(?:ar|e|em|ando)": "ligar para, falar com",
    r"ressaltamos": "(apagar)",
    r"cumpre informar": "(apagar)",
}

# Termos pejorativos ou infantilizantes (técnica 7). ERRO.
PEJORATIVOS = [r"vov[óôo]s?", r"velhinh[oa]s?", r"idosinh[oa]s?", r"ingênu[oa]s?", r"desatent[oa]s?", r"patinho"]

# Siglas que exigem o nome completo antes (técnica 8).
SIGLAS = {
    "INSS": r"instituto nacional do seguro social",
    "SMS": r"mensagem de texto",
    "FGTS": r"fundo de garantia",
    "SAC": r"servi[çc]o de atendimento ao consumidor",
    "BO": r"boletim de ocorr[êe]ncia",
}
SIGLAS_LIVRES = {"CPF", "PIX"}

NOMINALIZACOES = [r"realiza[çc][ãa]o", r"efetiva[çc][ãa]o", r"utiliza[çc][ãa]o", r"solicita[çc][ãa]o", r"a fim de"]

EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF️]")
VOZ_PASSIVA = re.compile(
    r"\b(foi|foram|é|são|será|serão|seja|sejam|sendo)\s+(\w+(?:ad|id)[oa]s?)\b", re.IGNORECASE
)


def palavras(texto):
    limpo = re.sub(r"[*_`\"“”]", " ", texto)
    return [p for p in re.findall(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ$]+(?:[-'’][0-9A-Za-zÀ-ÖØ-öø-ÿ]+)*", limpo)]


def frases(texto):
    texto = re.sub(r"[*_`]", "", texto)
    partes = re.split(r"(?<=[.!?])\s+|\n+", texto)
    return [p.strip() for p in partes if p.strip()]


def normalizar(texto):
    return unicodedata.normalize("NFC", texto)


class Relatorio:
    def __init__(self):
        self.erros = []
        self.avisos = []

    def erro(self, regra, msg):
        self.erros.append({"regra": regra, "mensagem": msg})

    def aviso(self, regra, msg):
        self.avisos.append({"regra": regra, "mensagem": msg})


def separar_secoes(texto):
    """Divide em alerta, card e 'o que mudou'."""
    alerta, card, mudou = [], [], []
    alvo = alerta
    for linha in texto.splitlines():
        if re.match(r"^##\s*Card para WhatsApp", linha, re.IGNORECASE):
            alvo = card
            continue
        if re.match(r"^##\s*O que mudou", linha, re.IGNORECASE):
            alvo = mudou
            continue
        alvo.append(linha)
    return "\n".join(alerta), "\n".join(card).strip(), "\n".join(mudou).strip()


def verificar(texto):
    texto = normalizar(texto)
    r = Relatorio()
    primeira = next((l.strip() for l in texto.splitlines() if l.strip()), "")
    rascunho = bool(re.match(r"^RASCUNHO\s*[—–-]\s*N[ÃA]O PUBLICAR", primeira, re.IGNORECASE))

    alerta, card, _ = separar_secoes(texto)

    # Título
    m_titulo = re.search(r"^#\s+(.+)$", alerta, re.MULTILINE)
    titulo = m_titulo.group(1).strip() if m_titulo else ""
    if not titulo:
        r.erro("skill-formato", "Falta o título (linha começando com '# ').")
    elif ":" not in titulo:
        r.aviso("art5-10", "O título deveria ter o formato 'Nome do golpe: ação'.")

    # Campos
    valores = {}
    for campo in CAMPOS:
        m = re.search(r"^\*\*" + re.escape(campo) + r":\*\*\s*(.+)$", alerta, re.MULTILINE)
        if not m or not m.group(1).strip():
            r.erro("skill-formato", f"Falta o campo '{campo}'.")
        else:
            valores[campo] = m.group(1).strip()

    # Fontes
    m_fontes = re.search(r"^Fontes:\s*$(.*)", alerta, re.MULTILINE | re.DOTALL)
    links = re.findall(r"\[[^\]]+\]\((https?://[^)\s]+)\)", m_fontes.group(1)) if m_fontes else []
    if len(set(links)) < MIN_FONTES:
        r.erro("skill-fontes", f"São necessárias pelo menos {MIN_FONTES} fontes com link; encontradas {len(set(links))}.")

    # Corpo = título + campos
    corpo_partes = [titulo] + [valores[c] for c in CAMPOS if c in valores]
    corpo = "\n".join(corpo_partes)
    n_palavras = len(palavras(corpo))
    if n_palavras > LIMITE_PALAVRAS_CORPO:
        r.erro("art5-15", f"O corpo tem {n_palavras} palavras (máximo {LIMITE_PALAVRAS_CORPO}).")

    # Frases curtas e intercalações
    maior = 0
    for f in frases(corpo):
        n = len(palavras(f))
        maior = max(maior, n)
        trecho = f if len(f) <= 90 else f[:87] + "..."
        if n > LIMITE_FRASE_ERRO:
            r.erro("art5-2", f"Frase com {n} palavras (máximo {LIMITE_FRASE_ERRO}): \"{trecho}\"")
        elif n > LIMITE_FRASE_AVISO:
            r.aviso("art5-2", f"Frase com {n} palavras (ideal até {LIMITE_FRASE_AVISO}): \"{trecho}\"")
        if f.count(",") >= 3:
            r.aviso("art5-13", f"Frase com muitas vírgulas, possível intercalação: \"{trecho}\"")

    # Uma ação
    if "O que fazer" in valores and len(frases(valores["O que fazer"])) > 2:
        r.erro("skill-uma-acao", "'O que fazer' tem mais de duas frases; deixe uma única ação.")

    # Para lembrar
    if "Para lembrar" in valores:
        lembrar = valores["Para lembrar"]
        n = len(palavras(lembrar))
        if n > LIMITE_PARA_LEMBRAR:
            r.erro("skill-para-lembrar", f"'Para lembrar' tem {n} palavras (máximo {LIMITE_PARA_LEMBRAR}).")
        if not re.match(r'^["“].*["”]$', lembrar):
            r.aviso("skill-para-lembrar", "'Para lembrar' deveria estar entre aspas.")

    texto_avaliado = corpo + "\n" + card

    # Termos técnicos e estrangeiros
    for padrao, troca in TERMOS_EVITAR.items():
        for m in re.finditer(r"\b" + padrao + r"\b", texto_avaliado, re.IGNORECASE):
            depois = texto_avaliado[m.end():m.end() + 3]
            if "(" in depois:
                r.aviso("art5-5", f"'{m.group(0)}' mantido com explicação; confirme se é indispensável.")
            else:
                r.erro("art5-5", f"Termo técnico ou estrangeiro '{m.group(0)}'. Use: {troca}.")

    for padrao, troca in VERBOS_EVITAR.items():
        for m in re.finditer(r"\b" + padrao + r"\b", texto_avaliado, re.IGNORECASE):
            r.aviso("art5-4", f"'{m.group(0)}' soa como repartição pública. Prefira: {troca}.")

    for padrao in PEJORATIVOS:
        for m in re.finditer(r"\b" + padrao + r"\b", texto_avaliado, re.IGNORECASE):
            r.erro("art5-7", f"Termo pejorativo ou infantilizante: '{m.group(0)}'.")

    for padrao in NOMINALIZACOES:
        for m in re.finditer(r"\b" + padrao + r"\b", texto_avaliado, re.IGNORECASE):
            r.aviso("art5-14", f"'{m.group(0)}': prefira o verbo.")

    # Siglas
    for sigla, nome in SIGLAS.items():
        m = re.search(r"\b" + sigla + r"\b", texto_avaliado)
        if m:
            antes = texto_avaliado[:m.start()]
            if not re.search(nome, antes, re.IGNORECASE):
                r.erro("art5-8", f"Sigla '{sigla}' sem o nome completo antes.")

    # Caixa alta e alarmismo
    if re.search(r"\bPIX\b", texto_avaliado):
        r.aviso("skill-tom", "Escreva 'Pix', não 'PIX': é nome próprio.")
    for m in re.finditer(r"\b[A-ZÀ-Ý]{4,}\b", texto_avaliado):
        palavra = m.group(0)
        if palavra in SIGLAS or palavra in SIGLAS_LIVRES:
            continue
        r.erro("skill-tom", f"Palavra em caixa alta: '{palavra}'.")
    if re.search(r"\burgente\b", texto_avaliado, re.IGNORECASE):
        r.erro("skill-tom", "Evite 'urgente': o golpe usa pressa; o alerta usa calma.")
    if "!!" in texto_avaliado:
        r.erro("skill-tom", "Exclamações repetidas soam alarmistas.")
    elif "!" in texto_avaliado:
        r.aviso("skill-tom", "Ponto de exclamação: confirme se é necessário.")

    # Acessibilidade
    if EMOJI.search(texto_avaliado):
        r.erro("art5-17", "Há emoji; leitores de tela leem o nome de cada um em voz alta.")

    # Voz passiva (heurística)
    for m in VOZ_PASSIVA.finditer(corpo):
        r.aviso("art5-12", f"Possível voz passiva: '{m.group(0)}'. Prefira a voz ativa.")

    # Card
    if not card:
        r.erro("skill-card", "Falta a seção '## Card para WhatsApp'.")
    else:
        if len(card) > LIMITE_CARD:
            r.erro("skill-card", f"O card tem {len(card)} caracteres (máximo {LIMITE_CARD}).")
        if re.search(r"https?://|www\.", card):
            r.erro("skill-card", "O card não deve ter link.")
        linhas_card = [l for l in card.splitlines() if l.strip()]
        if linhas_card and not re.match(r"^\*[^*].*\*$", linhas_card[0].strip()):
            r.aviso("skill-card", "A primeira linha do card deveria ser o nome do golpe em *negrito*.")
        if linhas_card and not re.match(r"^\*[^*].*\*$", linhas_card[-1].strip()):
            r.aviso("skill-card", "O card deveria terminar com a frase para lembrar em *negrito*.")

    if rascunho:
        status = "RASCUNHO"
    else:
        status = "REPROVADO" if r.erros else "APROVADO"

    return {
        "status": status,
        "erros": r.erros,
        "avisos": r.avisos,
        "metricas": {
            "palavras_corpo": n_palavras,
            "maior_frase_palavras": maior,
            "caracteres_card": len(card),
            "fontes_com_link": len(set(links)),
        },
    }


def imprimir(resultado, nome):
    print(f"Verificação: {nome}")
    print(f"Status: {resultado['status']}")
    for e in resultado["erros"]:
        print(f"  ERRO  [{e['regra']}] {e['mensagem']}")
    for a in resultado["avisos"]:
        print(f"  AVISO [{a['regra']}] {a['mensagem']}")
    m = resultado["metricas"]
    print(
        f"Métricas: {m['palavras_corpo']} palavras no corpo; maior frase com {m['maior_frase_palavras']} palavras; "
        f"card com {m['caracteres_card']} caracteres; {m['fontes_com_link']} fontes com link."
    )
    print(f"Resumo: {len(resultado['erros'])} erro(s), {len(resultado['avisos'])} aviso(s).")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(64)
    caminho = args[0]
    with open(caminho, encoding="utf-8") as f:
        resultado = verificar(f.read())
    if "--json" in sys.argv:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        imprimir(resultado, caminho)
    codigos = {"APROVADO": 0, "REPROVADO": 1, "RASCUNHO": 2}
    sys.exit(codigos[resultado["status"]])


if __name__ == "__main__":
    main()
