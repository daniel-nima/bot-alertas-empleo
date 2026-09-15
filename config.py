# -*- coding: utf-8 -*-
"""
Configuración del bot de alertas de empleo.
Ajusta aquí las palabras clave, países y filtros sin tocar el código principal.
"""

# ----------------------------------------------------------------------
# 1) Palabras clave del PUESTO que te interesan (en inglés y español).
#    Una oferta pasa el filtro si su título contiene AL MENOS una de estas.
#    Están en minúscula: la comparación ignora mayúsculas/acentos básicos.
# ----------------------------------------------------------------------
KEYWORDS_PUESTO = [
    "data analyst", "data analytics", "data science", "data scientist",
    "business intelligence", "bi analyst", "bi developer",
    "analytics engineer", "data engineer",
    "power bi", "tableau", "looker",
    "sql", "python",
    # Español
    "analista de datos", "analista de negocio", "analista bi",
    "inteligencia de negocios", "ingeniero de datos", "científico de datos",
    "analista de información", "practicante de datos",
]

# ----------------------------------------------------------------------
# 2) Palabras que, si aparecen en el título, DESCARTAN la oferta
#    (para no recibir puestos senior o que no aplican a un practicante/junior).
#    Deja la lista vacía [] si quieres ver absolutamente todo.
# ----------------------------------------------------------------------
EXCLUIR_TITULO = [
    "senior", "sr.", "staff", "principal", "lead", "manager", "head of",
    "director", "vp ", "10+ years", "8+ years",
]

# ----------------------------------------------------------------------
# 3) Términos de búsqueda que se envían a las APIs que aceptan búsqueda.
#    (Remotive y Jobicy filtran del lado del servidor con estos).
# ----------------------------------------------------------------------
TERMINOS_BUSQUEDA = ["data", "business intelligence", "analytics", "sql"]

# ----------------------------------------------------------------------
# 4) ¿Cuántos IDs de ofertas ya vistas conservar? (evita que crezca infinito)
# ----------------------------------------------------------------------
MAX_VISTOS = 3000

# ----------------------------------------------------------------------
# 5) ¿Cuántas ofertas nuevas enviar como máximo por ejecución?
#    (protege contra un aluvión el primer día). None = sin límite.
# ----------------------------------------------------------------------
MAX_ENVIOS_POR_RUN = 40

# Archivo donde se guardan los IDs ya notificados
ARCHIVO_VISTOS = "seen_jobs.json"
