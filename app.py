import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuración de página
st.set_page_config(page_title="Gantt Pro SSO", layout="wide")

# Estilo CSS Corregido
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; }
    @media print {
        .stButton, .stDownloadButton, .stSelectbox, .stNumberInput, .css-1dp5ugw { display: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Gestión de Prevención de Riesgos")

## --- CONTROLES LATERALES ---
with st.sidebar:
    st.header("Configuración")
    num_filas = st.number_input("Número de ítems:", min_value=1, value=10)
    
    opciones_colores = {"Azul": "Blues", "Verde": "Greens", "Naranja": "Oranges"}
    color_sel = st.selectbox("Color del Gráfico:", list(opciones_colores.keys()))
    
    st.markdown("---")
    # Botón para imprimir PDF (Usa JS para llamar al navegador)
    if st.button("🖨️ Generar Reporte PDF"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
        st.info("Se ha abierto la ventana de impresión. Seleccione 'Guardar como PDF'.")

# 1. Datos iniciales
data_inicial = {
    "ID": [f"PR-{i+1:03}" for i in range(num_filas)],
    "Actividad": ["" for _ in range(num_filas)],
    "Inicio": [datetime.now().date()] * num_filas,
    "Fin": [(datetime.now() + timedelta(days=15)).date()] * num_filas,
    "Avance %": [0.0] * num_filas
}
df_base = pd.DataFrame(data_inicial)

# 2. Editor
st.subheader("📝 Matriz de Actividades")
df_editado = st.data_editor(df_base, num_rows="dynamic", use_container_width=True)

# 3. Gráfico
if not df_editado.empty and (df_editado["Actividad"] != "").any():
    fig = px.timeline(
        df_editado[df_editado["Actividad"] != ""],
        x_start="Inicio", x_end="Fin", y="Actividad",
        color="Avance %", color_continuous_scale=opciones_colores[color_sel],
        template="plotly_white"
    )
    fig.update_yaxes(autorange="reversed")
    # Selectores de meses/semestres
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1 mes", step="month", stepmode="backward"),
                dict(count=6, label="1 sem", step="month", stepmode="backward"),
                dict(step="all", label="Ver todo")
            ])
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# 4. EXPORTACIÓN A EXCEL (Mejor que CSV)
st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df_editado.to_excel(writer, index=False, sheet_name='Gantt_SSO')

st.download_button(
    label="📥 Descargar para Excel (.xlsx)",
    data=buffer.getvalue(),
    file_name=f"Plan_SSO_{datetime.now().date()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
