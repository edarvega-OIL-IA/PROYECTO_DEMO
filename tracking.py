import streamlit as st
import anthropic
from datetime import date

# ═══════════════════════════════════════════════════════════════════════════
# ETAPAS DEL PROCESO LOGÍSTICO INTERNACIONAL
# ═══════════════════════════════════════════════════════════════════════════

ETAPAS = [
    {"icono": "🏭", "nombre": "Retiro en origen"},
    {"icono": "✈️", "nombre": "Hub internacional (MIA/MAD/LHR)"},
    {"icono": "🚢", "nombre": "Embarque marítimo"},
    {"icono": "⚓", "nombre": "Puerto Chile"},
    {"icono": "🚛", "nombre": "Aduana Neuquén"},
    {"icono": "✅", "nombre": "Entrega al cliente"},
]

ORIGENES = ["Miami, USA", "Houston, USA", "Londres, UK", "Alemania", "Canadá", "China", "España", "Otro"]


# ═══════════════════════════════════════════════════════════════════════════
# DATOS DEMO
# ═══════════════════════════════════════════════════════════════════════════

def cargar_demo():
    return [
        {
            "invoice":      "PO# 02-0216 / INV. 00000001",
            "awb_bl":       "ONEY-XXXXXXXXXX",
            "hawb":         "HBOL000/CRT-0001",
            "agencia":      "EAV_01",
            "shipper":      "Flowserve Corporation",
            "cnee":         "EAV IA Empresa 01",
            "origen":       "Houston, USA",
            "bultos":       60,
            "kilos":        1607,
            "contenedor":   "TCKU0000000 / 40HC",
            "etapa_actual": 4,
            "etapas_ok":    [0, 1, 2, 3],
            "situacion":    "Esperando liberación AFIP — SIMI aprobada parcialmente.",
            "valor_fob":    "USD 148.500",
            "fecha_inicio": "2025-04-10",
        },
        {
            "invoice":      "PO# 02-0201 / INV. 00000002",
            "awb_bl":       "000-00000000",
            "hawb":         "HAW-NQN-0000-00",
            "agencia":      "EAV_02",
            "shipper":      "Honeywell Process Solutions",
            "cnee":         "EAV IA Empresa 02",
            "origen":       "Houston, USA",
            "bultos":       1,
            "kilos":        42,
            "contenedor":   "Aéreo — sin contenedor",
            "etapa_actual": 2,
            "etapas_ok":    [0, 1],
            "situacion":    "Carga en buque — ETD confirmado.",
            "valor_fob":    "USD 67.200",
            "fecha_inicio": "2025-04-28",
        },
        {
            "invoice":      "PO# 03-0088 / INV. 00000003",
            "awb_bl":       "MSCU-0000000000",
            "hawb":         "HBOL-NQN-0000-00",
            "agencia":      "EAV_03",
            "shipper":      "Baker Hughes GmbH",
            "cnee":         "EAV IA Empresa 03",
            "origen":       "Alemania",
            "bultos":       5,
            "kilos":        890,
            "contenedor":   "MSCU0000000 / 20DV",
            "etapa_actual": 1,
            "etapas_ok":    [0],
            "situacion":    "Documentación de exportación en trámite en origen.",
            "valor_fob":    "USD 312.000",
            "fecha_inicio": "2025-05-02",
        },
    ]


# ═══════════════════════════════════════════════════════════════════════════
# IA: GENERAR INFORME
# ═══════════════════════════════════════════════════════════════════════════

def generar_informe(emb):
    client   = anthropic.Anthropic()
    etapa    = ETAPAS[emb['etapa_actual']]
    progreso = int((emb['etapa_actual'] / (len(ETAPAS) - 1)) * 100)

    prompt = f"""Sos un operador de logística internacional especializado en importaciones Oil & Gas para Argentina.
Redactá un informe de estado profesional para enviar al cliente importador.

Datos del embarque:
- Invoice: {emb['invoice']}
- AWB / BL: {emb['awb_bl']} | HAWB: {emb['hawb']}
- Agencia: {emb['agencia']}
- Shipper: {emb['shipper']} ({emb['origen']})
- Consignatario: {emb['cnee']}
- Bultos: {emb['bultos']} | Kilos: {emb['kilos']} kg | FOB: {emb['valor_fob']}
- Contenedor: {emb['contenedor']}
- Etapa actual: {etapa['nombre']} ({progreso}% del trayecto)
- Situación: {emb['situacion']}

Requisitos del informe:
1. Asunto de mail sugerido
2. Conciso y profesional — máximo 12 líneas
3. Estado actual claro y próximos pasos concretos
4. Cierre con firma de Transporte EAV con IA
5. Español argentino formal — NO inventar fechas

Formato:
ASUNTO: [texto]
---
[cuerpo]"""

    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=800,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text


# ═══════════════════════════════════════════════════════════════════════════
# UI: PIPELINE VISUAL
# ═══════════════════════════════════════════════════════════════════════════

def render_pipeline(etapa_actual, etapas_ok):
    cols = st.columns(len(ETAPAS))
    for i, (col, etapa) in enumerate(zip(cols, ETAPAS)):
        with col:
            if i in etapas_ok:
                bg, fg, badge = "#1F4E79", "white", "✓"
            elif i == etapa_actual:
                bg, fg, badge = "#F0A500", "white", "●"
            else:
                bg, fg, badge = "#E8EDF2", "#999", str(i + 1)

            st.markdown(
                f"""<div style="background:{bg};color:{fg};border-radius:8px;
                padding:6px 3px;text-align:center;font-size:10px;font-weight:600;
                min-height:65px;display:flex;flex-direction:column;
                align-items:center;justify-content:center;gap:2px;">
                <div style="font-size:15px;">{etapa['icono']}</div>
                <div>{badge}</div>
                <div style="font-size:9px;line-height:1.2;">{etapa['nombre']}</div>
                </div>""",
                unsafe_allow_html=True
            )


# ═══════════════════════════════════════════════════════════════════════════
# PÁGINA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def tracking_page():
    st.title("🌐 TrackingAI")
    st.markdown("Seguimiento de embarques internacionales — Oil & Gas / Vaca Muerta")

    st.info(
        "💡 **Versión demo:** datos de ejemplo para demostración. "
        "En la **versión oficial** se integra con la operación real: "
        "invoice, AWB/BL, agencia, fechas por nodo y notificaciones automáticas al cliente.",
        icon="ℹ️"
    )

    if 'embarques' not in st.session_state:
        st.session_state['embarques'] = cargar_demo()

    embarques = st.session_state['embarques']
    tab1, tab2, tab3 = st.tabs(["📋 Embarques activos", "➕ Nuevo embarque", "📧 Generar informe"])

    # ─────────────────────────────────────────────────────────────────────
    # TAB 1: ACTIVOS
    # ─────────────────────────────────────────────────────────────────────
    with tab1:
        st.subheader(f"Embarques en curso: {len(embarques)}")

        for i, emb in enumerate(embarques):
            etapa    = ETAPAS[emb['etapa_actual']]
            progreso = int((emb['etapa_actual'] / (len(ETAPAS) - 1)) * 100)

            with st.expander(
                f"{etapa['icono']} **{emb['invoice'][:35]}**  |  "
                f"{emb['cnee']}  |  📦 {emb['bultos']} btos / {emb['kilos']} kg  |  ⏳ {progreso}%",
                expanded=(i == 0)
            ):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"**Consignatario:** {emb['cnee']}")
                    st.markdown(f"**Shipper:** {emb['shipper']} — {emb['origen']}")
                    st.markdown(f"**Agencia:** {emb['agencia']}")
                    st.markdown(f"**AWB / BL:** `{emb['awb_bl']}`  |  **HAWB:** `{emb['hawb']}`")
                    st.markdown(f"**Contenedor:** {emb['contenedor']}")
                    st.markdown(f"**Bultos:** {emb['bultos']}  |  **Kg:** {emb['kilos']}  |  **FOB:** {emb['valor_fob']}")

                with c2:
                    st.markdown("**Etapa actual:**")
                    st.markdown(
                        f"<div style='background:#F0A500;color:white;padding:8px;"
                        f"border-radius:8px;font-weight:600;text-align:center;'>"
                        f"{etapa['icono']} {etapa['nombre']}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown("")
                    st.progress(progreso / 100)
                    st.caption(f"Progreso: {progreso}%")

                st.markdown("**Situación:**")
                nueva_sit = st.text_input(
                    "sit", value=emb['situacion'],
                    label_visibility="collapsed", key=f"sit_{i}"
                )

                st.markdown("**Trazabilidad:**")
                render_pipeline(emb['etapa_actual'], emb['etapas_ok'])

                st.markdown("---")
                ca, cb, cc = st.columns([3, 1, 1])
                with ca:
                    opciones    = [f"{e['icono']} {e['nombre']}" for e in ETAPAS]
                    nueva_etapa = st.selectbox(
                        "Etapa", range(len(ETAPAS)),
                        index=emb['etapa_actual'],
                        format_func=lambda x: opciones[x],
                        key=f"etapa_{i}"
                    )
                with cb:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💾 Guardar", key=f"save_{i}", use_container_width=True):
                        embarques[i].update({
                            'etapa_actual': nueva_etapa,
                            'etapas_ok':    list(range(nueva_etapa)),
                            'situacion':    nueva_sit,
                        })
                        st.session_state['embarques'] = embarques
                        st.success("✅ Actualizado.")
                        st.rerun()
                with cc:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Quitar", key=f"del_{i}", use_container_width=True):
                        embarques.pop(i)
                        st.session_state['embarques'] = embarques
                        st.rerun()

    # ─────────────────────────────────────────────────────────────────────
    # TAB 2: NUEVO EMBARQUE
    # ─────────────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Registrar nuevo embarque")

        with st.form("form_nuevo"):
            c1, c2 = st.columns(2)
            with c1:
                invoice    = st.text_input("Invoice / Referencia *", placeholder="PO# 02-0300 / INV. 12345")
                awb_bl     = st.text_input("AWB / BL Madre *",        placeholder="ONEY-XXXXXXXX")
                hawb       = st.text_input("HAWB / BL Hijo",          placeholder="HBOL-XXX")
                agencia    = st.text_input("Agencia *",               placeholder="EAV_01")
            with c2:
                shipper    = st.text_input("Shipper *",               placeholder="Flowserve Corp.")
                cnee       = st.text_input("Consignatario *",         placeholder="NQN Petrol S.R.L.")
                origen     = st.selectbox("Origen *",                 ORIGENES)
                valor_fob  = st.text_input("Valor FOB",               placeholder="USD 50.000")

            c3, c4 = st.columns(2)
            with c3:
                bultos     = st.number_input("Bultos", min_value=1, value=1)
                kilos      = st.number_input("Kilos",  min_value=1, value=100)
            with c4:
                contenedor = st.text_input("Contenedor", placeholder="TCKU-XXXXXXX / 40HC")

            situacion = st.text_area("Situación inicial", height=70,
                                     placeholder="Ej: Documentación en trámite en origen.")

            if st.form_submit_button("➕ Registrar", use_container_width=True, type="primary"):
                if invoice and awb_bl and agencia and shipper and cnee:
                    embarques.append({
                        "invoice": invoice, "awb_bl": awb_bl, "hawb": hawb,
                        "agencia": agencia, "shipper": shipper, "cnee": cnee,
                        "origen": origen, "bultos": bultos, "kilos": kilos,
                        "contenedor": contenedor or "Sin asignar",
                        "etapa_actual": 0, "etapas_ok": [],
                        "situacion": situacion,
                        "valor_fob": valor_fob or "No informado",
                        "fecha_inicio": str(date.today()),
                    })
                    st.session_state['embarques'] = embarques
                    st.success(f"✅ Embarque registrado: {invoice}")
                    st.rerun()
                else:
                    st.warning("⚠️ Completá los campos obligatorios.")

    # ─────────────────────────────────────────────────────────────────────
    # TAB 3: GENERAR INFORME
    # ─────────────────────────────────────────────────────────────────────
    with tab3:
        st.subheader("Generar informe de estado para el cliente")
        st.markdown("La IA redacta el mail listo para enviar.")

        if not embarques:
            st.info("No hay embarques registrados.")
            return

        sel = st.selectbox(
            "Seleccioná el embarque",
            range(len(embarques)),
            format_func=lambda x: f"{embarques[x]['invoice'][:40]} — {embarques[x]['cnee']}"
        )

        emb_sel  = embarques[sel]
        etapa_sel = ETAPAS[emb_sel['etapa_actual']]
        progreso  = int((emb_sel['etapa_actual'] / (len(ETAPAS) - 1)) * 100)

        c1, c2, c3 = st.columns(3)
        c1.metric("Cliente",      emb_sel['cnee'])
        c2.metric("Etapa actual", etapa_sel['nombre'])
        c3.metric("Progreso",     f"{progreso}%")
        render_pipeline(emb_sel['etapa_actual'], emb_sel['etapas_ok'])
        st.markdown("")

        if st.button("🤖 Generar informe con IA", use_container_width=True, type="primary"):
            with st.spinner("Redactando informe..."):
                informe = generar_informe(emb_sel)

            st.markdown("---")
            st.subheader("📧 Informe generado")

            asunto, cuerpo_lineas, sep = "", [], False
            for linea in informe.split('\n'):
                if linea.startswith("ASUNTO:"):
                    asunto = linea.replace("ASUNTO:", "").strip()
                elif linea.strip() == "---":
                    sep = True
                elif sep:
                    cuerpo_lineas.append(linea)

            cuerpo = '\n'.join(cuerpo_lineas).strip() if cuerpo_lineas else informe

            if asunto:
                st.markdown(f"**Asunto sugerido:** `{asunto}`")
                st.markdown("")

            st.text_area("Cuerpo del mail — listo para copiar",
                         value=cuerpo, height=320, key="informe_output")
            st.caption("💡 Revisá el contenido antes de enviar.")
