#!/usr/bin/env python3
"""Monta o site público do Sentinela 60+ na pasta docs/, servida pelo GitHub Pages.

A página do produto (05-produto/index.html) é escrita no formato das páginas do Claude, que recebem o cabeçalho do
documento na hora da publicação. Fora do Claude, o navegador precisa do documento completo. Este script:

  1. envolve a página num documento HTML completo (doctype, idioma, codificação, viewport), levando o título,
     a descrição e as fontes tipográficas para o cabeçalho;
  2. copia dados.json e a pasta imagens/ para docs/;
  3. grava docs/.nojekyll, para o GitHub Pages servir os arquivos sem processá-los.

Uso: python3 05-produto/montar_site.py [--dados <dados.json>] [--imagens <pasta>]
Sem argumentos, usa os arquivos de 05-produto/. Rode depois de cada mudança na página ou nos dados.
"""
import argparse
import re
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SITE = RAIZ / "docs"

RESET = ("*,*::before,*::after{box-sizing:border-box}body{margin:0;background:#fff}"
         "img{max-width:100%}[hidden]{display:none!important}")


def montar(dados, imagens):
    pagina = (AQUI / "index.html").read_text(encoding="utf-8")
    cabecalho = []
    # Leva para o <head> as linhas de topo que pertencem a ele: <title>, <meta> e <link>
    linhas = pagina.splitlines()
    corpo_inicio = 0
    for i, linha in enumerate(linhas):
        s = linha.strip()
        if re.match(r"<(title|meta|link)\b", s):
            if 'name="claude:' not in s:
                cabecalho.append(s)
            corpo_inicio = i + 1
        elif s == "":
            continue
        else:
            break
    corpo = "\n".join(linhas[corpo_inicio:])
    documento = (
        "<!doctype html>\n<html lang=\"pt-BR\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
        + "\n".join(cabecalho)
        + f"\n<style>{RESET}</style>\n</head>\n<body>\n{corpo}\n</body>\n</html>\n"
    )
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(documento, encoding="utf-8")
    shutil.copyfile(dados, SITE / "dados.json")
    destino = SITE / "imagens"
    destino.mkdir(exist_ok=True)
    copiadas = 0
    for png in sorted(Path(imagens).glob("*.png")):
        shutil.copyfile(png, destino / png.name)
        copiadas += 1
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    return copiadas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dados", default=str(AQUI / "dados.json"))
    ap.add_argument("--imagens", default=str(AQUI / "imagens"))
    args = ap.parse_args()
    n = montar(Path(args.dados), Path(args.imagens))
    print(f"Site montado em {SITE}: index.html, dados.json e {n} imagem(ns).")


if __name__ == "__main__":
    main()
