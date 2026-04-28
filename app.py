import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# 1. Configuración de la App
st.set_page_config(page_title="Gantt Pro Chile", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { background-color: #1e5631; color: white; border-radius: 8px; height: 3em; width: 100%;}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Generador de Plan de Trabajo Preventivo")

# 2. Información del Proyecto
with st.expander("📝 Datos del Proyecto / Empresa", expanded=True):
    col1, col2 = st.columns(2)
    empresa = col1.text_input("Empresa", "Nombre de la Empresa S.A.")
    proyecto = col2.text_input("Proyecto / Obra", "Instalación de Faenas")

# 3. Datos de entrada
if 'data_v5' not in st.session_state:
    data = {
        "ACTIVIDAD / HITO": ["GESTIÓN PREVENTIVA", "Inducción hombre nuevo", "IDENTIFICACIÓN DE PELIGROS", "Matriz IPER"],
        "RESPONSABLE": ["Prevencionista" for _ in range(4)],
        "FRECUENCIA": ["Mensual" for _ in range(4)],
        "INICIO": [datetime.now().date()] * 4,
        "FIN": [(datetime.now() + timedelta(days=15)).date()] * 4,
        "CUMPLIMIENTO %": [0] * 4
    }
    st.session_state.data_v5 = pd.DataFrame(data)

# 4. Editor de Datos
df_editado = st.data_editor(st.session_state.data_v5, num_rows="dynamic", use_container_width=True)

# 5. Gráfico de Gantt Profesional
df_plot = df_editado[df_editado["ACTIVIDAD / HITO"].str.strip() != ""].copy()
if not df_plot.empty:
    df_plot["Tipo"] = df_plot["ACTIVIDAD / HITO"].apply(lambda x: "HITO" if str(x).isupper() else "TAREA")
    fig = px.timeline(
        df_plot, x_start="INICIO", x_end="FIN", y="ACTIVIDAD / HITO",
        color="Tipo", color_discrete_map={"HITO": "#004d40", "TAREA": "#4db6ac"},
        template="plotly_white", title="Cronograma Operativo SSO"
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# 6. EXPORTACIÓN EXCEL CORREGIDA
st.markdown("---")
buffer = io.BytesIO()

# El nombre de la hoja DEBE ser idéntico en ambos lados
sheet_name = 'Plan_Trabajo'

with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_editado.to_excel(writer, index=False, sheet_name=sheet_name, startrow=4)
    
    workbook  = writer.book
    worksheet = writer.sheets[sheet_name] # <--- CORREGIDO: Ahora coinciden

    # Formatos de Excel
    fmt_header = workbook.add_format({'bold': True, 'bg_color': '#1e5631', 'font_color': 'white', 'border': 1, 'align': 'center'})
    fmt_titulo = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#1e5631'})
    fmt_hito   = workbook.add_format({'bold': True, 'bg_color': '#e0f2f1', 'border': 1})
    fmt_normal = workbook.add_format({'border': 1})

    # Encabezados estéticos
    worksheet.write('A1', 'PLAN DE TRABAJO PREVENTIVO - CHILE', fmt_titulo)
    worksheet.write('A2', f'EMPRESA: {empresa}')
    worksheet.write('A3', f'PROYECTO: {proyecto}')

    # Aplicar formato a la tabla
    for col_num, value in enumerate(df_editado.columns.values):
        worksheet.write(4, col_num, value, fmt_header)
        worksheet.set_column(col_num, col_num, 22)

    for row_num in range(len(df_editado)):
        task = str(df_editado.iloc[row_num, 0])
        estilo = fmt_hito if task.isupper() else fmt_normal
        for col_num in range(len(df_editado.columns)):
            val = df_editado.iloc[row_num, col_num]
            if isinstance(val, (datetime, pd.Timestamp)):
                val = val.strftime('%d-%m-%Y')
            worksheet.write(row_num + 5, col_num, val, estilo)

st.download_button(
    label="📥 DESCARGAR EXCEL PROFESIONAL",
    data=buffer.getvalue(),
    file_name=f"Plan_Trabajo_{empresa}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
