import pandas as pd
import numpy as np
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================
# os.chdir(r'C:\Users\20171\OneDrive - Insideo Org\Desktop\Formatos\03_Calidad_agua_subterranea')

archivo = 'bbdd_molde.xlsx'
nombre_hoja_bbdd = "datos"
salida_txt = "informe_aguas_subterraneas.txt"

# --- OPCIONES DE VALOR DE REFERENCIA ---
# Activa con True o desactiva con False según lo que necesites comparar
CALCULAR_REF_ALTO = False  # Promedio + 2 DE (Para ver excesos)
CALCULAR_REF_BAJO = True  # Promedio - 2 DE (Para ver valores por debajo)

# =====================================================
# LECTURA Y LIMPIEZA DE DATOS
# =====================================================
if __name__ == "__main__":
    datos = pd.read_excel(archivo, sheet_name=nombre_hoja_bbdd)

    datos['parametro'] = datos['parametro'].str.strip()
    datos['unidad'] = datos['unidad'].str.strip()
    datos['valor'] = datos['valor'].astype(str)
    datos['es_LD'] = datos['valor'].str.contains("<")

    def limpiar_a_numerico(row):
        try:
            val_str = row['valor'].replace("<", "").replace(",", ".")
            val_num = float(val_str)
            return val_num / 2 if row['es_LD'] else val_num
        except:
            return np.nan

    datos['valor_num'] = datos.apply(limpiar_a_numerico, axis=1)
    df = datos.dropna(subset=["valor_num"])

# =====================================================
# FUNCIÓN PARA GENERAR TEXTO (CRITERIO ESTADÍSTICO)
# =====================================================
def generar_texto_subterranea(grupo):
    param = grupo["parametro"].iloc[0]
    unidad = grupo["unidad"].iloc[0]
    valores_num = grupo["valor_num"].tolist()
    es_LD_list = grupo["es_LD"].tolist()
    n_muestras = len(valores_num)
    
    # --- Estadísticos Base ---
    promedio = sum(valores_num) / n_muestras
    desviacion = np.std(valores_num, ddof=1) if n_muestras > 1 else 0
    minimo_val = min(valores_num)
    maximo_val = max(valores_num)
    
    # Formateo base %g
    # Formateo asegurando la coma decimal en cualquier sistema
    prom_t = ("%g" % promedio).replace('.', ',')
    min_t = ("%g" % minimo_val).replace('.', ',')
    max_t = ("%g" % maximo_val).replace('.', ',')

    # --- Texto de línea base ---
    ld_unicos = sorted(list(set([v.replace(".", ",") for v in grupo.loc[grupo['es_LD'], 'valor']])))
    
    if all(es_LD_list):
        resumen_base = f"se encontraron por debajo del límite de detección ({', '.join(ld_unicos)} {unidad})"
    elif not any(es_LD_list):
        resumen_base = f"variaron desde un mínimo igual a {min_t} {unidad} hasta un máximo igual a {max_t} {unidad}, contando con un valor promedio de {prom_t} {unidad}"
    else:
        resumen_base = f"variaron desde por debajo del límite de detección ({', '.join(ld_unicos)} {unidad}) hasta un máximo igual a {max_t} {unidad}, con un valor promedio de {prom_t} {unidad}"

    texto = [f"Como se observa en el Gráfico XXX, los valores de {param} registrados en todas las estaciones {resumen_base}."]

    # --- Lógica de Valores de Referencia ---
    if CALCULAR_REF_ALTO or CALCULAR_REF_BAJO:
        intro_eca = " Debido a que no se cuenta con un Estándar de Calidad Ambiental (ECA) específico para aguas subterráneas, se estableció como valor de referencia "
        partes_intro = []
        
        # Cálculos y comparaciones
        ref_alto = promedio + (2 * desviacion)
        ref_bajo = promedio - (2 * desviacion)
        
        res_alto = ""
        res_bajo = ""

        if CALCULAR_REF_ALTO:
            ref_alto_t = ("%g" % ref_alto).replace('.', ',')
            partes_intro.append(f"el promedio más dos veces la desviación estándar ({ref_alto_t} {unidad})")
            
            exceden = [v for v in valores_num if v > ref_alto]
            n_exc = len(exceden)
            porc_exc = str(round((n_exc / n_muestras) * 100, 2)).replace(".", ",")
            
            if n_exc == 0:
                res_alto = "todos los registros se encuentran por debajo del valor de referencia alto"
            elif n_exc == n_muestras:
                res_alto = "la totalidad de los registros exceden el valor de referencia alto"
            else:
                res_alto = f"{n_exc} ({porc_exc} %) de los registros exceden el valor de referencia alto"

        if CALCULAR_REF_BAJO:
            ref_bajo_t = ("%g" % ref_bajo).replace('.', ',')
            partes_intro.append(f"el promedio menos dos veces la desviación estándar ({ref_bajo_t} {unidad})")
            
            debajo = [v for v in valores_num if v < ref_bajo]
            n_deb = len(debajo)
            porc_deb = str(round((n_deb / n_muestras) * 100, 2)).replace(".", ",")
            
            if n_deb == 0:
                res_bajo = "todos los registros se encuentran por encima del valor de referencia bajo"
            elif n_deb == n_muestras:
                res_bajo = "la totalidad de los registros se encuentran por debajo del valor de referencia bajo"
            else:
                res_bajo = f"{n_deb} ({porc_deb} %) de los registros se encuentran por debajo del valor de referencia bajo"

        # Unir introducción
        texto.append(intro_eca + " y ".join(partes_intro) + ".")

        # Unir resultados de comparación
        if CALCULAR_REF_ALTO and CALCULAR_REF_BAJO:
            texto.append(f" Al realizar la comparación, se observa que {res_alto}; mientras que {res_bajo}.")
        elif CALCULAR_REF_ALTO:
            texto.append(f" Al realizar la comparación, se observa que {res_alto}.")
        elif CALCULAR_REF_BAJO:
            texto.append(f" Al realizar la comparación, se observa que {res_bajo}.")

    return "".join(texto)

# =====================================================
# EJECUCIÓN
# =====================================================
if __name__ == "__main__":
    resultados = []
    for param, grupo in df.groupby("parametro"):
        if not grupo.empty:
            texto_param = generar_texto_subterranea(grupo)
            resultados.append(f"### {param.upper()}\n\n{texto_param}\n")

    with open(salida_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(resultados))

    print(f"✅ Informe generado en: {salida_txt}")