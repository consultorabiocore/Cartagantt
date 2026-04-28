import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# 1. Configuración Profesional
st.set_page_config(page_title="Plan Preventivo Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; border-left: 5px solid #1e5631; }
    </style>
    """, unsafe_allow_html=True)

st.title("📋 Plan de Trabajo Preventivo (DS 40)")
st.caption("Para crear una **Actividad Principal**, escríbela en MAYÚSCULAS o inicia con un asterisco (*).")

# 2. Barra Lateral
with st.sidebar:
    st.header("⚙️ Opciones")
    num_filas = st.number_input("Filas de la matriz:", min_value=1, value=12)
    st.markdown("---")
    st.info("El gráfico agrupa por colores: las tareas principales resaltan sobre las secundarias.")

# 3. Datos con Estructura de Ejemplo (Jerárquica)
if 'df_gantt_v3' not in st.session_state or len(st.session_state.df_gantt_v3) != num_filas:
    data = {
        "Actividad / Hito": [
            "* GESTIÓN ADMINISTRATIVA", "Elaborar política SST", "Difundir política",
            "* IDENTIFICACIÓN DE RIESGOS", "Matriz IPER", "Actualizar matriz",
            "* MEDIDAS DE CONTROL", "Entrega de EPP", "Capacitaciones"
        ] + [""] * (max(0, num_filas - 9)),
        "Responsable": ["Prevencionista" for _ in range(num_filas)],
        "Frecuencia": ["Mensual" for _ in range(num_filas)],
        "Medio de Verificación": ["Registro" for _ in range(num_filas)],
        "Inicio": [datetime.now().date()] * num_filas,
        "Fin": [(datetime.now() + timedelta(days=15)).date()] * num_filas,
        "Avance %": [0 for _ in range(num_filas)]
    }
    st.session_state.df_gantt_v3 = pd.DataFrame(data)

# 4. Editor de Datos
df_editado = st.data_editor(
    st.session_state.df_gantt_v3,
    column_config={
        "Actividad / Hito": st.column_config.TextColumn(width="large"),
        "Avance %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d%%"),
        "Inicio": st.column_config.DateColumn(),
        "Fin": st.column_config.DateColumn(),
    },
    num_rows="dynamic",
    use_container_width=True
)

# 5. Lógica de Colores para Jerarquía
def definir_tipo(row):
    nombre = str(row["Actividad / Hito"])
    if nombre.startswith("*") or nombre.isupper():
        return "Principal"
    return "Secundaria"

if not df_editado.empty:
    df_plot = df_editado[df_editado["Actividad / Hito"].str.strip() != ""].copy()
    
    if not df_plot.empty:
        # Aplicamos la lógica de tipo
        df_plot["Tipo"] = df_plot.apply(definir_tipo, axis=1)

        # Gráfico con distinción de colores
        fig = px.timeline(
            df_plot,
            x_start="Inicio",
            x_end="Fin",
            y="Actividad / Hito",
            color="Tipo", 
            # Definimos colores manuales: Verde oscuro para principales, Verde claro para secundarias
            color_discrete_map={"Principal": "#1e5631", "Secundaria": "#81c784"},
            hover_data=["Responsable", "Avance %", "Medio de Verificación"],
            template="plotly_white"
        )

        fig.update_yaxes(autorange="reversed", title="")
        
        # Selectores de Tiempo (Mes/Semestre)
        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1 Mes", step="month", stepmode="backward"),
                    dict(count=6, label="1 Semestre", step="month", stepmode="backward"),
                    dict(step="all", label="Ver Todo")
                ])
            ),
            rangeslider=dict(visible=True, thickness=0.03)
        )

        st.plotly_chart(fig, use_container_width=True)

# 6. Exportar a Excel
st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df_editado.to_excel(writer, index=False, sheet_name='Plan de Trabajo')

st.download_button(
    label="📥 Descargar Plan de Trabajo (.xlsx)",
    data=buffer.getvalue(),
    file_name=f"Plan_Trabajo_SSO_{datetime.now().strftime('%Y')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
