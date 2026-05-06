import os
import sys
from utils import separador, timestamp
import contractai
import dataai

# ── Menú principal ──
def mostrar_menu():
    print("\n╔══════════════════════════════════════════╗")
    print("║     OilAI — Asistente para Vaca Muerta   ║")
    print("╠══════════════════════════════════════════╣")
    print("║  1. ContractAI — Analizar contrato       ║")
    print("║  2. DataAI     — Consultar datos         ║")
    print("║  3. Salir                                ║")
    print("╚══════════════════════════════════════════╝")

def opcion_contractai():
    separador("ContractAI")
    ruta = input("\n📄 Ruta del PDF a analizar:\n> ").strip()
    ruta = ruta.strip('"')

    if not os.path.exists(ruta):
        print(f"\n❌ Archivo no encontrado: {ruta}")
        return

    datos = contractai.analizar_contrato(ruta)

    if not datos:
        print("\n❌ No se pudo analizar el contrato.")
        return

    contractai.mostrar_resultado(datos)

    print("\n💾 ¿Generar reporte Word? (s/n): ", end="")
    if input().strip().lower() == "s":
        carpeta = os.path.dirname(ruta)
        if not carpeta:
            carpeta = "."
        nombre = f"reporte_contractai_{timestamp()}.docx"
        ruta_reporte = os.path.join(carpeta, nombre)
        try:
            contractai.generar_reporte(datos, ruta_reporte)
        except Exception as e:
            print(f"  ❌ No se pudo guardar el reporte: {e}")
            print("  💡 Verificá que tengas permisos de escritura en esa carpeta.")

def opcion_dataai():
    dataai.iniciar()

# ── MAIN ──
def main():
    print("\n  Iniciando OilAI...")
    print("  Verificando conexión con Anthropic API...")

    # Verificar API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ ERROR: ANTHROPIC_API_KEY no configurada.")
        print("   Ejecutá: setx ANTHROPIC_API_KEY 'tu-clave'")
        sys.exit(1)

    print("  ✅ API key detectada\n")

    while True:
        mostrar_menu()
        opcion = input("\n  Elegí una opción (1-3): ").strip()

        if opcion == "1":
            opcion_contractai()
        elif opcion == "2":
            opcion_dataai()
        elif opcion == "3":
            print("\n  Hasta la próxima. 👋\n")
            break
        else:
            print("\n  ⚠️  Opción inválida. Elegí 1, 2 o 3.")

if __name__ == "__main__":
    main()