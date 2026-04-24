import pandas as pd
import numpy as np
import os
import locale

# Configuración del locale para usar comas decimales (Windows y Linux)
try:
    locale.setlocale(locale.LC_NUMERIC, "Spanish_Spain")
except:
    try:
        locale.setlocale(locale.LC_NUMERIC, "es_ES.UTF-8")
    except:
        pass

# =====================================================
# CONFIGURACIÓN
# =====================================================
# Nombre de archivo Excel
archivo = 'bbdd_molde_efluentes.xlsx'

# Archivo de salida
salida_txt = "informe_efluentes.txt"

#Elección de LMP (activar o desactivar el ECA de interés cambiando a True y False, respectivamente)
#NMP 1996 minero-metalúrgicas
NMP_MINERO = False

#LMP 2010 doméstico
LMP_2010_DOMESTICO = False

#LMP 2010 minero
LMP_2010_MINERO = True

# =====================================================
# LECTURA DE DATOS (Solo si se ejecuta como script)
# =====================================================
if __name__ == "__main__":
    datos = pd.read_excel(archivo, sheet_name='datos')
    eca = pd.read_excel(archivo, sheet_name='lmp')

    # Eliminamos los espacios en blanco al inicio y al final de cada valor de texto en la columna "parametro"
    datos['parametro'] = datos['parametro'].str.strip()
    eca['parametro'] = eca['parametro'].str.strip()

    # Manejar <LD
    datos['valor'] = datos['valor'].astype(str)
    datos['es_LD'] = datos['valor'].str.startswith("<")

    # convertir <LD en LD/2
    datos.loc[datos['es_LD'], 'valor_num'] = datos.loc[datos['es_LD'], 'valor'].str.replace("<", "", regex=False).astype(float) / 2
    datos.loc[~datos['es_LD'], 'valor_num'] = datos.loc[~datos['es_LD'], 'valor'].astype(float)
    datos['valor_num'] = datos['valor_num'].astype(float)

    # Merge con ECA y eliminación de nan
    df = datos.merge(eca, on=['parametro', 'unidad'], how="left")
    df["valor"] = df["valor"].replace(["nan", "NaN"], np.nan)
    df = df.dropna(subset=["valor"])

    # Asegurar tipo datetime
    df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True)

# =====================================================
# FUNCIÓN PARA GENERAR TEXTO
# =====================================================
def generar_texto(grupo):
    #grupo['valor'] = grupo['valor'].replace(["nan", "NaN"], np.nan)
    #grupo = grupo.dropna(subset=["valor"])
    param = grupo["parametro"].iloc[0]
    unidad = grupo["unidad"].iloc[0]
    es_LD = grupo["es_LD"].tolist()
    
    valores_originales = grupo["valor"].astype(str).tolist()
    valores_unicos_LD = []
    valores_numericos = []
    texto = []
    
    for val in valores_originales:
        if val.startswith("<"):
            if val not in valores_unicos_LD:  # no repetir <LD
                valores_unicos_LD.append(val)
            try:
                ld = float(val.replace("<", ""))
                valores_numericos.append(ld / 2)  # <LD = LD/2
            except:
                pass
        else:
            valores_numericos.append(float(val))
            
    #valores_unicos_LD_unidos = ", ".join(valores_unicos_LD) + f" {unidad}"
    
    minimo = min(valores_numericos)
    maximo = max(valores_numericos)
    promedio = sum(valores_numericos) / len(valores_numericos)
    minimo = locale.format_string("%g",minimo)
    maximo = locale.format_string("%g",maximo)
    promedio = locale.format_string("%g",promedio)
    
    #---- Texto de línea base ----
    if all(es_LD):
        valores_unicos_LD = [x.replace(".", ",") for x in valores_unicos_LD]
        valores_resumen = f"se encontraron por debajo del límite de detección ({', '.join(valores_unicos_LD)} {unidad})"
    elif not any(es_LD):
        valores_resumen = f"variaron desde un mínimo igual a {minimo} {unidad} hasta un máximo igual a {maximo} {unidad}, contando con un valor promedio de {promedio} {unidad}"
    else:
        valores_unicos_LD = [x.replace(".", ",") for x in valores_unicos_LD]
        valores_resumen = f"variaron desde por debajo del límite de detección ({', '.join(valores_unicos_LD)} {unidad}) hasta un máximo igual a {maximo} {unidad}, con un valor promedio de {promedio} {unidad}"

    texto.append(f"Como se observa en el Gráfico XXX, los valores de {param} registrados en todas las estaciones {valores_resumen}.")    

    #################### Comparación con Normativa ####################
    #NMP 1996 minero-metalúrgicas
    if NMP_MINERO is True:
        n_total_nmp_minero = len(valores_numericos)
    
        lim_inf_nmp_minero = grupo["lim_inf_nmp_minero"].iloc[0] if "lim_inf_nmp_minero" in grupo.columns else None
        lim_sup_nmp_minero = grupo["lim_sup_nmp_minero"].iloc[0] if "lim_sup_nmp_minero" in grupo.columns else None
        n_inc_nmp_minero = 0
        if pd.isna(lim_inf_nmp_minero) is not True or pd.isna(lim_sup_nmp_minero) is not True:
            for v in valores_numericos:
                if (lim_inf_nmp_minero is not None and v < lim_inf_nmp_minero) or (lim_sup_nmp_minero is not None and v > lim_sup_nmp_minero):
                    n_inc_nmp_minero += 1
            porc_nmp_minero = round(100 * n_inc_nmp_minero / n_total_nmp_minero,2)
        else:
            porc_nmp_minero = None
            
    #LMP 2010 doméstico
    if LMP_2010_DOMESTICO is True:
        n_total_lmp_2010_domestico = len(valores_numericos)
    
        lim_inf_lmp_2010_domestico = grupo["lim_inf_lmp_2010_domestico"].iloc[0] if "lim_inf_lmp_2010_domestico" in grupo.columns else None
        lim_sup_lmp_2010_domestico = grupo["lim_sup_lmp_2010_domestico"].iloc[0] if "lim_sup_lmp_2010_domestico" in grupo.columns else None
        n_inc_lmp_2010_domestico = 0
        if pd.isna(lim_inf_lmp_2010_domestico) is not True or pd.isna(lim_sup_lmp_2010_domestico) is not True:
            for v in valores_numericos:
                if (lim_inf_lmp_2010_domestico is not None and v < lim_inf_lmp_2010_domestico) or (lim_sup_lmp_2010_domestico is not None and v > lim_sup_lmp_2010_domestico):
                    n_inc_lmp_2010_domestico += 1
            porc_lmp_2010_domestico = round(100 * n_inc_lmp_2010_domestico / n_total_lmp_2010_domestico,2)
        else:
            porc_lmp_2010_domestico = None
            
    #LMP 2010 minero
    if LMP_2010_MINERO is True:
        n_total_lmp_2010_minero = len(valores_numericos)
    
        lim_inf_lmp_2010_minero = grupo["lim_inf_lmp_2010_minero"].iloc[0] if "lim_inf_lmp_2010_minero" in grupo.columns else None
        lim_sup_lmp_2010_minero = grupo["lim_sup_lmp_2010_minero"].iloc[0] if "lim_sup_lmp_2010_minero" in grupo.columns else None
        n_inc_lmp_2010_minero = 0
        if pd.isna(lim_inf_lmp_2010_minero) is not True or pd.isna(lim_sup_lmp_2010_minero) is not True:
            for v in valores_numericos:
                if (lim_inf_lmp_2010_minero is not None and v < lim_inf_lmp_2010_minero) or (lim_sup_lmp_2010_minero is not None and v > lim_sup_lmp_2010_minero):
                    n_inc_lmp_2010_minero += 1
            porc_lmp_2010_minero = round(100 * n_inc_lmp_2010_minero / n_total_lmp_2010_minero,2)
        else:
            porc_lmp_2010_minero = None    
        
    # ---- Texto final según casos ----
    ################## LMP 2010 MINERO ##################
    if LMP_2010_MINERO is True and LMP_2010_DOMESTICO is False:
        if pd.notna(lim_inf_lmp_2010_minero) and pd.notna(lim_sup_lmp_2010_minero):
            lmp_formateado_1 = str(lim_inf_lmp_2010_minero).replace(".", ",") + ' a '+ str(lim_sup_lmp_2010_minero).replace(".", ",")
        elif pd.isna(lim_inf_lmp_2010_minero) and pd.notna(lim_sup_lmp_2010_minero):
            lmp_formateado_1 = str(lim_sup_lmp_2010_minero).replace(".", ",")
        elif pd.notna(lim_inf_lmp_2010_minero) and pd.isna(lim_sup_lmp_2010_minero):
            lmp_formateado_1 = str(lim_inf_lmp_2010_minero).replace(".", ",")
            
        if porc_lmp_2010_minero is None and porc_lmp_2010_minero is None:
            texto.append(f" Cabe mencionar que no existe un LMP 2010 para efluentes minero-metalúrgicos (valor en cualquier momento) aplicable para este parámetro.")
        else:
            if porc_lmp_2010_minero == 0:
                texto.append(f" Al comparar los resultados obtenidos con el LMP 2010 para efluentes minero-metalúrgicos ({lmp_formateado_1} {unidad}), se observa que todos los registros cumplen con el LMP.")
            elif porc_lmp_2010_minero == 100:
                texto.append(f" Al comparar los resultados obtenidos con el LMP 2010 para efluentes minero-metalúrgicos ({lmp_formateado_1} {unidad}), se observa que todos los registros no cumplen con el LMP.")          
            else:
                parte1_lmp_2010_minero = []                
                if porc_lmp_2010_minero not in (None, 0, 100):
                    parte1_lmp_2010_minero.append(f"Al comparar los resultados obtenidos con el LMP 2010 para efluentes minero-metalúrgicos ({lmp_formateado_1} {unidad}), se observa que {n_inc_lmp_2010_minero} ({str(porc_lmp_2010_minero).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lmp_2010_minero[0]}")
                    
            
    ################## LMP 2010 MINERO Y DOMÉSTICO ##################             
    if LMP_2010_MINERO is True and LMP_2010_DOMESTICO is True:
        if pd.notna(lim_inf_lmp_2010_minero) and pd.notna(lim_sup_lmp_2010_minero):
            lmp_formateado_1 = str(lim_inf_lmp_2010_minero).replace(".", ",") + ' a '+ str(lim_sup_lmp_2010_minero).replace(".", ",")
        elif pd.isna(lim_inf_lmp_2010_minero) and pd.notna(lim_sup_lmp_2010_minero):
            lmp_formateado_1 = str(lim_sup_lmp_2010_minero).replace(".", ",")
        elif pd.notna(lim_inf_lmp_2010_minero) and pd.isna(lim_sup_lmp_2010_minero):
            lmp_formateado_1 = str(lim_inf_lmp_2010_minero).replace(".", ",")
                
        if porc_lmp_2010_minero is None and porc_lmp_2010_minero is None:
            texto.append(f" Cabe mencionar que no existe un LMP 2010 para efluentes minero-metalúrgicos (valor en cualquier momento) aplicable para este parámetro.")
        else:
            if porc_lmp_2010_minero == 0:
                texto.append(f" Al comparar los resultados obtenidos con el LMP 2010 para efluentes minero-metalúrgicos ({lmp_formateado_1} {unidad}), se observa que todos los registros cumplen con el LMP.")
            elif porc_lmp_2010_minero == 100:
                texto.append(f" Al comparar los resultados obtenidos con el LMP 2010 para efluentes minero-metalúrgicos ({lmp_formateado_1} {unidad}), se observa que todos los registros no cumplen con el LMP.")          
            else:
                parte1_lmp_2010_minero = []                
                if porc_lmp_2010_minero not in (None, 0, 100):
                    parte1_lmp_2010_minero.append(f"Al comparar los resultados obtenidos con el LMP 2010 para efluentes minero-metalúrgicos ({lmp_formateado_1} {unidad}), se observa que {n_inc_lmp_2010_minero} ({str(porc_lmp_2010_minero).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lmp_2010_minero[0]}")
                
        if pd.notna(lim_inf_lmp_2010_domestico) and pd.notna(lim_sup_lmp_2010_domestico):
            lmp_formateado_2 = str(lim_inf_lmp_2010_domestico).replace(".", ",") + ' a '+ str(lim_sup_lmp_2010_domestico).replace(".", ",")
        elif pd.isna(lim_inf_lmp_2010_domestico) and pd.notna(lim_sup_lmp_2010_domestico):
            lmp_formateado_2 = str(lim_sup_lmp_2010_domestico).replace(".", ",")
        elif pd.notna(lim_inf_lmp_2010_domestico) and pd.isna(lim_sup_lmp_2010_domestico):
            lmp_formateado_2 = str(lim_inf_lmp_2010_domestico).replace(".", ",")
                    
        if porc_lmp_2010_domestico is None and porc_lmp_2010_domestico is None:
            texto.append(f" Por otro lado, no existe un valor en los LMP 2010 para efluentes domésticos o municipales aplicable para este parámetro.")
        else:
            if porc_lmp_2010_domestico == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el LMP 2010 para efluentes domésticos o municipales ({lmp_formateado_2} {unidad}), se observa que todos los registros cumplen con el LMP.")
            elif porc_lmp_2010_domestico == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el LMP 2010 para efluentes domésticos o municipales ({lmp_formateado_2} {unidad}), se observa que todos los registros no cumplen con el LMP.")          
            else:
                parte1_lmp_2010_domestico = []                
                if porc_lmp_2010_domestico not in (None, 0, 100):
                    parte1_lmp_2010_domestico.append(f"Por otro lado, al comparar los resultados obtenidos con LMP 2010 para efluentes domésticos o municipales ({lmp_formateado_2} {unidad}), se observa que {n_inc_lmp_2010_domestico} ({str(porc_lmp_2010_domestico).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lmp_2010_domestico[0]}")
                    
    ################## LMP 2010 DOMESTICO ##################
    if LMP_2010_DOMESTICO is True and LMP_2010_MINERO is False:
        if pd.notna(lim_inf_lmp_2010_domestico) and pd.notna(lim_sup_lmp_2010_domestico):
            lmp_formateado_1 = str(lim_inf_lmp_2010_domestico).replace(".", ",") + ' a '+ str(lim_sup_lmp_2010_domestico).replace(".", ",")
        elif pd.isna(lim_inf_lmp_2010_domestico) and pd.notna(lim_sup_lmp_2010_domestico):
            lmp_formateado_1 = str(lim_sup_lmp_2010_domestico).replace(".", ",")
        elif pd.notna(lim_inf_lmp_2010_domestico) and pd.isna(lim_sup_lmp_2010_domestico):
            lmp_formateado_1 = str(lim_inf_lmp_2010_domestico).replace(".", ",")
        
        if porc_lmp_2010_domestico is None and porc_lmp_2010_domestico is None:
            texto.append(f" Cabe mencionar que no existe un LMP 2010 para efluentes domésticos o municipales aplicable para este parámetro.")
        else:
            if porc_lmp_2010_domestico == 0:
                texto.append(f" Al comparar los resultados obtenidos con el LMP 2010 para efluentes domésticos o municipales ({lmp_formateado_1} {unidad}), se observa que todos los registros cumplen con el LMP.")
            elif porc_lmp_2010_domestico == 100:
                texto.append(f" Al comparar los resultados obtenidos con el LMP 2010 para efluentes domésticos o municipales ({lmp_formateado_1} {unidad}), se observa que todos los registros no cumplen con el LMP.")          
            else:
                parte1_lmp_2010_domestico = []                
                if porc_lmp_2010_domestico not in (None, 0, 100):
                    parte1_lmp_2010_domestico.append(f"Al comparar los resultados obtenidos con el LMP 2010 para efluentes domésticos o municipales ({lmp_formateado_1} {unidad}), se observa que {n_inc_lmp_2010_domestico} ({str(porc_lmp_2010_domestico).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lmp_2010_domestico[0]}")
                                      
    ################## NMP MINERO ##################
    if NMP_MINERO is True:
        if pd.notna(lim_inf_nmp_minero) and pd.notna(lim_sup_nmp_minero):
            lmp_formateado_1 = str(lim_inf_nmp_minero).replace(".", ",") + ' a '+ str(lim_sup_nmp_minero).replace(".", ",")
        elif pd.isna(lim_inf_nmp_minero) and pd.notna(lim_sup_nmp_minero):
            lmp_formateado_1 = str(lim_sup_nmp_minero).replace(".", ",")
        elif pd.notna(lim_inf_nmp_minero) and pd.isna(lim_sup_nmp_minero):
            lmp_formateado_1 = str(lim_inf_nmp_minero).replace(".", ",")
            
        if porc_nmp_minero is None and porc_nmp_minero is None:
            texto.append(f" Por otro lado, no existe un valor en los NMP 1996 para efluentes minero-metalúrgicos (valor en cualquier momento) aplicable para este parámetro.")
        else:
            if porc_nmp_minero == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el NMP 1996 para efluentes minero-metalúrgicos ({lmp_formateado_1} {unidad}), se observa que todos los registros cumplen con el NMP.")
            elif porc_nmp_minero == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el NMP 1996 para efluentes minero-metalúrgicos ({lmp_formateado_1} {unidad}), se observa que todos los registros no cumplen con el NMP.")          
            else:
                parte1_nmp_minero = []                
                if porc_nmp_minero not in (None, 0, 100):
                    parte1_nmp_minero.append(f"Por otro lado, al comparar los resultados obtenidos con el NMP 1996 para efluentes minero-metalúrgicos ({lmp_formateado_1} {unidad}), se observa que {n_inc_nmp_minero} ({str(porc_nmp_minero).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_nmp_minero[0]}")
                    
    return "".join(texto)

# =====================================================
# GENERAR TEXTO PARA TODOS LOS PARÁMETROS
# =====================================================
if __name__ == "__main__":
    resultados = []
    for param, grupo in df.groupby("parametro"):
        texto_param = generar_texto(grupo)
        resultados.append(f"### {param}\n\n{texto_param}\n")

    # Guardar en archivo
    with open(salida_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(resultados))

    print(f"✅ Informe generado en: {salida_txt}")
