#!/usr/bin/env python3
"""Verificador do "É golpe ou não?", da skill linguagem-simples-60mais.

Lê um quiz em JSON (os campos estão em references/quiz.md) e aponta:
  ERRO  -> impede a publicação; corrija antes de entregar.
  AVISO -> pede julgamento.

O texto escrito pelo projeto (sinal, explicação, frase para lembrar e os cards) segue as mesmas regras do
alerta: frases curtas, palavras do dia a dia, siglas explicadas, sem caixa alta, sem emoji e sem termo
pejorativo. A mensagem de exemplo pode imitar o tom do golpe, mas nunca traz link, telefone, perfil ou
endereço de site de verdade: use [link] e [número]. Com a pasta do repositório completa, as fontes passam
pelas regras de 03-agente/fontes.json: estar na lista, ter data e ter pelo menos uma fonte primária com
orientação dos últimos 12 meses.

Uso:
  python3 scripts/checar_quiz.py quiz.json [--hoje AAAA-MM-DD] [--json]
  python3 scripts/checar_quiz.py --dados dados.json --id 2026-11-21-quiz

Código de saída: 0 = aprovado, 1 = reprovado, 2 = erro de uso. Só usa a biblioteca padrão do Python.
"""
import argparse
import importlib.util
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CHECAR_FONTES = AQUI.parents[2] / "03-agente" / "scripts" / "checar_fontes.py"

CANAIS = {"WhatsApp", "mensagem de texto", "ligação", "e-mail", "rede social"}
RESPOSTAS = {"golpe", "nao-golpe"}
LIMITES = {"mensagem": 45, "sinal": 25, "explicacao": 40, "para_lembrar": 10}
LIMITE_CARD = 500
DIAS_ORIENTACAO = 365

RE_LINK = re.compile(r"https?://|www\.|\b[\w-]+\.(?:com|net|org|gov|br|io|co|site|online|xyz|app)\b", re.IGNORECASE)
RE_TELEFONE = re.compile(r"(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b|\b0800[\s-]?\d{3}[\s-]?\d{4}\b")
RE_PERFIL = re.compile(r"(?<![\w.])@[A-Za-z0-9_.]{3,}")


def carregar(caminho, nome):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ca = carregar(AQUI / "checar_alerta.py", "checar_alerta")


def hoje_sao_paulo():
    return (datetime.now(timezone.utc) - timedelta(hours=3)).date()


def checar_texto_nosso(texto, r, rotulo):
    """Regras do alerta aplicadas ao texto escrito pelo projeto."""
    for f in ca.frases(texto):
        n = len(ca.palavras(f))
        if n > ca.LIMITE_FRASE_ERRO:
            r.erro("art5-2", f"{rotulo}: frase com {n} palavras (máximo {ca.LIMITE_FRASE_ERRO}).")
        elif n > ca.LIMITE_FRASE_AVISO:
            r.aviso("art5-2", f"{rotulo}: frase com {n} palavras (ideal até {ca.LIMITE_FRASE_AVISO}).")
    for padrao, troca in ca.TERMOS_EVITAR.items():
        for m in re.finditer(r"\b" + padrao + r"\b", texto, re.IGNORECASE):
            if "(" not in texto[m.end():m.end() + 3]:
                r.erro("art5-5", f"{rotulo}: termo técnico '{m.group(0)}'. Use: {troca}.")
    for padrao in ca.PEJORATIVOS:
        for m in re.finditer(r"\b" + padrao + r"\b", texto, re.IGNORECASE):
            r.erro("art5-7", f"{rotulo}: termo pejorativo ou infantilizante '{m.group(0)}'.")
    for m in re.finditer(r"\b[A-ZÀ-Ý]{4,}\b", texto):
        if m.group(0) not in ca.SIGLAS and m.group(0) not in ca.SIGLAS_LIVRES:
            r.erro("skill-tom", f"{rotulo}: palavra em caixa alta '{m.group(0)}'.")
    if re.search(r"\burgente\b", texto, re.IGNORECASE) or "!!" in texto:
        r.erro("skill-tom", f"{rotulo}: tom alarmista ('urgente' ou '!!').")


def checar_sem_contato(texto, r, rotulo):
    """Nada que vire golpe: link, telefone, perfil ou emoji."""
    if RE_LINK.search(texto):
        r.erro("skill-sem-link", f"{rotulo}: tem link ou endereço de site. Use [link].")
    if RE_TELEFONE.search(texto):
        r.erro("skill-sem-telefone", f"{rotulo}: tem número de telefone. Use [número].")
    if RE_PERFIL.search(texto):
        r.erro("skill-sem-perfil", f"{rotulo}: tem perfil de rede social.")
    if ca.EMOJI.search(texto):
        r.erro("art5-17", f"{rotulo}: tem emoji.")


def checar_fontes_quiz(fontes, r, hoje):
    if len(fontes) < 1:
        r.erro("skill-fontes", "O quiz precisa de pelo menos uma fonte.")
        return
    if not CHECAR_FONTES.exists():
        r.aviso("skill-fontes", "Sem 03-agente/fontes.json por perto: confira à mão que há uma fonte primária.")
        return
    cf = carregar(CHECAR_FONTES, "checar_fontes")
    lista = cf.carregar_lista()
    rel = cf.checar({"golpe": "quiz", "fontes": fontes, "tipo": "recorrente"}, lista, hoje)
    ignorar = {"POUCAS_FONTES", "MESMO_GRUPO", "SETOR_BANCARIO_SOZINHO", "SEM_PRIMARIA", "ORIENTACAO_VENCIDA"}
    for e in rel["erros"]:
        if e["codigo"] not in ignorar:
            r.erro("fontes-" + e["codigo"].lower(), e["mensagem"])
    primarias = set(lista["origens_primarias"])
    validas = [f for f in rel["fontes"] if f.get("grupo") and f.get("origem") in primarias]
    if not validas:
        r.erro("fontes-sem-primaria", "Falta uma fonte primária (órgão público, polícia, Procon ou banco) da lista.")
        return
    recentes = [f for f in validas if f.get("data") and date.fromisoformat(f["data"]) >= hoje - timedelta(days=DIAS_ORIENTACAO)]
    if not recentes:
        r.erro("fontes-orientacao-vencida",
               f"A fonte primária mais recente tem mais de {DIAS_ORIENTACAO} dias: abra uma orientação atual.")


def verificar(q, hoje=None):
    hoje = hoje or hoje_sao_paulo()
    r = ca.Relatorio()
    obrig = ["canal", "mensagem", "resposta", "sinal", "explicacao", "para_lembrar", "fontes",
             "card_pergunta", "card_resposta"]
    for c in obrig:
        if not q.get(c):
            r.erro("quiz-formato", f"Falta o campo '{c}'.")
    if q.get("resposta") and q["resposta"] not in RESPOSTAS:
        r.erro("quiz-formato", "A resposta tem de ser 'golpe' ou 'nao-golpe'.")
    if q.get("canal") and q["canal"] not in CANAIS:
        r.aviso("quiz-formato", f"Canal '{q['canal']}' fora da lista: {', '.join(sorted(CANAIS))}.")
    if q.get("publicado_em") and q.get("resposta_em"):
        try:
            p, s = date.fromisoformat(q["publicado_em"]), date.fromisoformat(q["resposta_em"])
            if s != p + timedelta(days=1):
                r.erro("quiz-formato", "A resposta sai no dia seguinte: resposta_em = publicado_em + 1 dia.")
        except ValueError:
            r.erro("quiz-formato", "Datas inválidas em publicado_em ou resposta_em.")

    metricas = {}
    for campo, limite in LIMITES.items():
        n = len(ca.palavras(str(q.get(campo, ""))))
        metricas[campo] = n
        if n > limite:
            r.erro("quiz-tamanho", f"'{campo}' tem {n} palavras (máximo {limite}).")
    lembrar = str(q.get("para_lembrar", ""))
    if lembrar[:1] in "\"“":
        r.erro("quiz-formato", "'para_lembrar' vai sem aspas no JSON; a página põe as aspas.")

    nosso = "\n".join(str(q.get(c, "")) for c in ("sinal", "explicacao", "para_lembrar"))
    checar_texto_nosso(nosso, r, "texto do quiz")
    checar_texto_nosso(str(q.get("card_resposta", "")).replace("*", ""), r, "card da resposta")
    for c in ("mensagem", "sinal", "explicacao", "card_pergunta", "card_resposta"):
        checar_sem_contato(str(q.get(c, "")), r, c)

    for c in ("card_pergunta", "card_resposta"):
        card = str(q.get(c, ""))
        metricas[c] = len(card)
        if len(card) > LIMITE_CARD:
            r.erro("skill-card", f"'{c}' tem {len(card)} caracteres (máximo {LIMITE_CARD}).")
    if q.get("card_pergunta") and "golpe ou não" not in q["card_pergunta"].lower():
        r.erro("skill-card", "O card da pergunta tem de trazer a pergunta 'É golpe ou não?'.")
    if q.get("card_pergunta") and q.get("resposta") and re.search(
            r"\b(é golpe\.|não é golpe)", q["card_pergunta"], re.IGNORECASE):
        r.erro("skill-card", "O card da pergunta não pode entregar a resposta.")
    if q.get("card_resposta"):
        primeira = q["card_resposta"].strip().splitlines()[0]
        esperado = "não é golpe" if q.get("resposta") == "nao-golpe" else "é golpe"
        if esperado not in primeira.lower() or (esperado == "é golpe" and "não é golpe" in primeira.lower()):
            r.erro("skill-card", f"A primeira linha do card da resposta tem de dizer '{esperado}'.")

    checar_fontes_quiz(q.get("fontes", []), r, hoje)
    return {"status": "REPROVADO" if r.erros else "APROVADO", "erros": r.erros, "avisos": r.avisos,
            "metricas": metricas}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quiz", nargs="?")
    ap.add_argument("--dados")
    ap.add_argument("--id")
    ap.add_argument("--hoje")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.quiz:
        q = json.loads(Path(a.quiz).read_text(encoding="utf-8"))
        nome = a.quiz
    elif a.dados and a.id:
        achados = [x for x in json.loads(Path(a.dados).read_text(encoding="utf-8")).get("quizzes", [])
                   if x.get("id") == a.id]
        if not achados:
            print(f"Nenhum quiz com id {a.id}.")
            return 2
        q, nome = achados[0], a.id
    else:
        ap.print_help()
        return 2
    hoje = date.fromisoformat(a.hoje) if a.hoje else None
    res = verificar(q, hoje)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"Verificação: {nome}\nStatus: {res['status']}")
        for e in res["erros"]:
            print(f"  ERRO  [{e['regra']}] {e['mensagem']}")
        for v in res["avisos"]:
            print(f"  AVISO [{v['regra']}] {v['mensagem']}")
        m = res["metricas"]
        print("Métricas: " + "; ".join(f"{k} {v}" for k, v in m.items()))
    return 0 if res["status"] == "APROVADO" else 1


if __name__ == "__main__":
    sys.exit(main())
