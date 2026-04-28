import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# 1. Configuración de Interfaz
st.set_page_config(page_title="Gantt Pro Prevención", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #1e5631; color: white; border-radius: 10px; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

st.title("📑 Plan de Trabajo Preventivo (Art. 8, DS 40)")

# 2. Datos de Cabecera
col_a, col_b = st.columns(2)
with col_a:
    empresa = st.text_input("Empresa Cliente", "Empresa de Servicios S.A.")
    rut = st.text_input("RUT Empresa", "76.000.000-K")
with col_b:
    proyecto = st.text_input("Obra / Proyecto", "Mantenimiento Planta Central")
    emisor = st.text_input("Elaborado por", "Experto en Prevención de Riesgos")

# 3. Estructura de Datos
if 'df_final' not in st.session_state:
    data = {
        "ACTIVIDAD / HITO": ["POLÍTICA SST", "Elaborar documento", "GESTIÓN RIESGOS", "Matriz IPER", "Instalar señalética"],
        "RESPONSABLE": ["Prevencionista" for _ in range(5)],
        "FRECUENCIA": ["Anual", "Mensual", "Anual", "Mensual", "Mensual"],
        "INICIO": [datetime.now().date()] * 5,
        "FIN": [(datetime.now() + timedelta(days=15)).date()] * 5,
        "CUMPLIMIENTO %": [0] * 5
    }
    st.session_state.df_final = pd.DataFrame(data)

# 4. Editor de Datos
df_editado = st.data_editor(st.session_state.df_final, num_rows="dynamic", use_container_width=True)

# 5. Exportación Estética (XLSXWRITER)
st.markdown("---")
buffer = io.BytesIO()

with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    # Escribimos los datos empezando en la fila 7 para dejar espacio al encabezado
    df_editado.to_excel(writer, index=False, sheet_name='Plan_Trabajo', startrow=7)
    
    workbook  = writer.book
    worksheet = writer.sheets['Plan_Trabajo']

    # --- DEFINICIÓN DE FORMATOS ---
    f_titulo = workbook.add_format({'bold': True, 'font_size': 16, 'font_color': '#1e5631', 'align': 'center'})
    f_sub = workbook.add_format({'bold': True, 'bg_color': '#f2f2f2', 'border': 1})
    f_val = workbook.add_format({'border': 1})
    f_header = workbook.add_format({'bold': True, 'bg_color': '#1e5631', 'font_color': 'white', 'border': 1, 'align': 'center'})
    f_principal = workbook.add_format({'bold': True, 'bg_color': '#c8e6c9', 'border': 1}) # Verde ChilePrevención
    f_normal = workbook.add_format({'border': 1})

    # --- DISEÑO DEL ENCABEZADO (Igual a ChilePrevención) ---
    worksheet.merge_range('A1:F2', 'CARTA GANTT: PLAN DE TRABAJO PREVENTIVO PERSONALIZADO', f_titulo)
    
    worksheet.write('A4', 'EMPRESA:', f_sub)
    worksheet.write('B4', empresa, f_val)
    worksheet.write('A5', 'RUT:', f_sub)
    worksheet.write('B5', rut, f_val)
    
    worksheet.write('C4', 'PROYECTO:', f_sub)
    worksheet.write('D4', proyecto, f_val)
    worksheet.write('C5', 'ELABORÓ:', f_sub)
    worksheet.write('D5', emisor, f_val)

    # --- FORMATO DE TABLA ---
    for col_num, value in enumerate(df_editado.columns.values):
        worksheet.write(7, col_num, value, f_header)
        worksheet.set_column(col_num, col_num, 22)

    for row_num in range(len(df_editado)):
        task = str(df_editado.iloc[row_num, 0])
        # Si es mayúscula es Actividad Principal
        style = f_principal if (task.isupper() and task.strip() != "") else f_normal
        
        for col_num in range(len(df_editado.columns)):
            val = df_editado.iloc[row_num, col_num]
            if isinstance(val, (datetime, pd.Timestamp)):
                val = val.strftime('%d-%m-%Y')
            worksheet.write(row_num + 8, col_num, val, style)

st.download_button(
    label="📥 DESCARGAR PLAN DE TRABAJO (FORMATO OFICIAL)",
    data=buffer.getvalue(),
    file_name=f"Plan_SSO_{empresa.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
