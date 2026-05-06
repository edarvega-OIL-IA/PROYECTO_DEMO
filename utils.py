import re
import json
from datetime import datetime

# ── Limpiar respuesta JSON de Claude ──
def limpiar_json(texto):
    texto = texto.replace("```json", "").replace("```", "").strip()
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None

# ── Limpiar SQL de Claude ──
def limpiar_sql(texto):
    texto = texto.replace("```sql", "").replace("```", "").strip()
    return texto

# ── Verificar stop_reason ──
def verificar_respuesta(response):
    if response.stop_reason == "max_tokens":
        return False, "Respuesta cortada — documento muy largo"
    return True, None

# ── Timestamp para nombres de archivo ──
def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# ── Separador visual ──
def separador(titulo=""):
    if titulo:
        print(f"\n{'─' * 20} {titulo} {'─' * 20}")
    else:
        print("─" * 50)