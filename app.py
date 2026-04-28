import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# 1. Configuración de la App
st.set_page_config(page_title="Generador Plan de Trabajo - ChilePrevención Style", layout="wide")

# Estilo para la interfaz de Streamlit
st.markdown("""
    <style>
    .stHeader { color: #1e5631; }
    .stButton>button { background-color: #1e5631; color: white; font-weight: bold; border-radius: 5px; height: 3em;}
    </style>
    """, unsafe_allow_html=True)

st.title("📑 Plan de Trabajo Preventivo (Art. 8, DS 40)")
st.write("Herramienta técnica para la generación de Cartas Gantt de cumplimiento normativo.")

# 2. Información del Proyecto (Para el encabezado del Excel)
with st.expander("🏗️ Información de la Empresa / Proyecto", expanded=True):
    col_emp1, col_emp2, col_emp3 = st.columns(3)
    nombre_empresa = col_emp1.text_input("Nombre de la Empresa", "EMPRESA DE EJEMPLO SPA")
    rut_empresa = col_emp2.text_input("RUT Empresa", "12.345.678-9")
    obra_proyecto = col_emp3.text_input("Obra / Faena", "Proyecto Central")

# 3. Sidebar de Configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    num_filas = st.number_input("Número de actividades:", min_value=1, value=12)
    st.info("**Tip:** Las actividades en MAYÚSCULAS se marcarán como Títulos de Sección con color sólido.")

# 4. Datos Iniciales
if 'df_chile' not in st.session_state or len(st.session_state.df_chile) != num_filas:
    data = {
        "ACTIVIDAD / HITO": ["POLÍTICA DE SEGURIDAD Y SALUD", "Elaborar política SST", "Difundir política", "IDENTIFICACIÓN DE RIESGOS", "Matriz IPER"] + [""] * (num_filas - 5),
        "RESPONSABLE": ["Prevencionista" for _ in range(num_filas)],
        "FRECUENCIA": ["Mensual" for _ in range(num_filas)],
        "MEDIO DE VERIFICACIÓN": ["Registro / Acta" for _ in range(num_filas)],
        "INICIO": [datetime.now().date()] * num_filas,
        "FIN": [(datetime.now() + timedelta(days=15)).date()] * num_filas,
        "AVANCE %": [0 for _ in range(num_filas)]
    }
    st.session_state.df_chile = pd.DataFrame(data)

# 5. Editor de Datos
df_editado = st.data_editor(st.session_state.df_chile, num_rows="dynamic", use_container_width=True)

# 6. Visualización Gantt (En pantalla)
df_plot = df_editado[df_editado["ACTIVIDAD / HITO"].str.strip() != ""].copy()
if not df_plot.empty:
    df_plot["Tipo"] = df_plot["ACTIVIDAD / HITO"].apply(lambda x: "Título" if str(x).isupper() else "Tarea")
    fig = px.timeline(
        df_plot, x_start="INICIO", x_end="FIN", y="ACTIVIDAD / HITO",
        color="Tipo", color_discrete_map={"Título": "#1e5631", "Tarea": "#81c784"},
        template="plotly_white"
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# 7. EXPORTACIÓN NIVEL PREMIUM (XLSXWRITER)
st.markdown("---")
buffer = io.BytesIO()

with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    # No escribimos el dataframe directamente para controlar la posición
    df_editado.to_excel(writer, index=False, sheet_name='PLAN DE TRABAJO', startrow=5)
    
    workbook  = writer.book
    worksheet = writer.sheets['PLAN DE DE TRABAJO']

    # --- DEFINICIÓN DE FORMATOS ---
    fmt_titulo_doc = workbook.add_format({'bold': True, 'font_size': 16, 'font_color': '#1e5631'})
    fmt_info_label = workbook.add_format({'bold': True, 'bg_color': '#f2f2f2', 'border': 1})
    fmt_info_val   = workbook.add_format({'border': 1})
    
    fmt_header = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter',
        'fg_color': '#1e5631', 'font_color': 'white', 'border': 1
    })
    
    fmt_fila_principal = workbook.add_format({
        'bold': True, 'fg_color': '#c8e6c9', 'border': 1 # Verde suave para resaltar
    })
    
    fmt_celda_normal = workbook.add_format({'border': 1})

    # --- DISEÑO DEL ENCABEZADO ---
    worksheet.write('B2', 'CARTA GANTT PLAN DE TRABAJO PREVENTIVO', fmt_titulo_doc)
    worksheet.write('B3', 'EMPRESA:', fmt_info_label)
    worksheet.write('C3', nombre_empresa, fmt_info_val)
    worksheet.write('B4', 'RUT:', fmt_info_label)
    worksheet.write('C4', rut_empresa, fmt_info_val)
    worksheet.write('D3', 'OBRA / PROYECTO:', fmt_info_label)
    worksheet.write('E3', obra_proyecto, fmt_info_val)
    worksheet.write('D4', 'FECHA EMISIÓN:', fmt_info_label)
    worksheet.write('E4', datetime.now().strftime('%d/%m/%Y'), fmt_info_val)

    # --- FORMATO DE LA TABLA ---
    # Encabezados de columna (Fila 6 en Excel, que es startrow=5)
    columnas = df_editado.columns.values
    for col_num, value in enumerate(columnas):
        worksheet.write(5, col_num, value, fmt_header)
        worksheet.set_column(col_num, col_num, 22) # Ajuste de ancho

    # Filas de datos
    for row_num in range(len(df_editado)):
        task_name = str(df_editado.iloc[row_num, 0])
        # Si es mayúscula, aplicamos formato de fila principal
        current_fmt = fmt_fila_principal if (task_name.isupper() and task_name.strip() != "") else fmt_celda_normal
        
        for col_num in range(len(df_editado.columns)):
            val = df_editado.iloc[row_num, col_num]
            # Formatear fechas
            if isinstance(val, (datetime, pd.Timestamp)):
                val = val.strftime('%d-%m-%Y')
            worksheet.write(row_num + 6, col_num, val, current_fmt)

st.download_button(
    label="📥 DESCARGAR PLAN DE TRABAJO OFICIAL (EXCEL)",
    data=buffer.getvalue(),
    file_name=f"Plan_Trabajo_SSO_{nombre_empresa.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
