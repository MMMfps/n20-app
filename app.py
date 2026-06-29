import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuracion profesional de la pagina
st.set_page_config(
    page_title="Verificacion N20 + Six Sigma Real", 
    page_icon="🔬", 
    layout="wide"
)

# Titulo principal
st.title("🔬 Plataforma de Calidad Analítica Avanzada: N20 & Six Sigma")
st.markdown("""
Esta aplicacion automatiza el calculo de imprecision mediante **20 replicas (N20)** y calcula la **Metrica Sigma Real** integrando el error sistematico (Sesgo) de tu control externo o PEEC.
""")

# --- BARRA LATERAL DE CONFIGURACIÓN ---
st.sidebar.header("⚙️ Configuracion del Analito")
analito = st.sidebar.text_input("Nombre del Analito:", value="Glucosa")
unidad = st.sidebar.text_input("Unidad de medida:", value="mg/dL")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Metas Analiticas")
tea_permitido = st.sidebar.number_input("Error Total Aceptable (TEa%) deseado:", value=5.0, step=0.1, help="Margen de error maximo permitido para este analito (ej. CLIA, Variabilidad Biologica).")

# NUEVA CASILLA: Ingreso del Sesgo
sesgo_ingresado = st.sidebar.number_input("Sesgo / Bias (%) del Laboratorio:", value=0.0, step=0.1, help="Introduce el porcentaje de sesgo reportado en tu ultimo informe PEEC, CAP, ISP o RIQAS.")

st.markdown("---")

# --- TABLA DE ENTRADA DE DATOS ---
st.subheader(f"🔢 Ingrese los 20 resultados para: {analito} ({unidad})")
st.info("Modifique los valores de la tabla a continuacion con sus datos reales del protocolo N20:")

datos_iniciales = {"Replica": [f"R{i}" for i in range(1, 21)], "Resultado": [0.0] * 20}
df_input = pd.DataFrame(datos_iniciales)
df_editado = st.data_editor(df_input, num_rows="fixed", use_container_width=True, hide_index=True)

st.markdown("---")

# --- BOTÓN DE CÁLCULO ---
if st.button("📊 Ejecutar Analisis Metrologico Completo", type="primary"):
    lista_valores = df_editado["Resultado"].tolist()
    
    if sum(lista_valores) == 0:
        st.error("❌ Todos los valores estan en 0. Por favor, ingrese sus datos analiticos en la tabla.")
    else:
        # 1. Calculos Estadisticos de Imprecision
        datos = np.array(lista_valores)
        media = np.mean(datos)
        sd = np.std(datos, ddof=1) # SD muestral
        cv = (sd / media) * 100
        
        # 2. Validacion de la formula Sigma Real (Evitar division por cero o numerador negativo)
        sesgo_abs = abs(sesgo_ingresado)
        
        if sesgo_abs >= tea_permitido:
            st.error(f"🚨 **ERROR METROLÓGICO CRÍTICO**: El Sesgo ingresado ({sesgo_abs}%) es MAYOR o igual al TEa permitido ({tea_permitido}%). Tu error sistematico ya consumio todo el margen de error; el calculo de Sigma no es matematicamente viable.")
        else:
            # Formula oficial completa
            sigma = (tea_permitido - sesgo_abs) / cv
            
            # Despliegue de Resultados de precision
            st.subheader("📋 Informe de Imprecision Muestral (N20)")
            c1, c2, c3 = st.columns(3)
            c1.metric(label=f"Media de {analito}", value=f"{media:.4f} {unidad}")
            c2.metric(label="Desviacion Estandar (SD)", value=f"{sd:.4f}")
            c3.metric(label="Coeficiente de Variacion (CV%)", value=f"{cv:.2f}%")
            
            st.markdown("---")
            
            # 3. Seccion de Desempeño Six Sigma Real
            st.subheader("🎯 Evaluacion del Desempeño Six Sigma Real")
            
            col_metric, col_info = st.columns([1, 3])
            with col_metric:
                st.metric(label="Métrica Sigma Real", value=f"{sigma:.2f} σ")
            
            with col_info:
                st.markdown(f"**Variables utilizadas:** TEa: `{tea_permitido}%` | Sesgo: `{sesgo_abs}%` | CV%: `{cv:.2f}%`")
            
            # Semaforo internacional de calidad
            if sigma >= 6.0:
                st.success(f"🟢 **DESEMPEÑO EXCELENTE ({sigma:.2f} σ):** Calidad de clase mundial. El metodo es extremadamente robusto frente a imprecisiones y variaciones de sesgo. Tolerancia maxima a fallas.")
            elif 3.0 <= sigma < 6.0:
                st.warning(f"🟡 **DESEMPEÑO ACEPTABLE ({sigma:.2f} σ):** Calidad controlable. Requiere una planificacion estricta de Control de Calidad Interno (reglas de Westgard y mayor frecuencia de controles).")
            else:
                st.error(f"🔴 **DESEMPEÑO INACEPTABLE ({sigma:.2f} σ):** Calidad inestable. La combinacion de tu Sesgo y tu CV% sobrepasan los limites aceptables. Debes intervenir el ensayo (mantencion, calibracion, revisar matriz).")
            
            st.markdown("---")
            
            # 4. Grafica de Levey-Jennings
            st.subheader("📈 Grafico de Levey-Jennings (N20)")
            fig, ax = plt.subplots(figsize=(10, 5))
            replicas_numeros = list(range(1, 21))
            
            ax.plot(replicas_numeros, datos, marker="o", linestyle="-", color="black", label="Valores N20")
            ax.axhline(media, color="green", linestyle="-", label=f"Media ({media:.2f})")
            
            # Limites SD
            ax.axhline(media + sd, color="orange", linestyle="--", alpha=0.5)
            ax.axhline(media - sd, color="orange", linestyle="--", alpha=0.5)
            ax.axhline(media + 2*sd, color="blue", linestyle="--", label=f"+2 SD ({(media + 2*sd):.2f})")
            ax.axhline(media - 2*sd, color="blue", linestyle="--", label=f"-2 SD ({(media - 2*sd):.2f})")
            ax.axhline(media + 3*sd, color="red", linestyle="-", label=f"+3 SD ({(media + 3*sd):.2f})")
            ax.axhline(media - 3*sd, color="red", linestyle="-", label=f"-3 SD ({(media - 3*sd):.2f})")
            
            ax.set_title(f"Grafico de Control para {analito} ({unidad})")
            ax.set_xlabel("Numero de Replica")
            ax.set_ylabel(f"Concentracion ({unidad})")
            ax.set_xticks(replicas_numeros)
            ax.grid(axis="x", alpha=0.3)
            ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
            
            st.pyplot(fig)
