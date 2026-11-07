#!/usr/bin/env python3
"""Gera a imagem de um alerta aprovado (1080 x 1350, PNG) e confere se ela pode circular.

Uso:
  python3 gerar_imagem.py --dados dados.json --id 2026-11-06-falso-bloqueio-biometria-inss --saida imagens/<id>.png
  python3 gerar_imagem.py --alerta alerta.json --saida imagem.png

O alerta precisa ter: titulo, sinal, o_que_fazer, para_lembrar e publicado_em (AAAA-MM-DD).
A saída é um relatório em JSON com status APROVADO ou REPROVADO, o texto alternativo da imagem e as medidas.
Só uma imagem APROVADA pode ser publicada. Código de saída: 0 aprovado, 1 reprovado, 2 erro de uso.
"""
import argparse
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MODELO = AQUI.parent / "assets" / "imagem" / "modelo-imagem.html"

LARGURA, ALTURA = 1080, 1350
ESCALAS = [1.0, 0.94, 0.88]          # tenta caber reduzindo no máximo 12%
LIMITE_PALAVRAS = {"titulo": 12, "sinal": 20, "o_que_fazer": 22, "para_lembrar": 10}
LIMITE_TOTAL = 60
FONTE_MINIMA = {"#titulo": 68, "#sinal": 48, "#acao": 48, "#lembrar": 54}
CONTRASTE_TEXTO = 7.0                # nível AAA da WCAG para texto
CONTRASTE_ROTULO = 4.5               # rótulos e rodapé, em letra grande ou secundária
PREFIXOS_SERVICO = ("0800", "0300", "3003", "4004", "4020")
TEMAS_PERMITIDOS = {"atencao"}       # "institucional" e "alarme" existem só para comparação

RE_URL = re.compile(r"(https?://|www\.|\b[\w-]+\.(com|br|org|net|gov|app|io|info|site|online)\b)", re.I)
RE_ARROBA = re.compile(r"@\w")
RE_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
RE_NUMERO = re.compile(r"\d[\d\s.\-()]{1,}\d|\d")


def palavras(t):
    return len(re.findall(r"[\wÀ-ÿ]+", t or ""))


def data_longa(iso):
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
             "setembro", "outubro", "novembro", "dezembro"]
    a, m, d = iso.split("-")
    return f"{int(d)} de {meses[int(m) - 1]} de {a}"


def frase(t):
    t = (t or "").strip()
    return t if t.endswith((".", "!", "?")) else t + "."


def texto_alternativo(a):
    return (f"Alerta de golpe do Sentinela 60+, {data_longa(a['publicado_em'])}. {frase(a['titulo'])} "
            f"O sinal: {frase(a['sinal'])} O que fazer: {frase(a['o_que_fazer'])} "
            f"Para lembrar: {frase(a['para_lembrar'])}")


def luminancia(cor):
    cor = cor.strip()
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", cor)
    if m:
        rgb = [int(x) / 255 for x in m.groups()]
    else:
        h = cor.lstrip("#")
        rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted([luminancia(a), luminancia(b)], reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def checar_texto(a, erros, avisos):
    for campo in ("titulo", "sinal", "o_que_fazer", "para_lembrar", "publicado_em"):
        if not str(a.get(campo, "")).strip():
            erros.append(f"campo obrigatório vazio: {campo}")
    if erros:
        return
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a["publicado_em"]):
        erros.append("publicado_em precisa estar no formato AAAA-MM-DD")
    total = 0
    for campo, limite in LIMITE_PALAVRAS.items():
        n = palavras(a[campo])
        total += n
        if n > limite:
            erros.append(f"{campo} tem {n} palavras; o limite na imagem é {limite}")
    if total > LIMITE_TOTAL:
        erros.append(f"a imagem teria {total} palavras; o limite é {LIMITE_TOTAL}")
    texto = " ".join(a[c] for c in LIMITE_PALAVRAS)
    if RE_URL.search(texto):
        erros.append("a imagem não pode ter link nem endereço de site")
    if RE_ARROBA.search(texto):
        erros.append("a imagem não pode ter perfil de rede social (@)")
    if RE_EMOJI.search(texto):
        erros.append("a imagem não pode ter emoji")
    for bruto in RE_NUMERO.findall(texto):
        digitos = re.sub(r"\D", "", bruto)
        if len(digitos) >= 8 and not digitos.startswith(PREFIXOS_SERVICO):
            erros.append(f"número parecido com telefone pessoal: {bruto.strip()}. Só números oficiais de atendimento")
        elif len(digitos) >= 3:
            avisos.append(f"confira que o número {bruto.strip()} está nas fontes do alerta")


def renderizar(a, tema, saida, erros, avisos):
    from playwright.sync_api import sync_playwright

    medidas = {}
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(viewport={"width": LARGURA, "height": ALTURA}, device_scale_factor=1)
        pagina.goto(MODELO.as_uri())
        pagina.evaluate("document.fonts.ready.then(() => true)")
        escala_ok = None
        for escala in ESCALAS:
            dados = dict(a, tema=tema, escala=escala)
            pagina.evaluate("a => preencher(a)", dados)
            pagina.evaluate("document.fonts.ready.then(() => true)")
            cabe = pagina.evaluate("""() => {
                const q = document.getElementById('quadro'), c = document.getElementById('corpo');
                return q.scrollHeight <= q.clientHeight + 1 && c.scrollHeight <= c.clientHeight + 1;
            }""")
            if cabe:
                escala_ok = escala
                break
        if escala_ok is None:
            erros.append("o texto não cabe na imagem, mesmo reduzido em 12%: encurte o título, o sinal ou a ação")
        medidas["escala"] = escala_ok
        fonte_ok = pagina.evaluate("""() => document.fonts.check('700 56px "Atkinson Hyperlegible"')
                                         && document.fonts.check('400 56px "Atkinson Hyperlegible"')""")
        if not fonte_ok:
            erros.append("a fonte Atkinson Hyperlegible não carregou (pasta assets/imagem/fontes)")
        tamanhos = pagina.evaluate("""(sels) => Object.fromEntries(sels.map(s =>
            [s, parseFloat(getComputedStyle(document.querySelector(s)).fontSize)]))""", list(FONTE_MINIMA))
        medidas["tamanho_letra_px"] = tamanhos
        for sel, minimo in FONTE_MINIMA.items():
            if tamanhos[sel] + 0.01 < minimo:
                erros.append(f"letra de {sel} com {tamanhos[sel]:.0f}px; o mínimo é {minimo}px")
        cores = pagina.evaluate("""() => {
            const s = getComputedStyle(document.getElementById('quadro'));
            const v = n => s.getPropertyValue('--' + n).trim();
            return Object.fromEntries(['fundo','texto','faixa-fundo','faixa-texto','sinal-fundo','sinal-rotulo',
              'sinal-texto','acao-fundo','acao-rotulo','acao-texto','lembrar-fundo','lembrar-rotulo',
              'lembrar-texto','rodape'].map(n => [n, v(n)]));
        }""")
        pares = [
            ("título", "texto", "fundo", CONTRASTE_TEXTO),
            ("faixa", "faixa-texto", "faixa-fundo", CONTRASTE_TEXTO),
            ("sinal", "sinal-texto", "sinal-fundo", CONTRASTE_TEXTO),
            ("ação", "acao-texto", "acao-fundo", CONTRASTE_TEXTO),
            ("para lembrar", "lembrar-texto", "lembrar-fundo", CONTRASTE_TEXTO),
            ("rótulo do sinal", "sinal-rotulo", "sinal-fundo", CONTRASTE_ROTULO),
            ("rótulo da ação", "acao-rotulo", "acao-fundo", CONTRASTE_ROTULO),
            ("rótulo para lembrar", "lembrar-rotulo", "lembrar-fundo", CONTRASTE_ROTULO),
            ("rodapé", "rodape", "fundo", CONTRASTE_ROTULO),
        ]
        medidas["contraste"] = {}
        for nome, frente, fundo, minimo in pares:
            c = contraste(cores[frente], cores[fundo])
            medidas["contraste"][nome] = c
            if c < minimo:
                erros.append(f"contraste de {nome} é {c}:1; o mínimo é {minimo}:1")
        if saida:
            Path(saida).parent.mkdir(parents=True, exist_ok=True)
            pagina.locator("#quadro").screenshot(path=str(saida))
        navegador.close()
    return medidas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dados", help="dados.json da página do produto")
    ap.add_argument("--id", help="id do alerta em dados.json")
    ap.add_argument("--alerta", help="arquivo JSON com um alerta (alternativa a --dados e --id)")
    ap.add_argument("--saida", help="caminho do PNG a gravar; sem ele, só confere")
    ap.add_argument("--tema", default="atencao", help="atencao (padrão); institucional e alarme só para comparação")
    args = ap.parse_args()

    if args.alerta:
        alerta = json.loads(Path(args.alerta).read_text(encoding="utf-8"))
    elif args.dados and args.id:
        dados = json.loads(Path(args.dados).read_text(encoding="utf-8"))
        achados = [x for x in dados.get("alertas", []) if x.get("id") == args.id]
        if not achados:
            print(json.dumps({"status": "REPROVADO", "erros": [f"alerta {args.id} não está em alertas"]},
                             ensure_ascii=False, indent=2))
            return 1
        alerta = achados[0]
    else:
        ap.print_usage(sys.stderr)
        return 2

    erros, avisos = [], []
    if args.tema not in TEMAS_PERMITIDOS:
        avisos.append(f"tema {args.tema} serve só para comparação; a publicação usa o tema atencao")
    checar_texto(alerta, erros, avisos)
    medidas = {}
    if not erros:
        medidas = renderizar(alerta, args.tema, args.saida, erros, avisos)
    aprovado = not erros and args.tema in TEMAS_PERMITIDOS
    relatorio = {
        "status": "APROVADO" if aprovado else "REPROVADO",
        "erros": erros,
        "avisos": avisos,
        "imagem": args.saida if (args.saida and not erros) else None,
        "imagem_alt": texto_alternativo(alerta) if not erros else None,
        "medidas": medidas,
    }
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    return 0 if aprovado else 1


if __name__ == "__main__":
    sys.exit(main())
