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

# Estilo CSS personalizado
st.markdown("""
    <style>
    .main-title { color: #0F2C59; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 700; margin-bottom: 5px; }
    .subtitle { color: #64748B; font-size: 18px; margin-bottom: 25px; }
    .stButton>button { background-color: #0F2C59 !important; color: white !important; border-radius: 6px !important; padding: 10px 24px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE LA BASE DE DATOS EN MEMORIA
# Si es la primera vez que abre la app, creamos el almacén del historial
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
tea_clia = st.sidebar.number_input("ETa (%) sugerido (Glucosa = 8.0):", value=8.0, step=0.1)
sesgo_peec = st.sidebar.number_input("Sesgo / Bias (%) del Laboratorio:", value=0.0, step=0.1)

# 4. CUERPO PRINCIPAL
st.markdown("<h1 class='main-title'>🔬 Verona Quality Lab</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Sistema Inteligente de Gestión de Calidad Analítica y Optimización Metrológica</p>", unsafe_allow_html=True)

# Añadimos la tercera pestaña: "Historial del Laboratorio"
tab1, tab2, tab3 = st.tabs([
    "⚡ Verificación N20 (Repetibilidad)", 
    "📅 Precisión Intermedia (Protocolo 5 Días)",
    "🗄️ Historial del Laboratorio"
])

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
            
            # GUARDAR EN EL HISTORIAL
            nuevo_registro = {
                "id": len(st.session_state['historial_laboratorio']) + 1,
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tipo": "Verificación N20",
                "analito": analito,
                "unidad": unidad,
                "media": media,
                "sd": sd,
                "cv": cv,
                "sigma": sigma,
                "tea": tea_clia,
                "sesgo": sesgo_peec,
                "valores": valores.tolist()
            }
            st.session_state['historial_laboratorio'].append(nuevo_registro)
            st.success("💾 ¡Análisis N20 procesado y guardado en el Historial con éxito!")

            # Mostrar Resultados Inmediatos
            st.markdown("#### 📋 Resultados Estadísticos")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Media Calculada", f"{media:.2f} {unidad}")
            c2.metric("Imprecisión (CV%)", f"{cv:.2f}%")
            c3.metric("Métrica Sigma Real", f"{sigma:.2f} σ")
            if cv <= (tea_clia/3): c4.success("✅ PASA (CV < 1/3 ETa)")
            else: c4.error("🚨 REVISAR (CV Alto)")
            
            # Gráfico
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#F8FAFC')
            ax.plot(range(1, 21), valores, marker='o', color='#0F2C59', linewidth=2)
            ax.axhline(media, color='#22C55E', linewidth=2)
            ax.axhline(media + 2*sd, color='#3B82F6', ls='--')
            ax.axhline(media - 2*sd, color='#3B82F6', ls='--')
            ax.axhline(media + 3*sd, color='#EF4444', ls='-')
            ax.axhline(media - 3*sd, color='#EF4444', ls='-')
            ax.set_xticks(range(1, 21))
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
            
            # GUARDAR EN EL HISTORIAL
            nuevo_registro = {
                "id": len(st.session_state['historial_laboratorio']) + 1,
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tipo": "Precisión Intermedia (5D)",
                "analito": analito,
                "unidad": unidad,
                "media": media,
                "sd": sd,
                "cv": cv,
                "sigma": sigma,
                "tea": tea_clia,
                "sesgo": sesgo_peec,
                "valores": valores.tolist()
            }
            st.session_state['historial_laboratorio'].append(nuevo_registro)
            st.success("💾 ¡Análisis Intermedio procesado y guardado en el Historial con éxito!")

            # Resultados
            st.markdown("#### 🎯 Evaluación del Desempeño Six Sigma")
            col_s1, col_s2 = st.columns([1, 3])
            col_s1.metric("Sigma Intermedio", f"{sigma:.2f} σ")
            if sigma >= 6: col_s2.success("🟢 **CALIDAD DE CLASE MUNDIAL (6 Sigma)**")
            elif sigma >= 3: col_s2.warning("🟡 **CALIDAD MARGINAL / ACEPTABLE**")
            else: col_s2.error("🔴 **CALIDAD NO ACEPTABLE**")

            # Gráfico
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#F8FAFC')
            ax.plot(range(1, 6), valores, marker='s', color='#10B981', linewidth=2)
            ax.axhline(media, color='#22C55E', linewidth=2)
            ax.axhline(media + 2*sd, color='#3B82F6', ls='--')
            ax.axhline(media - 2*sd, color='#3B82F6', ls='--')
            ax.axhline(media + 3*sd, color='#EF4444', ls='-')
            ax.axhline(media - 3*sd, color='#EF4444', ls='-')
            ax.set_xticks(range(1, 6))
            st.pyplot(fig)

# --- TAB 3:🗄️ HISTORIAL DEL LABORATORIO ---
with tab3:
    st.markdown("### 🗄️ Registro Histórico Metrológico")
    st.caption("Consulte y audite todos los análisis guardados previamente en Verona Quality Lab.")
    
    historial = st.session_state['historial_laboratorio']
    
    if len(historial) == 0:
        st.info("ℹ️ El historial está vacío. Ejecute y guarde un análisis en las pestañas anteriores para verlo aquí.")
    else:
        # 1. Crear una tabla resumen de todo lo guardado
        resumen_datos = []
        for reg in historial:
            resumen_datos.append({
                "ID": reg["id"],
                "Fecha/Hora": reg["fecha"],
                "Tipo de Estudio": reg["tipo"],
                "Analito": reg["analito"],
                "Media": f"{reg['media']:.2f} {reg['unidad']}",
                "CV%": f"{reg['cv']:.2f}%",
                "Métrica Sigma": f"{reg['sigma']:.2f} σ"
            })
        
        df_resumen = pd.DataFrame(resumen_datos)
        st.dataframe(df_resumen, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 🔍 Buscador y Visor de Gráficos Históricos")
        
        # 2. Selector interactivo para cargar un gráfico antiguo
        opciones_selector = [f"ID {reg['id']} - {reg['analito']} ({reg['tipo']}) | {reg['fecha']}" for reg in historial]
        seleccion = st.selectbox("Seleccione el registro que desea revisar detalladamente:", opciones_selector)
        
        # Obtener el ID seleccionado
        id_seleccionado = int(seleccion.split(" ")[1])
        registro_activo = next(item for item in historial if item["id"] == id_seleccionado)
        
        # Re-dibujar la información y el gráfico del pasado
        st.markdown(f"#### 📊 Reporte Reconstruído para: **{registro_activo['analito']}**")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Media Histórica", f"{registro_activo['media']:.2f} {registro_activo['unidad']}")
        m_col2.metric("CV% Registrado", f"{registro_activo['cv']:.2f}%")
        m_col3.metric("Sigma Guardado", f"{registro_activo['sigma']:.2f} σ")
        m_col4.metric("ETa Base (CLIA)", f"{registro_activo['tea']}%")
        
        # Volver a graficar los puntos exactos guardados en ese momento
        valores_viejos = registro_activo["valores"]
        n_puntos = len(valores_viejos)
        h_media = registro_activo["media"]
        h_sd = registro_activo["sd"]
        
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#F8FAFC')
        ax.set_facecolor('#FFFFFF')
        
        color_linea = '#0F2C59' if registro_activo["tipo"] == "Verificación N20" else '#10B981'
        ax.plot(range(1, n_puntos + 1), valores_viejos, marker='o', linestyle='-', color=color_linea, linewidth=2, label='Datos Registrados')
        ax.axhline(h_media, color='#22C55E', linewidth=2, label=f'Media ({h_media:.2f})')
        ax.axhline(h_media + 2*h_sd, color='#3B82F6', ls='--', alpha=0.7, label='±2 SD')
        ax.axhline(h_media - 2*h_sd, color='#3B82F6', ls='--')
        ax.axhline(h_media + 3*h_sd, color='#EF4444', ls='-', alpha=0.7, label='±3 SD')
        ax.axhline(h_media - 3*h_sd, color='#EF4444', ls='-')
        
        ax.set_title(f"Gráfico Recuperado de Levey-Jennings ({registro_activo['tipo']})", color='#0F2C59', fontsize=12, fontweight='bold')
        ax.set_xticks(range(1, n_puntos + 1))
        ax.grid(True, color='#E2E8F0', linestyle=':', alpha=0.6)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        st.pyplot(fig)
