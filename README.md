# 🤖 Bot de Alertas de Empleo (Data / BI / Analytics) → Telegram

Bot que **cada 3 horas** busca ofertas de empleo remoto/internacional en varias
plataformas, filtra las que te interesan (Data, Business Intelligence, Analytics,
SQL, Python…) y te envía **solo las nuevas** por Telegram. Corre solo en la nube
con **GitHub Actions** — no necesitas tener tu computadora encendida.

> Proyecto de automatización con Python. Sin dependencias externas (solo librería estándar).

---

## ✨ Qué hace

- Consulta 4 APIs **gratuitas y legales** de empleo remoto:
  [Remotive](https://remotive.com), [Jobicy](https://jobicy.com),
  [Arbeitnow](https://www.arbeitnow.com) (Europa) y [RemoteOK](https://remoteok.com).
- Filtra por **palabras clave del puesto** y descarta seniors/managers (configurable).
- Recuerda lo que ya te avisó (`seen_jobs.json`) para **no repetir** ofertas.
- Te manda cada oferta nueva a Telegram con título, empresa, ubicación y enlace.

---

## 🚀 Puesta en marcha (10 minutos, una sola vez)

### Paso 1 — Crea tu bot de Telegram
1. En Telegram, busca **@BotFather** y escríbele `/newbot`.
2. Ponle un nombre y un usuario (debe terminar en `bot`, p. ej. `nima_empleos_bot`).
3. BotFather te dará un **token** parecido a `123456789:AAExxxxxxxxxxxxxxxxxxx`.
   Guárdalo — es tu `TELEGRAM_TOKEN`.

### Paso 2 — Obtén tu Chat ID
1. Abre tu nuevo bot y pulsa **Start** (o escríbele cualquier cosa).
2. Busca **@userinfobot** en Telegram y escríbele `/start`: te dirá tu **Id**
   (un número como `987654321`). Ese es tu `TELEGRAM_CHAT_ID`.

### Paso 3 — Sube este proyecto a un repositorio de GitHub
Crea un repo nuevo (p. ej. `bot-alertas-empleo`) y sube estos archivos.

### Paso 4 — Agrega los secretos en GitHub
En tu repo: **Settings → Secrets and variables → Actions → New repository secret**
y crea estos dos:

| Nombre | Valor |
|---|---|
| `TELEGRAM_TOKEN` | el token del Paso 1 |
| `TELEGRAM_CHAT_ID` | el número del Paso 2 |

### Paso 5 — Enciende el bot
1. Ve a la pestaña **Actions** del repo y activa los workflows si te lo pide.
2. Abre **“Alertas de empleo” → Run workflow** para probarlo al instante.
3. La **primera ejecución** solo guarda el catálogo actual como base y te manda un
   mensaje de *“Bot activado”* (así no te llegan 200 avisos de golpe).
   A partir de ahí, cada 3 horas recibirás **solo las ofertas nuevas**. ✅

---

## ⚙️ Personalización

Todo se ajusta en **`config.py`**, sin tocar el código:

- `KEYWORDS_PUESTO` — los puestos que te interesan (agrega/quita libremente).
- `EXCLUIR_TITULO` — palabras que descartan una oferta (senior, manager…).
- `TERMINOS_BUSQUEDA` — qué se le pide a las APIs que aceptan búsqueda.
- `MAX_ENVIOS_POR_RUN` — tope de avisos por ejecución.

Para cambiar la frecuencia, edita el `cron` en
`.github/workflows/job-alerts.yml` (`0 */3 * * *` = cada 3 horas).

---

## 🇵🇪 ¿Y Computrabajo, Bumeran, LinkedIn, Indeed?

Estas plataformas **no ofrecen una API pública gratuita** y su *scraping* va contra
sus Términos de Uso (además bloquean IPs y cambian el HTML seguido, así que un bot
así se rompe cada poco). La forma **estable y recomendada** de cubrirlas es usar sus
**alertas nativas por correo**, que hacen exactamente esto de forma oficial:

1. Crea tu cuenta en cada portal.
2. Haz la búsqueda (ej. *“analista de datos”*, Lima / remoto).
3. Guarda la búsqueda y **activa la alerta por email** (diaria o instantánea).

Así este bot te cubre el mercado **remoto e internacional** (tu prioridad) de forma
automática y confiable, y las alertas nativas te cubren el mercado **local**.

---

## 🧱 Estructura

```
job_alert_bot.py              # lógica principal
config.py                     # keywords y ajustes
requirements.txt              # (sin dependencias externas)
seen_jobs.json                # se crea solo: ofertas ya notificadas
.github/workflows/job-alerts.yml   # automatización (GitHub Actions)
```

## 🛠️ Ejecutar en local (opcional, para probar)

```bash
export TELEGRAM_TOKEN="tu_token"
export TELEGRAM_CHAT_ID="tu_chat_id"
python job_alert_bot.py
```

---

Hecho por **Daniel Nima** · [github.com/daniel-nima](https://github.com/daniel-nima)
