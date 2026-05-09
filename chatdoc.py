import anthropic
import fitz
import re
from datetime import datetime

client = anthropic.Anthropic()

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
    paginas = []
    for i, pagina in enumerate(doc):
        texto = pagina.get_text()
        texto = texto.replace('\x00', '').strip()
        if len(texto) > 50:
            paginas.append({
                "pagina": i + 1,
                "texto": texto
            })
    doc.close()
    return paginas

def dividir_en_chunks(paginas, max_chars=1500):
    """Divide el texto en chunks para búsqueda."""
    chunks = []
    for pag in paginas:
        texto = pag["texto"]
        pagina = pag["pagina"]
        if len(texto) <= max_chars:
            chunks.append({"texto": texto, "pagina": pagina})
        else:
            partes = [texto[i:i+max_chars] for i in range(0, len(texto), max_chars)]
            for parte in partes:
                if parte.strip():
                    chunks.append({"texto": parte, "pagina": pagina})
    return chunks

def buscar_chunks_relevantes(chunks, pregunta, n=6):
    """
    Búsqueda simple por palabras clave.
    Sin vectores ni embeddings — funciona en cualquier entorno.
    """
    pregunta_lower = pregunta.lower()
    palabras = [p for p in pregunta_lower.split() if len(p) > 3]

    scored = []
    for chunk in chunks:
        texto_lower = chunk["texto"].lower()
        score = sum(1 for p in palabras if p in texto_lower)
        if score > 0:
            scored.append((score, chunk))

    # Ordenar por relevancia y tomar los mejores
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:n]]

def indexar_documento(ruta_pdf, nombre_archivo):
    """Lee y prepara el documento para consultas."""
    paginas = leer_pdf(ruta_pdf)
    chunks = dividir_en_chunks(paginas)
    return chunks, len(chunks), len(paginas)

def responder_pregunta(chunks, pregunta, nombre_doc, historial):
    """Busca fragmentos relevantes y genera respuesta con Claude."""

    fragmentos_relevantes = buscar_chunks_relevantes(chunks, pregunta)

    # Si no encuentra por palabras clave, tomar los primeros chunks
    if not fragmentos_relevantes:
        fragmentos_relevantes = chunks[:6]

    # Armar contexto
    contexto = ""
    paginas_usadas = []
    for i, frag in enumerate(fragmentos_relevantes):
        contexto += f"\n--- Sección {i+1} (Página {frag['pagina']}) ---\n"
        contexto += frag["texto"] + "\n"
        paginas_usadas.append(str(frag["pagina"]))

    prompt = f"""
<documento nombre="{nombre_doc}">
{contexto}
</documento>

<pregunta>
{pregunta}
</pregunta>

<instruccion>
Respondé la pregunta basándote EXCLUSIVAMENTE en el contenido 
del documento mostrado arriba.
Al final indicá: "📄 Fuente: páginas {', '.join(set(paginas_usadas))}"
Si la información no está en los fragmentos, decilo claramente.
</instruccion>
"""

    historial.append({"role": "user", "content": prompt})

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        temperature=0,
        system=SYSTEM_CHATDOC,
        messages=historial
    )

    respuesta = response.content[0].text

    # Guardar en historial la pregunta original, no el prompt completo
    historial[-1] = {"role": "user", "content": pregunta}
    historial.append({"role": "assistant", "content": respuesta})

    return respuesta