# -*- coding: utf-8 -*-
"""
Bot de alertas de empleo -> Telegram
====================================
Consulta varias APIs GRATUITAS de empleo remoto/internacional, filtra por
las palabras clave que te interesan (Data / BI / Analytics), descarta las
ofertas que ya te avisó antes y te manda las nuevas por Telegram.

Diseñado para correr solo en GitHub Actions cada pocas horas.

Autor: Daniel Nima (github.com/daniel-nima)
"""
import os
import re
import json
import time
import html
import unicodedata
import urllib.request
import urllib.parse

import config

# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
UA = "JobAlertBot/1.0 (+https://github.com/daniel-nima)"


def http_get_json(url, timeout=25):
    """Descarga una URL y devuelve el JSON, o None si algo falla."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def normaliza(texto):
    """minúsculas + sin acentos, para comparar de forma robusta."""
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def pasa_filtro(titulo):
    """True si el título contiene una keyword deseada y ninguna excluida."""
    t = normaliza(titulo)
    if not any(normaliza(k) in t for k in config.KEYWORDS_PUESTO):
        return False
    if any(normaliza(x) in t for x in config.EXCLUIR_TITULO):
        return False
    return True


def job_id(url):
    """ID estable de una oferta a partir de su URL."""
    return re.sub(r"[?#].*$", "", (url or "").strip().rstrip("/"))


# --------------------------------------------------------------------------
# Cada función devuelve una lista de dicts normalizados:
#   {titulo, empresa, ubicacion, url, fuente}
# Si una fuente falla, NO rompe el bot: se registra y se sigue con las demás.
# --------------------------------------------------------------------------
def fuente_remotive():
    ofertas = []
    for termino in config.TERMINOS_BUSQUEDA:
        url = "https://remotive.com/api/remote-jobs?" + urllib.parse.urlencode({"search": termino})
        data = http_get_json(url)
        for j in data.get("jobs", []):
            ofertas.append({
                "titulo": j.get("title", ""),
                "empresa": j.get("company_name", ""),
                "ubicacion": j.get("candidate_required_location", "Remoto"),
                "url": j.get("url", ""),
                "fuente": "Remotive",
            })
    return ofertas


def fuente_jobicy():
    ofertas = []
    for termino in config.TERMINOS_BUSQUEDA:
        url = "https://jobicy.com/api/v2/remote-jobs?" + urllib.parse.urlencode({"count": 50, "tag": termino})
        data = http_get_json(url)
        for j in data.get("jobs", []):
            ofertas.append({
                "titulo": j.get("jobTitle", ""),
                "empresa": j.get("companyName", ""),
                "ubicacion": j.get("jobGeo", "Remoto"),
                "url": j.get("url", ""),
                "fuente": "Jobicy",
            })
    return ofertas


def fuente_arbeitnow():
    """Empleos en Europa (muchos remotos). Devuelve una sola página grande."""
    data = http_get_json("https://www.arbeitnow.com/api/job-board-api")
    ofertas = []
    for j in data.get("data", []):
        loc = j.get("location", "")
        if j.get("remote"):
            loc = (loc + " · Remoto").strip(" ·")
        ofertas.append({
            "titulo": j.get("title", ""),
            "empresa": j.get("company_name", ""),
            "ubicacion": loc or "Europa",
            "url": j.get("url", ""),
            "fuente": "Arbeitnow",
        })
    return ofertas


def fuente_remoteok():
    """RemoteOK: el primer elemento del arreglo es metadata legal, se ignora."""
    data = http_get_json("https://remoteok.com/api")
    ofertas = []
    for j in data:
        if not isinstance(j, dict) or "position" not in j:
            continue
        ofertas.append({
            "titulo": j.get("position", "") or j.get("title", ""),
            "empresa": j.get("company", ""),
            "ubicacion": j.get("location") or "Remoto",
            "url": j.get("url", ""),
            "fuente": "RemoteOK",
        })
    return ofertas


FUENTES = {
    "Remotive": fuente_remotive,
    "Jobicy": fuente_jobicy,
    "Arbeitnow": fuente_arbeitnow,
    "RemoteOK": fuente_remoteok,
}


# --------------------------------------------------------------------------
# Estado (ofertas ya notificadas)
# --------------------------------------------------------------------------
def cargar_vistos():
    try:
        with open(config.ARCHIVO_VISTOS, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def guardar_vistos(vistos):
    # conserva solo los últimos MAX_VISTOS para no crecer sin límite
    recorte = list(vistos)[-config.MAX_VISTOS:]
    with open(config.ARCHIVO_VISTOS, "w", encoding="utf-8") as f:
        json.dump(recorte, f, ensure_ascii=False, indent=0)


# --------------------------------------------------------------------------
# Telegram
# --------------------------------------------------------------------------
def enviar_telegram(token, chat_id, texto):
    url = "https://api.telegram.org/bot%s/sendMessage" % token
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status == 200


def formatea(oferta):
    t = html.escape(oferta["titulo"])
    e = html.escape(oferta["empresa"] or "—")
    loc = html.escape(oferta["ubicacion"] or "—")
    return ("💼 <b>%s</b>\n"
            "🏢 %s\n"
            "🌍 %s  ·  <i>%s</i>\n"
            "🔗 <a href=\"%s\">Ver oferta</a>"
            % (t, e, loc, oferta["fuente"], oferta["url"]))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit("Faltan las variables TELEGRAM_TOKEN y/o TELEGRAM_CHAT_ID")

    vistos = cargar_vistos()
    primera_vez = len(vistos) == 0

    # 1) Recolectar de todas las fuentes (tolerante a fallos)
    todas = []
    for nombre, fn in FUENTES.items():
        try:
            res = fn()
            print("  [%s] %d ofertas traídas" % (nombre, len(res)))
            todas.extend(res)
        except Exception as e:  # noqa
            print("  [%s] ERROR: %s (se continúa con las demás)" % (nombre, e))

    # 2) Filtrar por keywords + quitar duplicados por URL
    nuevas = []
    ids_en_lote = set()
    for o in todas:
        oid = job_id(o["url"])
        if not oid or oid in ids_en_lote or oid in vistos:
            continue
        if not pasa_filtro(o["titulo"]):
            continue
        ids_en_lote.add(oid)
        nuevas.append(o)

    print("Total recolectadas: %d | Nuevas que pasan el filtro: %d" % (len(todas), len(nuevas)))

    # 3) La primera corrida solo marca lo existente como "visto" (sin spamear)
    if primera_vez:
        for o in todas:
            oid = job_id(o["url"])
            if oid:
                vistos.add(oid)
        guardar_vistos(vistos)
        # aviso de arranque
        try:
            enviar_telegram(token, chat_id,
                            "✅ <b>Bot de empleos activado.</b>\n"
                            "A partir de ahora te avisaré cuando aparezcan "
                            "ofertas nuevas de Data / BI / Analytics.")
        except Exception as e:  # noqa
            print("No se pudo enviar el aviso de arranque:", e)
        print("Primera ejecución: se marcó el catálogo actual como base. No se envían ofertas.")
        return

    # 4) Enviar las nuevas (con tope y throttling)
    if config.MAX_ENVIOS_POR_RUN:
        nuevas = nuevas[:config.MAX_ENVIOS_POR_RUN]

    enviadas = 0
    for o in nuevas:
        try:
            enviar_telegram(token, chat_id, formatea(o))
            enviadas += 1
            vistos.add(job_id(o["url"]))
            time.sleep(1.2)  # respeta el límite de Telegram
        except Exception as e:  # noqa
            print("Error enviando '%s': %s" % (o["titulo"], e))

    guardar_vistos(vistos)
    print("Enviadas %d ofertas nuevas a Telegram." % enviadas)


if __name__ == "__main__":
    main()
