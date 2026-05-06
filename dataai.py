import anthropic
import sqlite3
from prompts import DATAAI_SYSTEM, DATAAI_INTERPRETE, prompt_interpreta_sql
from utils import limpiar_sql, separador

client = anthropic.Anthropic()

DB_PATH = r"E:\PERSONAL\2026_TRABAJO\ASESOR_IA\SEMANA_05\pozos_vaca_muerta.db"

SCHEMA = """
Base de datos SQLite de operaciones petroleras en Vaca Muerta.

TABLA: pozos
  - id_pozo TEXT (PK): identificador único. Ej: VM-YPF-001
  - nombre TEXT: nombre del pozo
  - operadora TEXT: YPF, Shell, TotalEnergies, Pampa Energía, Vista Oil & Gas
  - cuenca TEXT: Loma Campana, Aguada Pichana, Bajada del Palo, Sierra Chata
  - fecha_inicio DATE: fecha de inicio de producción (YYYY-MM-DD)
  - profundidad_m INTEGER: profundidad en metros
  - tipo TEXT: Productor shale oil, Productor shale gas, Inyector
  - estado TEXT: Activo, Suspendido

TABLA: produccion
  - id INTEGER (PK)
  - id_pozo TEXT (FK → pozos.id_pozo)
  - fecha DATE: fecha del registro (YYYY-MM-DD)
  - produccion_bbl REAL: producción diaria en barriles
  - gas_mpc REAL: producción de gas en miles de pies cúbicos
  - agua_bbl REAL: producción de agua en barriles
  - presion_psi REAL: presión del pozo en PSI
  - horas_operacion REAL: horas operativas en el día

TABLA: incidentes_hse
  - id INTEGER (PK)
  - id_pozo TEXT (FK → pozos.id_pozo)
  - fecha DATE: fecha del incidente (YYYY-MM-DD)
  - tipo TEXT: Near Miss, Primeros auxilios, Derrame menor,
               Falla de equipo, Condición insegura
  - descripcion TEXT: descripción del incidente
  - horas_perdidas REAL: horas de producción perdidas
  - severidad TEXT: Bajo, Medio, Alto
"""

# ── Ejecutar SQL ──
def ejecutar_sql(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        columnas = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()
        conn.close()
        return {"exitoso": True, "columnas": columnas, "filas": filas}
    except Exception as e:
        return {"exitoso": False, "error": str(e)}


# ── Generar SQL ──
def generar_sql(pregunta):
    system_con_schema = DATAAI_SYSTEM + f"\n\nSCHEMA DE LA BASE DE DATOS:\n{SCHEMA}"
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=system_con_schema,
            messages=[{"role": "user", "content": pregunta}]
        )
        return limpiar_sql(response.content[0].text)
    except Exception as e:
        return f"ERROR: {str(e)}"



# ── Interpretar resultado ──
def interpretar_resultado(pregunta, sql, columnas, filas):
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=DATAAI_INTERPRETE,
            messages=[{"role": "user", "content":
                      prompt_interpreta_sql(pregunta, sql, columnas, filas)}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"❌ Error al interpretar resultado: {str(e)}"


# ── Procesar una pregunta ──
def procesar_pregunta(pregunta):
    print("\n⚙️  Generando consulta SQL...")
    sql = generar_sql(pregunta)

    if sql.startswith("ERROR:"):
        print(f"\n❌ {sql}")
        separador()
        return

    print(f"   SQL:\n{sql}\n")

    print("🔍 Consultando base de datos...")
    resultado = ejecutar_sql(sql)

    if not resultado["exitoso"]:
        print(f"\n❌ Error en la consulta: {resultado['error']}")
        print("   Intentá reformular la pregunta.")
        separador()
        return

    filas = resultado["filas"]
    if not filas:
        print("\n📭 No se encontraron datos para esa consulta.")
        separador()
        return

    print(f"   {len(filas)} registro(s) encontrado(s)")
    print("\n🤖 DataAI:")
    respuesta = interpretar_resultado(
        pregunta, sql, resultado["columnas"], filas
    )
    print(respuesta)
    separador()

# ── Loop de conversación ──
def iniciar():
    print("=== DataAI — Asistente de datos de Vaca Muerta ===")
    print("Hacé preguntas sobre pozos, producción e incidentes HSE.")
    separador()
    print("💡 Ejemplos:")
    print("   ¿Cuáles son los 5 pozos con mayor producción?")
    print("   ¿Cuántos incidentes HSE tuvimos este mes?")
    print("   ¿Qué operadora produce más en promedio?")
    separador()

    while True:
        pregunta = input("\n📝 Tu consulta: ").strip()

        if pregunta.lower() == "salir":
            print("\n✅ Sesión finalizada.")
            break

        if not pregunta:
            print("⚠️  Escribí una pregunta o 'salir' para terminar.")
            continue

        procesar_pregunta(pregunta)