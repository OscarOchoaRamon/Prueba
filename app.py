import streamlit as st

from processing import load_data, clean_data, merge_data, get_regulation_groups, calculate_reference_statistics
from plotting import create_chart
import os
import shutil

# --- CUSTOM FONT REGISTRATION ---
# --- CUSTOM FONT REGISTRATION ---
# --- CUSTOM FONT REGISTRATION ---
# Attempt to register Bookman Old Style fonts if they exist
# Windows filenames: BOOKOS.TTF (Regular), BOOKOSB.TTF (Bold), BOOKOSI.TTF (Italic), BOOKOSBI.TTF (Bold Italic)
font_files = ["BOOKOS.TTF", "BOOKOSB.TTF", "BOOKOSI.TTF", "BOOKOSBI.TTF", "BookmanOldStyle.ttf"]

# Target paths for Linux fonts (covering both standards)
target_dirs = [
    os.path.expanduser("~/.fonts"),
    os.path.expanduser("~/.local/share/fonts")
]

font_registered = False

for font_dir in target_dirs:
    if not os.path.exists(font_dir):
        os.makedirs(font_dir, exist_ok=True)

    for font_file in font_files:
        if os.path.exists(font_file):
            target_path = os.path.join(font_dir, font_file)
            # Always overwrite to ensure we have the right version
            shutil.copy(font_file, target_path)
            font_registered = True

if font_registered:
    # Refresh font cache
    # Try multiple commands to be safe
    os.system("fc-cache -f -v")

# Page Configuration
st.set_page_config(
    page_title="Calidad ambiental",
    page_icon="🌍",
    layout="wide"
)

# Initialize Session State for Navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'landing'

def navigate_to(page):
    st.session_state['page'] = page

# --- VIEWS ---

def landing_page():
    st.title("🌍 Calidad ambiental")
    st.markdown("### Seleccione el módulo que desea consultar:")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🌊 Agua Superficial", use_container_width=True):
            navigate_to('surface')
            st.rerun()
            
    with col2:
        if st.button("💧 Agua Subterránea", use_container_width=True):
            navigate_to('groundwater')
            st.rerun()

    with col3:
        if st.button("🏭 Efluentes", use_container_width=True):
            navigate_to('effluents')
            st.rerun()

    with col4:
        if st.button("⛰️ Sedimentos", use_container_width=True):
            navigate_to('sediments')
            st.rerun()



def water_quality_module(module_type="surface"):
    """
    Generic function to render the water quality module.
    module_type: 'surface' or 'effluents'
    """
    
    # Configuration based on module type
    if module_type == "surface":
        title = "🌊 Agua Superficial - Comparativa ECA"
        default_file = "bbdd_molde.xlsx"
        reg_defaults_filter = ["ECA 2017 3D1", "ECA 2017 3D2"]
        success_msg_prefix = "Agua Superficial"
    elif module_type == "effluents":
        title = "🏭 Efluentes - Comparativa LMP/NMP"
        default_file = "bbdd_molde_efluentes.xlsx"
        reg_defaults_filter = [] # No smart filter for effluents defined yet, or default to all
        success_msg_prefix = "Efluentes"
    elif module_type == "sediments":
        title = "⛰️ Sedimentos - Comparativa CCME"
        default_file = "bbdd_molde_sedimentos.xlsx"
        reg_defaults_filter = [] # Defaults handled later
        success_msg_prefix = "Sedimentos"
    elif module_type == "sediments":
        title = "⛰️ Sedimentos - Comparativa CCME"
        default_file = "bbdd_molde_sedimentos.xlsx"
        reg_defaults_filter = [] # Defaults handled later
        success_msg_prefix = "Sedimentos"
    elif module_type == "groundwater":
        title = "💧 Agua Subterránea - Análisis Estadístico"
        default_file = "bbdd_molde.xlsx" # Use same mold, will ignore ECA
        reg_defaults_filter = [] 
        success_msg_prefix = "Agua Subterránea"
    else:
        title = "Módulo Desconocido"
        default_file = ""
        reg_defaults_filter = []
        success_msg_prefix = "Datos"

    # Navigation Back Button
    if st.button("⬅️ Volver al Inicio"):
        navigate_to('landing')
        st.rerun()

    st.title(title)
    st.markdown(f"""
    Sube tu archivo Excel con los datos de monitoreo de **{success_msg_prefix}**. 
    La aplicación detectará automáticamente los valores y las líneas de referencia.
    """)
    
    # File Uploader
    uploaded_file = st.file_uploader("Cargar archivo Excel (.xlsx)", type=["xlsx"], key=f"uploader_{module_type}")
    
    # Auto-load debug/default file
    if not uploaded_file:
        if os.path.exists(default_file):
            st.info(f"Modo Debug: Cargando automáticamente '{default_file}'")
            uploaded_file = default_file
            
    if uploaded_file:
        with st.spinner('Procesando datos...'):
            # 1. Load Data
            (df_raw, df_eca), error = load_data(uploaded_file)
            
            if error:
                st.error(error)
            else:
                # 2. Process Data
                try:
                    # Clean 'valor' column
                    df_clean = clean_data(df_raw)
                    
                    # Merge with Regulations
                    df_final = merge_data(df_clean, df_eca)

                    # --- GROUNDWATER SPECIFIC LOGIC ---
                    if module_type == "groundwater":
                         # Calculate Reference Statistics per Parameter
                         df_final['lim_referencia_gw'] = None # Initialize
                         for param in df_final['parametro'].unique():
                             mask = df_final['parametro'] == param
                             subset = df_final[mask]
                             ref_val = calculate_reference_statistics(subset)
                             df_final.loc[mask, 'lim_referencia_gw'] = ref_val
                    
                    st.success(f"Archivo de {success_msg_prefix} cargado con éxito. {len(df_final)} registros procesados.")
                    
                    # 3. Sidebar Controls
                    st.sidebar.header(f"Filtros ({success_msg_prefix})")
                    
                    # Get unique parameters
                    params = df_final['parametro'].unique()
                    selected_param = st.sidebar.selectbox("Seleccionar Parámetro", params)
                    
                    selected_cols = []
                    
                    # --- Regulation Filtering (SKIP FOR GROUNDWATER) ---
                    if module_type != "groundwater":
                        st.sidebar.subheader("Normativas")
                        # Group regulation columns
                        reg_groups = get_regulation_groups(df_final)
                        
                        # Create options list
                        standard_names = list(reg_groups.keys())
                        
                        if standard_names:
                            # Smart defaults
                            defaults = []
                            if module_type == "surface":
                                defaults = [
                                    name for name in standard_names 
                                    if any(f in name for f in reg_defaults_filter)
                                ]
                            else:
                                # For effluents, maybe default to all is safer initially?
                                defaults = standard_names

                            # Fallback if filter found nothing
                            if not defaults: 
                                defaults = standard_names

                            selected_standards = st.sidebar.multiselect(
                                "Seleccionar Normativas a visualizar",
                                standard_names,
                                default=defaults
                            )
                            
                            # Flatten the selection back to a list of columns
                            selected_cols = []
                            for std in selected_standards:
                                selected_cols.extend(reg_groups[std])
                        else:
                            selected_cols = None
                            st.sidebar.info("No se encontraron normativas en el archivo.")
                    else:
                        # For Groundwater, automatically select the reference column
                        selected_cols = ['lim_referencia_gw']
                        st.sidebar.info("Se mostrará el Valor Referencial (Promedio + 2 Desviaciones Estándar).")
                    
                    # --- CUSTOMIZATION CONTROLS ---
                    st.sidebar.markdown("---")
                    st.sidebar.subheader("Personalización del Gráfico")
                    
                    # Legend Position
                    legend_pos_options = {"Derecha": "right", "Abajo": "bottom"}
                    selected_legend_pos = st.sidebar.selectbox(
                        "Posición de la Leyenda",
                        options=list(legend_pos_options.keys()),
                        index=0
                    )
                    
                    # Date Angle
                    angle_options = [0, 90, 45, -45, -90]
                    selected_angle = st.sidebar.selectbox(
                        "Ángulo de Etiquetas (Fechas)",
                        options=angle_options,
                        index=4 
                    )
                    
                    # Date Format
                    date_format_options = {"Mes-Año (Ene-25)": "MM-YY", "Día-Mes-Año (23-Ene-25)": "DD-MM-YY"}
                    selected_date_format_label = st.sidebar.selectbox(
                        "Formato de Fecha (Eje X)",
                        options=list(date_format_options.keys()),
                        index=0
                    )
                    selected_date_format = date_format_options[selected_date_format_label]
                    
                    # Number of X-axis Labels (0 = Auto)
                    custom_x_labels = st.sidebar.number_input(
                        "Cantidad de Etiquetas (Eje X) (0 = Auto)",
                        min_value=0,
                        max_value=50,
                        value=0,
                        step=1,
                        help="Establece un número fijo de etiquetas en el eje X. Deja en 0 para automático."
                    )
                    
                    # Symbol Style
                    symbol_options = {"Círculo": "circle", "Variado": "varied"}
                    selected_symbol_label = st.sidebar.selectbox(
                        "Símbolos de Estaciones",
                        options=list(symbol_options.keys()),
                        index=0
                    )
                    selected_symbol_style = symbol_options[selected_symbol_label]
                    
                    # 4. Visualization
                    if selected_param:
                        # Pass the filtered columns AND styling options to the plotting function
                        fig = create_chart(
                            df_final, 
                            selected_param, 
                            selected_columns=selected_cols,
                            date_angle=selected_angle,
                            date_format=selected_date_format,
                            x_label_count=custom_x_labels,
                            legend_position=legend_pos_options[selected_legend_pos],
                            symbol_style=selected_symbol_style
                        )
                        
                        if fig:
                            # --- STATIC DISPLAY ---
                            try:
                                # Fixed dimensions for static preview
                                img_bytes = fig.to_image(format="png", width=586, height=302, scale=3)
                                
                                st.image(img_bytes, caption=f"Vista Previa Estática: {selected_param}", output_format="PNG")
                                
                                # --- DOWNLOAD BUTTONS ---
                                st.download_button(
                                    label="📸 Descargar Imagen (PNG)",
                                    data=img_bytes,
                                    file_name=f"{selected_param}.png",
                                    mime="image/png"
                                )

                            except Exception as e:
                                st.error(f"Error generando visualización estática: {e}. Asegúrate de tener 'kaleido' instalado.")
                                st.plotly_chart(fig, use_container_width=False)
                        else:
                            st.warning("No hay datos para graficar con este parámetro.")
                            
                    # 5. Data Table
                    with st.expander("Ver Datos Detallados"):
                        st.dataframe(df_final[df_final['parametro'] == selected_param])
                        
                except Exception as e:
                    st.error(f"Ocurrió un error durante el procesamiento: {e}")
                    st.exception(e)

# --- MAIN ROUTER ---

if st.session_state['page'] == 'landing':
    landing_page()
elif st.session_state['page'] == 'surface':
    water_quality_module(module_type="surface")
elif st.session_state['page'] == 'groundwater':
    water_quality_module(module_type="groundwater")
elif st.session_state['page'] == 'effluents':
    water_quality_module(module_type="effluents")
elif st.session_state['page'] == 'sediments':
    water_quality_module(module_type="sediments")


