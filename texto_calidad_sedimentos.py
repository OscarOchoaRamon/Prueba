import pandas as pd
import numpy as np
import os
import locale

# Configuración del locale para usar comas decimales (Windows)
try:
    locale.setlocale(locale.LC_NUMERIC, "Spanish_Spain")
except:
    try:
        locale.setlocale(locale.LC_NUMERIC, "es_ES.UTF-8")
    except:
        pass # Si falla el locale, continuará con puntos por defecto

# =====================================================
# 1. CONFIGURACIÓN DE RUTA Y ARCHIVOS
# =====================================================
# Cambia esta ruta si es necesario
# os.chdir(r'C:\Users\20171\OneDrive - Insideo Org\Desktop\Formatos\03_Calidad_sedimentos')

archivo = 'bbdd_molde_sedimentos.xlsx'
salida_txt = "informe_sedimentos.txt"

# Elección de normativa (True para activar, False para desactivar)
CCME_2001_FRESHWATER = False
CCME_2001_MARINE = True

# =====================================================
# 2. LECTURA Y PREPARACIÓN DE DATOS
# =====================================================
if __name__ == "__main__":
    datos = pd.read_excel(archivo, sheet_name='datos')
    eca = pd.read_excel(archivo, sheet_name='normativa')

    # Limpieza de espacios en nombres
    datos['parametro'] = datos['parametro'].str.strip()
    eca['parametro'] = eca['parametro'].str.strip()
    datos['unidad'] = datos['unidad'].str.strip()
    eca['unidad'] = eca['unidad'].str.strip()

    # Manejo de <LD (Límites de Detección)
    datos['valor'] = datos['valor'].astype(str)
    datos['es_LD'] = datos['valor'].str.contains("<")

    def limpiar_valor_num(row):
        try:
            val_str = row['valor'].replace("<", "").replace(",", ".")
            val_num = float(val_str)
            # Si es <LD, usamos la mitad del valor (LD/2)
            return val_num / 2 if row['es_LD'] else val_num
        except:
            return np.nan

    datos['valor_num'] = datos.apply(limpiar_valor_num, axis=1)

    # Unimos los datos con la normativa
    df = datos.merge(eca, on=['parametro', 'unidad'], how="left")
    df = df.dropna(subset=["valor_num"])

# =====================================================
# 3. FUNCIÓN PARA GENERAR EL TEXTO DEL INFORME
# =====================================================
def generar_texto(grupo):
    param = grupo["parametro"].iloc[0]
    unidad = grupo["unidad"].iloc[0]
    valores_num = grupo["valor_num"].tolist()
    es_LD_list = grupo["es_LD"].tolist()
    
    # --- Estadísticos ---
    min_v = min(valores_num)
    max_v = max(valores_num)
    prom_v = sum(valores_num) / len(valores_num)
    
    # Formateo con "%g" para coincidir exactamente con el código original
    min_t = locale.format_string("%g", min_v)
    max_t = locale.format_string("%g", max_v)
    prom_t = locale.format_string("%g", prom_v)
    
    # --- Texto de Línea Base ---
    ld_unicos = sorted(list(set([v.replace(".", ",") for v in grupo.loc[grupo['es_LD'], 'valor']])))
    
    if all(es_LD_list):
        resumen = f"se encontraron por debajo del límite de detección ({', '.join(ld_unicos)} {unidad})"
    elif not any(es_LD_list):
        resumen = f"variaron desde un mínimo igual a {min_t} {unidad} hasta un máximo igual a {max_t} {unidad}, contando con un valor promedio de {prom_t} {unidad}"
    else:
        resumen = f"variaron desde por debajo del límite de detección ({', '.join(ld_unicos)} {unidad}) hasta un máximo igual a {max_t} {unidad}, con un valor promedio de {prom_t} {unidad}"

    texto_final = [f"Como se observa en el Gráfico XXX, los valores de {param} registrados en todas las estaciones {resumen}."]

    # --- Función interna para comparar con límites (ISQG / PEL) ---
    def comparar_con_limite(valor_limite, nombre_limite):
        if pd.isna(valor_limite):
            return None
        
        # Un registro no cumple si es MAYOR al límite establecido
        n_inc = sum(1 for v in valores_num if v > valor_limite)
        porc = round((n_inc / len(valores_num)) * 100, 2)
        lim_f = str(valor_limite).replace(".", ",")
        porc_f = str(porc).replace(".", ",")
        
        if n_inc == 0:
            return f" Al comparar los resultados obtenidos con el {nombre_limite} ({lim_f} {unidad}), se observa que todos los registros cumplen con el valor establecido."
        elif porc == 100:
            return f" Al comparar los resultados obtenidos con el {nombre_limite} ({lim_f} {unidad}), se observa que todos los registros exceden el valor establecido."
        else:
            return f" Al comparar los resultados obtenidos con el {nombre_limite} ({lim_f} {unidad}), se observa que {n_inc} ({porc_f} %) de los registros exceden el valor establecido."

    # --- Selección de columnas de normativa ---
    if CCME_2001_FRESHWATER:
        col_isqg, col_pel = "ISQG_freshwater", "PEL_freshwater"
        tipo_env = "sedimentos de agua dulce"
    else:
        col_isqg, col_pel = "ISQG_marine", "PEL_marine"
        tipo_env = "sedimentos marinos"

    val_isqg = grupo[col_isqg].iloc[0] if col_isqg in grupo.columns else np.nan
    val_pel = grupo[col_pel].iloc[0] if col_pel in grupo.columns else np.nan

    txt_isqg = comparar_con_limite(val_isqg, "ISQG")
    txt_pel = comparar_con_limite(val_pel, "PEL")

    # --- Construcción final del párrafo con casos de normativa faltante ---
    if txt_isqg is None and txt_pel is None:
        texto_final.append(f" Cabe mencionar que no existe un ISQG ni un PEL para {tipo_env} aplicable para este parámetro.")
    else:
        # Lógica para ISQG
        if txt_isqg:
            texto_final.append(txt_isqg)
        else:
            texto_final.append(f" Cabe mencionar que no existe un ISQG para {tipo_env} aplicable para este parámetro.")
            
        # Lógica para PEL
        if txt_pel:
            texto_final.append(txt_pel)
        else:
            texto_final.append(f" Cabe mencionar que no existe un PEL para {tipo_env} aplicable para este parámetro.")

    return "".join(texto_final)

# =====================================================
# 4. EJECUCIÓN Y GUARDADO
# =====================================================
if __name__ == "__main__":
    informe_completo = []

    for parametro, datos_grupo in df.groupby("parametro"):
        if not datos_grupo.empty:
            parrafo = generar_texto(datos_grupo)
            informe_completo.append(f"### {parametro.upper()}\n{parrafo}")

    with open(salida_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(informe_completo))

    print(f"✅ Informe generado en: {salida_txt}")