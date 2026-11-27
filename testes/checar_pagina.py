#!/usr/bin/env python3
"""Mede o contraste e o tamanho da letra da página do produto, como ela aparece num celular.

Abre docs/index.html num navegador sem janela (Playwright), com largura de celular, espera a página carregar o
dados.json, abre os blocos recolhidos e mede cada trecho de texto visível:

  - contraste entre a cor da letra e a cor de fundo efetiva (fórmula da WCAG 2.2, critério 1.4.3);
  - tamanho e peso da letra, para saber se o trecho conta como texto grande (24 px, ou 18,66 px em negrito);
  - se a página cabe na largura da tela, sem rolagem lateral (critério 1.4.10, a 320 px).

Nível AA: 4,5:1 para texto normal e 3:1 para texto grande. Nível AAA: 7:1 e 4,5:1.

Uso: python3 testes/checar_pagina.py [--json]
Código de saída: 0 se todo texto passa no nível AA e a página cabe na tela; 1 se não; 2 se faltar o Playwright.

Não entra no rodar_testes.py: a medição depende do dados.json do dia e serve de registro, não de trava.
"""
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / "docs"
LARGURAS = [320, 360, 390]

MEDIR = r"""
() => {
  const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const lum = ([r, g, b]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  const cor = (s) => {
    const m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\/ ]+/).filter(Boolean).map(Number);
    return { rgb: [p[0], p[1], p[2]], a: p.length > 3 ? p[3] : 1 };
  };
  const mistura = (cima, a, baixo) => cima.map((v, i) => v * a + baixo[i] * (1 - a));
  const fundo = (el) => {
    const camadas = [];
    for (let e = el; e; e = e.parentElement) {
      const c = cor(getComputedStyle(e).backgroundColor);
      if (c && c.a > 0) { camadas.push(c); if (c.a === 1) break; }
    }
    let base = [255, 255, 255];
    for (const c of camadas.reverse()) base = mistura(c.rgb, c.a, base);
    return base;
  };
  const visivel = (el) => {
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const itens = [];
  const andar = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = andar.nextNode(); n; n = andar.nextNode()) {
    const texto = n.textContent.replace(/\s+/g, ' ').trim();
    const el = n.parentElement;
    if (!texto || !el || ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(el.tagName)) continue;
    let ok = true;
    for (let e = el; e; e = e.parentElement) if (!visivel(e)) { ok = false; break; }
    if (!ok) continue;
    const s = getComputedStyle(el);
    const f = fundo(el);
    const c = cor(s.color);
    const letra = mistura(c.rgb, c.a, f);
    const l1 = lum(letra), l2 = lum(f);
    const razao = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const px = parseFloat(s.fontSize);
    const peso = parseInt(s.fontWeight, 10) || 400;
    const grande = px >= 24 || (px >= 18.66 && peso >= 700);
    const hex = (v) => '#' + v.map((x) => Math.round(x).toString(16).padStart(2, '0')).join('').toUpperCase();
    itens.push({ texto: texto.slice(0, 60), letra: hex(letra), fundo: hex(f), razao: Math.round(razao * 100) / 100,
                 px: Math.round(px * 10) / 10, peso, grande, tag: el.tagName.toLowerCase(),
                 classe: (el.className && el.className.baseVal === undefined ? el.className : '') || '' });
  }
  return { itens, largura_conteudo: document.documentElement.scrollWidth, largura_tela: window.innerWidth,
           idioma: document.documentElement.lang, viewport: !!document.querySelector('meta[name=viewport]') };
}
"""


def servir():
    class Silencioso(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass

    manipulador = functools.partial(Silencioso, directory=str(SITE))
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manipulador)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor


def medir():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Falta o Playwright: pip install playwright && python -m playwright install chromium")
        sys.exit(2)
    servidor = servir()
    url = f"http://127.0.0.1:{servidor.server_address[1]}/index.html"
    saida = {}
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        for largura in LARGURAS:
            pagina = navegador.new_page(viewport={"width": largura, "height": 800})
            pagina.goto(url, wait_until="load")
            pagina.wait_for_function(
                "!document.body.innerText.includes('Carregando o alerta mais recente')", timeout=15000)
            pagina.evaluate("document.querySelectorAll('details').forEach((d) => { d.open = true; })")
            pagina.wait_for_timeout(300)
            saida[largura] = pagina.evaluate(MEDIR)
        navegador.close()
    servidor.shutdown()
    return saida


def resumir(medida):
    itens = medida["itens"]
    grupos = {}
    for i in itens:
        chave = (i["letra"], i["fundo"], i["grande"])
        g = grupos.setdefault(chave, {"letra": i["letra"], "fundo": i["fundo"], "grande": i["grande"],
                                      "razao": i["razao"], "trechos": 0, "menor_px": i["px"], "exemplo": i["texto"]})
        g["trechos"] += 1
        g["menor_px"] = min(g["menor_px"], i["px"])
    lista = sorted(grupos.values(), key=lambda g: g["razao"])
    for g in lista:
        g["aa"] = g["razao"] >= (3.0 if g["grande"] else 4.5)
        g["aaa"] = g["razao"] >= (4.5 if g["grande"] else 7.0)
    return {
        "trechos": len(itens),
        "combinacoes": lista,
        "menor_razao": min(i["razao"] for i in itens),
        "reprovados_aa": sum(g["trechos"] for g in lista if not g["aa"]),
        "abaixo_aaa": sum(g["trechos"] for g in lista if not g["aaa"]),
        "menor_px": min(i["px"] for i in itens),
        "abaixo_16px": sum(1 for i in itens if i["px"] < 16),
        "cabe_na_tela": medida["largura_conteudo"] <= medida["largura_tela"],
        "largura_conteudo": medida["largura_conteudo"],
        "idioma": medida["idioma"],
        "viewport": medida["viewport"],
    }


def main():
    medidas = medir()
    relatorio = {str(l): resumir(m) for l, m in medidas.items()}
    if "--json" in sys.argv:
        print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    falhou = False
    for largura, r in relatorio.items():
        if "--json" not in sys.argv:
            print(f"Largura {largura} px: {r['trechos']} trechos de texto; menor contraste {r['menor_razao']}:1; "
                  f"reprovados no AA: {r['reprovados_aa']}; abaixo do AAA: {r['abaixo_aaa']}; "
                  f"menor letra {r['menor_px']} px ({r['abaixo_16px']} trechos abaixo de 16 px); "
                  f"cabe na tela: {'sim' if r['cabe_na_tela'] else 'não'}")
            for g in r["combinacoes"]:
                marca = "ok " if g["aa"] else "ERRO"
                print(f"  {marca} {g['razao']:>5}:1  letra {g['letra']} sobre {g['fundo']}  "
                      f"{'grande' if g['grande'] else 'normal'}  {g['trechos']} trechos, a partir de {g['menor_px']} px  "
                      f"ex.: {g['exemplo'][:40]}")
        if r["reprovados_aa"] or not r["cabe_na_tela"]:
            falhou = True
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
