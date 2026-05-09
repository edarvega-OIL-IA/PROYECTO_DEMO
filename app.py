import streamlit as st
import os
import tempfile
import pandas as pd
import contractai
import dataai
import hseai
import hseai_v2
import licitaciones as licitai
import chatdoc
from utils import timestamp

# ── Configuración ──
st.set_page_config(
    page_title="OilAI — Asistente para Vaca Muerta",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ── Estilos ──
st.markdown("""
<style>
    .stApp { background-color: #0F1923; }

    .main-header {
        background: linear-gradient(135deg, #1A3A5C 0%, #0F1923 60%, #1A2A1A 100%);
        border-bottom: 2px solid #2A6496;
        padding: 2rem 2rem 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
    }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #FFFFFF; letter-spacing: 0.05em; margin: 0; }
    .main-title span { color: #4A9FD4; }
    .main-subtitle { font-size: 1rem; color: #8AABB8; margin-top: 0.4rem; letter-spacing: 0.08em; text-transform: uppercase; }
    .main-badge { display: inline-block; background: #1E4D2B; color: #5DCB7A; font-size: 0.75rem; padding: 3px 12px; border-radius: 20px; margin-top: 0.5rem; border: 1px solid #2A7A40; letter-spacing: 0.05em; }

    .metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 1.5rem; }
    .metric-card { background: #162330; border: 1px solid #1E3A50; border-radius: 10px; padding: 1rem 1.25rem; text-align: center; border-top: 3px solid #2A6496; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #FFFFFF; margin: 0; }
    .metric-label { font-size: 0.75rem; color: #7A9BB0; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 4px; }
    .metric-delta-up { font-size: 0.75rem; color: #5DCB7A; margin-top: 4px; }
    .metric-delta-neutral { font-size: 0.75rem; color: #4A9FD4; margin-top: 4px; }

    .stTabs [data-baseweb="tab-list"] { background: #162330; border-radius: 10px; padding: 4px; gap: 4px; border: 1px solid #1E3A50; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #7A9BB0; border-radius: 8px; padding: 8px 16px; font-size: 0.85rem; font-weight: 500; }
    .stTabs [aria-selected="true"] { background: #1A3A5C !important; color: #FFFFFF !important; }

    .stMarkdown, .stText, p, label { color: #C8D8E4 !important; }
    h1, h2, h3 { color: #FFFFFF !important; }

    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #2A6496, #1A4A7A); color: white; border: none; border-radius: 8px; padding: 0.5rem 1.5rem; font-weight: 600; }
    .stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #3A74A6, #2A5A8A); }

    .stFileUploader { background: #162330 !important; border: 2px dashed #2A6496 !important; border-radius: 10px !important; }

    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #7A9BB0 !important; }
    [data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

    hr { border-color: #1E3A50 !important; }

    .footer { text-align: center; color: #3A5A70; font-size: 0.75rem; padding: 1rem 0; border-top: 1px solid #1E3A50; margin-top: 2rem; letter-spacing: 0.05em; }

    .streamlit-expanderHeader { background: #162330 !important; color: #C8D8E4 !important; border: 1px solid #1E3A50 !important; border-radius: 8px !important; }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea { background: #162330 !important; color: #FFFFFF !important; border: 1px solid #2A6496 !important; border-radius: 8px !important; }

    .stSuccess { background: #1A2E1A !important; border-left: 4px solid #5DCB7A !important; }
    .stError { background: #2E1A1A !important; border-left: 4px solid #E05C5C !important; }
    .stWarning { background: #2E2A1A !important; border-left: 4px solid #F0A500 !important; }
    .stInfo { background: #1A2A3A !important; border-left: 4px solid #4A9FD4 !important; }

    [data-testid="stDataFrame"] { background: #162330 !important; }
    .stSpinner > div { border-top-color: #4A9FD4 !important; }
    .stProgress > div > div { background: #2A6496 !important; }
    [data-testid="stSidebar"] { display: none; }

    /* ── Evitar traducción automática ── */
    .main-header, .main-title, .main-subtitle, .main-badge {
        -webkit-user-select: none;
    }
    [translate="no"] { translate: no; }


</style>
""", unsafe_allow_html=True)




# ── Header ──
st.markdown("""
<div class="main-header" translate="no" lang="en">
    <div class="main-title">🛢️ Oil<span>AI</span></div>
    <div class="main-subtitle" translate="no">
        INTELIGENCIA ARTIFICIAL PARA OIL &amp; GAS · VACA MUERTA, NEUQUÉN
    </div>
    <div class="main-badge" translate="no">⚡ Eduardo Ariel Vega by Claude AI</div>
</div>
""", unsafe_allow_html=True)



# ── API Key ──
if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("❌ ANTHROPIC_API_KEY no configurada.")
    st.stop()

# ── Métricas ──
st.markdown("""
<div class="metrics-row">
    <div class="metric-card">
        <div class="metric-value">127</div>
        <div class="metric-label">Contratos analizados</div>
        <div class="metric-delta-up">↑ 12 esta semana</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">843</div>
        <div class="metric-label">Cláusulas problemáticas</div>
        <div class="metric-delta-up">↑ 67 esta semana</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">28 seg</div>
        <div class="metric-label">Tiempo promedio análisis</div>
        <div class="metric-delta-neutral">↓ 3 seg vs mes anterior</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">14</div>
        <div class="metric-label">Empresas usuarias</div>
        <div class="metric-delta-up">↑ 2 nuevas este mes</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Tabs ──
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📄 ContractAI — Análisis de contratos",
    "📊 DataAI — Consulta de datos",
    "🦺 HSE — Reporte de incidentes",
    "🏆 Licitaciones — Comparador",
    "💬 ChatDoc — Chat con documentos",
    "🦺 HSE Pro — Formato Shell/Peduzzi"
])

# ════════════════════════════════════════
# TAB 1: ContractAI
# ════════════════════════════════════════
with tab1:
    st.subheader("Analizá contratos y licitaciones de Oil & Gas")
    st.caption("Subí un PDF y ContractAI identificará riesgos, obligaciones y recomendaciones.")

    pdf_file = st.file_uploader(
        "Seleccioná el contrato en PDF",
        type=["pdf"],
        help="Contratos, licitaciones, pliegos de condiciones"
    )

    if pdf_file is not None:
        st.info(f"📄 Archivo cargado: **{pdf_file.name}** ({pdf_file.size:,} bytes)")
        analizar = st.button("🔍 Analizar contrato", type="primary")

        if analizar:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_file.read())
                ruta_tmp = tmp.name

            try:
                with st.spinner("🤖 ContractAI analizando el contrato..."):
                    datos = contractai.analizar_contrato(ruta_tmp)

                if not datos:
                    st.error("❌ No se pudo analizar el contrato.")
                else:
                    st.divider()
                    col1, col2, col3 = st.columns(3)
                    riesgo = datos.get("riesgo_general", "—").upper()
                    firmar = datos.get("firmar", False)
                    with col1:
                        st.metric("Riesgo general", riesgo)
                    with col2:
                        st.metric("Decisión", "✅ Firmar" if firmar else "❌ No firmar")
                    with col3:
                        st.metric("Tipo", datos.get("tipo_documento", "—"))

                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Contratante:**")
                        st.write(datos.get("partes", {}).get("contratante", "—"))
                    with col2:
                        st.markdown("**Contratista:**")
                        st.write(datos.get("partes", {}).get("contratista", "—"))

                    st.divider()
                    st.subheader("📋 Resumen ejecutivo")
                    st.write(datos.get("resumen", "—"))

                    st.divider()
                    st.subheader("⚠️ Puntos críticos")
                    for punto in datos.get("puntos_criticos", []):
                        st.markdown(f"• {punto}")

                    st.divider()
                    st.subheader("✅ Recomendaciones")
                    for rec in datos.get("recomendaciones", []):
                        st.markdown(f"• {rec}")

                    st.divider()
                    nombre = f"reporte_contractai_{timestamp()}.docx"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
                        ruta_reporte = tmp_docx.name
                    contractai.generar_reporte(datos, ruta_reporte)
                    with open(ruta_reporte, "rb") as f:
                        contenido = f.read()
                    st.download_button(
                        label="💾 Descargar reporte Word",
                        data=contenido,
                        file_name=nombre,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            finally:
                os.unlink(ruta_tmp)

# ════════════════════════════════════════
# TAB 2: DataAI
# ════════════════════════════════════════
with tab2:
    st.subheader("Consultá datos de pozos en lenguaje natural")
    st.caption("Hacé preguntas sobre producción, incidentes HSE y operaciones.")

    st.markdown("**💡 Ejemplos de consultas:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("5 pozos con mayor producción", use_container_width=True):
            st.session_state.pregunta_data = "¿Cuáles son los 5 pozos con mayor producción promedio?"
            st.rerun()
    with col2:
        if st.button("Incidentes HSE graves", use_container_width=True):
            st.session_state.pregunta_data = "¿Cuántos incidentes HSE de severidad alta hubo este mes?"
            st.rerun()
    with col3:
        if st.button("Producción por operadora", use_container_width=True):
            st.session_state.pregunta_data = "¿Qué operadora tiene mayor producción promedio?"
            st.rerun()

    if "pregunta_data" not in st.session_state:
        st.session_state.pregunta_data = ""

    pregunta = st.text_input(
        "Escribí tu consulta:",
        value=st.session_state.pregunta_data,
        placeholder="¿Cuántos pozos activos tiene YPF?"
    )

    if pregunta != st.session_state.pregunta_data:
        st.session_state.pregunta_data = pregunta

    if st.button("🔍 Consultar", type="primary") and st.session_state.pregunta_data:
        pregunta = st.session_state.pregunta_data
        with st.spinner("⚙️ Generando consulta y buscando datos..."):
            sql = dataai.generar_sql(pregunta)

            if sql.startswith("ERROR:"):
                st.error(f"❌ {sql}")
            else:
                with st.expander("🔧 Ver consulta SQL generada"):
                    st.code(sql, language="sql")

                resultado = dataai.ejecutar_sql(sql)

                if not resultado["exitoso"]:
                    st.error(f"❌ Error: {resultado['error']}")
                    st.info("💡 Intentá reformular la pregunta.")
                elif not resultado["filas"]:
                    st.warning("📭 No se encontraron datos.")
                else:
                    respuesta = dataai.interpretar_resultado(
                        pregunta, sql,
                        resultado["columnas"],
                        resultado["filas"]
                    )
                    st.success("🤖 **DataAI:**")
                    st.write(respuesta)

                    with st.expander(f"📊 Ver datos crudos ({len(resultado['filas'])} registros)"):
                        df = pd.DataFrame(
                            resultado["filas"],
                            columns=resultado["columnas"]
                        )
                        st.dataframe(df, use_container_width=True)

    if st.button("🗑️ Limpiar"):
        st.session_state.pregunta_data = ""
        st.rerun()

# ════════════════════════════════════════
# TAB 3: HSE
# ════════════════════════════════════════
with tab3:
    st.subheader("Generador de reportes HSE")
    st.caption("Describí el incidente en lenguaje natural y el sistema genera el reporte formal automáticamente.")

    if "hse_descripcion" not in st.session_state:
        st.session_state.hse_descripcion = ""
    if "hse_preguntas" not in st.session_state:
        st.session_state.hse_preguntas = []
    if "hse_respuestas" not in st.session_state:
        st.session_state.hse_respuestas = {}
    if "hse_etapa" not in st.session_state:
        st.session_state.hse_etapa = "descripcion"
    if "hse_datos" not in st.session_state:
        st.session_state.hse_datos = None

    if st.session_state.hse_etapa == "descripcion":
        st.markdown("**📝 Descripción del evento:**")
        descripcion = st.text_area(
            "Describí lo que ocurrió:",
            placeholder="Ej: Hoy a las 14:30 en el pad 5, un operario resbaló cerca del flowback tank...",
            height=120
        )
        if st.button("➡️ Continuar", type="primary") and descripcion:
            st.session_state.hse_descripcion = descripcion
            with st.spinner("🔍 Analizando información disponible..."):
                analisis = hseai.detectar_info_faltante(descripcion)
            if analisis and not analisis.get("suficiente_para_reporte", True):
                faltantes = [
                    f for f in analisis.get("informacion_faltante", [])
                    if f.get("obligatorio", False)
                ][:5]
                if faltantes:
                    st.session_state.hse_preguntas = faltantes
                    st.session_state.hse_etapa = "preguntas"
                    st.rerun()
                else:
                    st.session_state.hse_etapa = "generar"
                    st.rerun()
            else:
                st.session_state.hse_etapa = "generar"
                st.rerun()

    elif st.session_state.hse_etapa == "preguntas":
        st.info(f"📋 Descripción recibida. Necesito {len(st.session_state.hse_preguntas)} dato(s) adicional(es):")
        st.divider()
        with st.form("form_preguntas_hse"):
            respuestas_form = {}
            for i, item in enumerate(st.session_state.hse_preguntas):
                respuestas_form[item["campo"]] = st.text_input(
                    f"❓ {item['pregunta']}",
                    key=f"hse_q_{i}"
                )
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.form_submit_button("🤖 Generar reporte", type="primary"):
                    st.session_state.hse_respuestas = respuestas_form
                    st.session_state.hse_etapa = "generar"
                    st.rerun()
            with col2:
                if st.form_submit_button("↩️ Volver a describir"):
                    st.session_state.hse_etapa = "descripcion"
                    st.session_state.hse_preguntas = []
                    st.rerun()

    elif st.session_state.hse_etapa == "generar":
        descripcion_completa = st.session_state.hse_descripcion
        if st.session_state.hse_respuestas:
            adicionales = "\n".join([
                f"{campo}: {valor}"
                for campo, valor in st.session_state.hse_respuestas.items()
                if valor
            ])
            if adicionales:
                descripcion_completa += f"\n\nInformación adicional:\n{adicionales}"
        with st.spinner("🤖 Generando reporte HSE formal..."):
            datos = hseai.generar_reporte_hse(descripcion_completa)
        if not datos:
            st.error("❌ No se pudo generar el reporte. Intentá de nuevo.")
            if st.button("↩️ Volver"):
                st.session_state.hse_etapa = "descripcion"
                st.rerun()
        else:
            st.session_state.hse_datos = datos
            st.session_state.hse_etapa = "resultado"
            st.rerun()

    elif st.session_state.hse_etapa == "resultado":
        datos = st.session_state.hse_datos
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tipo", datos.get("tipo_incidente", "—"))
        with col2:
            st.metric("Severidad", datos.get("severidad", "—"))
        with col3:
            investiga = datos.get("requiere_investigacion_formal", False)
            st.metric("Investigación", "⚠️ Requerida" if investiga else "✅ No requerida")

        st.divider()
        st.markdown(f"**N° Reporte:** {datos.get('numero_reporte', '—')}")
        st.markdown(f"**Fecha:** {datos.get('fecha_hora', '—')}")

        st.divider()
        st.subheader("📋 Descripción formal")
        st.write(datos.get("descripcion_formal", "—"))

        st.divider()
        st.subheader("🔍 Análisis de causas")
        st.markdown(f"**Causa inmediata:** {datos.get('causa_inmediata', '—')}")
        st.markdown(f"**Causa raíz:** {datos.get('causa_raiz', '—')}")

        cinco = datos.get("cinco_porques", [])
        if any(cinco):
            with st.expander("Ver análisis 5 Por Qués"):
                for i, porque in enumerate(cinco):
                    if porque:
                        st.markdown(f"**¿Por qué {i+1}?** {porque}")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Acciones correctivas")
            for ac in datos.get("acciones_correctivas", []):
                st.markdown(f"• **{ac.get('accion', '—')}**")
                st.caption(f"  Responsable: {ac.get('responsable', '—')} | Plazo: {ac.get('plazo', '—')}")
        with col2:
            st.subheader("🛡️ Acciones preventivas")
            for ap in datos.get("acciones_preventivas", []):
                st.markdown(f"• **{ap.get('accion', '—')}**")
                st.caption(f"  Responsable: {ap.get('responsable', '—')} | Plazo: {ap.get('plazo', '—')}")

        st.divider()
        st.subheader("💡 Lecciones aprendidas")
        st.write(datos.get("lecciones_aprendidas", "—"))

        st.divider()
        nombre_word = f"reporte_hse_{timestamp()}.docx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            ruta_tmp = tmp.name
        hseai.generar_word_hse(datos, ruta_tmp)
        with open(ruta_tmp, "rb") as f:
            contenido = f.read()
        st.download_button(
            label="💾 Descargar reporte Word",
            data=contenido,
            file_name=nombre_word,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        st.divider()
        if st.button("➕ Generar nuevo reporte"):
            st.session_state.hse_etapa = "descripcion"
            st.session_state.hse_descripcion = ""
            st.session_state.hse_preguntas = []
            st.session_state.hse_respuestas = {}
            st.session_state.hse_datos = None
            st.rerun()

# ════════════════════════════════════════
# TAB 4: Licitaciones
# ════════════════════════════════════════
with tab4:
    st.subheader("Comparador de licitaciones Oil & Gas")
    st.caption("Subí 2 o más pliegos en PDF y el sistema te dice cuál conviene más presentar.")

    pdfs_licitaciones = st.file_uploader(
        "Seleccioná los pliegos a comparar (mínimo 2)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Podés subir hasta 5 licitaciones para comparar"
    )

    if pdfs_licitaciones:
        st.info(f"📄 {len(pdfs_licitaciones)} archivo(s) cargado(s): "
                f"{', '.join([f.name for f in pdfs_licitaciones])}")

        if len(pdfs_licitaciones) < 2:
            st.warning("⚠️ Necesitás subir al menos 2 licitaciones para comparar.")
        else:
            if st.button("🏆 Comparar licitaciones", type="primary"):
                analisis_lista = []
                errores = []
                progress = st.progress(0)

                for i, pdf_file in enumerate(pdfs_licitaciones):
                    with st.spinner(f"Analizando {pdf_file.name}..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(pdf_file.read())
                            ruta_tmp = tmp.name
                        try:
                            texto = licitai.leer_pdf(ruta_tmp)
                            analisis = licitai.analizar_licitacion(texto, pdf_file.name)
                            if analisis:
                                analisis_lista.append(analisis)
                            else:
                                errores.append(pdf_file.name)
                        finally:
                            os.unlink(ruta_tmp)
                    progress.progress((i + 1) / len(pdfs_licitaciones))

                if errores:
                    st.error(f"❌ No se pudo analizar: {', '.join(errores)}")

                if len(analisis_lista) >= 2:
                    with st.spinner("🏆 Generando ranking comparativo..."):
                        comparacion = licitai.comparar_licitaciones(analisis_lista)

                    if not comparacion:
                        st.error("❌ No se pudo generar el ranking.")
                    else:
                        st.divider()
                        st.subheader("🏆 Ranking de licitaciones")

                        medallas = {1: "🥇", 2: "🥈", 3: "🥉"}
                        colores = {
                            "presentar": "green",
                            "evaluar": "orange",
                            "no_presentar": "red"
                        }

                        for item in comparacion.get("ranking", []):
                            pos = item.get("posicion", 0)
                            medalla = medallas.get(pos, f"#{pos}")
                            rec = item.get("recomendacion", "evaluar")
                            color = colores.get(rec, "gray")

                            with st.expander(
                                f"{medalla} Posición {pos} — "
                                f"{item.get('titulo', item.get('nombre_archivo', '—'))} "
                                f"| Score: {item.get('score', 0)}/100",
                                expanded=(pos == 1)
                            ):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Score", f"{item.get('score', 0)}/100")
                                with col2:
                                    st.metric("Monto estimado", f"USD {item.get('monto_estimado_usd', 0):,.0f}")
                                with col3:
                                    st.metric("Prob. de ganar", item.get("probabilidad_ganar", "—").upper())

                                st.markdown(f"**Recomendación:** :{color}[{rec.upper().replace('_', ' ')}]")
                                st.write(item.get("motivo_ranking", "—"))

                                ventajas = item.get("ventajas_clave", [])
                                if ventajas:
                                    st.markdown("**✅ Ventajas:**")
                                    for v in ventajas:
                                        st.markdown(f"• {v}")

                                riesgos = item.get("riesgos_clave", [])
                                if riesgos:
                                    st.markdown("**⚠️ Riesgos:**")
                                    for r in riesgos:
                                        st.markdown(f"• {r}")

                        st.divider()
                        st.info(f"💡 **Recomendación general:** {comparacion.get('recomendacion_general', '—')}")

                        advertencias = comparacion.get("advertencias", [])
                        if advertencias:
                            st.warning("⚠️ **Advertencias:**\n" + "\n".join([f"• {a}" for a in advertencias]))

                        st.divider()
                        nombre_word = f"comparativo_licitaciones_{timestamp()}.docx"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
                            ruta_docx = tmp_docx.name
                        licitai.generar_word_comparativo(analisis_lista, comparacion, ruta_docx)
                        with open(ruta_docx, "rb") as f:
                            contenido = f.read()
                        st.download_button(
                            label="💾 Descargar reporte comparativo Word",
                            data=contenido,
                            file_name=nombre_word,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

# ════════════════════════════════════════
# TAB 5: ChatDoc
# ════════════════════════════════════════
with tab5:
    st.subheader("💬 Chat con tus documentos")
    st.caption("Subí cualquier manual, contrato o procedimiento y hacele preguntas en lenguaje natural.")

    # Inicializar session state
    if "chatdoc_coleccion" not in st.session_state:
        st.session_state.chatdoc_coleccion = None
    if "chatdoc_nombre" not in st.session_state:
        st.session_state.chatdoc_nombre = ""
    if "chatdoc_historial" not in st.session_state:
        st.session_state.chatdoc_historial = []
    if "chatdoc_mensajes" not in st.session_state:
        st.session_state.chatdoc_mensajes = []
    if "chatdoc_info" not in st.session_state:
        st.session_state.chatdoc_info = {}

    # ── Paso 1: subir documento ──
    if st.session_state.chatdoc_coleccion is None:
        st.markdown("**📁 Paso 1: Cargá tu documento**")

        pdf_chat = st.file_uploader(
            "Seleccioná el PDF",
            type=["pdf"],
            help="Manuales HSE, contratos, procedimientos, especificaciones técnicas",
            key="uploader_chatdoc"
        )

        if pdf_chat is not None:
            st.info(f"📄 **{pdf_chat.name}** — {pdf_chat.size:,} bytes")

            if st.button("📥 Cargar y procesar documento", type="primary"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(pdf_chat.read())
                    ruta_tmp = tmp.name

                try:
                    with st.spinner("🔍 Procesando documento..."):
                        coleccion, n_chunks, n_paginas = chatdoc.indexar_documento(
                            ruta_tmp, pdf_chat.name
                        )

                    st.session_state.chatdoc_coleccion = coleccion
                    st.session_state.chatdoc_nombre = pdf_chat.name
                    st.session_state.chatdoc_historial = []
                    st.session_state.chatdoc_mensajes = []
                    st.session_state.chatdoc_info = {
                        "chunks": n_chunks,
                        "paginas": n_paginas
                    }
                    st.rerun()
                finally:
                    os.unlink(ruta_tmp)

    # ── Paso 2: chat ──
    else:
        info = st.session_state.chatdoc_info
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.success(f"✅ **{st.session_state.chatdoc_nombre}** cargado y listo")
        with col2:
            st.metric("Páginas", info.get("paginas", "—"))
        with col3:
            st.metric("Fragmentos", info.get("chunks", "—"))

        st.divider()

        # Ejemplos de preguntas
        st.markdown("**💡 Preguntas de ejemplo:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("¿Cuál es el objeto del contrato?", use_container_width=True):
                st.session_state.chatdoc_pregunta = "¿Cuál es el objeto del contrato?"
                st.rerun()
        with col2:
            if st.button("¿Cuáles son las obligaciones principales?", use_container_width=True):
                st.session_state.chatdoc_pregunta = "¿Cuáles son las obligaciones principales?"
                st.rerun()
        with col3:
            if st.button("¿Qué penalidades se establecen?", use_container_width=True):
                st.session_state.chatdoc_pregunta = "¿Qué penalidades se establecen?"
                st.rerun()

        st.divider()

        # Mostrar historial de conversación
        for msg in st.session_state.chatdoc_mensajes:
            if msg["rol"] == "usuario":
                with st.chat_message("user"):
                    st.write(msg["texto"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["texto"])

        # Input de pregunta
        if "chatdoc_pregunta" not in st.session_state:
            st.session_state.chatdoc_pregunta = ""

        pregunta = st.chat_input("Hacé una pregunta sobre el documento...")

        # También procesar si viene de un botón de ejemplo
        if not pregunta and st.session_state.chatdoc_pregunta:
            pregunta = st.session_state.chatdoc_pregunta
            st.session_state.chatdoc_pregunta = ""

        if pregunta:
            # Mostrar pregunta
            with st.chat_message("user"):
                st.write(pregunta)

            # Generar respuesta
            with st.chat_message("assistant"):
                with st.spinner("🔍 Buscando en el documento..."):
                    respuesta = chatdoc.responder_pregunta(
                        st.session_state.chatdoc_coleccion,
                        pregunta,
                        st.session_state.chatdoc_nombre,
                        st.session_state.chatdoc_historial
                    )
                st.write(respuesta)

            # Guardar en historial visual
            st.session_state.chatdoc_mensajes.append(
                {"rol": "usuario", "texto": pregunta}
            )
            st.session_state.chatdoc_mensajes.append(
                {"rol": "asistente", "texto": respuesta}
            )
            st.rerun()

        st.divider()

        # Botón para cargar otro documento
        if st.button("📁 Cargar otro documento"):
            st.session_state.chatdoc_coleccion = None
            st.session_state.chatdoc_nombre = ""
            st.session_state.chatdoc_historial = []
            st.session_state.chatdoc_mensajes = []
            st.session_state.chatdoc_info = {}
            st.session_state.chatdoc_pregunta = ""
            st.rerun()

# ════════════════════════════════════════
# TAB 6: HSE Pro
# ════════════════════════════════════════
with tab6:
    st.subheader("🦺 HSE Pro — Formato Shell / Peduzzi")
    st.caption("Generador de reportes HSE con el formato estándar usado por Shell, YPF y empresas contratistas de Vaca Muerta.")

    col1, col2 = st.columns(2)
    with col1:
        st.info("📋 **Reporte Preliminar** — para Near Miss y Casi-Accidentes (formato RG-11-01 Shell)")
    with col2:
        st.warning("📋 **Reporte de Investigación** — para accidentes con lesiones (formato F01 PG-14 Peduzzi)")

    st.divider()

    if "hsev2_descripcion" not in st.session_state:
        st.session_state.hsev2_descripcion = ""
    if "hsev2_preguntas" not in st.session_state:
        st.session_state.hsev2_preguntas = []
    if "hsev2_respuestas" not in st.session_state:
        st.session_state.hsev2_respuestas = {}
    if "hsev2_etapa" not in st.session_state:
        st.session_state.hsev2_etapa = "descripcion"
    if "hsev2_datos" not in st.session_state:
        st.session_state.hsev2_datos = None

    if st.session_state.hsev2_etapa == "descripcion":
        st.markdown("**📝 Descripción del evento:**")
        descripcion = st.text_area(
            "Describí lo que ocurrió:",
            placeholder="Ej: El operario Luis Andrade fue detectado conduciendo con licencia vencida en la locación SB.x1001h durante inspección de Shell...",
            height=120,
            key="textarea_hsev2"
        )
        if st.button("➡️ Continuar", type="primary", key="btn_hsev2_continuar") and descripcion:
            st.session_state.hsev2_descripcion = descripcion
            with st.spinner("🔍 Analizando información disponible..."):
                analisis = hseai_v2.detectar_info_faltante(descripcion)
            if analisis and not analisis.get("suficiente_para_reporte", True):
                faltantes = [
                    f for f in analisis.get("informacion_faltante", [])
                    if f.get("obligatorio", False)
                ][:5]
                if faltantes:
                    st.session_state.hsev2_preguntas = faltantes
                    st.session_state.hsev2_etapa = "preguntas"
                    st.rerun()
                else:
                    st.session_state.hsev2_etapa = "generar"
                    st.rerun()
            else:
                st.session_state.hsev2_etapa = "generar"
                st.rerun()

    elif st.session_state.hsev2_etapa == "preguntas":
        st.info(f"📋 Necesito {len(st.session_state.hsev2_preguntas)} dato(s) adicional(es):")
        st.divider()
        with st.form("form_hsev2"):
            respuestas_form = {}
            for i, item in enumerate(st.session_state.hsev2_preguntas):
                respuestas_form[item["campo"]] = st.text_input(
                    f"❓ {item['pregunta']}",
                    key=f"hsev2_q_{i}"
                )
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.form_submit_button("🤖 Generar reporte", type="primary"):
                    st.session_state.hsev2_respuestas = respuestas_form
                    st.session_state.hsev2_etapa = "generar"
                    st.rerun()
            with col2:
                if st.form_submit_button("↩️ Volver"):
                    st.session_state.hsev2_etapa = "descripcion"
                    st.session_state.hsev2_preguntas = []
                    st.rerun()

    elif st.session_state.hsev2_etapa == "generar":
        descripcion_completa = st.session_state.hsev2_descripcion
        if st.session_state.hsev2_respuestas:
            adicionales = "\n".join([
                f"{campo}: {valor}"
                for campo, valor in st.session_state.hsev2_respuestas.items()
                if valor
                ])
            if adicionales:
                    descripcion_completa += f"\n\nInformación adicional:\n{adicionales}"

        with st.spinner("🤖 Generando reporte HSE Pro..."):
            datos = hseai_v2.generar_reporte_hse_v2(descripcion_completa)

        if not datos:
            st.error("❌ No se pudo generar el reporte.")
            st.warning("💡 El sistema reintentó 3 veces sin éxito. Hacé clic en Reintentar.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Reintentar", type="primary", key="btn_hsev2_reintentar"):
                    st.rerun()
            with col2:
                if st.button("↩️ Volver a describir", key="btn_hsev2_volver_generar"):
                    st.session_state.hsev2_etapa = "descripcion"
                    st.rerun()
        else:
            st.session_state.hsev2_datos = datos
            st.session_state.hsev2_etapa = "resultado"
            st.rerun()

    elif st.session_state.hsev2_etapa == "resultado":
        datos = st.session_state.hsev2_datos
        formato = datos.get("formato", "preliminar")

        # Badge de formato
        if formato == "investigacion":
            st.warning(f"📋 Formato generado: **REPORTE DE INVESTIGACIÓN** (F01 PG-14)")
        else:
            st.info(f"📋 Formato generado: **INFORME PRELIMINAR** (RG-11-01)")

        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("N° Reporte", datos.get("numero_reporte", "—").split("-")[-1])
        with col2:
            st.metric("Gravedad", datos.get("gravedad", "—"))
        with col3:
            investiga = datos.get("requiere_investigacion_formal", False)
            st.metric("Investigación", "⚠️ Requerida" if investiga else "✅ No requerida")

        st.divider()
        acc = datos.get("datos_accidentado", {})
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Accidentado:** {acc.get('nombre', '—')} {acc.get('apellido', '—')}")
            st.markdown(f"**Función:** {acc.get('funcion', '—')}")
        with col2:
            st.markdown(f"**Ubicación:** {datos.get('ubicacion', '—')}")
            st.markdown(f"**Circunstancia:** {datos.get('circunstancia', '—')}")

        st.divider()
        st.subheader("📋 Descripción del suceso")
        st.write(datos.get("descripcion_suceso", "—"))

        st.divider()
        st.subheader("🔍 Causas raíz identificadas")

        for ac in datos.get("acciones_correctivas", []):
            if isinstance(ac, dict):
                st.markdown(f"**{ac.get('numero', '—')}.** {ac.get('descripcion', '—')}")
                st.caption(f"Responsable: {ac.get('responsable', '—')} | Plazo: {ac.get('plazo', '—')}")
            elif isinstance(ac, str):
                st.markdown(f"• {ac}")

        st.divider()
        st.subheader("✅ Acciones correctivas")

        for ac in datos.get("acciones_correctivas", []):
            if isinstance(ac, dict):
                st.markdown(f"**{ac.get('numero', '—')}.** {ac.get('descripcion', '—')}")
                st.caption(f"Responsable: {ac.get('responsable', '—')} | Plazo: {ac.get('plazo', '—')}")
            elif isinstance(ac, str):
                st.markdown(f"• {ac}")



        # Descargar Word
        st.divider()
        nombre_word = f"reporte_hse_pro_{timestamp()}.docx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            ruta_tmp = tmp.name
        hseai_v2.generar_word_hse_v2(datos, ruta_tmp)
        with open(ruta_tmp, "rb") as f:
            contenido = f.read()
        st.download_button(
            label="💾 Descargar reporte Word (formato Shell/Peduzzi)",
            data=contenido,
            file_name=nombre_word,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        st.divider()
        if st.button("➕ Nuevo reporte", key="btn_hsev2_nuevo"):
            st.session_state.hsev2_etapa = "descripcion"
            st.session_state.hsev2_descripcion = ""
            st.session_state.hsev2_preguntas = []
            st.session_state.hsev2_respuestas = {}
            st.session_state.hsev2_datos = None
            st.rerun()


# ── Footer ──
st.markdown("""
<div class="footer">
    OilAI · Desarrollado por Eduardo Ariel Vega con Claude IA · Vaca Muerta, Neuquén · 2026
</div>
""", unsafe_allow_html=True)