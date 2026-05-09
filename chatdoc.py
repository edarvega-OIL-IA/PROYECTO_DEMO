import anthropic
import fitz
import chromadb
import re
import os
import uuid
from datetime import datetime

client = anthropic.Anthropic()

# ── Inicializar ChromaDB en memoria ──
# En memoria significa que los documentos se guardan
# mientras dura la sesión — cuando se cierra la app se borran
chroma_client = chromadb.Client()

SYSTEM_CHATDOC = """
Sos un asistente especializado en responder preguntas sobre 
documentos de empresas de Oil & Gas en Vaca Muerta, Argentina.

TUS REGLAS:
- Respondés ÚNICAMENTE basándote en el contenido del documento proporcionado
- Si la respuesta no está en el documento, decís claramente: 
  'Esta información no está en el documento cargado'
- Siempre citás de qué parte del documento viene la respuesta
- Respondés en español rioplatense formal y de forma concisa
- Nunca inventás información que no esté en el documento
"""

def leer_pdf(ruta):
    """Lee un PDF y devuelve lista de fragmentos con número de página."""
    doc = fitz.open(ruta)
    fragmentos = []
    for i, pagina in enumerate(doc):
        texto = pagina.get_text()
        texto = texto.replace('\x00', '').strip()
        if len(texto) > 100:  # ignorar páginas vacías
            fragmentos.append({
                "pagina": i + 1,
                "texto": texto
            })
    doc.close()
    return fragmentos

def dividir_en_chunks(fragmentos, max_chars=1000):
    """Divide el texto en chunks más pequeños para mejor búsqueda."""
    chunks = []
    for frag in fragmentos:
        texto = frag["texto"]
        pagina = frag["pagina"]

        # Si el fragmento cabe en un chunk, agregarlo directo
        if len(texto) <= max_chars:
            chunks.append({
                "id": str(uuid.uuid4()),
                "texto": texto,
                "pagina": pagina
            })
        else:
            # Dividir por párrafos
            parrafos = texto.split('\n\n')
            chunk_actual = ""
            for parrafo in parrafos:
                if len(chunk_actual) + len(parrafo) <= max_chars:
                    chunk_actual += parrafo + "\n\n"
                else:
                    if chunk_actual.strip():
                        chunks.append({
                            "id": str(uuid.uuid4()),
                            "texto": chunk_actual.strip(),
                            "pagina": pagina
                        })
                    chunk_actual = parrafo + "\n\n"
            if chunk_actual.strip():
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "texto": chunk_actual.strip(),
                    "pagina": pagina
                })
    return chunks

def crear_coleccion(nombre_doc):
    """Crea una colección ChromaDB para el documento."""
    # Limpiar nombre para usarlo como ID
    nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '_', nombre_doc)[:50]
    nombre_coleccion = f"doc_{nombre_limpio}_{datetime.now().strftime('%H%M%S')}"
    return chroma_client.create_collection(name=nombre_coleccion)

def indexar_documento(ruta_pdf, nombre_archivo):
    """Lee, divide e indexa el PDF en ChromaDB."""
    print(f"  📄 Leyendo {nombre_archivo}...")
    fragmentos = leer_pdf(ruta_pdf)

    print(f"  ✂️  Dividiendo en chunks...")
    chunks = dividir_en_chunks(fragmentos)

    print(f"  🔍 Indexando {len(chunks)} fragmentos...")
    coleccion = crear_coleccion(nombre_archivo)

    # Agregar chunks a ChromaDB en lotes
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        coleccion.add(
            ids=[c["id"] for c in batch],
            documents=[c["texto"] for c in batch],
            metadatas=[{"pagina": c["pagina"]} for c in batch]
        )

    print(f"  ✅ Documento indexado — {len(chunks)} fragmentos en {len(fragmentos)} páginas")
    return coleccion, len(chunks), len(fragmentos)

def buscar_fragmentos_relevantes(coleccion, pregunta, n_resultados=5):
    """Busca los fragmentos más relevantes para la pregunta."""
    resultados = coleccion.query(
        query_texts=[pregunta],
        n_results=min(n_resultados, coleccion.count())
    )
    fragmentos = []
    if resultados and resultados["documents"]:
        for doc, meta in zip(
            resultados["documents"][0],
            resultados["metadatas"][0]
        ):
            fragmentos.append({
                "texto": doc,
                "pagina": meta.get("pagina", "?")
            })
    return fragmentos

def responder_pregunta(coleccion, pregunta, nombre_doc, historial):
    """Busca fragmentos relevantes y genera respuesta con Claude."""

    # Buscar fragmentos relevantes
    fragmentos = buscar_fragmentos_relevantes(coleccion, pregunta)

    if not fragmentos:
        return "No encontré información relevante en el documento para responder esa pregunta."

    # Armar contexto con los fragmentos encontrados
    contexto = ""
    paginas_usadas = []
    for i, frag in enumerate(fragmentos):
        contexto += f"\n--- Fragmento {i+1} (Página {frag['pagina']}) ---\n"
        contexto += frag["texto"] + "\n"
        paginas_usadas.append(str(frag["pagina"]))

    # Prompt con contexto
    prompt_con_contexto = f"""
<documento nombre="{nombre_doc}">
{contexto}
</documento>

<pregunta>
{pregunta}
</pregunta>

<instruccion>
Respondé la pregunta basándote EXCLUSIVAMENTE en el contenido 
del documento mostrado arriba.
Al final de tu respuesta indicá: "📄 Fuente: páginas {', '.join(set(paginas_usadas))}"
Si la información no está en los fragmentos mostrados, decilo claramente.
</instruccion>
"""

    # Agregar al historial
    historial.append({"role": "user", "content": prompt_con_contexto})

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        temperature=0,
        system=SYSTEM_CHATDOC,
        messages=historial
    )

    respuesta = response.content[0].text

    # Guardar en historial solo la pregunta original (no el contexto)
    historial[-1] = {"role": "user", "content": pregunta}
    historial.append({"role": "assistant", "content": respuesta})

    return respuesta