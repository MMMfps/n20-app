import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓN VISUAL DE LA PÁGINA (Colores y Estilo)
st.set_page_config(
    page_title="Verona Quality Lab", 
    page_icon="🐕", 
    layout="wide"
)

# Estilo CSS personalizado para mejorar la tipografía y diseño
st.markdown("""
    <style>
    .main-title {
        color: #0F2C59;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .subtitle {
        color: #64748B;
        font-size: 18px;
        margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #0F2C59 !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 10px 24px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. BARRA LATERAL: LOGO Y CONFIGURACIÓN
st.sidebar.markdown("<h2 style='text-align: center; color: #0F2C59;'>Verona Quality Lab</h2>", unsafe_allow_html=True)

# Logo Automatizado: Usamos una imagen profesional de un Cane Corso Atigrado
logo_url = "https://images.unsplash.com/photo-1628634125301-443b78298715?auto=format&fit=crop&q=80&w=400"
st.sidebar.image(logo_url, caption="📐 Vigilancia y Rigor Metrológico", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuración Global")
analito = st.sidebar.text_input("Analito:", value="Glucosa")
unidad = st.sidebar.text_input("Unidad:", value="mg/dL")

st.sidebar.subheader("🎯 Metas Analíticas (CLIA 2024)")
tea_clia = st.sidebar.number_input("ETa (%) sugerido (Glucosa = 8.0):", value=8.0, step=0.1)
sesgo_peec = st.sidebar.number_input("Sesgo / Bias (%) del Laboratorio:", value=0.0, step=0.1)

# 3. CUERPO PRINCIPAL
st.markdown("<h1 class='main-title'>🔬 Verona Quality Lab</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Sistema Inteligente de Gestión de Calidad Analítica y Optimización Metrológica</p>", unsafe_allow_html=True)

# Pestañas con diseño limpio
tab1, tab2 = st.tabs(["⚡ Verificación N20 (Repetibilidad)", "📅 Precisión Intermedia (Protocolo 5 Días)"])

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
            
            # Tarjetas de resultados elegantes
            st.markdown("#### 📋 Resultados Estadísticos")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Media Calculada", f"{media:.2f} {unidad}")
            c2.metric("Imprecisión (CV%)", f"{cv:.2f}%")
            c3.metric("Métrica Sigma Real", f"{sigma:.2f} σ")
            
            if cv <= (tea_clia/3):
                c4.success("✅ PASA (CV < 1/3 ETa)")
            else:
                c4.error("🚨 REVISAR (CV Alto)")
            
            # Gráfico de Levey-Jennings Estilizado
            st.markdown("#### 📈 Gráfico de Control Levey-Jennings")
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#F8FAFC') # Fondo gris suave para el gráfico
            ax.set_facecolor('#FFFFFF')
            
            ax.plot(range(1, 21), valores, marker='o', linestyle='-', color='#0F2C59', linewidth=2, label='Valores N20')
            ax.axhline(media, color='#22C55E', linewidth=2, label=f'Media ({media:.2f})')
            ax.axhline(media + 2*sd, color='#3B82F6', ls='--', alpha=0.7, label='±2 SD')
            ax.axhline(media - 2*sd, color='#3B82F6', ls='--', alpha=0.7)
            ax.axhline(media + 3*sd, color='#EF4444', ls='-', alpha=0.7, label='±3 SD')
            ax.axhline(media - 3*sd, color='#EF4444', ls='-', alpha=0.7)
            
            ax.set_title(f"Control de Repetibilidad - {analito}", color='#0F2C59', fontsize=12, fontweight='bold')
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
            
            st.markdown("#### 🎯 Evaluación del Desempeño Six Sigma")
            col_s1, col_s2 = st.columns([1, 3])
            col_s1.metric("Sigma Intermedio", f"{sigma:.2f} σ")
            
            if sigma >= 6: 
                col_s2.success("🟢 **CALIDAD DE CLASE MUNDIAL (6 Sigma):** El proceso es extremadamente robusto. Verona Quality Lab certifica una tasa de error prácticamente nula.")
            elif sigma >= 3: 
                col_s2.warning("🟡 **CALIDAD MARGINAL / ACEPTABLE:** El método es controlable, pero requiere vigilancia continua mediante reglas de Westgard rigurosas.")
            else: 
                col_s2.error("🔴 **CALIDAD NO ACEPTABLE:** Alto riesgo analítico. La variación interdiaria consume tu error permitido. Se requiere acción correctiva inmediata.")

            # Gráfico de Levey-Jennings de 5 puntos Estilizado
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
            
            ax.set_title(f"Evolución de Precisión Intermedia - {analito}", color='#0F2C59', fontsize=12, fontweight='bold')
            ax.set_ylabel(unidad)
            ax.set_xlabel("Día de Evaluación")
            ax.set_xticks(range(1, 6))
            ax.grid(True, color='#E2E8F0', linestyle=':', alpha=0.6)
            ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
            st.pyplot(fig)
