import pandas as pd
import numpy as np
import math

def format_number(val):
    if pd.isna(val):
        return "NaN"
    # Formateo nativo %g reemplazando el punto por coma decimal
    return ("%g" % val).replace('.', ',')

def format_promedio_dinamico(val):
    """
    Da formato al valor promedio siguiendo reglas específicas de cifras significativas:
    - >= 100: Sin decimales.
    - >= 10 y < 100: 3 cifras significativas.
    - >= 1 y < 10: 2 cifras significativas.
    - < 1: 1 cifra significativa.
    """
    if pd.isna(val) or val is None:
        return "NaN"
    
    # Trabajamos con el valor absoluto para aplicar las reglas de escala
    abs_val = abs(val)
    
    if abs_val == 0:
        return "0"
        
    if abs_val >= 100:
        # Colocar sin decimales (redondeo al entero más cercano)
        res = round(val)
        return str(res)
        
    elif abs_val >= 10:
        # Mayores o iguales a 10 y menores a 100: 3 cifras significativas.
        # En el rango [10, 100), 3 cifras significativas equivale a exactamente 1 decimal (ej: 12.3 o 99.9).
        res = round(val, 1)
        return ("%.1f" % res).replace('.', ',')
        
    elif abs_val >= 1:
        # Mayores o iguales a 1 y menores a 10: 2 cifras significativas.
        # En el rango [1, 10), 2 cifras significativas equivale a exactamente 1 decimal (ej: 1.2 o 9.9).
        res = round(val, 1)
        return ("%.1f" % res).replace('.', ',')
        
    else:
        # Menores a 1: 1 cifra significativa.
        # Calculamos dinámicamente la posición del primer dígito diferente de cero.
        decimals = -int(math.floor(math.log10(abs_val)))
        res = round(val, decimals)
        # Formateamos con la cantidad de decimales calculados para evitar problemas de coma flotante
        fmt = "%." + str(decimals) + "f"
        return (fmt % res).replace('.', ',')

def obtener_estaciones_extremo(grupo, columna_valor, tipo="max"):
    """
    Encuentra la estación o estaciones que tienen el valor máximo o mínimo,
    y devuelve una cadena formateada con los nombres correspondientes.
    """
    if grupo.empty:
        return ""
    
    val_extremo = grupo[columna_valor].max() if tipo == "max" else grupo[columna_valor].min()
    
    # CORRECCIÓN: Convertimos explícitamente a str cada estación para evitar fallas si son números
    estaciones = [
        str(est) for est in grupo[grupo[columna_valor] == val_extremo]['estacion'].dropna().unique()
    ]
    
    if not estaciones:
        return ""
    
    if len(estaciones) == 1:
        return f" (estación {estaciones[0]})"
    elif len(estaciones) == 2:
        return f" (estaciones {estaciones[0]} y {estaciones[1]})"
    else:
        # Para 3 o más estaciones: "X, Y y Z" sin importar si originalmente eran números
        return f" (estaciones {', '.join(estaciones[:-1])} y {estaciones[-1]})"

def get_base_statistics_text(grupo, grafico_label="Gráfico XXX"):
    """
    Calcula las estadísticas base de un parámetro e incluye las estaciones
    del valor máximo y mínimo entre paréntesis al costado de cada valor.
    """
    param = grupo["parametro"].iloc[0]
    unidad = grupo["unidad"].iloc[0]
    es_LD_list = grupo["es_LD"].tolist()
    valores_numericos = grupo["valor_num"].tolist()
    
    # Extraer valores unicos de LD (<LD) formateando comas
    ld_unicos = sorted(list(set([str(v).replace(".", ",") for v in grupo.loc[grupo['es_LD'], 'valor']])))
    
    if valores_numericos:
        minimo = min(valores_numericos)
        maximo = max(valores_numericos)
        promedio = sum(valores_numericos) / len(valores_numericos)
        
        # Obtener las estaciones correspondientes a los extremos
        estaciones_max = obtener_estaciones_extremo(grupo, 'valor_num', tipo='max')
        estaciones_min = obtener_estaciones_extremo(grupo, 'valor_num', tipo='min')
        
        min_t = f"{format_number(minimo)} {unidad}{estaciones_min}"
        max_t = f"{format_number(maximo)} {unidad}{estaciones_max}"
        
        # NUEVO: Aplicamos el formateo de cifras significativas dinámicas al promedio
        prom_t = f"{format_promedio_dinamico(promedio)} {unidad}"
    else:
        min_t, max_t, prom_t = "NaN", "NaN", "NaN"
    
    if all(es_LD_list):
        resumen = f"se encontraron por debajo del límite de detección ({', '.join(ld_unicos)} {unidad})"
    elif not any(es_LD_list):
        resumen = f"variaron desde un mínimo igual a {min_t} hasta un máximo igual a {max_t}, contando con un valor promedio de {prom_t}"
    else:
        resumen = f"variaron desde por debajo del límite de detección ({', '.join(ld_unicos)} {unidad}) hasta un máximo igual a {max_t}, con un valor promedio de {prom_t}"

    return f"Como se observa en el {grafico_label}, los valores de {param} registrados en todas las estaciones {resumen}.", valores_numericos, unidad

# =====================================================
# MULTIMÓDULO: AGUA SUPERFICIAL (ECA)
# =====================================================
def generar_texto_superficial(grupo, selected_standards, custom_otros_name="Otros"):
    texto_base, valores_numericos, unidad = get_base_statistics_text(grupo, "Gráfico XXX")
    texto_list = [texto_base]
    n_total = len(valores_numericos)
    
    if not selected_standards or not valores_numericos:
        return texto_base

    def check_compliance(lim_inf_col, lim_sup_col):
        if lim_inf_col not in grupo.columns and lim_sup_col not in grupo.columns:
            return None
        lim_inf = grupo[lim_inf_col].iloc[0] if lim_inf_col in grupo.columns else None
        lim_sup = grupo[lim_sup_col].iloc[0] if lim_sup_col in grupo.columns else None
        
        if pd.isna(lim_inf) and pd.isna(lim_sup):
            return None
        
        n_inc = 0
        for v in valores_numericos:
            if (pd.notna(lim_inf) and v < lim_inf) or (pd.notna(lim_sup) and v > lim_sup):
                n_inc += 1
        return n_inc

    def format_limits(lim_inf_col, lim_sup_col):
        lim_inf = grupo[lim_inf_col].iloc[0] if lim_inf_col in grupo.columns else None
        lim_sup = group_sup = grupo[lim_sup_col].iloc[0] if lim_sup_col in grupo.columns else None
        if pd.notna(lim_inf) and pd.notna(lim_sup):
            return f"{format_number(lim_inf)} a {format_number(lim_sup)}"
        elif pd.notna(lim_sup):
            return format_number(lim_sup)
        elif pd.notna(lim_inf):
            return format_number(lim_inf)
        return ""

    # Lógica combinada específica para ECA 2017 Categoría 3 D1 y D2
    if "ECA 2017 3D1" in selected_standards and "ECA 2017 3D2" in selected_standards:
        inc1 = check_compliance("lim_inf_eca_2017_3d1", "lim_sup_eca_2017_3d1")
        inc2 = check_compliance("lim_inf_eca_2017_3d2", "lim_sup_eca_2017_3d2")
        lim_fmt1 = format_limits("lim_inf_eca_2017_3d1", "lim_sup_eca_2017_3d1")
        lim_fmt2 = format_limits("lim_inf_eca_2017_3d2", "lim_sup_eca_2017_3d2")
        
        if inc1 is None and inc2 is None:
            texto_list.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 – D1 (riego de vegetales) y 3 - D2 (bebida de animales) aplicable para este parámetro.")
        else:
            porc1 = ("%g" % round(100 * inc1 / n_total, 2)).replace('.', ',') if inc1 is not None else "0"
            porc2 = ("%g" % round(100 * inc2 / n_total, 2)).replace('.', ',') if inc2 is not None else "0"
            
            if inc1 == 0 and inc2 == 0:
                texto_list.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({lim_fmt1} {unidad}) y 3 - D2 ({lim_fmt2} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif inc1 == n_total and inc2 == n_total:
                texto_list.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({lim_fmt1} {unidad}) y 3 - D2 ({lim_fmt2} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")
            else:
                p1 = "todos los registros cumplen con el ECA 2017" if inc1 == 0 else (f"todos los registros no cumplen con el ECA 2017" if inc1 == n_total else f"{inc1} ({porc1} %) de los registros no cumplen con el valor establecido")
                p2 = "todos los registros cumplen con el ECA 2017" if inc2 == 0 else (f"todos los registros no cumplen con el ECA 2017" if inc2 == n_total else f"{inc2} ({porc2} %) de los registros no cumplen con el valor establecido")
                texto_list.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({lim_fmt1} {unidad}), se observa que {p1}; y comparando con el ECA 2017 para agua para la categoría 3 - D2 ({lim_fmt2} {unidad}), se observa que {p2}.")
        
        # Eliminar de la lista común para evitar duplicación
        selected_standards = [s for s in selected_standards if s not in ["ECA 2017 3D1", "ECA 2017 3D2"]]

    # Mapeo estándar para el resto de normativas individuales
    for std in selected_standards:
        slug = std.lower().replace(" ", "_")
        if std == "Otros":
            slug = "otros"
            std_title = custom_otros_name
            ref_wording = f"el {custom_otros_name}"
            desc_str = ""
        elif slug.startswith("lga"):
            std_title = "LGA"
            ref_wording = f"la LGA para la categoría {std.split()[-1]}"
            desc_str = ""
        else:
            std_title = std
            ref_wording = f"el {std} para agua para la categoría {std.replace('ECA 2017 ', '').replace('ECA 2015 ', '').replace('ECA 2008 ', '')}"
            desc_str = " (conservación del ambiente acuático para ríos)" if "4E2" in std else ""

        inf_col = f"lim_inf_{slug}"
        sup_col = f"lim_sup_{slug}"
        
        inc = check_compliance(inf_col, sup_col)
        lim_fmt = format_limits(inf_col, sup_col)
        
        if inc is None:
            texto_list.append(f" Cabe mencionar que no existe {ref_wording}{desc_str} aplicable para este parámetro.")
        else:
            porc = ("%g" % round(100 * inc / n_total, 2)).replace('.', ',')
            if inc == 0:
                texto_list.append(f" Al comparar los resultados obtenidos con {ref_wording} ({lim_fmt} {unidad}), se observa que todos los registros cumplen con el {std_title.split()[0]}.")
            elif inc == n_total:
                texto_list.append(f" Al comparar los resultados obtenidos con {ref_wording} ({lim_fmt} {unidad}), se observa que todos los registros no cumplen con el {std_title.split()[0]}.")
            else:
                texto_list.append(f" Al comparar los resultados obtenidos con {ref_wording} ({lim_fmt} {unidad}), se observa que {inc} ({porc} %) de los registros no cumplen con el valor establecido.")
                
    return "".join(texto_list)

# =====================================================
# MULTIMÓDULO: AGUA SUBTERRÁNEA
# =====================================================
def generar_texto_subterranea(grupo, calc_ref_alto=True, calc_ref_bajo=False):
    texto_base, valores_numericos, unidad = get_base_statistics_text(grupo, "Gráfico XXX")
    texto_list = [texto_base]
    n_muestras = len(valores_numericos)
    
    if not valores_numericos:
        return texto_base
        
    promedio = sum(valores_numericos) / n_muestras
    desviacion = np.std(valores_numericos, ddof=1) if n_muestras > 1 else 0
    
    if calc_ref_alto or calc_ref_bajo:
        intro_eca = " Debido a que no se cuenta con un Estándar de Calidad Ambiental (ECA) específico para aguas subterráneas, se estableció como valor de referencia "
        partes_intro = []
        res_alto, res_bajo = "", ""
        
        if calc_ref_alto:
            ref_alto = promedio + (2 * desviacion)
            partes_intro.append(f"el promedio más dos veces la desviación estándar ({format_number(ref_alto)} {unidad})")
            n_exc = sum(1 for v in valores_numericos if v > ref_alto)
            porc_exc = f"{('%g' % round((n_exc/n_muestras)*100, 2))}".replace(".", ",")
            res_alto = "todos los registros se encuentran por debajo del valor de referencia alto" if n_exc == 0 else ("la totalidad de los registros exceden el valor de referencia alto" if n_exc == n_muestras else f"{n_exc} ({porc_exc} %) de los registros exceden el valor de referencia alto")
            
        if calc_ref_bajo:
            ref_bajo = promedio - (2 * desviacion)
            partes_intro.append(f"el promedio menos dos veces la desviación estándar ({format_number(ref_bajo)} {unidad})")
            n_deb = sum(1 for v in valores_numericos if v < ref_bajo)
            porc_deb = f"{('%g' % round((n_deb/n_muestras)*100, 2))}".replace(".", ",")
            res_bajo = "todos los registros se encuentran por encima del valor de referencia bajo" if n_deb == 0 else ("la totalidad de los registros se encuentran por debajo del valor de referencia bajo" if n_deb == n_muestras else f"{n_deb} ({porc_deb} %) de los registros se encuentran por debajo del valor de referencia bajo")
            
        texto_list.append(intro_eca + " y ".join(partes_intro) + ".")
        
        if calc_ref_alto and calc_ref_bajo:
            texto_list.append(f" Al realizar la comparación, se observa que {res_alto}; mientras que {res_bajo}.")
        elif calc_ref_alto:
            texto_list.append(f" Al realizar la comparación, se observa que {res_alto}.")
        elif calc_ref_bajo:
            texto_list.append(f" Al realizar la comparación, se observa que {res_bajo}.")
            
    return "".join(texto_list)

# =====================================================
# MULTIMÓDULO: EFLUENTES (LMP)
# =====================================================
def generar_texto_efluentes(grupo, selected_standards):
    texto_base, valores_numericos, unidad = get_base_statistics_text(grupo, "Gráfico XXX")
    texto_list = [texto_base]
    n_total = len(valores_numericos)
    
    if not selected_standards or not valores_numericos:
        return texto_base

    standards_clean = [s.lower().replace(" ", "_") for s in selected_standards]
    has_prior = False

    # 1. NMP MINERO 1996
    if "nmp_minero" in standards_clean:
        inf = grupo["lim_inf_nmp_minero"].iloc[0] if "lim_inf_nmp_minero" in grupo.columns else None
        sup = grupo["lim_sup_nmp_minero"].iloc[0] if "lim_sup_nmp_minero" in group.columns else None
        
        if pd.isna(inf) and pd.isna(sup):
            texto_list.append(" Cabe mencionar que no existe un NMP 1996 para efluentes minero-metalúrgicos aplicable para este parámetro.")
        else:
            n_inc = sum(1 for v in valores_numericos if (pd.notna(inf) and v < inf) or (pd.notna(sup) and v > sup))
            porc = ("%g" % round(100 * n_inc / n_total, 2)).replace('.', ',')
            lim_str = f"{format_number(inf)} a {format_number(sup)}" if pd.notna(inf) and pd.notna(sup) else format_number(sup or inf)
            
            if n_inc == 0:
                texto_list.append(f" Al comparar los resultados obtenidos con el NMP 1996 para efluentes minero-metalúrgicos ({lim_str} {unidad}), se observa que todos los registros cumplen con el NMP.")
            elif n_inc == n_total:
                texto_list.append(f" Al comparar los resultados obtenidos con el NMP 1996 para efluentes minero-metalúrgicos ({lim_str} {unidad}), se observa que todos los registros no cumplen con el NMP.")
            else:
                texto_list.append(f" Al comparar los resultados obtenidos con el NMP 1996 para efluentes minero-metalúrgicos ({lim_str} {unidad}), se observa que {n_inc} ({porc} %) de los registros no cumplen con el valor establecido.")
        has_prior = True

    # 2. LMP MINERO 2010
    if "lmp_2010_minero" in standards_clean:
        inf = grupo["lim_inf_lmp_2010_minero"].iloc[0] if "lim_inf_lmp_2010_minero" in grupo.columns else None
        sup = grupo["lim_sup_lmp_2010_minero"].iloc[0] if "lim_sup_lmp_2010_minero" in grupo.columns else None
        
        connector = " Por otro lado, no " if has_prior else " No "
        word_comp = "al" if has_prior else "Al"
        
        if pd.isna(inf) and pd.isna(sup):
            texto_list.append(f"{connector.lower()}existe un LMP 2010 para efluentes minero-metalúrgicos (valor en cualquier momento) aplicable para este parámetro.")
        else:
            n_inc = sum(1 for v in valores_numericos if (pd.notna(inf) and v < inf) or (pd.notna(sup) and v > sup))
            porc = ("%g" % round(100 * n_inc / n_total, 2)).replace('.', ',')
            lim_str = f"{format_number(inf)} a {format_number(sup)}" if pd.notna(inf) and pd.notna(sup) else format_number(sup or inf)
            prefix = " Por otro lado, al" if has_prior else " Al"
            
            if n_inc == 0:
                texto_list.append(f"{prefix} comparar los resultados obtenidos con el LMP 2010 para efluentes minero-metalúrgicos ({lim_str} {unidad}), se observa que todos los registros cumplen con el LMP.")
            elif n_inc == n_total:
                texto_list.append(f"{prefix} comparar los resultados obtenidos con el LMP 2010 para efluentes minero-metalúrgicos ({lim_str} {unidad}), se observa que todos los registros no cumplen con el LMP.")
            else:
                texto_list.append(f"{prefix} comparar los resultados obtenidos con el LMP 2010 para efluentes minero-metalúrgicos ({lim_str} {unidad}), se observa que {n_inc} ({porc} %) de los registros no cumplen con el valor establecido.")
        has_prior = True

    # 3. LMP DOMÉSTICO 2010
    if "lmp_2010_domestico" in standards_clean:
        inf = grupo["lim_inf_lmp_2010_domestico"].iloc[0] if "lim_inf_lmp_2010_domestico" in grupo.columns else None
        sup = grupo["lim_sup_lmp_2010_domestico"].iloc[0] if "lim_sup_lmp_2010_domestico" in grupo.columns else None
        
        prefix = " Por otro lado, no " if has_prior else " No "
        if pd.isna(inf) and pd.isna(sup):
            texto_list.append(f"{prefix}existe un valor en los LMP 2010 para efluentes domésticos o municipales aplicable para este parámetro.")
        else:
            n_inc = sum(1 for v in valores_numericos if (pd.notna(inf) and v < inf) or (pd.notna(sup) and v > sup))
            porc = ("%g" % round(100 * n_inc / n_total, 2)).replace('.', ',')
            lim_str = f"{format_number(inf)} a {format_number(sup)}" if pd.notna(inf) and pd.notna(sup) else format_number(sup or inf)
            prefix_comp = " Por otro lado, al" if has_prior else " Al"
            
            if n_inc == 0:
                texto_list.append(f"{prefix_comp} comparar los resultados obtenidos con el LMP 2010 para efluentes domésticos o municipales ({lim_str} {unidad}), se observa que todos los registros cumplen con el LMP.")
            elif n_inc == n_total:
                texto_list.append(f"{prefix_comp} comparar los resultados obtenidos con el LMP 2010 para efluentes domésticos o municipales ({lim_str} {unidad}), se observa que todos los registros no cumplen con el LMP.")
            else:
                texto_list.append(f"{prefix_comp} comparar los resultados obtenidos con LMP 2010 para efluentes domésticos o municipales ({lim_str} {unidad}), se observa que {n_inc} ({porc} %) de los registros no cumplen con el valor establecido.")

    return "".join(texto_list)

# =====================================================
# MULTIMÓDULO: SEDIMENTOS (CCME)
# =====================================================
def generar_texto_sedimentos(grupo, selected_standards):
    texto_base, valores_numericos, unidad = get_base_statistics_text(grupo, "Gráfico XXX")
    texto_list = [texto_base]
    
    if not selected_standards or not valores_numericos:
        return texto_base

    # Detectar el sufijo según la selección
    is_fresh = any("freshwater" in c.lower() or "fresh" in c.lower() for c in selected_standards)
    suffix = "freshwater" if is_fresh else "marine"
    tipo_env = "sedimentos de agua dulce" if is_fresh else "sedimentos marinos"
    
    val_isqg = grupo[f"ISQG_{suffix}"].iloc[0] if f"ISQG_{suffix}" in grupo.columns else np.nan
    val_pel = grupo[f"PEL_{suffix}"].iloc[0] if f"PEL_{suffix}" in grupo.columns else np.nan
    
    def comparar_ccme(val_limite, nombre_limite):
        if pd.isna(val_limite):
            return f" Cabe mencionar que no existe un {nombre_limite} para {tipo_env} aplicable para este parámetro."
        
        n_exc = sum(1 for v in valores_numericos if v > val_limite)
        porc = ("%g" % round((n_exc / len(valores_numericos)) * 100, 2)).replace(".", ",")
        lim_f = format_number(val_limite)
        
        if n_exc == 0:
            return f" Al comparar los resultados obtenidos con el {nombre_limite} ({lim_f} {unidad}), se observa que todos los registros cumplen con el valor establecido."
        elif n_exc == len(valores_numericos):
            return f" Al comparar los resultados obtenidos con el {nombre_limite} ({lim_f} {unidad}), se observa que todos los registros exceden el valor establecido."
        else:
            return f" Al comparar los resultados obtenidos con el {nombre_limite} ({lim_f} {unidad}), se observa que {n_exc} ({porc} %) de los registros exceden el valor establecido."

    texto_list.append(comparar_ccme(val_isqg, "ISQG"))
    texto_list.append(comparar_ccme(val_pel, "PEL"))
    
    return "".join(texto_list)
