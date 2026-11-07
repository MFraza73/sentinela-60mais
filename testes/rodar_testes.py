#!/usr/bin/env python3
"""Testes de regressão do Sentinela 60+.

Roda tudo o que pode ser checado sem interpretação:
  1. verificador de fontes contra os casos de testes/casos_fontes.json (execuções reais e casos-limite);
  2. gerador da imagem do alerta contra os casos de testes/imagem/ (precisa do Playwright com Chromium);
  3. verificador de linguagem simples contra o alerta da primeira execução;
  4. sincronia entre 03-agente/fontes.json e 03-agente/fontes.md;
  5. coerência do 05-produto/dados.json (campos dos alertas, imagens e correções).

Uso: python3 testes/rodar_testes.py [--sem-imagem]
Rode sempre antes de mudar regras do agente, a skill ou o mapa de fontes. Código de saída 0 só se tudo passar.
"""
import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TESTES = RAIZ / "testes"
SKILL = RAIZ / "02-skill" / "linguagem-simples-60mais"
AGENTE = RAIZ / "03-agente"
PRODUTO = RAIZ / "05-produto"

resultados = []


def registrar(grupo, nome, ok, detalhe=""):
    resultados.append((grupo, nome, ok, detalhe))
    marca = "ok   " if ok else "FALHA"
    print(f"  {marca} {nome}" + (f" — {detalhe}" if detalhe and not ok else ""))


def carregar_modulo(caminho, nome):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def testar_fontes():
    print("1. Verificador de fontes")
    cf = carregar_modulo(AGENTE / "scripts" / "checar_fontes.py", "checar_fontes")
    lista = cf.carregar_lista(AGENTE / "fontes.json")
    casos = json.loads((TESTES / "casos_fontes.json").read_text(encoding="utf-8"))["casos"]
    for c in casos:
        rel = cf.checar(c["item"], lista, date.fromisoformat(c["hoje"]), c.get("dados"))
        esp = c["esperado"]
        erros = sorted({e["codigo"] for e in rel["erros"]})
        avisos = {a["codigo"] for a in rel["avisos"]}
        problemas = []
        if rel["status"] != esp["status"]:
            problemas.append(f"status {rel['status']}, esperado {esp['status']}")
        if erros != sorted(set(esp.get("erros", []))):
            problemas.append(f"erros {erros}, esperado {sorted(set(esp.get('erros', [])))}")
        faltam = set(esp.get("avisos", [])) - avisos
        if faltam:
            problemas.append(f"faltam avisos {sorted(faltam)}")
        registrar("fontes", c["nome"], not problemas, "; ".join(problemas))


def testar_imagem():
    print("2. Gerador da imagem do alerta")
    script = SKILL / "scripts" / "gerar_imagem.py"
    casos = [
        ("bom.json", "calma", "APROVADO", []),
        ("ruim-link-telefone-emoji.json", "calma", "REPROVADO", ["link", "telefone", "emoji"]),
        ("ruim-titulo-longo.json", "calma", "REPROVADO", ["titulo tem"]),
        ("bom.json", "alarme", "REPROVADO", ["contraste"]),
    ]
    for arquivo, tema, status, trechos in casos:
        nome = f"{arquivo} (tema {tema})"
        proc = subprocess.run([sys.executable, str(script), "--alerta", str(TESTES / "imagem" / arquivo), "--tema", tema],
                              capture_output=True, text=True)
        try:
            rel = json.loads(proc.stdout)
        except json.JSONDecodeError:
            registrar("imagem", nome, False, (proc.stderr or proc.stdout)[-300:])
            continue
        texto_erros = " ".join(rel.get("erros", []))
        problemas = []
        if rel.get("status") != status:
            problemas.append(f"status {rel.get('status')}, esperado {status}")
        for t in trechos:
            if t not in texto_erros:
                problemas.append(f"erro esperado com '{t}' não apareceu")
        registrar("imagem", nome, not problemas, "; ".join(problemas))


def testar_alerta():
    print("3. Verificador de linguagem simples")
    alerta = AGENTE / "execucoes" / "2026-11-06-teste" / "alerta.md"
    proc = subprocess.run([sys.executable, str(SKILL / "scripts" / "checar_alerta.py"), str(alerta)],
                          capture_output=True, text=True)
    registrar("alerta", "alerta da execução de 06/11", "Status: APROVADO" in proc.stdout, proc.stdout[-300:])


def testar_sincronia():
    print("4. Sincronia do mapa de fontes")
    lista = json.loads((AGENTE / "fontes.json").read_text(encoding="utf-8"))
    md = (AGENTE / "fontes.md").read_text(encoding="utf-8")
    faltam = [e["dominio"] for e in lista["dominios"] if e["dominio"] not in md]
    registrar("sincronia", "todo domínio de fontes.json aparece em fontes.md", not faltam, f"faltam: {faltam}")


def testar_dados():
    print("5. Coerência do dados.json")
    dados = json.loads((PRODUTO / "dados.json").read_text(encoding="utf-8"))
    campos = ["id", "golpe", "publicado_em", "titulo", "como_chega", "o_que_pedem", "sinal", "o_que_fazer",
              "para_lembrar", "fontes", "card_whatsapp"]
    for a in dados.get("alertas", []):
        faltam = [c for c in campos if not a.get(c)]
        registrar("dados", f"alerta {a.get('id')} tem os campos obrigatórios", not faltam, f"faltam: {faltam}")
        if a.get("imagem"):
            existe = (PRODUTO / a["imagem"]).exists()
            registrar("dados", f"imagem do alerta {a.get('id')} existe", existe, a["imagem"])
    ids = {a.get("id") for a in dados.get("alertas", [])}
    for c in dados.get("correcoes", []):
        ok = c.get("alerta_id") in ids and c.get("data") and c.get("o_que_mudou") and c.get("por_que")
        registrar("dados", f"correção de {c.get('data')} aponta para um alerta e explica o porquê", bool(ok))


def main():
    sem_imagem = "--sem-imagem" in sys.argv
    testar_fontes()
    if sem_imagem:
        print("2. Gerador da imagem do alerta — pulado (--sem-imagem)")
    else:
        testar_imagem()
    testar_alerta()
    testar_sincronia()
    testar_dados()
    falhas = [r for r in resultados if not r[2]]
    print(f"\n{len(resultados) - len(falhas)} de {len(resultados)} testes passaram.")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
