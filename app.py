import streamlit as st
import os
import tempfile
import pandas as pd
import contractai
import dataai
from utils import timestamp

# ── Configuración ──
st.set_page_config(
    page_title="OilAI — Asistente para Vaca Muerta",
    page_icon="🛢️",
    layout="wide"
)

st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: bold; color: #1F5C99; text-align: center; padding: 1rem 0; }
    .sub-header { font-size: 1rem; color: #666; text-align: center; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🛢️ OilAI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Asistente de IA para empresas de Oil & Gas — Vaca Muerta, Neuquén</div>', unsafe_allow_html=True)

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("❌ ANTHROPIC_API_KEY no configurada.")
    st.stop()

tab1, tab2 = st.tabs(["📄 ContractAI — Análisis de contratos", "📊 DataAI — Consulta de datos"])

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
                    ruta_reporte = os.path.join(tempfile.gettempdir(), nombre)
                    contractai.generar_reporte(datos, ruta_reporte)
                    with open(ruta_reporte, "rb") as f:
                        st.download_button(
                            label="💾 Descargar reporte Word",
                            data=f,
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

# ── Footer ──
st.divider()
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.8rem'>"
    "OilAI — Desarrollado con Claude IA · Vaca Muerta, Neuquén · 2026"
    "</div>",
    unsafe_allow_html=True
)