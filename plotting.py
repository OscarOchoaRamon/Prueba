import plotly.graph_objects as go
import pandas as pd

def create_chart(df, parameter, selected_columns=None, date_angle=-90, date_format="MM-YY", x_label_count=0, legend_position="right", symbol_style="circle", legend_size=None, legend_cols=None):
    """
    Creates an interactive Plotly chart for a specific parameter.
    Dynamically adds regulation lines found in the dataframe.
    
    Args:
        df: DataFrame with data
        parameter: Selected parameter name
        selected_columns: List of regulation columns to include
        date_angle: Angle for x-axis labels (0, 45, 90, -45, etc.)
        legend_position: 'right' (default) or 'bottom'
        symbol_style: 'circle' (default) or 'varied'
    """
    # Filter data for the specific parameter
    subset = df[df['parametro'] == parameter].copy()
    
    if subset.empty:
        return None
        
    # Get the unit for display
    unit = subset['unidad'].iloc[0] if 'unidad' in subset.columns else ""
    title = f"{parameter} ({unit})"
    
    # Create base scatter plot
    # We use graph_objects for more control over layers
    fig = go.Figure()
    
    # Define symbol sequence for "varied" option
    # Combines filled and open shapes to maximize visual distinction, avoiding similar looking squares/rectangles
    symbol_sequence = [
        'circle', 'square', 'diamond', 'triangle-up', 'pentagon', 
        'hexagon', 'star', 'circle-open', 'square-open', 'diamond-open', 
        'triangle-up-open', 'pentagon-open', 'hexagon-open', 'star-open', 'cross', 
        'x', 'bowtie', 'hourglass', 'triangle-down', 'triangle-left', 
        'triangle-right', 'triangle-down-open', 'triangle-left-open', 'triangle-right-open', 'cross-open', 
        'hash', 'y-up', 'y-down', 'y-left', 'y-right', 
        'octagon', 'octagon-open', 'hexagram'
    ]
    
    # Define color sequence to prevent duplicates for up to 33 stations.
    # Uses highly distinct colors (Glasbey/Boynton/Kelly standard) for maximum human eye distinction.
    color_sequence = [
        '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', 
        '#911eb4', '#42d4f4', '#f032e6', '#7fff00', '#fabed4', 
        '#469990', '#dcbeff', '#9a6324', '#4b0082', '#800000', 
        '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9', 
        '#333333', '#ffd700', '#ff7f50', '#87ceeb', '#a87858', 
        '#ff69b4', '#dda0dd', '#40e0d0', '#d2691e', '#4682b4', 
        '#7fff00', '#4b0082', '#04bbfc'
    ]
    
    # 1. Add Scatter Traces for each station
    # Group by station
    stations = subset['estacion'].unique()
    for i, station in enumerate(stations):
        station_data = subset[subset['estacion'] == station]
        
        # Determine symbol
        if symbol_style == "varied":
            # Cycle through symbols if more stations than symbols
            marker_symbol = symbol_sequence[i % len(symbol_sequence)]
        else:
            marker_symbol = 'circle'
            
        # Determine color from custom palette
        marker_color = color_sequence[i % len(color_sequence)]
            
        fig.add_trace(go.Scatter(
            x=station_data['fecha'],
            y=station_data.get('valor_num', station_data['valor']),
            mode='markers',
            name=station,
            marker=dict(
                size=5.5, # Increased size to make open/filled shapes and colors clearly visible
                symbol=marker_symbol,
                color=marker_color
            ) 
        ))
        
    # 2. Add Regulation Lines
    # Identify regulation columns
    limit_cols = [col for col in df.columns if col.startswith('lim_') or col.startswith('ISQG') or col.startswith('PEL')]
    
    # Filter if user selected specific ones
    if selected_columns is not None:
        limit_cols = [col for col in limit_cols if col in selected_columns]
        
        def get_legend_label(col_name, single_line=False):
            """
            Translates column name to specific multi-line legend label
            matching requirements from original script.
            E.g. lim_inf_eca_2017_3d1 -> 'Lím. inf. ECA-2017\nCat. 3-D1'
            """
            # 1. Determine Type (Inf/Sup)
            if 'lim_inf_' in col_name:
                prefix = "L.inf." if single_line else "Lím. inf."
                clean_col = col_name.replace('lim_inf_', '')
            elif 'lim_sup_' in col_name:
                prefix = "L.sup." if single_line else "Lím. sup."
                clean_col = col_name.replace('lim_sup_', '')
            else:
                prefix = "L." if single_line else "Lím."
                clean_col = col_name.replace('lim_', '')
                
            # 2. Determine Regulation Body (ECA-2017, LGA, etc.)
            # Common patterns: eca_2017_..., eca_2008_..., lga_...
            
            parts = clean_col.split('_')
            
            if parts[0] == 'lga':
                reg_body = "LGA"
                # categories like I, II, III
                cat_part = parts[1] if len(parts) > 1 else ""
                category = f"C.{cat_part}" if single_line else f"Cat. {cat_part}"
                
            elif parts[0] == 'eca':
                # eca_2017_3d1 -> parts: ['eca', '2017', '3d1']
                year = parts[1]
                reg_body = f"ECA-{year[-2:]}" if single_line else f"ECA-{year}"
                
                # Category formatting is tricky: 3d1 -> 3-D1, 4e2_cys -> 4-E2 costa y sierra
                # Let's join the rest
                cat_raw = "_".join(parts[2:])
                
                # Specific Mappings for categories
                # We can try to format generically: 3d1 -> 3-D1
                # But 'cys' -> 'costa y sierra' needs explicit map
                
                cat_map = {
                    'cys': 'costa y sierra',
                    's': 'selva',
                    'e': 'estuario',
                    'm': 'mar'
                }
                
                # Check for special suffixes
                suffix_desc = ""
                for k, v in cat_map.items():
                    if cat_raw.endswith(f"_{k}"):
                         suffix_desc = f" {v}"
                         cat_raw = cat_raw.replace(f"_{k}", "") # Remove suffix to format the code
                         break
                
                # Format code like '3d1' -> '3-D1'
                # Assuming pattern digit-letter-digit
                if len(cat_raw) >= 3 and cat_raw[0].isdigit() and cat_raw[-1].isdigit():
                     # 3d1 -> 3-D1
                     code = f"{cat_raw[0]}-{cat_raw[1:].upper()}"
                     category = f"{code}{suffix_desc}" if single_line else f"Cat. {code}{suffix_desc}"
                elif len(cat_raw) >= 3 and cat_raw[0].isdigit():
                     # 4e1 -> 4-E1
                     code = f"{cat_raw[0]}-{cat_raw[1:].upper()}"
                     category = f"{code}{suffix_desc}" if single_line else f"Cat. {code}{suffix_desc}"
                else:
                     # Fallback
                     category = f"{cat_raw.upper()}{suffix_desc}" if single_line else f"Cat. {cat_raw.upper()}{suffix_desc}"

            # --- EFFLUENTS LABELS ---
            elif parts[0] == 'nmp':
                reg_body = "NMP"
                category = "Min-96" if single_line else " ".join(parts[1:]).replace("_", " ").lower() # minero -> minero
            
            elif parts[0] == 'lmp':
                # lmp_2010_domestico -> parts: ['lmp', '2010', 'domestico']
                year = parts[1]
                reg_body = f"LMP-{year[-2:]}" if single_line else f"LMP {year}"
                category = "Dom" if "domestico" in col_name else ("Min" if "minero" in col_name else " ".join(parts[2:]).replace("_", " ").lower())

            # --- SEDIMENTS LABELS ---
            elif 'ISQG' in col_name or 'PEL' in col_name:
                 # ISQG_freshwater -> parts: ['ISQG', 'freshwater']
                 reg_body = parts[0] # ISQG or PEL
                 category = "Fresh" if "freshwater" in col_name else ("Mar" if "marine" in col_name else " ".join(parts[1:]).capitalize())
                 
                 prefix = "" # No Lim. inf./sup. prefix for these usually
                 if single_line:
                     return f"{reg_body} {category}"
                 return f"{reg_body}<br>{category}"

            # --- GROUNDWATER REFERENCE ---
            elif 'referencia_gw_sup' in col_name:
                reg_body = "Valor Referencial"
                category = "Promedio + 2 Desv. Est."
                prefix = "" 
                if single_line:
                    return "Ref. Prom+2DE"
                return f"{reg_body}<br>{category}"
                
            elif 'referencia_gw_inf' in col_name:
                reg_body = "Valor Referencial"
                category = "Promedio - 2 Desv. Est."
                prefix = "" 
                if single_line:
                    return "Ref. Prom-2DE"
                return f"{reg_body}<br>{category}"

            else:
                reg_body = parts[0].upper()
                category = " ".join(parts[1:]).upper()
                
            if single_line:
                return f"{prefix} {reg_body} {category}"
            return f"{prefix} {reg_body}<br>{category}" # Plotly uses <br> for newline

    for col in limit_cols:
        # Get the single value for this parameter
        val = subset[col].iloc[0]
        
        if pd.notna(val):
            label = get_legend_label(col, single_line=(legend_position == "bottom"))
            
            # --- STYLE LOGIC ---
            # Defaults
            color = 'black' # Should not happen usually
            dash = 'solid'
            width = 2
            opacity = 1.0 # Default opacity
            
            # Normalize for checks
            col_lower = col.lower()
            
            # Helper to return color string
            # Plotly line dict doesn't take 'alpha', need rgba or opacity
            # We can use rgba string for specific colors
            
            # 1. ECA 2017 3-D2 (Specific Exception: Blue)
            if 'eca_2017_3d2' in col_lower:
                base_color = '255' # Blue in RGBA is 0,0,255
                # But wait, let's just use CSS names or RGBA
                
                if 'lim_inf' in col_lower:
                    # Original: color='b', linestyle='--' (No alpha)
                    dash = 'dash'
                    color = 'blue'
                else: # lim_sup
                    # Original: color='b', linestyle='-', alpha=0.5
                    dash = 'solid'
                    color = 'rgba(0, 0, 255, 0.5)' # Blue with 0.5 alpha
                    
            # 2. ECA 2017 (General): Red
            elif 'eca_2017' in col_lower:
                # Base is Red
                if 'lim_inf' in col_lower:
                    # Original: color='r', linestyle='-', alpha=0.5
                    dash = 'solid'
                    color = 'rgba(255, 0, 0, 0.5)' # Red with 0.5 alpha
                else: # lim_sup
                    # Original: color='r', linestyle='--'
                    dash = 'dash'
                    color = 'red'
            
            # 3. LGA & ECA 2008 & ECA 2015: Green
            # These had NO alpha in original script (default 1.0)
            elif 'lga' in col_lower or 'eca_2008' in col_lower or 'eca_2015' in col_lower:
                color = 'green'
                if 'lim_inf' in col_lower:
                    dash = 'dot' 
                else: # lim_sup
                    # ECA 2015 3D2 exception check?
                    # Script lines 439, 445: ECA 2015 3D2 is BLUE but NO ALPHA mentioned.
                    # "plt.axhline(..., color='b', linestyle='-.', ...)"
                    pass
                    
                # Specific check for ECA 2015 3D2 colors (Blue)
                # But kept logic simple above, let's refine for correctness:
                if 'eca_2015_3d2' in col_lower:
                     color = 'blue'
                
                # Refine dash style for older regs
                if 'lim_inf' in col_lower:
                    dash = 'dot'
                else:
                    dash = 'dashdot'
            
            # --- EFFLUENTS STYLES ---
            # 4. NMP Minero 1996 (Purple)
            elif 'nmp_minero' in col_lower:
                color = 'purple'
                if 'lim_inf' in col_lower:
                    dash = 'dashdot' # -.
                else:
                    dash = 'dot' # :
            
            # 5. LMP 2010 Domestico (Green)
            elif 'lmp_2010_domestico' in col_lower:
                color = 'green'
                if 'lim_inf' in col_lower:
                    dash = 'dot' # :
                else:
                    dash = 'solid' # -, alpha=0.5 in script, we use rgba
                    color = 'rgba(0, 128, 0, 0.5)'
            
            # 6. LMP 2010 Minero (Red)
            elif 'lmp_2010_minero' in col_lower:
                color = 'red'
                if 'lim_inf' in col_lower:
                    dash = 'solid' # -, alpha=0.5
                    color = 'rgba(255, 0, 0, 0.5)'
                else:
                    dash = 'dash' # --, alpha=0.5
                    color = 'rgba(255, 0, 0, 0.5)'

            # --- SEDIMENTS STYLES ---
            elif 'isqg' in col_lower:
                color = 'purple'
                dash = 'dashdot' # -.
            
            elif 'pel' in col_lower:
                color = 'red'
                dash = 'dashdot' # -.

            # --- GROUNDWATER STYLE ---
            elif 'referencia_gw_sup' in col_lower:
                color = 'red'
                dash = 'dash'
                width = 2
            
            elif 'referencia_gw_inf' in col_lower:
                color = 'red' 
                dash = 'dot'
                width = 2

            # Add Line Trace
            fig.add_trace(go.Scatter(
                x=[subset['fecha'].min(), subset['fecha'].max()],
                y=[val, val],
                mode='lines',
                name=label,
                line=dict(color=color, dash=dash, width=width),
                hoverinfo='name+y'
            ))
            
    # Layout updates with custom styling
    # Conversion: 1 cm is approximately 37.8 pixels
    # Requested: 15.5 cm x 8 cm
    # Width: 15.5 cm * 37.8 = 586 px
    # Height: 8 cm * 37.8 = 302 px
    
    # Count how many legend items there will be to determine dynamic layout
    stations = subset['estacion'].unique()
    num_stations = len(stations)
    num_limits = 0
    for col in limit_cols:
        val = subset[col].iloc[0]
        if pd.notna(val):
            num_limits += 1
    total_legend_items = num_stations + num_limits

    # Margin adjustments based on legend
    margin = dict(l=50, r=50, t=20, b=50)

    # Legend Position & Margin Logic
    # We dynamically adjust font size and margins to fit all legend elements
    if legend_position == "bottom":
        if legend_size is not None:
            font_size = legend_size
        else:
            if total_legend_items <= 15:
                font_size = 7.0
            elif total_legend_items <= 25:
                font_size = 6.5
            else:
                font_size = 6.0
            
        if legend_cols is not None and legend_cols > 0:
            entrywidth = int(480 / legend_cols)
            cols_count = legend_cols
        else:
            entrywidth = 90
            cols_count = 5
            
        legend_layout = dict(
            font=dict(family="Bookman Old Style, serif", size=font_size, color="black"),
            title=dict(text=""),
            orientation="h",
            yanchor="top",
            y=-0.25, # Pull it slightly closer to the axis
            xanchor="center",
            x=0.5,
            entrywidth=entrywidth, # Size elements based on requested columns count
            entrywidthmode="pixels"
        )
        
        # Adjust bottom margin dynamically based on estimated rows of legend
        estimated_rows = max(1, total_legend_items // cols_count + 1)
        margin = dict(l=50, r=50, t=20, b=max(70, 45 + estimated_rows * 12))
    else: # right (default)
        if legend_size is not None:
            font_size = legend_size
        else:
            if total_legend_items <= 12:
                font_size = 7.0
            elif total_legend_items <= 20:
                font_size = 6.5
            elif total_legend_items <= 30:
                font_size = 6.0
            else:
                font_size = 5.5
            
        legend_layout = dict(
            font=dict(family="Bookman Old Style, serif", size=font_size, color="black"),
            title=dict(text=""),
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    
    fig.update_layout(
        # Title removed as requested
        # title=dict(text=title, font=dict(family="Bookman Old Style", size=20)),
        
        # X-axis title removed ("Fecha" gone)
        xaxis_title=None,
        
        # Y-axis now uses the parameter name plus unit for clarity
        yaxis_title=dict(text=f"{parameter} ({unit})", font=dict(family="Bookman Old Style, serif", weight="bold", size=9, color="black")),
        
        # Legend logic
        legend=legend_layout,
        
        # Colors & Fonts
        font=dict(family="Bookman Old Style, serif", color="black", size=9),
        paper_bgcolor="white",
        plot_bgcolor="white",
        
        # Decimal separator configuration
        separators=",.", # Comma for decimals, Dot for thousands
        
        hovermode="x unified",
        template="plotly_white",
        width=586,  # 15.5 cm
        height=302, # 8 cm
        margin=margin
    )
    
    # Date formatting on X-axis (Spanish manually enforced)
    # We create explicit ticks to ensure "Ene-2022", "Feb-2022" etc regardless of locale
    # User requested proper spacing (not every single month)
    
    # 1. Generate range of months covered
    if not df['fecha'].empty:
        min_date = df['fecha'].min()
        max_date = df['fecha'].max()
        
        # Calculate time span in days
        delta_days = (max_date - min_date).days
        
        # Heuristic for "appropriate amount" of ticks (Python choosing defaults)
        # Target: Avoid overcrowding. For 15cm width (~570px), maybe 8-12 labels max.
        
        if x_label_count > 0:
            # Manual count: Generate 'periods=x_label_count' evenly spaced dates
            # We want at least the start and end, and intermediates
            if x_label_count == 1:
                tick_dates = pd.DatetimeIndex([min_date])
            else:
                 tick_dates = pd.date_range(start=min_date, end=max_date, periods=x_label_count)
        else:
            # Auto logic
            if delta_days <= 60:
                 freq = '5D' # Every 5 days for short ranges
            elif delta_days <= 365: # 1 year -> Monthly
                freq = 'MS' # Month Start
            elif delta_days <= 365 * 2: # 2 years -> Every 2 months
                freq = '2MS'
            elif delta_days <= 365 * 5: # 5 years -> Every 6 months
                freq = '6MS'
            else: # > 5 years -> Yearly
                try:
                    # Test if 'YS' is supported (Pandas 2.2.0+)
                    pd.date_range(start=min_date, end=max_date, freq='YS')
                    freq = 'YS'
                except ValueError:
                    freq = 'AS'
                
            tick_dates = pd.date_range(start=min_date, end=max_date, freq=freq)
        
        # Spanish Month Names map
        spanish_months = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }
        
        tick_vals = tick_dates
        # Use 2-digit year (e.g., '21' instead of '2021')
        if date_format == "DD-MM-YY":
            # Format: 23-Ene-25
            tick_text = [f"{d.day}-{spanish_months[d.month]}-{str(d.year)[-2:]}" for d in tick_dates]
        else:
            # Format: Ene-25 (Default)
            tick_text = [f"{spanish_months[d.month]}-{str(d.year)[-2:]}" for d in tick_dates]
        
        fig.update_xaxes(
            tickmode='array', # CRITICAL: Forces Plotly to use our custom vals/text/
            tickvals=tick_vals,
            ticktext=tick_text,
            tickfont=dict(family="Bookman Old Style, serif", size=9, color="black"),
            tickangle=date_angle, # Configurable angle
            showline=True, linewidth=1, linecolor='black', mirror=True
        )
    else:
        # Fallback if no dates
         fig.update_xaxes(tickfont=dict(family="Bookman Old Style, serif", size=9, color="black"))

    fig.update_yaxes(
        tickfont=dict(family="Bookman Old Style, serif", size=9, color="black"),
        showline=True, linewidth=1, linecolor='black', mirror=True
    )
    
    # Update global layout font too
    fig.update_layout(font=dict(family="Bookman Old Style, serif", size=9, color="black"))
    
    return fig




















