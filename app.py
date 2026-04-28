import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuración de página
st.set_page_config(page_title="Sistema de Gestión de Seguridad - Gantt Pro", layout="wide")

# Estilo CSS para limpieza visual
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🛡️ Control de Gestión de Prevención de Riesgos")
st.markdown("---")

## --- BARRA LATERAL: CONFIGURACIÓN Y PERSONALIZACIÓN ---
with st.sidebar:
    st.header("⚙️ Configuración del Plan")
    num_filas = st.number_input("Número de ítems:", min_value=1, max_value=100, value=10)
    
    st.markdown("---")
    st.header("🎨 Personalización Visual")
    # Selector de color: 'Blues' es el predefinido
    opciones_colores = {
        "Azul Corporativo (Default)": "Blues",
        "Esmeralda Seguridad": "Greens",
        "Contraste Térmico": "Viridis",
        "Alerta / Energía": "Magma",
        "Escala de Grises": "Greys"
    }
    color_seleccionado = st.selectbox(
        "Seleccione la paleta de colores del gráfico:",
        options=list(opciones_colores.keys()),
        index=0 # Blues por defecto
    )
    paleta_plotly = opciones_colores[color_seleccionado]

    st.markdown("---")
    st.info("Utilice esta herramienta para reportes mensuales o semestrales de cumplimiento normativo.")

# 1. Estructura de datos
if 'data' not in st.session_state:
    data_inicial = {
        "ID": [f"PR-{i+1:03}" for i in range(num_filas)],
        "Actividad": ["" for _ in range(num_filas)],
        "Responsable": ["Prevencionista" for _ in range(num_filas)],
        "Inicio": [datetime.now().date()] * num_filas,
        "Fin": [(datetime.now() + timedelta(days=30)).date()] * num_filas,
        "Estado": ["Programado"] * num_filas,
        "Avance %": [0.0] * num_filas
    }
    st.session_state.data = pd.DataFrame(data_inicial)

# 2. KPIs Superiores
col1, col2, col3 = st.columns(3)

# 3. Editor de Datos Profesional
st.markdown("### 📋 Matriz de Planificación Operativa")
df_editado = st.data_editor(
    st.session_state.data,
    column_config={
        "ID": st.column_config.TextColumn(disabled=True),
        "Actividad": st.column_config.TextColumn(width="large", placeholder="Describa la tarea..."),
        "Estado": st.column_config.SelectboxColumn(options=["Programado", "En Curso", "Detenido", "Finalizado"]),
        "Avance %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%"),
        "Inicio": st.column_config.DateColumn(),
        "Fin": st.column_config.DateColumn(),
    },
    num_rows="dynamic",
    use_container_width=True,
    key="editor_gantt"
)

# Actualizar métricas
avance_prom = df_editado["Avance %"].mean() if not df_editado.empty else 0
col1.metric("Actividades Planificadas", len(df_editado))
col2.metric("Cumplimiento Promedio", f"{avance_prom:.1f}%")
col3.metric("Estatus del Plan", "Vigente")

# 4. Gráfico Gantt Interactiva con Color Dinámico
if not df_editado.empty and (df_editado["Actividad"].str.strip() != "").any():
    st.markdown("### 📊 Línea de Tiempo Ejecutiva")
    
    # Filtrar solo filas que tengan nombre de actividad para no ensuciar el gráfico
    df_plot = df_editado[df_editado["Actividad"].str.strip() != ""]

    fig = px.timeline(
        df_plot,
        x_start="Inicio",
        x_end="Fin",
        y="Actividad",
        color="Avance %",
        hover_data=["Responsable", "Estado"],
        color_continuous_scale=paleta_plotly, # Usamos la variable del selector
        template="plotly_white"
    )

    fig.update_yaxes(autorange="reversed", title="")
    fig.update_xaxes(
        title="Cronograma de Ejecución",
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="VISTA MENSUAL", step="month", stepmode="backward"),
                dict(count=6, label="VISTA SEMESTRAL", step="month", stepmode="backward"),
                dict(step="all", label="VER TODO")
            ]),
            bgcolor="#e9ecef"
        ),
        rangeslider=dict(visible=True, thickness=0.05)
    )

    fig.update_layout(
        height=400 + (len(df_plot) * 20), # Altura dinámica según tareas
        margin=dict(l=10, r=10, t=50, b=10),
        coloraxis_colorbar=dict(title="Progreso")
    )

    st.plotly_chart(fig, use_container_width=True)

# 5. Exportación
st.download_button(
    label="💾 Exportar Planificación (CSV)",
    data=df_editado.to_csv(index=False).encode('utf-8'),
    file_name=f"Gantt_SSO_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
)
