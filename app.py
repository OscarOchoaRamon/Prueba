import streamlit as st

from processing import load_data, clean_data, merge_data, get_regulation_groups, calculate_reference_statistics
from plotting import create_chart
import os
import shutil
import texto_calidad_agua_superficial
import texto_calidad_agua_subterránea
import texto_calidad_efluente
import texto_calidad_sedimentos

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
    
    # --- GROUNDWATER SETTINGS (Pre-processing) ---
    gw_ref_options = []
    if module_type == "groundwater":
        st.sidebar.header("Configuración Agua Subterránea")
        gw_ref_options = st.sidebar.multiselect(
            "Valores de Referencia",
            ["Promedio + 2 Desviaciones Estándar", "Promedio - 2 Desviaciones Estándar"],
            default=["Promedio + 2 Desviaciones Estándar"]
        )

    st.markdown(f"""
    Sube tu archivo Excel con los datos de monitoreo de **{success_msg_prefix}**. 
    La aplicación detectará automáticamente los valores y las líneas de referencia.
    """)
    
    # --- Botón de descarga de plantilla ---
    # Verifica si la plantilla existe en el repositorio/servidor antes de mostrar el botón
    if os.path.exists(default_file):
        with open(default_file, "rb") as file:
            st.download_button(
                label=f"📥 Descargar plantilla Excel ({success_msg_prefix})",
                data=file,
                file_name=default_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Descarga este molde, llénalo con tus datos de monitoreo y súbelo en el recuadro de abajo."
            )
    else:
        # Mensaje de seguridad en caso de que el archivo no se haya subido a Github
        st.warning(f"⚠️ El archivo de plantilla '{default_file}' no se encuentra disponible en el servidor en este momento.")
    # ---------------------------------------------
    
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
                        df_final['lim_referencia_gw_sup'] = None
                        df_final['lim_referencia_gw_inf'] = None
                        
                        for param in df_final['parametro'].unique():
                            mask = df_final['parametro'] == param
                            subset = df_final[mask]
                            
                            ref_val_sup = calculate_reference_statistics(subset, method='mean_plus_2std')
                            ref_val_inf = calculate_reference_statistics(subset, method='mean_minus_2std')
                            
                            df_final.loc[mask, 'lim_referencia_gw_sup'] = ref_val_sup
                            df_final.loc[mask, 'lim_referencia_gw_inf'] = ref_val_inf
                    
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
                                defaults = standard_names

                            if not defaults: 
                                defaults = standard_names

                            selected_standards = st.sidebar.multiselect(
                                "Seleccionar Normativas a visualizar",
                                standard_names,
                                default=defaults
                            )

                            # --- NUEVA LÓGICA DE INTERFAZ PARA "OTROS" ---
                            custom_otros_name = "Otros"
                            if selected_standards and "Otros" in selected_standards:
                                custom_otros_name = st.sidebar.text_input(
                                    "Nombre para la normativa 'Otros'", 
                                    value="PIA Lauricocha",
                                    help="Este nombre aparecerá en la leyenda del gráfico y en la interpretación."
                                )
                            # ---------------------------------------------
                            
                            selected_cols = []
                            for std in selected_standards:
                                selected_cols.extend(reg_groups[std])
                        else:
                            selected_cols = None
                            st.sidebar.info("No se encontraron normativas en el archivo.")
                    else:
                        selected_cols = []
                        if "Promedio + 2 Desviaciones Estándar" in gw_ref_options:
                            selected_cols.append('lim_referencia_gw_sup')
                        if "Promedio - 2 Desviaciones Estándar" in gw_ref_options:
                            selected_cols.append('lim_referencia_gw_inf')
                            
                        st.sidebar.info(f"Mostrando {len(selected_cols)} niveles de referencia.")
                    
                    # --- CUSTOMIZATION CONTROLS ---
                    st.sidebar.markdown("---")
                    st.sidebar.subheader("Personalización del Gráfico")
                    
                    # Legend Position
                    legend_pos_options = {"Derecha": "right", "Abajo": "bottom"}
                    selected_legend_pos = st.sidebar.selectbox(
                        "Posición de la Leyenda",
                        options=list(legend_pos_options.keys()),
                        index=1  # <-- CAMBIADO A 1 PARA QUE EL DEFAULT SEA "Abajo"
                    )
                    
                    # Legend Font Size
                    selected_legend_size = st.sidebar.slider(
                        "Tamaño de Letra de la Leyenda",
                        min_value=4.0,
                        max_value=12.0,
                        value=7.0,
                        step=0.5,
                        help="Ajusta el tamaño del texto de la leyenda en la gráfica."
                    )
                    
                    # Separación de la Leyenda
                    selected_legend_spacing = st.sidebar.slider(
                        "Separación de líneas en Leyenda",
                        min_value=0.0,
                        max_value=1.5,
                        value=0.2,
                        step=0.1,
                        help="Controla el espacio vertical entre las líneas de la leyenda (0.2 es muy compacto)."
                    )
                    
                    # Columnas de Leyenda (Solo visible si la leyenda está abajo)
                    selected_legend_cols = 5
                    if legend_pos_options[selected_legend_pos] == "bottom":
                        selected_legend_cols = st.sidebar.number_input(
                            "Columnas de la Leyenda",
                            min_value=1,
                            max_value=10,
                            value=5,
                            step=1,
                            help="Número de columnas en las que se dividirá la leyenda."
                        )
                    
                    # Date Angle
                    angle_options = [0, 90, 45, -45, -90]
                    selected_angle = st.sidebar.selectbox(
                        "Ángulo de Etiquetas (Fechas)",
                        options=angle_options,
                        index=2  # El índice 2 corresponde a 45 grados
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
                        index=1  # <-- CAMBIADO A 1 PARA QUE EL DEFAULT SEA "Variado"
                    )
                    selected_symbol_style = symbol_options[selected_symbol_label]
                    
                    # Tamaño de los símbolos
                    selected_symbol_size = st.sidebar.slider(
                        "Tamaño de los Símbolos",
                        min_value=1.0,
                        max_value=15.0,
                        value=3.0, 
                        step=0.5,
                        help="Ajusta el tamaño de los puntos de las estaciones en el gráfico."
                    )

                    #Escala logarítmica ---
                    use_log_scale = st.sidebar.checkbox(
                        "Escala logarítmica (Eje Y)",
                        value=False,
                        help="Aplica escala logarítmica al eje Y. Útil cuando los datos tienen rangos muy amplios."
                    )
                    
                    # --- GENERAR TEXTO ---
                    if selected_param:
                        st.markdown("### Interpretación")
                        try:
                            param_group = df_final[df_final['parametro'] == selected_param]
                            texto_generado = ""
                            
                            if module_type == "surface":
                                # 1. Apagamos todas las variables para limpiar la memoria antes de evaluar
                                for var in dir(texto_calidad_agua_superficial):
                                    if var.startswith("ECA_") or var.startswith("LGA_") or var == "OTROS":
                                        setattr(texto_calidad_agua_superficial, var, False)
                                
                                # 2. Asignamos el nombre personalizado que escribió el usuario en la interfaz
                                texto_calidad_agua_superficial.NOMBRE_OTROS = custom_otros_name
                                
                                # 3. Recorremos las normativas seleccionadas para encender las banderas correspondientes
                                if selected_standards:
                                    for std in selected_standards:
                                        if std == "Otros":
                                            texto_calidad_agua_superficial.OTROS = True
                                        elif std.startswith("ECA"):
                                            var_name = std.replace("ECA ", "ECA_").replace(" ", "_CAT_", 1).replace(" ", "_")
                                            if hasattr(texto_calidad_agua_superficial, var_name):
                                                setattr(texto_calidad_agua_superficial, var_name, True)
                                        elif std.startswith("LGA"):
                                            var_name = std.replace(" ", "_")
                                            if hasattr(texto_calidad_agua_superficial, var_name):
                                                setattr(texto_calidad_agua_superficial, var_name, True)
                                                
                                texto_generado = texto_calidad_agua_superficial.generar_texto(param_group)
                                
                            elif module_type == "effluents":
                                texto_calidad_efluente.NMP_MINERO = False
                                texto_calidad_efluente.LMP_2010_DOMESTICO = False
                                texto_calidad_efluente.LMP_2010_MINERO = False
                                if selected_standards:
                                    for std in selected_standards:
                                        var_name = std.replace(" ", "_")
                                        if hasattr(texto_calidad_efluente, var_name):
                                            setattr(texto_calidad_efluente, var_name, True)
                                texto_generado = texto_calidad_efluente.generar_texto(param_group)
                                
                            elif module_type == "sediments":
                                texto_calidad_sedimentos.CCME_2001_FRESHWATER = False
                                texto_calidad_sedimentos.CCME_2001_MARINE = False
                                if selected_standards:
                                    for std in selected_standards:
                                        var_name = std.replace("CCME ", "CCME_2001_")
                                        if hasattr(texto_calidad_sedimentos, var_name):
                                            setattr(texto_calidad_sedimentos, var_name, True)
                                texto_generado = texto_calidad_sedimentos.generar_texto(param_group)
                                
                            elif module_type == "groundwater":
                                texto_calidad_agua_subterránea.CALCULAR_REF_ALTO = "Promedio + 2 Desviaciones Estándar" in gw_ref_options
                                texto_calidad_agua_subterránea.CALCULAR_REF_BAJO = "Promedio - 2 Desviaciones Estándar" in gw_ref_options
                                texto_generado = texto_calidad_agua_subterránea.generar_texto_subterranea(param_group)
                                
                            st.write(texto_generado)
                        except Exception as e:
                            st.error(f"Ocurrió un error al generar el texto: {e}")

                    # 4. Visualization
                    if selected_param:
                        fig = create_chart(
                            df_final, 
                            selected_param, 
                            selected_columns=selected_cols,
                            date_angle=selected_angle,
                            date_format=selected_date_format,
                            x_label_count=custom_x_labels,
                            legend_position=legend_pos_options[selected_legend_pos],
                            symbol_style=selected_symbol_style,
                            legend_size=selected_legend_size,
                            legend_cols=selected_legend_cols,
                            symbol_size=selected_symbol_size,        
                            legend_spacing=selected_legend_spacing,
                            log_scale=use_log_scale,
                            custom_otros_name=custom_otros_name if 'custom_otros_name' in locals() else "Otros" # <--- NUEVO
                        )
                        
                        if fig:
                            import io
                            
                            # Generar buffer PNG
                            buf_png = io.BytesIO()
                            fig.savefig(buf_png, format="png", dpi=300, bbox_inches='tight', pad_inches=0.1)
                            buf_png.seek(0)
                            
                            # Generar buffer SVG
                            buf_svg = io.BytesIO()
                            fig.savefig(buf_svg, format="svg", bbox_inches='tight', pad_inches=0.1)
                            buf_svg.seek(0)
                            
                            st.image(buf_png, caption=f"Gráfico Generado: {selected_param}", output_format="PNG")
                            
                            # Mostrar botones de descarga en columnas
                            col_down1, col_down2 = st.columns(2)
                            
                            with col_down1:
                                st.download_button(
                                    label="📸 Descargar Imagen (PNG)",
                                    data=buf_png.getvalue(),
                                    file_name=f"{selected_param}.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                                
                            with col_down2:
                                st.download_button(
                                    label="🖼️ Descargar Vector (SVG)",
                                    data=buf_svg.getvalue(),
                                    file_name=f"{selected_param}.svg",
                                    mime="image/svg+xml",
                                    use_container_width=True
                                )
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
