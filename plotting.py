import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as font_manager
import matplotlib.ticker as ticker
import pandas as pd
import os

# --- REGISTRO DIRECTO DE FUENTES PARA MATPLOTLIB ---
font_files = ["BOOKOS.TTF", "BOOKOSB.TTF", "BOOKOSI.TTF", "BOOKOSBI.TTF", "BookmanOldStyle.ttf"]
custom_font_name = 'serif' 

for font_file in font_files:
    if os.path.exists(font_file):
        try:
            font_manager.fontManager.addfont(font_file)
            prop = font_manager.FontProperties(fname=font_file)
            custom_font_name = prop.get_name()
        except Exception:
            pass

def create_chart(df, parameter, selected_columns=None, date_angle=-90, date_format="MM-YY", x_label_count=0, legend_position="right", symbol_style="circle", legend_size=7.0, legend_cols=5, symbol_size=3.0, legend_spacing=0.2, log_scale=False, custom_otros_name="Otros", custom_line_styles=None):
    
    # Filtrar datos
    subset = df[df['parametro'] == parameter].copy()
    if subset.empty:
        return None
    
    # Asegurar que 'fecha' sea formato datetime
    subset['fecha'] = pd.to_datetime(subset['fecha'])
    unit = subset['unidad'].iloc[0] if 'unidad' in subset.columns else ""
    
    # --- CONFIGURACIÓN GLOBAL DE FUENTES ---
    plt.rcParams['font.family'] = custom_font_name
    if custom_font_name == 'serif':
        plt.rcParams['font.serif'] = ['Bookman Old Style', 'Times New Roman', 'serif']
        
    plt.rcParams['font.size'] = 9
    
    # NUEVO: Obligar al texto matemático a usar la fuente normal (Bookman Old Style)
    plt.rcParams['mathtext.fontset'] = 'custom'
    plt.rcParams['mathtext.bf']  = f'{custom_font_name}:bold'
    plt.rcParams['mathtext.bfit'] = f'{custom_font_name}:bold:italic'  # <-- clave
    plt.rcParams['mathtext.it']  = f'{custom_font_name}:italic'
    plt.rcParams['mathtext.rm']  = custom_font_name
    
    plt.rcParams['axes.edgecolor'] = 'black'        
    plt.rcParams['axes.linewidth'] = 1.0            
    plt.rcParams['axes.spines.top'] = True          
    plt.rcParams['axes.spines.right'] = True        
    plt.rcParams['axes.spines.bottom'] = True       
    plt.rcParams['axes.spines.left'] = True         
    
    # Crear Figura
    fig, ax = plt.subplots(figsize=(15.5 / 2.54, 8 / 2.54))
    
    # --- DICCIONARIO DE FORMAS Y COLORES ---
    marker_configs = [
        ('o', True),  ('s', True),  ('D', True),  ('^', True),  ('p', True),
        ('h', True),  ('*', True),  ('v', True),  ('<', True),  ('>', True), 
        ('X', True),  ('d', True),  ('P', True),  ('H', True),  ('8', True),
        
        ('o', False), ('s', False), ('D', False), ('^', False), ('p', False),
        ('h', False), ('*', False), ('v', False), ('<', False), ('>', False),
        ('X', False), ('d', False), ('P', False), ('H', False), ('8', False),
        
        ('+', True),  ('x', True),  ('|', True),  ('_', True),  ('1', True),
        ('2', True),  ('3', True),  ('4', True)
    ]
    
    colors = [
        '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', 
        '#911eb4', '#42d4f4', '#f032e6', '#7fff00', '#fabed4', 
        '#469990', '#dcbeff', '#9a6324', '#4b0082', '#800000', 
        '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9', 
        '#333333', '#ffd700', '#ff7f50', '#87ceeb', '#a87858', 
        '#ff69b4', '#dda0dd', '#40e0d0', '#d2691e', '#4682b4', 
        '#7fff00', '#4b0082', '#04bbfc'
    ]
    
    # 1. Trazar las Estaciones
    stations = subset['estacion'].unique()
    for i, station in enumerate(stations):
        station_data = subset[subset['estacion'] == station]
        c = colors[i % len(colors)]
        
        if symbol_style == "varied":
            m_shape, is_filled = marker_configs[i % len(marker_configs)]
            mfc = c if is_filled else 'none'
            
            ax.plot(station_data['fecha'], station_data.get('valor_num', station_data['valor']),
                    marker=m_shape, linestyle='', color=c, 
                    markerfacecolor=mfc, markeredgecolor=c,
                    label=station, markersize=symbol_size)
        else:
            ax.plot(station_data['fecha'], station_data.get('valor_num', station_data['valor']),
                    marker='o', linestyle='', color=c, 
                    markerfacecolor=c, markeredgecolor=c,
                    label=station, markersize=symbol_size)

    # 2. Trazar Líneas de Normativa
    limit_cols = [col for col in df.columns if col.startswith('lim_') or col.startswith('ISQG') or col.startswith('PEL')]
    if selected_columns is not None:
        limit_cols = [col for col in limit_cols if col in selected_columns]

    def get_legend_label(col_name, single_line=True):
        if 'lim_inf_' in col_name:
            prefix, clean_col = ("L.inf." if single_line else "Lím. inf."), col_name.replace('lim_inf_', '')
        elif 'lim_sup_' in col_name:
            prefix, clean_col = ("L.sup." if single_line else "Lím. sup."), col_name.replace('lim_sup_', '')
        else:
            prefix, clean_col = ("L." if single_line else "Lím."), col_name.replace('lim_', '')
            
        parts = clean_col.split('_')
        
        if parts[0] == 'lga':
            reg_body, category = "LGA", (f"C.{parts[1]}" if single_line else f"Cat. {parts[1]}")
        elif parts[0] == 'eca':
            year, cat_raw = parts[1], "_".join(parts[2:])
            reg_body = f"ECA-{year[-2:]}" if single_line else f"ECA-{year}"
            suffix_desc = " costa y sierra" if cat_raw.endswith("_cys") else (" selva" if cat_raw.endswith("_s") else (" estuario" if cat_raw.endswith("_e") else (" mar" if cat_raw.endswith("_m") else "")))
            for suffix in ["_cys", "_s", "_e", "_m"]:
                cat_raw = cat_raw.replace(suffix, "")
            
            if len(cat_raw) >= 3 and cat_raw[0].isdigit():
                code = f"{cat_raw[0]}-{cat_raw[1:].upper()}"
                category = f"{code}{suffix_desc}" if single_line else f"Cat. {code}{suffix_desc}"
            else:
                category = f"{cat_raw.upper()}{suffix_desc}" if single_line else f"Cat. {cat_raw.upper()}{suffix_desc}"
        elif parts[0] == 'nmp':
            reg_body, category = "NMP", ("Min-96" if single_line else " ".join(parts[1:]).replace("_", " ").lower())
        elif parts[0] == 'lmp':
            reg_body = f"LMP-{parts[1][-2:]}" if single_line else f"LMP {parts[1]}"
            category = "Dom" if "domestico" in col_name else ("Min" if "minero" in col_name else " ".join(parts[2:]).replace("_", " ").lower())
        elif 'ISQG' in col_name or 'PEL' in col_name:
            reg_body = parts[0]
            category = "Fresh" if "freshwater" in col_name else ("Mar" if "marine" in col_name else " ".join(parts[1:]).capitalize())
            return f"{reg_body} {category}" if single_line else f"{reg_body}\n{category}"
        elif 'referencia_gw' in col_name:
            reg_body = "Valor Referencial"
            category = "Promedio + 2 Desv. Est." if 'sup' in col_name else "Promedio - 2 Desv. Est."
            return "Ref. Prom+2DE" if single_line and 'sup' in col_name else ("Ref. Prom-2DE" if single_line else f"{reg_body}\n{category}")
        # NUEVA REGLA PARA OTROS
        elif 'otros' in clean_col.lower():
            reg_body = custom_otros_name
            return f"{prefix} {reg_body}"
        else:
            reg_body, category = parts[0].upper(), " ".join(parts[1:]).upper()

        separator = " " if single_line else "\n"
        return f"{prefix} {reg_body}{separator}{category}"

    for col in limit_cols:
        val = subset[col].iloc[0]
        if pd.notna(val):
            label = get_legend_label(col, single_line=True)
            
            col_lower, color, linestyle, alpha, lw = col.lower(), 'black', '-', 1.0, 1.5
            
            if 'eca_2017_3d2' in col_lower:
                color, linestyle = 'blue', ('--' if 'lim_inf' in col_lower else '-')
            elif 'eca_2017' in col_lower:
                color, linestyle = 'red', ('-' if 'lim_inf' in col_lower else '--')
            elif 'lga' in col_lower or 'eca_2008' in col_lower or 'eca_2015' in col_lower:
                color, linestyle = 'green', (':' if 'lim_inf' in col_lower else '-.')
                if 'eca_2015_3d2' in col_lower:
                    color = 'blue'
            elif 'nmp_minero' in col_lower:
                color, linestyle = 'purple', ('-.' if 'lim_inf' in col_lower else ':')
            elif 'lmp_2010' in col_lower:
                color = 'green' if 'domestico' in col_lower else 'red'
                linestyle = ':' if 'lim_inf' in col_lower and 'domestico' in col_lower else ('-' if 'domestico' in col_lower else ('-' if 'lim_inf' in col_lower else '--'))
            elif 'isqg' in col_lower or 'pel' in col_lower:
                color, linestyle = ('purple' if 'isqg' in col_lower else 'red'), '-.'
            elif 'referencia_gw' in col_lower:
                color, linestyle = 'red', ('--' if 'sup' in col_lower else ':')
            elif 'otros' in col_lower:
                color, linestyle = 'darkorange', ('-' if 'lim_inf' in col_lower else '--')

            # --- NUEVA LÓGICA: SOBRESCRIBIR SI EL USUARIO ELIGIÓ UN COLOR/ESTILO ---
            if custom_line_styles is not None and col in custom_line_styles:
                color = custom_line_styles[col]['color']
                linestyle = custom_line_styles[col]['linestyle']
            # -----------------------------------------------------------------------

            ax.axhline(y=val, color=color, linestyle=linestyle, alpha=alpha, label=label, linewidth=lw)

    # 3. Formato de Ejes
    # --- CONVERSIÓN DE SUBÍNDICES MATEMÁTICO ---
    # Usamos $_3$ pero como forzamos 'mathtext.default' a 'regular', 
    # tomará el '3' de Bookman Old Style y lo hará subíndice manteniendo la negrita.
    display_parameter = parameter.replace("NO3",  r"NO$_{\mathbf{3}}$").replace("NO2",  r"NO$_{\mathbf{2}}$").replace("DBO5", r"DBO$_{\mathbf{5}}$").replace("Escherichia coli", r"$\mathbfit{Escherichia\ coli}$")

    if "Escherichia coli" in parameter:    
        ax.set_ylabel(f"{display_parameter}\n ({unit})", fontweight='bold', fontsize=9)
    else:
        ax.set_ylabel(f"{display_parameter} ({unit})", fontweight='bold', fontsize=9)
    
    # --- ESCALA LOGARÍTMICA Y FORMATO DEL EJE Y ---
    if log_scale:
        ax.set_yscale('log')
        def y_fmt(x, pos):
            if x >= 1000:
                return f"{x:.0f}"
            elif x >= 1:
                return f"{x:g}".replace('.', ',')
            else:
                return f"{x:.4g}".replace('.', ',')
    else:
        def y_fmt(x, pos):
            return f"{x:g}".replace('.', ',')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(y_fmt))
    
    # --- ACTIVACIÓN DE GRILLAS GRISES ---
    if log_scale:
        ax.grid(True, which='major', axis='both', color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
        ax.minorticks_off()
    else:
        ax.grid(True, which='both', axis='both', color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    
    spanish_months = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
    
    def span_date_fmt(x, pos):
        dt = mdates.num2date(x)
        if date_format == "DD-MM-YY":
            return f"{dt.day}-{spanish_months[dt.month]}-{str(dt.year)[-2:]}"
        else:
            return f"{spanish_months[dt.month]}-{str(dt.year)[-2:]}"
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(span_date_fmt))
    
    if x_label_count > 0:
        ax.xaxis.set_major_locator(plt.MaxNLocator(x_label_count))
    else:
        ax.xaxis.set_major_locator(plt.MaxNLocator(8)) 
        
    plt.xticks(rotation=date_angle)
    
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    
    # 4. LA LEYENDA
    if legend_position == "bottom":
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25),
                  ncol=legend_cols, fontsize=legend_size, frameon=False,
                  labelspacing=legend_spacing, handletextpad=0.3, columnspacing=0.8)
    else: 
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
                  ncol=1, fontsize=legend_size, frameon=False,
                  labelspacing=legend_spacing, handletextpad=0.3)
                  
    plt.tight_layout()
    
    return fig
