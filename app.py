import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# 1. Configuración de Marca y Estilo
st.set_page_config(page_title="Plan de Trabajo Preventivo", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9fbf9; }
    .stHeader { color: #1e5631; }
    div[data-testid="stMetricValue"] { color: #1e5631; font-weight: bold; }
    .stButton>button { background-color: #1e5631; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Encabezado tipo Informe
col_logo, col_titulo = st.columns([1, 4])
with col_titulo:
    st.title("📋 Carta Gantt: Plan de Trabajo Preventivo")
    st.write("**Normativa:** Art. 8, DS 40/44 - Gestión de Seguridad y Salud en el Trabajo")

# 3. Panel Lateral
with st.sidebar:
    st.header("⚙️ Configuración")
    num_filas = st.number_input("Cantidad de actividades:", min_value=1, value=8)
    st.markdown("---")
    st.success("Esta herramienta genera el cronograma y la matriz de cumplimiento lista para descargar.")

# 4. Estructura de Datos (Basada en tus imágenes)
if 'df_seguridad' not in st.session_state or len(st.session_state.df_seguridad) != num_filas:
    actividades_pro = [
        "Elaboración de Política SST", "Identificación de Riesgos", 
        "Capacitación de uso de EPP", "Simulacro de Emergencia",
        "Inspección de Herramientas", "Reunión Comité Paritario"
    ]
    data = {
        "Actividad": [(actividades_pro[i] if i < len(actividades_pro) else "") for i in range(num_filas)],
        "Responsable": ["Representante Legal / Prevencionista" for _ in range(num_filas)],
        "Frecuencia": ["Mensual" for _ in range(num_filas)],
        "Medio de Verificación": ["Registro de Asistencia" for _ in range(num_filas)],
        "Inicio": [datetime.now().date()] * num_filas,
        "Fin": [(datetime.now() + timedelta(days=30)).date()] * num_filas,
        "Cumplimiento %": [0 for _ in range(num_filas)]
    }
    st.session_state.df_seguridad = pd.DataFrame(data)

# 5. Matriz de Trabajo Editable
st.subheader("📝 Matriz de Planificación")
df_editado = st.data_editor(
    st.session_state.df_seguridad,
    column_config={
        "Actividad": st.column_config.TextColumn("Actividad / Hito", width="large"),
        "Frecuencia": st.column_config.SelectboxColumn("Frecuencia", options=["Única", "Mensual", "Semestral", "Anual"]),
        "Medio de Verificación": st.column_config.TextColumn("Evidencia (Doc/Registro)"),
        "Cumplimiento %": st.column_config.ProgressColumn("Avance", min_value=0, max_value=100, format="%d%%"),
        "Inicio": st.column_config.DateColumn("Fecha Programada"),
        "Fin": st.column_config.DateColumn("Fecha Revisión"),
    },
    num_rows="dynamic",
    use_container_width=True
)

# 6. Gráfico de Gantt Estilo "Chile Prevención"
df_plot = df_editado[df_editado["Actividad"].str.strip() != ""].copy()

if not df_plot.empty:
    st.markdown("---")
    st.subheader("📊 Cronograma de Actividades Planificadas")
    
    fig = px.timeline(
        df_plot,
        x_start="Inicio",
        x_end="Fin",
        y="Actividad",
        color="Cumplimiento %",
        hover_data=["Responsable", "Medio de Verificación", "Frecuencia"],
        color_continuous_scale=["#e8f5e9", "#2e7d32"], # Escala de verdes
        range_color=[0, 100],
        template="plotly_white"
    )

    fig.update_yaxes(autorange="reversed", title="")
    fig.update_xaxes(
        title="Meses de Ejecución",
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="Mes", step="month", stepmode="backward"),
                dict(count=6, label="Semestre", step="month", stepmode="backward"),
                dict(step="all", label="Año Completo")
            ])
        ),
        rangeslider=dict(visible=True, thickness=0.03)
    )

    st.plotly_chart(fig, use_container_width=True)

# 7. Descarga de Reporte a Excel
st.markdown("---")
col_descarga1, col_descarga2 = st.columns(2)

with col_descarga1:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_editado.to_excel(writer, index=False, sheet_name='Plan de Trabajo')
    
    st.download_button(
        label="📥 Descargar Plan de Trabajo en Excel",
        data=buffer.getvalue(),
        file_name=f"Plan_Trabajo_Preventivo_{datetime.now().year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with col_descarga2:
    st.info("💡 **Tip:** Para obtener el PDF, presiona **Ctrl + P**, elige 'Guardar como PDF' y activa 'Gráficos de fondo' en la configuración.")
