#!/usr/bin/env python3
"""Verificador de fontes do agente Sentinela 60+.

Transforma em código as regras de confirmação de 03-agente/fontes.md, lidas de 03-agente/fontes.json:

  - pelo menos duas fontes que confirmam, de grupos diferentes (organizações independentes);
  - pelo menos uma fonte primária (órgão público, polícia, Procon ou banco);
  - o setor bancário inteiro (Febraban e bancos) vale como uma fonte só;
  - checagem, site fora da lista e site que a ferramenta não abre nunca confirmam;
  - origem declarada coerente com o domínio;
  - toda fonte com data, nenhuma no futuro; o golpe noticiado nos últimos 14 dias (pela data mais recente entre
    noticiado_em e as datas de todas as fontes); orientação com mais de 90 dias gera aviso;
  - com --dados, o golpe não pode ter sido publicado nas últimas 8 semanas nem estar na fila;
  - item que já está na fila vale por 28 dias desde a última notícia (a entrada exige 14);
  - golpe recorrente ("tipo": "recorrente") dispensa a janela de notícia, mas exige orientação de fonte
    primária com no máximo 12 meses e 26 semanas sem publicar o mesmo golpe.

O que exige leitura (se as fontes descrevem o mesmo mecanismo e a mesma ação, se uma só reproduz a outra) continua
com o agente. Este script só barra o que pode ser checado sem interpretação.

Uso:
  python3 checar_fontes.py --item candidato.json [--hoje AAAA-MM-DD] [--dados dados.json]
  python3 checar_fontes.py --dados dados.json --golpe falso-advogado [--hoje AAAA-MM-DD]

O item é um objeto com "golpe" e "fontes" (lista de {nome, url, origem, data}); um item da fila com "alerta" também
serve. Saída: relatório JSON com status APROVADO ou REPROVADO. Código de saída: 0 aprovado, 1 reprovado, 2 erro de uso.
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
LISTA = AQUI.parent / "fontes.json"
SEMANAS_PUBLICADO = 8
DIAS_ORIENTACAO_ANTIGA = 90
RE_DATA_NOME = re.compile(r"\((\d{1,2})/(\d{1,2})/(\d{4})\)")


def hoje_sao_paulo():
    return (datetime.now(timezone.utc) - timedelta(hours=3)).date()


def carregar_lista(caminho=LISTA):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    return dados


def achar_dominio(host, lista):
    """Devolve a entrada mais específica da lista para o host, ou None."""
    host = host.lower().rstrip(".")
    sem_www = host[4:] if host.startswith("www.") else host
    melhor = None
    for e in lista["dominios"]:
        d = e["dominio"]
        if e.get("exato"):
            casa = sem_www == d
        else:
            casa = sem_www == d or sem_www.endswith("." + d)
        if casa and (melhor is None or len(d) > len(melhor["dominio"])):
            melhor = e
    return melhor


def grupo_da_fonte(entrada, url):
    if entrada["grupo"] != "caminho":
        return entrada["grupo"]
    partes = [p for p in urlparse(url).path.split("/") if p]
    primeiro = partes[0] if partes else ""
    return f'{entrada["dominio"]}/{primeiro}'


def data_da_fonte(f):
    bruto = str(f.get("data", "")).strip()
    if bruto:
        try:
            return date.fromisoformat(bruto), None
        except ValueError:
            return None, f"data inválida: {bruto}"
    m = RE_DATA_NOME.search(str(f.get("nome", "")))
    if m:
        d, mes, a = (int(x) for x in m.groups())
        try:
            return date(a, mes, d), None
        except ValueError:
            return None, "data inválida no nome"
    return None, None


def checar(item, lista, hoje, dados=None):
    erros, avisos, detalhe = [], [], []

    def erro(codigo, msg):
        erros.append({"codigo": codigo, "mensagem": msg})

    def aviso(codigo, msg):
        avisos.append({"codigo": codigo, "mensagem": msg})

    if "alerta" in item and "fontes" not in item:
        fontes = item["alerta"].get("fontes", [])
    else:
        fontes = item.get("fontes", [])
    golpe = item.get("golpe") or item.get("alerta", {}).get("golpe")
    primarias = set(lista["origens_primarias"])
    confirmam = set(lista["origens_que_confirmam"])

    validas = []          # fontes que contam para confirmar
    todas_datas = []      # datas de todas as fontes, para saber se o golpe é recente
    vistas = set()
    for f in fontes:
        url = str(f.get("url", "")).strip()
        origem = f.get("origem")
        reg = {"nome": f.get("nome"), "url": url, "origem": origem}
        detalhe.append(reg)
        if url in vistas:
            erro("URL_REPETIDA", f"a mesma página aparece duas vezes: {url}")
            continue
        vistas.add(url)
        p = urlparse(url)
        if p.scheme != "https" or not p.netloc:
            erro("URL_INVALIDA", f"endereço precisa começar com https://: {url}")
            continue
        entrada = achar_dominio(p.netloc, lista)
        reg["dominio_lista"] = entrada["dominio"] if entrada else None
        reg["papel"] = entrada["papel"] if entrada else "fora-da-lista"
        quando, problema = data_da_fonte(f)
        reg["data"] = quando.isoformat() if quando else None
        if problema:
            erro("SEM_DATA", f"{problema} ({url})")
        elif quando is None:
            erro("SEM_DATA", f"fonte sem data de publicação: informe o campo data ({url})")
        elif quando > hoje:
            erro("DATA_FUTURA", f"data de publicação depois de hoje: {quando} ({url})")
        else:
            todas_datas.append(quando)
        if origem not in ("orgao", "policia", "procon", "banco", "imprensa", "checador", "outro", "apoio"):
            erro("ORIGEM_INVALIDA", f"origem ausente ou desconhecida: {origem!r} ({url})")
            continue
        if entrada is None:
            if origem in confirmam:
                erro("DOMINIO_FORA_DA_LISTA",
                     f"{p.netloc} não está na lista de fontes que confirmam; declare origem outro ou troque a fonte")
            else:
                aviso("NAO_CONTA", f"{p.netloc} fica no alerta, mas não conta para confirmar")
            continue
        if entrada["papel"] == "recusado":
            erro("DOMINIO_RECUSADO", f"{entrada['dominio']} é recusado pela ferramenta de busca")
            continue
        if entrada["papel"] == "sinal":
            if "checador" in entrada["origens"] and origem != "checador":
                erro("ORIGEM_INCOERENTE", f"{entrada['dominio']} é agência de checagem: declare origem checador")
            elif origem == "checador":
                aviso("NAO_CONTA", f"agência de checagem ({entrada['dominio']}) indica, mas não confirma")
            else:
                erro("DOMINIO_SO_SINAL",
                     f"{entrada['dominio']} não abre para a ferramenta: só pode indicar o golpe, não confirmá-lo")
            continue
        if entrada["papel"] == "apoio" or origem == "apoio":
            aviso("NAO_CONTA", f"{entrada['dominio']} é orientação geral e não conta como fonte")
            continue
        if origem not in entrada["origens"]:
            erro("ORIGEM_INCOERENTE",
                 f"origem {origem} não combina com {entrada['dominio']} (esperado: {', '.join(entrada['origens'])})")
            continue
        if origem in ("checador", "outro"):
            aviso("NAO_CONTA", f"fonte de origem {origem} não conta para confirmar ({url})")
            continue
        grupo = grupo_da_fonte(entrada, url)
        reg["grupo"] = grupo
        validas.append({"origem": origem, "grupo": grupo, "uf": entrada.get("uf"), "data": quando,
                        "dominio": entrada["dominio"], "exato": entrada.get("exato", False)})

    grupos = {v["grupo"] for v in validas}
    if len(validas) < 2:
        erro("POUCAS_FONTES", f"são precisas duas fontes que confirmam; há {len(validas)}")
    elif len(grupos) < 2:
        if grupos == {"setor-bancario"}:
            erro("SETOR_BANCARIO_SOZINHO",
                 "o setor bancário vale como uma fonte só: falta uma fonte de fora (órgão, polícia, Procon ou imprensa)")
        else:
            erro("MESMO_GRUPO", f"as fontes são da mesma organização ({', '.join(sorted(grupos))}): não são independentes")
    if validas and not any(v["origem"] in primarias for v in validas):
        erro("SEM_PRIMARIA", "nenhuma fonte primária: falta órgão público, polícia, Procon ou banco")

    ufs = [v["uf"] for v in validas if v["uf"]]
    repetidas = {u for u in ufs if ufs.count(u) > 1}
    if repetidas and len(grupos) >= 2:
        aviso("MESMO_ESTADO", f"duas fontes do mesmo governo estadual ({', '.join(sorted(repetidas))}): "
                              "confira se uma não só republica a outra")
    for v in validas:
        if v["exato"]:
            aviso("DOMINIO_AMPLO", f"{v['dominio']} reúne vários órgãos: confira quem publicou a página")
            break

    recorrente = item.get("tipo") == "recorrente"
    regras_rec = lista.get("recorrente", {})
    na_fila = bool(item.get("adicionado_em"))
    janela = lista.get("validade_fila_dias", 28) if na_fila else lista.get("janela_dias", 14)
    noticiado = item.get("noticiado_em")
    if noticiado:
        try:
            d = date.fromisoformat(str(noticiado))
            if d <= hoje:
                todas_datas.append(d)
        except ValueError:
            erro("SEM_DATA", f"noticiado_em inválido: {noticiado}")
    datas_conf = [v["data"] for v in validas if v["data"]]
    if recorrente:
        limite_or = regras_rec.get("orientacao_max_dias", 365)
        datas_prim = [v["data"] for v in validas if v["data"] and v["origem"] in primarias]
        if datas_prim and max(datas_prim) < hoje - timedelta(days=limite_or):
            erro("ORIENTACAO_VENCIDA", f"golpe recorrente: a orientação primária mais recente é de {max(datas_prim)}; "
                                       f"o limite é de {limite_or} dias")
        aviso("RECORRENTE", "golpe recorrente: confirme, na página aberta hoje, que a orientação continua valendo")
    else:
        if todas_datas and max(todas_datas) < hoje - timedelta(days=janela):
            erro("FORA_DA_JANELA", f"a notícia mais recente do golpe é de {max(todas_datas)}; "
                                   f"a janela é de {janela} dias até {hoje}")
        if datas_conf and max(datas_conf) < hoje - timedelta(days=DIAS_ORIENTACAO_ANTIGA):
            aviso("ORIENTACAO_ANTIGA", f"a orientação mais recente é de {max(datas_conf)}: confira se continua válida")

    if dados is not None and golpe:
        semanas = regras_rec.get("semanas_sem_republicar", 26) if recorrente else SEMANAS_PUBLICADO
        limite = hoje - timedelta(weeks=semanas)
        for a in dados.get("alertas", []):
            if a.get("golpe") == golpe and a.get("publicado_em", "") >= limite.isoformat() and a is not item:
                erro("JA_PUBLICADO", f"o golpe {golpe} foi publicado em {a.get('publicado_em')}")
        for f in dados.get("fila", []):
            if f.get("golpe") == golpe and f.get("status") == "aguardando" and f is not item:
                erro("JA_NA_FILA", f"o golpe {golpe} já está na fila")

    return {
        "status": "REPROVADO" if erros else "APROVADO",
        "golpe": golpe,
        "hoje": hoje.isoformat(),
        "erros": erros,
        "avisos": avisos,
        "fontes": detalhe,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--item", help="JSON de um candidato, item da fila ou alerta")
    ap.add_argument("--dados", help="dados.json da página (para checar duplicatas, ou com --golpe)")
    ap.add_argument("--golpe", help="com --dados: checa o item aguardando na fila com este golpe")
    ap.add_argument("--hoje", help="data de referência AAAA-MM-DD (padrão: hoje em São Paulo)")
    ap.add_argument("--lista", default=str(LISTA), help="caminho do fontes.json")
    args = ap.parse_args()

    hoje = date.fromisoformat(args.hoje) if args.hoje else hoje_sao_paulo()
    lista = carregar_lista(args.lista)
    dados = json.loads(Path(args.dados).read_text(encoding="utf-8")) if args.dados else None

    if args.item:
        item = json.loads(Path(args.item).read_text(encoding="utf-8"))
    elif dados is not None and args.golpe:
        achados = [f for f in dados.get("fila", []) if f.get("golpe") == args.golpe and f.get("status") == "aguardando"]
        if not achados:
            print(json.dumps({"status": "REPROVADO", "erros": [{"codigo": "NAO_ACHADO",
                  "mensagem": f"nenhum item aguardando na fila com o golpe {args.golpe}"}]}, ensure_ascii=False, indent=2))
            return 1
        item = achados[0]
    else:
        ap.print_usage(sys.stderr)
        return 2

    rel = checar(item, lista, hoje, dados)
    print(json.dumps(rel, ensure_ascii=False, indent=2))
    return 0 if rel["status"] == "APROVADO" else 1


if __name__ == "__main__":
    sys.exit(main())
