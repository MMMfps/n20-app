import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuracion de la pagina
st.set_page_config(page_title="BioLab Quality Suite", page_icon="🔬", layout="wide")

st.title("🔬 BioLab Quality Suite: Gestión Metrológica")
st.markdown("Plataforma avanzada para la validación de métodos y control de calidad analítico.")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración Global")
analito = st.sidebar.text_input("Analito:", value="Glucosa")
unidad = st.sidebar.text_input("Unidad:", value="mg/dL")

# Criterio CLIA 2024 para Glucosa es 8%
st.sidebar.subheader("🎯 Metas Analíticas (CLIA 2024)")
tea_clia = st.sidebar.number_input("ETa (%) sugerido (Glucosa = 8.0):", value=8.0, step=0.1)
sesgo_peec = st.sidebar.number_input("Sesgo / Bias (%) reportado:", value=0.0, step=0.1)

# --- NAVEGACIÓN POR PESTAÑAS ---
tab1, tab2 = st.tabs(["⚡ Verificación N20 (Repetibilidad)", "📅 Precisión Intermedia (Dentro de Lab)"])

# --- TAB 1: VERIFICACIÓN N20 ---
with tab1:
    st.subheader(f"Validación de Repetibilidad (N20) - {analito}")
    st.write("Ingrese 20 réplicas procesadas en la misma serie analítica.")
    
    data_n20 = {"Réplica": [f"R{i}" for i in range(1, 21)], "Resultado": [0.0] * 20}
    df_n20 = st.data_editor(pd.DataFrame(data_n20), key="editor_n20", hide_index=True, use_container_width=True)
    
    if st.button("📊 Analizar N20", type="primary"):
        valores = np.array(df_n20["Resultado"].tolist())
        if sum(valores) == 0:
            st.error("Ingrese datos para procesar.")
        else:
            media = np.mean(valores); sd = np.std(valores, ddof=1); cv = (sd/media)*100
            sigma = (tea_clia - abs(sesgo_peec)) / cv
            
            # Resultados
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Media", f"{media:.2f}")
            c2.metric("CV%", f"{cv:.2f}%")
            c3.metric("Sigma Real", f"{sigma:.2f} σ")
            c4.metric("Estatus", "Pasa" if cv <= (tea_clia/3) else "Revisar") # Regla de oro: CV < 1/3 ETa
            
            # Gráfico
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(range(1,21), valores, 'ko-')
            ax.axhline(media, color='g', label='Media')
            ax.axhline(media + 2*sd, color='b', ls='--'); ax.axhline(media - 2*sd, color='b', ls='--')
            ax.axhline(media + 3*sd, color='r', ls='-'); ax.axhline(media - 3*sd, color='r', ls='-')
            ax.set_title(f"Levey-Jennings: Repetibilidad {analito}"); ax.legend()
            st.pyplot(fig)

# --- TAB 2: PRECISIÓN INTERMEDIA ---
with tab2:
    st.subheader(f"Precisión Intermedia (Día a Día) - {analito}")
    st.write("Ingrese los resultados de control de calidad de los últimos 20 días.")
    
    data_ip = {"Día": [f"D{i}" for i in range(1, 21)], "Resultado": [0.0] * 20}
    df_ip = st.data_editor(pd.DataFrame(data_ip), key="editor_ip", hide_index=True, use_container_width=True)
    
    if st.button("📈 Analizar Precisión Intermedia", type="primary"):
        valores = np.array(df_ip["Resultado"].tolist())
        if sum(valores) == 0:
            st.error("Ingrese datos para procesar.")
        else:
            media = np.mean(valores); sd = np.std(valores, ddof=1); cv = (sd/media)*100
            sigma = (tea_clia - abs(sesgo_peec)) / cv
            
            # Métricas Sigma
            st.subheader("Informe de Desempeño Sigma")
            col_s1, col_s2 = st.columns([1, 2])
            col_s1.metric("Sigma Intermedio", f"{sigma:.2f} σ")
            if sigma >= 6: col_s2.success("Calidad de Clase Mundial (6 Sigma)")
            elif sigma >= 3: col_s2.warning("Calidad Marginal (Requiere control estricto)")
            else: col_s2.error("Calidad No Aceptable (Fuera de control)")

            # Gráfico de Levey-Jennings
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(range(1,21), valores, 'bo-', label="Control Diario")
            ax.axhline(media, color='green', label='Media')
            ax.axhline(media + 2*sd, color='orange', ls='--', label='±2 SD')
            ax.axhline(media + 3*sd, color='red', ls='-', label='±3 SD')
            ax.set_title(f"Levey-Jennings: Precisión Intermedia {analito}")
            ax.set_ylabel(unidad); ax.set_xlabel("Día"); ax.legend(bbox_to_anchor=(1,1))
            st.pyplot(fig)
