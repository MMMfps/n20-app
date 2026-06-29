import streamlit as st
import numpy as np
import pandas as pd

Configuración profesional de la página
st.set_page_config(
page_title="Verificación N20 - Calidad Analítica",
page_icon="🔬",
layout="wide"
)

Título principal
st.title("🔬 Herramienta de Verificación Metrológica: N20")
st.markdown("""
Esta aplicación automatiza el cálculo de imprecisión para la verificación de métodos en el laboratorio clínico,
basado en 20 réplicas (N20) del mismo analito.
""")

st.sidebar.header("⚙️ Configuración del Analito")
analito = st.sidebar.text_input("Nombre del Analito:", value="Glucosa")
unidad = st.sidebar.text_input("Unidad de medida:", value="mg/dL")
tea_permitido = st.sidebar.number_input("Error Total Aceptable (TEa o CV% Máximo) deseado:", value=5.0, step=0.1)

st.markdown("---")

st.subheader(f"🔢 Ingrese los 20 resultados para: {analito} ({unidad})")
st.info("Modifique los valores de la tabla a continuación con sus datos reales:")

Creamos una estructura de datos vacía (20 filas) para que el usuario llene como Excel
datos_iniciales = {"Réplica": [f"R{i}" for i in range(1, 21)], "Resultado": [0.0] * 20}
df_input = pd.DataFrame(datos_iniciales)

Usamos el editor de datos interactivo de Streamlit (parecido a un Excel integrado)
df_editado = st.data_editor(df_input, num_rows="fixed", use_container_width=True, hide_index=True)

st.markdown("---")

Botón de cálculo
if st.button("📊 Ejecutar Análisis Estadístico", type="primary"):
lista_valores = df_editado["Resultado"].tolist()

# Validamos que el usuario haya metido datos
if sum(lista_valores) == 0:
st.error("❌ Todos los valores están en 0. Por favor, ingrese sus datos analíticos en la tabla.")
else:
# Convertir a numpy para cálculos
datos = np.array(lista_valores)
media = np.mean(datos)
sd = np.std(datos, ddof=1) # SD muestral
cv = (sd / media) * 100

# Despliegue de Resultados en Tarjetas
st.subheader("📋 Informe de Imprecisión Muestral")

c1, c2, c3 = st.columns(3)
c1.metric(label=f"Media (

) de {analito}", value=f"{media:.4f} {unidad}")
c2.metric(label="Desviación Estándar (SD)", value=f"{sd:.4f}")
c3.metric(label="Coeficiente de Variación Calculado (CV%)", value=f"{cv:.2f}%")

st.markdown("---")

# Evaluación automática de calidad
st.subheader("🎯 Evaluación de Desempeño Analítico")
if cv <= tea_permitido:
st.success(f"✅ APROBADO: El CV% obtenido ({cv:.2f}%) es MENOR o igual al límite permitido ({tea_permitido:.2f}%). El método demuestra una imprecisión aceptable.")
else:
st.error(f"🚨 RECHAZADO: El CV% obtenido ({cv:.2f}%) SUPERÓ el límite establecido ({tea_permitido:.2f}%). Se sugiere revisar la calibración, el lote de reactivo o el estado del sistema óptico/pipeteo.")