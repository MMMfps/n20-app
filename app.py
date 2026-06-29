import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuracion profesional de la pagina
st.set_page_config(
    page_title="Verificacion N20 - Calidad Analitica", 
    page_icon="🔬", 
    layout="wide"
)

# Titulo principal
st.title("🔬 Herramienta de Verificacion Metrologica: N20")
st.markdown("""
Esta aplicacion automatiza el calculo de imprecision para la verificacion de metodos en el laboratorio clinico, 
basado en **20 replicas (N20)** del mismo analito.
""")

st.sidebar.header("⚙️ Configuracion del Analito")
analito = st.sidebar.text_input("Nombre del Analito:", value="Glucosa")
unidad = st.sidebar.text_input("Unidad de medida:", value="mg/dL")
tea_permitido = st.sidebar.number_input("Error Total Aceptable (TEa o CV% Maximo) deseado:", value=5.0, step=0.1)

st.markdown("---")

st.subheader(f"🔢 Ingrese los 20 resultados para: {analito} ({unidad})")
st.info("Modifique los valores de la tabla a continuacion con sus datos reales:")

# Creamos una estructura de datos vacia (20 filas) para que el usuario llne como Excel
datos_iniciales = {"Replica": [f"R{i}" for i in range(1, 21)], "Resultado": [0.0] * 20}
df_input = pd.DataFrame(datos_iniciales)

# Usamos el editor de datos interactivo de Streamlit (parecido a un Excel integrado)
df_editado = st.data_editor(df_input, num_rows="fixed", use_container_width=True, hide_index=True)

st.markdown("---")

# Boton de calculo
if st.button("📊 Ejecutar Analisis Estadistico", type="primary"):
    lista_valores = df_editado["Resultado"].tolist()
    
    # Validamos que el usuario haya metido datos
    if sum(lista_valores) == 0:
        st.error("❌ Todos los valores estan en 0. Por favor, ingrese sus datos analiticos en la tabla.")
    else:
        # Convertir a numpy para calculos
        datos = np.array(lista_valores)
        media = np.mean(datos)
        sd = np.std(datos, ddof=1) # SD muestral
        cv = (sd / media) * 100
        
        # Despliegue de Resultados en Tarjetas
        st.subheader("📋 Informe de Imprecision Muestral")
        
        c1, c2, c3 = st.columns(3)
        c1.metric(label=f"Media de {analito}", value=f"{media:.4f} {unidad}")
        c2.metric(label="Desviacion Estandar (SD)", value=f"{sd:.4f}")
        c3.metric(label="Coeficiente de Variacion Calculado (CV%)", value=f"{cv:.2f}%")
        
        st.markdown("---")
        
        # Evaluacion automatica de calidad
        st.subheader("🎯 Evaluacion de Desempeno Analitico")
        if cv <= tea_permitido:
            st.success(f"✅ **APROBADO**: El CV% obtenido ({cv:.2f}%) es MENOR o igual al limite permitido ({tea_permitido:.2f}%). El metodo demuestra una imprecision aceptable.")
        else:
            st.error(f"🚨 **RECHAZADO**: El CV% obtenido ({cv:.2f}%) SUPERÓ el limite establecido ({tea_permitido:.2f}%). Se sugiere revisar la calibracion, el lote de reactivo o el estado del sistema optico/pipeteo.")
        
        st.markdown("---")
        
        # Generacion de la Grafica de Levey-Jennings al final
        st.subheader("📈 Grafico de Levey-Jennings (N20)")
        
        # Crear la figura de Matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Graficar los puntos introducidos por el usuario
        replicas_numeros = list(range(1, 21))
        ax.plot(replicas_numeros, datos, marker="o", linestyle="-", color="black", label="Valores N20")
        
        # Dibujar lineas horizontales de control basadas en los datos calculados
        ax.axhline(media, color="green", linestyle="-", label=f"Media ({media:.2f})")
        
        ax.axhline(media + sd, color="orange", linestyle="--", alpha=0.5)
        ax.axhline(media - sd, color="orange", linestyle="--", alpha=0.5)
        
        ax.axhline(media + 2*sd, color="blue", linestyle="--", label=f"+2 SD ({(media + 2*sd):.2f})")
        ax.axhline(media - 2*sd, color="blue", linestyle="--", label=f"-2 SD ({(media - 2*sd):.2f})")
        
        ax.axhline(media + 3*sd, color="red", linestyle="-", label=f"+3 SD ({(media + 3*sd):.2f})")
        ax.axhline(media - 3*sd, color="red", linestyle="-", label=f"-3 SD ({(media - 3*sd):.2f})")
        
        # Ajustes esteticos del grafico
        ax.set_title(f"Grafico de Control para {analito} ({unidad})")
        ax.set_xlabel("Numero de Replica")
        ax.set_ylabel(f"Concentracion ({unidad})")
        ax.set_xticks(replicas_numeros)
        ax.grid(axis="x", alpha=0.3)
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1)) # Pone la leyenda afuera para que no tape los puntos
        
        # Renderizar el grafico de Matplotlib en la interfaz de Streamlit
        st.pyplot(fig)
