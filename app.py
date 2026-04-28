import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# 1. Configuración de la App
st.set_page_config(page_title="Gantt Pro Prevención", layout="wide")

st.markdown("""
    <style>
    .stHeader { color: #1e5631; }
    .stButton>button { background-color: #1e5631; color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("📋 Plan de Trabajo Preventivo Profesional")

# 2. Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    num_filas = st.number_input("Filas de la matriz:", min_value=1, value=12)
    st.info("Escriba en MAYÚSCULAS para resaltar una actividad principal.")

# 3. Datos iniciales
if 'df_v4' not in st.session_state or len(st.session_state.df_v4) != num_filas:
    data = {
        "Actividad / Hito": ["GESTIÓN DE SEGURIDAD", "Elaborar política", "DIFUNDIR POLÍTICA"] + [""] * (num_filas - 3),
        "Responsable": ["Prevencionista" for _ in range(num_filas)],
        "Frecuencia": ["Mensual" for _ in range(num_filas)],
        "Medio de Verificación": ["Registro" for _ in range(num_filas)],
        "Inicio": [datetime.now().date()] * num_filas,
        "Fin": [(datetime.now() + timedelta(days=15)).date()] * num_filas,
        "Avance %": [0 for _ in range(num_filas)]
    }
    st.session_state.df_v4 = pd.DataFrame(data)

# 4. Editor de Datos
df_editado = st.data_editor(st.session_state.df_v4, num_rows="dynamic", use_container_width=True)

# 5. Gráfico de Gantt
df_plot = df_editado[df_editado["Actividad / Hito"].str.strip() != ""].copy()
if not df_plot.empty:
    df_plot["Tipo"] = df_plot["Actividad / Hito"].apply(lambda x: "Principal" if str(x).isupper() else "Secundaria")
    fig = px.timeline(
        df_plot, x_start="Inicio", x_end="Fin", y="Actividad / Hito",
        color="Tipo", color_discrete_map={"Principal": "#1e5631", "Secundaria": "#81c784"},
        template="plotly_white"
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# 6. EXPORTACIÓN CON ESTÉTICA PROFESIONAL (XLSXWRITER)
st.markdown("---")
buffer = io.BytesIO()

# Crear el Excel con formato
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_editado.to_excel(writer, index=False, sheet_name='Plan de Trabajo')
    
    workbook  = writer.book
    worksheet = writer.sheets['Plan de Trabajo']

    # Formatos
    header_fmt = workbook.add_format({
        'bold': True, 'text_wrap': True, 'valign': 'vcenter',
        'fg_color': '#1e5631', 'font_color': 'white', 'border': 1
    })
    main_task_fmt = workbook.add_format({'bold': True, 'bg_color': '#e8f5e9', 'border': 1})
    normal_fmt = workbook.add_format({'border': 1})

    # Aplicar formato a encabezados
    for col_num, value in enumerate(df_editado.columns.values):
        worksheet.write(0, col_num, value, header_fmt)
        worksheet.set_column(col_num, col_num, 20) # Ancho de columna

    # Aplicar formato a las filas según si es principal o no
    for row_num in range(len(df_editado)):
        task_name = str(df_editado.iloc[row_num, 0])
        fmt = main_task_fmt if task_name.isupper() else normal_fmt
        for col_num in range(len(df_editado.columns)):
            worksheet.write(row_num + 1, col_num, df_editado.iloc[row_num, col_num], fmt)

st.download_button(
    label="📥 Descargar Excel con Estética Profesional",
    data=buffer.getvalue(),
    file_name=f"Plan_Trabajo_SSO_{datetime.now().year}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
