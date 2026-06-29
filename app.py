import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# 1. CONFIGURACIÓN VISUAL DE LA PÁGINA
st.set_page_config(
    page_title="Verona Quality Lab", 
    page_icon="🐕", 
    layout="wide"
)

# Estilo CSS personalizado para la interfaz web
st.markdown("""
    <style>
    .main-title { color: #0F2C59; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 700; margin-bottom: 5px; }
    .subtitle { color: #64748B; font-size: 18px; margin-bottom: 25px; }
    .stButton>button { background-color: #0F2C59 !important; color: white !important; border-radius: 6px !important; padding: 10px 24px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE LA BASE DE DATOS EN MEMORIA
if 'historial_laboratorio' not in st.session_state:
    st.session_state['historial_laboratorio'] = []

# 3. BARRA LATERAL: LOGO Y CONFIGURACIÓN
st.sidebar.markdown("<h2 style='text-align: center; color: #0F2C59;'>Verona Quality Lab</h2>", unsafe_allow_html=True)
logo_url = "https://images.unsplash.com/photo-1628634125301-443b78298715?auto=format&fit=crop&q=80&w=400"
st.sidebar.image(logo_url, caption="📐 Vigilancia y Rigor Metrológico", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuración Global")
analito = st.sidebar.text_input("Analito:", value="Glucosa")
unidad = st.sidebar.text_input("Unidad:", value="mg/dL")

st.sidebar.subheader("🎯 Metas Analíticas (CLIA 2024)")
tea_clia = st.sidebar.number_input("ETa (%) sugerido:", value=8.0, step=0.1)
sesgo_peec = st.sidebar.number_input("Sesgo / Bias (%) del Laboratorio:", value=0.0, step=0.1)

# 4. CUERPO PRINCIPAL
st.markdown("<h1 class='main-title'>🔬 Verona Quality Lab</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Sistema Inteligente de Gestión de Calidad Analítica y Optimización Metrológica</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "⚡ Verificación N20 (Repetibilidad)", 
    "📅 Precisión Intermedia (Protocolo 5 Días)",
    "🗄️ Historial del Laboratorio"
])

# --- FUNCIÓN GENERADORA DEL REPORTE IMPRIMIBLE (CORREGIDA) ---
def generar_html_reporte(reg):
    estatus = "🟢 CLASE MUNDIAL" if reg['sigma'] >= 6 else ("🟡 ACEPTABLE" if reg['sigma'] >= 3 else "🔴 REVISAR")
    
    # Construimos las filas de la tabla fuera del f-string para evitar el SyntaxError
    filas_tabla = ""
    for i, v in enumerate(reg['valores']):
        filas_tabla += f"<tr><td>Punto {i+1}</td><td>{v}</td></tr>"
        
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #1e293b; padding: 30px; }}
            .header {{ border-bottom: 3px solid #0f2c59; padding-bottom: 10px; margin-bottom: 20px; }}
            .title {{ color: #0f2c59; font-size: 24px; font-weight: bold; margin: 0; }}
            .sub {{ color: #64748b; font-size: 14px; margin: 5px 0 0 0; }}
            .meta-table {{ width: 100%; margin: 20px 0; border-collapse: collapse; }}
            .meta-table td {{ padding: 8px; border: 1px solid #e2e8f0; font-size: 14px; }}
            .meta-label {{ font-weight: bold; background-color: #f8fafc; color: #0f2c59; width: 25%; }}
            .cards {{ display: flex; gap: 15px; margin: 20px 0; }}
            .card {{ flex: 1; background: #f1f5f9; padding: 15px; border-radius: 6px; text-align: center; border-bottom: 3px solid #0f2c59; }}
            .card-val {{ font-size: 20px; font-weight: bold; color: #0f2c59; }}
            .card-lbl {{ font-size: 11px; color: #64748b; text-transform: uppercase; }}
            .data-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .data-table th {{ background: #0f2c59; color: white; padding: 10px; font-size: 13px; }}
            .data-table td {{ padding: 8px; border: 1px solid #e2e8f0; text-align: center; font-size: 13px; }}
            .signature {{ margin-top: 60px; border-top: 1px solid #64748b; float: right; width: 250px; text-align: center; padding-top: 5px; font-size: 13px; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="header">
            <h1 class="title">🐕 Verona Quality Lab</h1>
            <p class="sub">Certificado Oficial de Validación Analítica y Auditoría Metrológica</p>
        </div>
        <table class="meta-table">
            <tr>
                <td class="meta-label">Analito Evaluado:</td><td>{reg['analito']}</td>
                <td class="meta-label">Fecha Registro:</td><td>{reg['fecha']}</td>
            </tr>
            <tr>
                <td class="meta-label">Estudio Metrológico:</td><td>{reg['tipo']}</td>
                <td class="meta-label">Unidad de Medida:</td><td>{reg['unidad']}</td>
            </tr>
            <tr>
                <td class="meta-label">Límite ETa (CLIA):</td><td>{reg['tea']}%</td>
                <td class="meta-label">Sesgo Declarado:</td><td>{reg['sesgo']}%</td>
            </tr>
        </table>
        <div class="cards">
            <div class="card"><div class="card-val">{reg['media']:.2f}</div><div class="card-lbl">Media Analítica</div></div>
            <div class="card"><div class="card-val">{reg['cv']:.2f}%</div><div class="card-lbl">Imprecisión (CV%)</div></div>
            <div class="card"><div class="card-val">{reg['sigma']:.2f} σ</div><div class="card-lbl">Métrica Sigma Real</div></div>
            <div class="card" style="border-bottom-color: #22c55e;"><div class="card-val">{estatus}</div><div class="card-lbl">Dictamen Final</div></div>
        </div>
        <h3>Valores Crudos del Protocolo</h3>
        <table class="data-table">
            <thead><tr><th>Punto / Réplica</th><th>Resultado Reportado ({reg['unidad']})</th></tr></thead>
            <tbody>
                {filas_tabla}
            </tbody>
        </table>
        <div class="signature">Firma Supervisor de Calidad</div>
    </body>
    </html>
    """
    return html

# --- TAB 1: VERIFICACIÓN N20 ---
with tab1:
    st.markdown("### 📊 Validación de Repetibilidad (N20)")
    st.caption("Ingrese las 20 réplicas analizadas en la misma serie de trabajo.")
    
    data_n20 = {"Réplica": [f"R{i}" for i in range(1, 21)], "Resultado": [0.0] * 20}
    df_n20 = st.data_editor(pd.DataFrame(data_n20), key="editor_n20", hide_index=True, use_container_width=True)
    
    if st.button("Ejecutar Análisis N20", type="primary"):
        valores = np.array(df_n20["Resultado"].tolist())
        if sum(valores) == 0: 
            st.error("Por favor, ingrese valores válidos en la tabla.")
        else:
            media = np.mean(valores); sd = np.std(valores, ddof=1); cv = (sd/media)*100
            sigma = (tea_clia - abs(sesgo_peec)) / cv
            
            # 1. Respaldo en historial
            nuevo_registro = {
                "id": len(st.session_state['historial_laboratorio']) + 1,
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tipo": "Verificación N20", "analito": analito, "unidad": unidad,
                "media": media, "sd": sd, "cv": cv, "sigma": sigma, "tea": tea_clia, "sesgo": sesgo_peec, "valores": valores.tolist()
            }
            st.session_state['historial_laboratorio'].append(nuevo_registro)
            st.success("💾 ¡Análisis procesado y guardado en el Historial con éxito!")

            # 2. Despliegue inmediato
            st.markdown("#### 📋 Resultados Estadísticos Obtenidos")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Media Calculada", f"{media:.2f} {unidad}")
            c2.metric("Imprecisión (CV%)", f"{cv:.2f}%")
            c3.metric("Métrica Sigma Real", f"{sigma:.2f} σ")
            
            if cv <= (tea_clia/3): c4.success("✅ PASA (CV < 1/3 ETa)")
            else: c4.error("🚨 REVISAR (CV Alto)")
            
            # 3. Gráfico inmediato
            st.markdown("#### 📈 Gráfico de Control Levey-Jennings (Inmediato)")
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#F8FAFC')
            ax.set_facecolor('#FFFFFF')
            
            ax.plot(range(1, 21), valores, marker='o', linestyle='-', color='#0F2C59', linewidth=2, label='Valores N20')
            ax.axhline(media, color='#22C55E', linewidth=2, label=f'Media ({media:.2f})')
            ax.axhline(media + 2*sd, color='#3B82F6', ls='--', alpha=0.7, label='±2 SD')
            ax.axhline(media - 2*sd, color='#3B82F6', ls='--')
            ax.axhline(media + 3*sd, color='#EF4444', ls='-', alpha=0.7, label='±3 SD')
            ax.axhline(media - 3*sd, color='#EF4444', ls='-')
            
            ax.set_xticks(range(1, 21))
            ax.grid(True, color='#E2E8F0', linestyle=':', alpha=0.6)
            ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
            st.pyplot(fig)

# --- TAB 2: PRECISIÓN INTERMEDIA ---
with tab2:
    st.markdown("### 📅 Precisión Intermedia (Protocolo 5 Días)")
    st.caption("Ingrese los resultados del control de calidad de 5 días consecutivos.")
    
    data_ip = {"Día": [f"D{i}" for i in range(1, 6)], "Resultado": [0.0] * 5}
    df_ip = st.data_editor(pd.DataFrame(data_ip), key="editor_ip", hide_index=True, use_container_width=True)
    
    if st.button("Ejecutar Análisis Intermedio", type="primary"):
        valores = np.array(df_ip["Resultado"].tolist())
        if sum(valores) == 0: 
            st.error("Por favor, ingrese valores válidos en la tabla.")
        else:
            media = np.mean(valores); sd = np.std(valores, ddof=1); cv = (sd/media)*100
            sigma = (tea_clia - abs(sesgo_peec)) / cv
            
            # 1. Respaldo en historial
            nuevo_registro = {
                "id": len(st.session_state['historial_laboratorio']) + 1,
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tipo": "Precisión Intermedia (5D)", "analito": analito, "unidad": unidad,
                "media": media, "sd": sd, "cv": cv, "sigma": sigma, "tea": tea_clia, "sesgo": sesgo_peec, "valores": valores.tolist()
            }
            st.session_state['historial_laboratorio'].append(nuevo_registro)
            st.success("💾 ¡Análisis procesado y guardado en el Historial con éxito!")

            # 2. Despliegue inmediato
            st.markdown("#### 🎯 Evaluación del Desempeño Six Sigma")
            col_s1, col_s2 = st.columns([1, 3])
            col_s1.metric("Sigma Intermedio", f"{sigma:.2f} σ")
            
            if sigma >= 6: col_s2.success("🟢 **CALIDAD DE CLASE MUNDIAL (6 Sigma):** El proceso es extremadamente robusto.")
            elif sigma >= 3: col_s2.warning("🟡 **CALIDAD MARGINAL / ACEPTABLE:** Requiere vigilancia continua mediante Westgard.")
            else: col_s2.error("🔴 **CALIDAD NO ACEPTABLE:** Se requiere acción correctiva inmediata.")

            # 3. Gráfico inmediato
            st.markdown("#### 📈 Historial de Control Diario (5D)")
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#F8FAFC')
            ax.set_facecolor('#FFFFFF')
            
            ax.plot(range(1, 6), valores, marker='s', linestyle='-', color='#10B981', linewidth=2, label='Control Diario')
            ax.axhline(media, color='#22C55E', linewidth=2, label='Media')
            ax.axhline(media + 2*sd, color='#3B82F6', ls='--', label='±2 SD')
            ax.axhline(media - 2*sd, color='#3B82F6', ls='--')
            ax.axhline(media + 3*sd, color='#EF4444', ls='-', label='±3 SD')
            ax.axhline(media - 3*sd, color='#EF4444', ls='-')
            
            ax.set_ylabel(unidad)
            ax.set_xlabel("Día de Evaluación")
            ax.set_xticks(range(1, 6))
            ax.grid(True, color='#E2E8F0', linestyle=':', alpha=0.6)
            ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
            st.pyplot(fig)

# --- TAB 3: HISTORIAL DEL LABORATORIO ---
with tab3:
    st.markdown("### 🗄️ Registro Histórico Metrológico")
    st.caption("Consulte y audite todos los análisis guardados previamente en Verona Quality Lab.")
    historial = st.session_state['historial_laboratorio']
    
    if len(historial) == 0:
        st.info("El historial está vacío. Ejecute un estudio en las pestañas anteriores para revisarlo aquí.")
    else:
        resumen_datos = [{"ID": r["id"], "Fecha": r["fecha"], "Estudio": r["tipo"], "Analito": r["analito"], "Sigma": f"{r['sigma']:.2f} σ"} for r in historial]
        st.dataframe(pd.DataFrame(resumen_datos), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        opciones_selector = [f"ID {r['id']} - {r['analito']} ({r['tipo']}) | {r['fecha']}" for r in historial]
        seleccion = st.selectbox("Seleccione el registro para visualizar y exportar:", opciones_selector)
        
        id_sel = int(seleccion.split(" ")[1])
        reg_activo = next(item for item in historial if item["id"] == id_sel)
        
        html_reporte = generar_html_reporte(reg_activo)
        st.download_button(
            label="📥 Descargar Certificado de Auditoría PDF",
            data=html_reporte,
            file_name=f"Reporte_Calidad_{reg_activo['analito']}_{reg_activo['id']}.html",
            mime="text/html"
        )
        
        # Gráfica recuperada
        fig, ax = plt.subplots(figsize=(10, 3.5))
        fig.patch.set_facecolor('#F8FAFC')
        v_viejos = reg_activo["valores"]
        ax.plot(range(1, len(v_viejos)+1), v_viejos, marker='o', color='#0F2C59')
        ax.axhline(reg_activo["media"], color='#22C55E', linewidth=2)
        ax.set_xticks(range(1, len(v_viejos)+1))
        st.pyplot(fig)
