import pandas as pd
import numpy as np
import os
import locale

locale.setlocale(locale.LC_NUMERIC, "Spanish_Spain")  # en Windows

# =====================================================
# CONFIGURACIÓN
# =====================================================
# Ruta de trabajo
# os.chdir(r'C:\Users\USER\Downloads')

# Nombre de archivo Excel
archivo = 'BBDD_manantiales (filtrada).xlsx'
nombre_hoja_bbdd = "datos"

# Archivo de salida
salida_txt = "informe_agua_superficial.txt"

#Elección de ECA (activar o desactivar el ECA de interés cambiando a True y False, respectivamente)
#Ley general de agua
LGA_I = False
LGA_II = False
LGA_III = False
LGA_IV = False
LGA_V = False
LGA_VI = False

#ECA 2008
ECA_2008_CAT_1A1 = False
ECA_2008_CAT_1A2 = False
ECA_2008_CAT_1A3 = False
ECA_2008_CAT_1B1 = False
ECA_2008_CAT_1B2 = False
ECA_2008_CAT_2C1 = False
ECA_2008_CAT_2C2 = False
ECA_2008_CAT_2C3 = False
ECA_2008_CAT_3D1 = False
ECA_2008_CAT_3D2 = False
ECA_2008_CAT_4E1 = False
ECA_2008_CAT_4E2_CYS = False
ECA_2008_CAT_4E2_S = False
ECA_2008_CAT_4E3_E = False
ECA_2008_CAT_4E3_M = False

#ECA 2015
ECA_2015_CAT_1A1 = False
ECA_2015_CAT_1A2 = False
ECA_2015_CAT_1A3 = False
ECA_2015_CAT_1B1 = False
ECA_2015_CAT_1B2 = False
ECA_2015_CAT_2C1 = False
ECA_2015_CAT_2C2 = False
ECA_2015_CAT_2C3 = False
ECA_2015_CAT_2C4 = False
ECA_2015_CAT_3D1 = False
ECA_2015_CAT_3D2 = False
ECA_2015_CAT_4E1 = False
ECA_2015_CAT_4E2_CYS = False
ECA_2015_CAT_4E2_S = False
ECA_2015_CAT_4E3_E = False
ECA_2015_CAT_4E3_M = False

#ECA 2017
ECA_2017_CAT_1A1 = False
ECA_2017_CAT_1A2 = False
ECA_2017_CAT_1A3 = False
ECA_2017_CAT_1B1 = False
ECA_2017_CAT_1B2 = False
ECA_2017_CAT_2C1 = False
ECA_2017_CAT_2C2 = False
ECA_2017_CAT_2C3 = False
ECA_2017_CAT_2C4 = False
ECA_2017_CAT_3D1 = True
ECA_2017_CAT_3D2 = True
ECA_2017_CAT_4E1 = False
ECA_2017_CAT_4E2_CYS = False
ECA_2017_CAT_4E2_S = False
ECA_2017_CAT_4E3_E = False
ECA_2017_CAT_4E3_M = False

# =====================================================
# LECTURA DE DATOS
# =====================================================
if __name__ == "__main__":
    datos = pd.read_excel(archivo, sheet_name=nombre_hoja_bbdd)
    eca = pd.read_excel(archivo, sheet_name='eca')

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

    #################### Comparación con ECA 2008 ####################
    #Categoría ECA 2008 1-A1
    if ECA_2008_CAT_1A1 is True:
        n_total_eca2008_1a1 = len(valores_numericos)
    
        lim_inf_eca2008_1a1 = grupo["lim_inf_eca_2008_1a1"].iloc[0] if "lim_inf_eca_2008_1a1" in grupo.columns else None
        lim_sup_eca2008_1a1 = grupo["lim_sup_eca_2008_1a1"].iloc[0] if "lim_sup_eca_2008_1a1" in grupo.columns else None
        n_inc_eca2008_1a1 = 0
        if pd.isna(lim_inf_eca2008_1a1) is not True or pd.isna(lim_sup_eca2008_1a1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_1a1 is not None and v < lim_inf_eca2008_1a1) or (lim_sup_eca2008_1a1 is not None and v > lim_sup_eca2008_1a1):
                    n_inc_eca2008_1a1 += 1
            porc_eca2008_1a1 = round(100 * n_inc_eca2008_1a1 / n_total_eca2008_1a1,2)
        else:
            porc_eca2008_1a1 = None
            
    #Categoría ECA 2008 1-A2
    if ECA_2008_CAT_1A2 is True:
        n_total_eca2008_1a2 = len(valores_numericos)
    
        lim_inf_eca2008_1a2 = grupo["lim_inf_eca_2008_1a2"].iloc[0] if "lim_inf_eca_2008_1a2" in grupo.columns else None
        lim_sup_eca2008_1a2 = grupo["lim_sup_eca_2008_1a2"].iloc[0] if "lim_sup_eca_2008_1a2" in grupo.columns else None
        n_inc_eca2008_1a2 = 0
        if pd.isna(lim_inf_eca2008_1a2) is not True or pd.isna(lim_sup_eca2008_1a2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_1a2 is not None and v < lim_inf_eca2008_1a2) or (lim_sup_eca2008_1a2 is not None and v > lim_sup_eca2008_1a2):
                    n_inc_eca2008_1a2 += 1
            porc_eca2008_1a2 = round(100 * n_inc_eca2008_1a2 / n_total_eca2008_1a2,2)
        else:
            porc_eca2008_1a2 = None
            
    #Categoría ECA 2008 1-A3
    if ECA_2008_CAT_1A3 is True:
        n_total_eca2008_1a3 = len(valores_numericos)
    
        lim_inf_eca2008_1a3 = grupo["lim_inf_eca_2008_1a3"].iloc[0] if "lim_inf_eca_2008_1a3" in grupo.columns else None
        lim_sup_eca2008_1a3 = grupo["lim_sup_eca_2008_1a3"].iloc[0] if "lim_sup_eca_2008_1a3" in grupo.columns else None
        n_inc_eca2008_1a3 = 0
        if pd.isna(lim_inf_eca2008_1a3) is not True or pd.isna(lim_sup_eca2008_1a3) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_1a3 is not None and v < lim_inf_eca2008_1a3) or (lim_sup_eca2008_1a3 is not None and v > lim_sup_eca2008_1a3):
                    n_inc_eca2008_1a3 += 1
            porc_eca2008_1a3 = round(100 * n_inc_eca2008_1a3 / n_total_eca2008_1a3,2)
        else:
            porc_eca2008_1a3 = None
            
    #Categoría ECA 2008 1-B1
    if ECA_2008_CAT_1B1 is True:
        n_total_eca2008_1b1 = len(valores_numericos)
    
        lim_inf_eca2008_1b1 = grupo["lim_inf_eca_2008_1b1"].iloc[0] if "lim_inf_eca_2008_1b1" in grupo.columns else None
        lim_sup_eca2008_1b1 = grupo["lim_sup_eca_2008_1b1"].iloc[0] if "lim_sup_eca_2008_1b1" in grupo.columns else None
        n_inc_eca2008_1b1 = 0
        if pd.isna(lim_inf_eca2008_1b1) is not True or pd.isna(lim_sup_eca2008_1b1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_1b1 is not None and v < lim_inf_eca2008_1b1) or (lim_sup_eca2008_1b1 is not None and v > lim_sup_eca2008_1b1):
                    n_inc_eca2008_1b1 += 1
            porc_eca2008_1b1 = round(100 * n_inc_eca2008_1b1 / n_total_eca2008_1b1,2)
        else:
            porc_eca2008_1b1 = None
            
    #Categoría ECA 2008 1-B2
    if ECA_2008_CAT_1B2 is True:
        n_total_eca2008_1b2 = len(valores_numericos)
    
        lim_inf_eca2008_1b2 = grupo["lim_inf_eca_2008_1b2"].iloc[0] if "lim_inf_eca_2008_1b2" in grupo.columns else None
        lim_sup_eca2008_1b2 = grupo["lim_sup_eca_2008_1b2"].iloc[0] if "lim_sup_eca_2008_1b2" in grupo.columns else None
        n_inc_eca2008_1b2 = 0
        if pd.isna(lim_inf_eca2008_1b2) is not True or pd.isna(lim_sup_eca2008_1b2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_1b2 is not None and v < lim_inf_eca2008_1b2) or (lim_sup_eca2008_1b2 is not None and v > lim_sup_eca2008_1b2):
                    n_inc_eca2008_1b2 += 1
            porc_eca2008_1b2 = round(100 * n_inc_eca2008_1b2 / n_total_eca2008_1b2,2)
        else:
            porc_eca2008_1b2 = None
            
    #Categoría ECA 2008 2-C1
    if ECA_2008_CAT_2C1 is True:
        n_total_eca2008_2c1 = len(valores_numericos)
    
        lim_inf_eca2008_2c1 = grupo["lim_inf_eca_2008_2c1"].iloc[0] if "lim_inf_eca_2008_2c1" in grupo.columns else None
        lim_sup_eca2008_2c1 = grupo["lim_sup_eca_2008_2c1"].iloc[0] if "lim_sup_eca_2008_2c1" in grupo.columns else None
        n_inc_eca2008_2c1 = 0
        if pd.isna(lim_inf_eca2008_2c1) is not True or pd.isna(lim_sup_eca2008_2c1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_2c1 is not None and v < lim_inf_eca2008_2c1) or (lim_sup_eca2008_2c1 is not None and v > lim_sup_eca2008_2c1):
                    n_inc_eca2008_2c1 += 1
            porc_eca2008_2c1 = round(100 * n_inc_eca2008_2c1 / n_total_eca2008_2c1,2)
        else:
            porc_eca2008_2c1 = None
            
    #Categoría ECA 2008 2-C2
    if ECA_2008_CAT_2C2 is True:
        n_total_eca2008_2c2 = len(valores_numericos)
    
        lim_inf_eca2008_2c2 = grupo["lim_inf_eca_2008_2c2"].iloc[0] if "lim_inf_eca_2008_2c2" in grupo.columns else None
        lim_sup_eca2008_2c2 = grupo["lim_sup_eca_2008_2c2"].iloc[0] if "lim_sup_eca_2008_2c2" in grupo.columns else None
        n_inc_eca2008_2c2 = 0
        if pd.isna(lim_inf_eca2008_2c2) is not True or pd.isna(lim_sup_eca2008_2c2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_2c2 is not None and v < lim_inf_eca2008_2c2) or (lim_sup_eca2008_2c2 is not None and v > lim_sup_eca2008_2c2):
                    n_inc_eca2008_2c2 += 1
            porc_eca2008_2c2 = round(100 * n_inc_eca2008_2c2 / n_total_eca2008_2c2,2)
        else:
            porc_eca2008_2c2 = None
            
    #Categoría ECA 2008 2-C3
    if ECA_2008_CAT_2C3 is True:
        n_total_eca2008_2c3 = len(valores_numericos)
    
        lim_inf_eca2008_2c3 = grupo["lim_inf_eca_2008_2c3"].iloc[0] if "lim_inf_eca_2008_2c3" in grupo.columns else None
        lim_sup_eca2008_2c3 = grupo["lim_sup_eca_2008_2c3"].iloc[0] if "lim_sup_eca_2008_2c3" in grupo.columns else None
        n_inc_eca2008_2c3 = 0
        if pd.isna(lim_inf_eca2008_2c3) is not True or pd.isna(lim_sup_eca2008_2c3) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_2c3 is not None and v < lim_inf_eca2008_2c3) or (lim_sup_eca2008_2c3 is not None and v > lim_sup_eca2008_2c3):
                    n_inc_eca2008_2c3 += 1
            porc_eca2008_2c3 = round(100 * n_inc_eca2008_2c3 / n_total_eca2008_2c3,2)
        else:
            porc_eca2008_2c3 = None
            
    #Categoría ECA 2008 3-D1
    if ECA_2008_CAT_3D1 is True and ECA_2008_CAT_3D2 is False:
        n_total_eca2008_3d1 = len(valores_numericos)
    
        lim_inf_eca2008_3d1 = grupo["lim_inf_eca_2008_3d1"].iloc[0] if "lim_inf_eca_2008_3d1" in grupo.columns else None
        lim_sup_eca2008_3d1 = grupo["lim_sup_eca_2008_3d1"].iloc[0] if "lim_sup_eca_2008_3d1" in grupo.columns else None
        n_inc_eca2008_3d1 = 0
        if pd.isna(lim_inf_eca2008_3d1) is not True or pd.isna(lim_sup_eca2008_3d1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_3d1 is not None and v < lim_inf_eca2008_3d1) or (lim_sup_eca2008_3d1 is not None and v > lim_sup_eca2008_3d1):
                    n_inc_eca2008_3d1 += 1
            porc_eca2008_3d1 = round(100 * n_inc_eca2008_3d1 / n_total_eca2008_3d1,2)
        else:
            porc_eca2008_3d1 = None
            
    #Categoría ECA 2008 3-D2
    if ECA_2008_CAT_3D2 is True and ECA_2008_CAT_3D1 is False:
        n_total_eca2008_3d2 = len(valores_numericos)
    
        lim_inf_eca2008_3d2 = grupo["lim_inf_eca_2008_3d2"].iloc[0] if "lim_inf_eca_2008_3d2" in grupo.columns else None
        lim_sup_eca2008_3d2 = grupo["lim_sup_eca_2008_3d2"].iloc[0] if "lim_sup_eca_2008_3d2" in grupo.columns else None
        n_inc_eca2008_3d2 = 0
        if pd.isna(lim_inf_eca2008_3d2) is not True or pd.isna(lim_sup_eca2008_3d2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_3d2 is not None and v < lim_inf_eca2008_3d2) or (lim_sup_eca2008_3d2 is not None and v > lim_sup_eca2008_3d2):
                    n_inc_eca2008_3d2 += 1
            porc_eca2008_3d2 = round(100 * n_inc_eca2008_3d2 / n_total_eca2008_3d2,2)
        else:
            porc_eca2008_3d2 = None
    
    #Categoría ECA 2008 3-D1 y 3-D2
    if ECA_2008_CAT_3D1 is True and ECA_2008_CAT_3D2 is True:
        n_total = len(valores_numericos)
    
        # Categoría 3 – D1
        lim_inf_eca2008_3d1 = grupo["lim_inf_eca_2008_3d1"].iloc[0] if "lim_inf_eca_2008_3d1" in grupo.columns else None
        lim_sup_eca2008_3d1 = grupo["lim_sup_eca_2008_3d1"].iloc[0] if "lim_sup_eca_2008_3d1" in grupo.columns else None
        n_inc_eca2008_3d1 = 0
        if pd.isna(lim_inf_eca2008_3d1) is not True or pd.isna(lim_sup_eca2008_3d1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_3d1 is not None and v < lim_inf_eca2008_3d1) or (lim_sup_eca2008_3d1 is not None and v > lim_sup_eca2008_3d1):
                    n_inc_eca2008_3d1 += 1
            porc_eca2008_3d1 = round(100 * n_inc_eca2008_3d1 / n_total,2)
        else:
            porc_eca2008_3d1 = None
    
        # Categoría 3 – D2
        lim_inf_eca2008_3d2 = grupo["lim_inf_eca_2008_3d2"].iloc[0] if "lim_inf_eca_2008_3d2" in grupo.columns else None
        lim_sup_eca2008_3d2 = grupo["lim_sup_eca_2008_3d2"].iloc[0] if "lim_sup_eca_2008_3d2" in grupo.columns else None
        n_inc_eca2008_3d2 = 0
        if pd.isna(lim_inf_eca2008_3d2) is not True or pd.isna(lim_sup_eca2008_3d2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_3d2 is not None and v < lim_inf_eca2008_3d2) or (lim_sup_eca2008_3d2 is not None and v > lim_sup_eca2008_3d2):
                    n_inc_eca2008_3d2 += 1
            porc_eca2008_3d2 = round(100 * n_inc_eca2008_3d2 / n_total,2)
        else:
            porc_eca2008_3d2 = None
            
    #Categoría ECA 2008 4-E1
    if ECA_2008_CAT_4E1 is True:
        n_total_eca2008_4e1 = len(valores_numericos)
    
        lim_inf_eca2008_4e1 = grupo["lim_inf_eca_2008_4e1"].iloc[0] if "lim_inf_eca_2008_4e1" in grupo.columns else None
        lim_sup_eca2008_4e1 = grupo["lim_sup_eca_2008_4e1"].iloc[0] if "lim_sup_eca_2008_4e1" in grupo.columns else None
        n_inc_eca2008_4e1 = 0
        if pd.isna(lim_inf_eca2008_4e1) is not True or pd.isna(lim_sup_eca2008_4e1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_4e1 is not None and v < lim_inf_eca2008_4e1) or (lim_sup_eca2008_4e1 is not None and v > lim_sup_eca2008_4e1):
                    n_inc_eca2008_4e1 += 1
            porc_eca2008_4e1 = round(100 * n_inc_eca2008_4e1 / n_total_eca2008_4e1,2)
        else:
            porc_eca2008_4e1 = None
            
    #Categoría ECA 2008 4-E2_CYS
    if ECA_2008_CAT_4E2_CYS is True:
        n_total_eca2008_4e2_cys = len(valores_numericos)
    
        lim_inf_eca2008_4e2_cys = grupo["lim_inf_eca_2008_4e2_cys"].iloc[0] if "lim_inf_eca_2008_4e2_cys" in grupo.columns else None
        lim_sup_eca2008_4e2_cys = grupo["lim_sup_eca_2008_4e2_cys"].iloc[0] if "lim_sup_eca_2008_4e2_cys" in grupo.columns else None
        n_inc_eca2008_4e2_cys = 0
        if pd.isna(lim_inf_eca2008_4e2_cys) is not True or pd.isna(lim_sup_eca2008_4e2_cys) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_4e2_cys is not None and v < lim_inf_eca2008_4e2_cys) or (lim_sup_eca2008_4e2_cys is not None and v > lim_sup_eca2008_4e2_cys):
                    n_inc_eca2008_4e2_cys += 1
            porc_eca2008_4e2_cys = round(100 * n_inc_eca2008_4e2_cys / n_total_eca2008_4e2_cys,2)
        else:
            porc_eca2008_4e2_cys = None
            
    #Categoría ECA 2008 4-E2_S
    if ECA_2008_CAT_4E2_S is True:
        n_total_eca2008_4e2_s = len(valores_numericos)
    
        lim_inf_eca2008_4e2_s = grupo["lim_inf_eca_2008_4e2_s"].iloc[0] if "lim_inf_eca_2008_4e2_s" in grupo.columns else None
        lim_sup_eca2008_4e2_s = grupo["lim_sup_eca_2008_4e2_s"].iloc[0] if "lim_sup_eca_2008_4e2_s" in grupo.columns else None
        n_inc_eca2008_4e2_s = 0
        if pd.isna(lim_inf_eca2008_4e2_s) is not True or pd.isna(lim_sup_eca2008_4e2_s) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_4e2_s is not None and v < lim_inf_eca2008_4e2_s) or (lim_sup_eca2008_4e2_s is not None and v > lim_sup_eca2008_4e2_s):
                    n_inc_eca2008_4e2_s += 1
            porc_eca2008_4e2_s = round(100 * n_inc_eca2008_4e2_s / n_total_eca2008_4e2_s,2)
        else:
            porc_eca2008_4e2_s = None
            
    #Categoría ECA 2008 4-E3_E
    if ECA_2008_CAT_4E3_E is True:
        n_total_eca2008_4e3_e = len(valores_numericos)
    
        lim_inf_eca2008_4e3_e = grupo["lim_inf_eca_2008_4e3_e"].iloc[0] if "lim_inf_eca_2008_4e3_e" in grupo.columns else None
        lim_sup_eca2008_4e3_e = grupo["lim_sup_eca_2008_4e3_e"].iloc[0] if "lim_sup_eca_2008_4e3_e" in grupo.columns else None
        n_inc_eca2008_4e3_e = 0
        if pd.isna(lim_inf_eca2008_4e3_e) is not True or pd.isna(lim_sup_eca2008_4e3_e) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_4e3_e is not None and v < lim_inf_eca2008_4e3_e) or (lim_sup_eca2008_4e3_e is not None and v > lim_sup_eca2008_4e3_e):
                    n_inc_eca2008_4e3_e += 1
            porc_eca2008_4e3_e = round(100 * n_inc_eca2008_4e3_e / n_total_eca2008_4e3_e,2)
        else:
            porc_eca2008_4e3_e = None
            
    #Categoría ECA 2008 4-E3_M
    if ECA_2008_CAT_4E3_M is True:
        n_total_eca2008_4e3_m = len(valores_numericos)
    
        lim_inf_eca2008_4e3_m = grupo["lim_inf_eca_2008_4e3_m"].iloc[0] if "lim_inf_eca_2008_4e3_m" in grupo.columns else None
        lim_sup_eca2008_4e3_m = grupo["lim_sup_eca_2008_4e3_m"].iloc[0] if "lim_sup_eca_2008_4e3_m" in grupo.columns else None
        n_inc_eca2008_4e3_m = 0
        if pd.isna(lim_inf_eca2008_4e3_m) is not True or pd.isna(lim_sup_eca2008_4e3_m) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2008_4e3_m is not None and v < lim_inf_eca2008_4e3_m) or (lim_sup_eca2008_4e3_m is not None and v > lim_sup_eca2008_4e3_m):
                    n_inc_eca2008_4e3_m += 1
            porc_eca2008_4e3_m = round(100 * n_inc_eca2008_4e3_m / n_total_eca2008_4e3_m,2)
        else:
            porc_eca2008_4e3_m = None
            
    #################### Comparación con ECA 2015 ####################
    #Categoría ECA 2015 1-A1
    if ECA_2015_CAT_1A1 is True:
        n_total_eca2015_1a1 = len(valores_numericos)
    
        lim_inf_eca2015_1a1 = grupo["lim_inf_eca_2015_1a1"].iloc[0] if "lim_inf_eca_2015_1a1" in grupo.columns else None
        lim_sup_eca2015_1a1 = grupo["lim_sup_eca_2015_1a1"].iloc[0] if "lim_sup_eca_2015_1a1" in grupo.columns else None
        n_inc_eca2015_1a1 = 0
        if pd.isna(lim_inf_eca2015_1a1) is not True or pd.isna(lim_sup_eca2015_1a1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_1a1 is not None and v < lim_inf_eca2015_1a1) or (lim_sup_eca2015_1a1 is not None and v > lim_sup_eca2015_1a1):
                    n_inc_eca2015_1a1 += 1
            porc_eca2015_1a1 = round(100 * n_inc_eca2015_1a1 / n_total_eca2015_1a1,2)
        else:
            porc_eca2015_1a1 = None
            
    #Categoría ECA 2015 1-A2
    if ECA_2015_CAT_1A2 is True:
        n_total_eca2015_1a2 = len(valores_numericos)
    
        lim_inf_eca2015_1a2 = grupo["lim_inf_eca_2015_1a2"].iloc[0] if "lim_inf_eca_2015_1a2" in grupo.columns else None
        lim_sup_eca2015_1a2 = grupo["lim_sup_eca_2015_1a2"].iloc[0] if "lim_sup_eca_2015_1a2" in grupo.columns else None
        n_inc_eca2015_1a2 = 0
        if pd.isna(lim_inf_eca2015_1a2) is not True or pd.isna(lim_sup_eca2015_1a2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_1a2 is not None and v < lim_inf_eca2015_1a2) or (lim_sup_eca2015_1a2 is not None and v > lim_sup_eca2015_1a2):
                    n_inc_eca2015_1a2 += 1
            porc_eca2015_1a2 = round(100 * n_inc_eca2015_1a2 / n_total_eca2015_1a2,2)
        else:
            porc_eca2015_1a2 = None
            
    #Categoría ECA 2015 1-A3
    if ECA_2015_CAT_1A3 is True:
        n_total_eca2015_1a3 = len(valores_numericos)
    
        lim_inf_eca2015_1a3 = grupo["lim_inf_eca_2015_1a3"].iloc[0] if "lim_inf_eca_2015_1a3" in grupo.columns else None
        lim_sup_eca2015_1a3 = grupo["lim_sup_eca_2015_1a3"].iloc[0] if "lim_sup_eca_2015_1a3" in grupo.columns else None
        n_inc_eca2015_1a3 = 0
        if pd.isna(lim_inf_eca2015_1a3) is not True or pd.isna(lim_sup_eca2015_1a3) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_1a3 is not None and v < lim_inf_eca2015_1a3) or (lim_sup_eca2015_1a3 is not None and v > lim_sup_eca2015_1a3):
                    n_inc_eca2015_1a3 += 1
            porc_eca2015_1a3 = round(100 * n_inc_eca2015_1a3 / n_total_eca2015_1a3,2)
        else:
            porc_eca2015_1a3 = None
            
    #Categoría ECA 2015 1-B1
    if ECA_2015_CAT_1B1 is True:
        n_total_eca2015_1b1 = len(valores_numericos)
    
        lim_inf_eca2015_1b1 = grupo["lim_inf_eca_2015_1b1"].iloc[0] if "lim_inf_eca_2015_1b1" in grupo.columns else None
        lim_sup_eca2015_1b1 = grupo["lim_sup_eca_2015_1b1"].iloc[0] if "lim_sup_eca_2015_1b1" in grupo.columns else None
        n_inc_eca2015_1b1 = 0
        if pd.isna(lim_inf_eca2015_1b1) is not True or pd.isna(lim_sup_eca2015_1b1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_1b1 is not None and v < lim_inf_eca2015_1b1) or (lim_sup_eca2015_1b1 is not None and v > lim_sup_eca2015_1b1):
                    n_inc_eca2015_1b1 += 1
            porc_eca2015_1b1 = round(100 * n_inc_eca2015_1b1 / n_total_eca2015_1b1,2)
        else:
            porc_eca2015_1b1 = None
            
    #Categoría ECA 2015 1-B2
    if ECA_2015_CAT_1B2 is True:
        n_total_eca2015_1b2 = len(valores_numericos)
    
        lim_inf_eca2015_1b2 = grupo["lim_inf_eca_2015_1b2"].iloc[0] if "lim_inf_eca_2015_1b2" in grupo.columns else None
        lim_sup_eca2015_1b2 = grupo["lim_sup_eca_2015_1b2"].iloc[0] if "lim_sup_eca_2015_1b2" in grupo.columns else None
        n_inc_eca2015_1b2 = 0
        if pd.isna(lim_inf_eca2015_1b2) is not True or pd.isna(lim_sup_eca2015_1b2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_1b2 is not None and v < lim_inf_eca2015_1b2) or (lim_sup_eca2015_1b2 is not None and v > lim_sup_eca2015_1b2):
                    n_inc_eca2015_1b2 += 1
            porc_eca2015_1b2 = round(100 * n_inc_eca2015_1b2 / n_total_eca2015_1b2,2)
        else:
            porc_eca2015_1b2 = None
            
    #Categoría ECA 2015 2-C1
    if ECA_2015_CAT_2C1 is True:
        n_total_eca2015_2c1 = len(valores_numericos)
    
        lim_inf_eca2015_2c1 = grupo["lim_inf_eca_2015_2c1"].iloc[0] if "lim_inf_eca_2015_2c1" in grupo.columns else None
        lim_sup_eca2015_2c1 = grupo["lim_sup_eca_2015_2c1"].iloc[0] if "lim_sup_eca_2015_2c1" in grupo.columns else None
        n_inc_eca2015_2c1 = 0
        if pd.isna(lim_inf_eca2015_2c1) is not True or pd.isna(lim_sup_eca2015_2c1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_2c1 is not None and v < lim_inf_eca2015_2c1) or (lim_sup_eca2015_2c1 is not None and v > lim_sup_eca2015_2c1):
                    n_inc_eca2015_2c1 += 1
            porc_eca2015_2c1 = round(100 * n_inc_eca2015_2c1 / n_total_eca2015_2c1,2)
        else:
            porc_eca2015_2c1 = None
            
    #Categoría ECA 2015 2-C2
    if ECA_2015_CAT_2C2 is True:
        n_total_eca2015_2c2 = len(valores_numericos)
    
        lim_inf_eca2015_2c2 = grupo["lim_inf_eca_2015_2c2"].iloc[0] if "lim_inf_eca_2015_2c2" in grupo.columns else None
        lim_sup_eca2015_2c2 = grupo["lim_sup_eca_2015_2c2"].iloc[0] if "lim_sup_eca_2015_2c2" in grupo.columns else None
        n_inc_eca2015_2c2 = 0
        if pd.isna(lim_inf_eca2015_2c2) is not True or pd.isna(lim_sup_eca2015_2c2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_2c2 is not None and v < lim_inf_eca2015_2c2) or (lim_sup_eca2015_2c2 is not None and v > lim_sup_eca2015_2c2):
                    n_inc_eca2015_2c2 += 1
            porc_eca2015_2c2 = round(100 * n_inc_eca2015_2c2 / n_total_eca2015_2c2,2)
        else:
            porc_eca2015_2c2 = None
            
    #Categoría ECA 2015 2-C3
    if ECA_2015_CAT_2C3 is True:
        n_total_eca2015_2c3 = len(valores_numericos)
    
        lim_inf_eca2015_2c3 = grupo["lim_inf_eca_2015_2c3"].iloc[0] if "lim_inf_eca_2015_2c3" in grupo.columns else None
        lim_sup_eca2015_2c3 = grupo["lim_sup_eca_2015_2c3"].iloc[0] if "lim_sup_eca_2015_2c3" in grupo.columns else None
        n_inc_eca2015_2c3 = 0
        if pd.isna(lim_inf_eca2015_2c3) is not True or pd.isna(lim_sup_eca2015_2c3) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_2c3 is not None and v < lim_inf_eca2015_2c3) or (lim_sup_eca2015_2c3 is not None and v > lim_sup_eca2015_2c3):
                    n_inc_eca2015_2c3 += 1
            porc_eca2015_2c3 = round(100 * n_inc_eca2015_2c3 / n_total_eca2015_2c3,2)
        else:
            porc_eca2015_2c3 = None
            
    #Categoría ECA 2015 2-C4
    if ECA_2015_CAT_2C4 is True:
        n_total_eca2015_2c4 = len(valores_numericos)
    
        lim_inf_eca2015_2c4 = grupo["lim_inf_eca_2015_2c4"].iloc[0] if "lim_inf_eca_2015_2c4" in grupo.columns else None
        lim_sup_eca2015_2c4 = grupo["lim_sup_eca_2015_2c4"].iloc[0] if "lim_sup_eca_2015_2c4" in grupo.columns else None
        n_inc_eca2015_2c4 = 0
        if pd.isna(lim_inf_eca2015_2c4) is not True or pd.isna(lim_sup_eca2015_2c4) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_2c4 is not None and v < lim_inf_eca2015_2c4) or (lim_sup_eca2015_2c4 is not None and v > lim_sup_eca2015_2c4):
                    n_inc_eca2015_2c4 += 1
            porc_eca2015_2c4 = round(100 * n_inc_eca2015_2c4 / n_total_eca2015_2c4,2)
        else:
            porc_eca2015_2c4 = None
            
    #Categoría ECA 2015 3-D1
    if ECA_2015_CAT_3D1 is True and ECA_2015_CAT_3D2 is False:
        n_total_eca2015_3d1 = len(valores_numericos)
    
        lim_inf_eca2015_3d1 = grupo["lim_inf_eca_2015_3d1"].iloc[0] if "lim_inf_eca_2015_3d1" in grupo.columns else None
        lim_sup_eca2015_3d1 = grupo["lim_sup_eca_2015_3d1"].iloc[0] if "lim_sup_eca_2015_3d1" in grupo.columns else None
        n_inc_eca2015_3d1 = 0
        if pd.isna(lim_inf_eca2015_3d1) is not True or pd.isna(lim_sup_eca2015_3d1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_3d1 is not None and v < lim_inf_eca2015_3d1) or (lim_sup_eca2015_3d1 is not None and v > lim_sup_eca2015_3d1):
                    n_inc_eca2015_3d1 += 1
            porc_eca2015_3d1 = round(100 * n_inc_eca2015_3d1 / n_total_eca2015_3d1,2)
        else:
            porc_eca2015_3d1 = None
            
    #Categoría ECA 2015 3-D2
    if ECA_2015_CAT_3D2 is True and ECA_2015_CAT_3D1 is False:
        n_total_eca2015_3d2 = len(valores_numericos)
    
        lim_inf_eca2015_3d2 = grupo["lim_inf_eca_2015_3d2"].iloc[0] if "lim_inf_eca_2015_3d2" in grupo.columns else None
        lim_sup_eca2015_3d2 = grupo["lim_sup_eca_2015_3d2"].iloc[0] if "lim_sup_eca_2015_3d2" in grupo.columns else None
        n_inc_eca2015_3d2 = 0
        if pd.isna(lim_inf_eca2015_3d2) is not True or pd.isna(lim_sup_eca2015_3d2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_3d2 is not None and v < lim_inf_eca2015_3d2) or (lim_sup_eca2015_3d2 is not None and v > lim_sup_eca2015_3d2):
                    n_inc_eca2015_3d2 += 1
            porc_eca2015_3d2 = round(100 * n_inc_eca2015_3d2 / n_total_eca2015_3d2,2)
        else:
            porc_eca2015_3d2 = None
            
    #Categoría ECA 2015 3-D1 y 3-D2
    if ECA_2015_CAT_3D1 is True and ECA_2015_CAT_3D2 is True:
        n_total = len(valores_numericos)
    
        # Categoría 3 – D1
        lim_inf_eca2015_3d1 = grupo["lim_inf_eca_2015_3d1"].iloc[0] if "lim_inf_eca_2015_3d1" in grupo.columns else None
        lim_sup_eca2015_3d1 = grupo["lim_sup_eca_2015_3d1"].iloc[0] if "lim_sup_eca_2015_3d1" in grupo.columns else None
        n_inc_eca2015_3d1 = 0
        if pd.isna(lim_inf_eca2015_3d1) is not True or pd.isna(lim_sup_eca2015_3d1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_3d1 is not None and v < lim_inf_eca2015_3d1) or (lim_sup_eca2015_3d1 is not None and v > lim_sup_eca2015_3d1):
                    n_inc_eca2015_3d1 += 1
            porc_eca2015_3d1 = round(100 * n_inc_eca2015_3d1 / n_total,2)
        else:
            porc_eca2015_3d1 = None
    
        # Categoría 3 – D2
        lim_inf_eca2015_3d2 = grupo["lim_inf_eca_2015_3d2"].iloc[0] if "lim_inf_eca_2015_3d2" in grupo.columns else None
        lim_sup_eca2015_3d2 = grupo["lim_sup_eca_2015_3d2"].iloc[0] if "lim_sup_eca_2015_3d2" in grupo.columns else None
        n_inc_eca2015_3d2 = 0
        if pd.isna(lim_inf_eca2015_3d2) is not True or pd.isna(lim_sup_eca2015_3d2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_3d2 is not None and v < lim_inf_eca2015_3d2) or (lim_sup_eca2015_3d2 is not None and v > lim_sup_eca2015_3d2):
                    n_inc_eca2015_3d2 += 1
            porc_eca2015_3d2 = round(100 * n_inc_eca2015_3d2 / n_total,2)
        else:
            porc_eca2015_3d2 = None
            
    #Categoría ECA 2015 4-E1
    if ECA_2015_CAT_4E1 is True:
        n_total_eca2015_4e1 = len(valores_numericos)
    
        lim_inf_eca2015_4e1 = grupo["lim_inf_eca_2015_4e1"].iloc[0] if "lim_inf_eca_2015_4e1" in grupo.columns else None
        lim_sup_eca2015_4e1 = grupo["lim_sup_eca_2015_4e1"].iloc[0] if "lim_sup_eca_2015_4e1" in grupo.columns else None
        n_inc_eca2015_4e1 = 0
        if pd.isna(lim_inf_eca2015_4e1) is not True or pd.isna(lim_sup_eca2015_4e1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_4e1 is not None and v < lim_inf_eca2015_4e1) or (lim_sup_eca2015_4e1 is not None and v > lim_sup_eca2015_4e1):
                    n_inc_eca2015_4e1 += 1
            porc_eca2015_4e1 = round(100 * n_inc_eca2015_4e1 / n_total_eca2015_4e1,2)
        else:
            porc_eca2015_4e1 = None
            
    #Categoría ECA 2015 4-E2 CYS
    if ECA_2015_CAT_4E2_CYS is True:
        n_total_eca2015_4e2_cys = len(valores_numericos)
    
        lim_inf_eca2015_4e2_cys = grupo["lim_inf_eca_2015_4e2_cys"].iloc[0] if "lim_inf_eca_2015_4e2_cys" in grupo.columns else None
        lim_sup_eca2015_4e2_cys = grupo["lim_sup_eca_2015_4e2_cys"].iloc[0] if "lim_sup_eca_2015_4e2_cys" in grupo.columns else None
        n_inc_eca2015_4e2_cys = 0
        if pd.isna(lim_inf_eca2015_4e2_cys) is not True or pd.isna(lim_sup_eca2015_4e2_cys) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_4e2_cys is not None and v < lim_inf_eca2015_4e2_cys) or (lim_sup_eca2015_4e2_cys is not None and v > lim_sup_eca2015_4e2_cys):
                    n_inc_eca2015_4e2_cys += 1
            porc_eca2015_4e2_cys = round(100 * n_inc_eca2015_4e2_cys / n_total_eca2015_4e2_cys,2)
        else:
            porc_eca2015_4e2_cys = None
            
    #Categoría ECA 2015 4-E2 S
    if ECA_2015_CAT_4E2_S is True:
        n_total_eca2015_4e2_s = len(valores_numericos)
    
        lim_inf_eca2015_4e2_s = grupo["lim_inf_eca_2015_4e2_s"].iloc[0] if "lim_inf_eca_2015_4e2_s" in grupo.columns else None
        lim_sup_eca2015_4e2_s = grupo["lim_sup_eca_2015_4e2_s"].iloc[0] if "lim_sup_eca_2015_4e2_s" in grupo.columns else None
        n_inc_eca2015_4e2_s = 0
        if pd.isna(lim_inf_eca2015_4e2_s) is not True or pd.isna(lim_sup_eca2015_4e2_s) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_4e2_s is not None and v < lim_inf_eca2015_4e2_s) or (lim_sup_eca2015_4e2_s is not None and v > lim_sup_eca2015_4e2_s):
                    n_inc_eca2015_4e2_s += 1
            porc_eca2015_4e2_s = round(100 * n_inc_eca2015_4e2_s / n_total_eca2015_4e2_s,2)
        else:
            porc_eca2015_4e2_s = None
            
    #Categoría ECA 2015 4-E3 E
    if ECA_2015_CAT_4E3_E is True:
        n_total_eca2015_4e3_e = len(valores_numericos)
    
        lim_inf_eca2015_4e3_e = grupo["lim_inf_eca_2015_4e3_e"].iloc[0] if "lim_inf_eca_2015_4e3_e" in grupo.columns else None
        lim_sup_eca2015_4e3_e = grupo["lim_sup_eca_2015_4e3_e"].iloc[0] if "lim_sup_eca_2015_4e3_e" in grupo.columns else None
        n_inc_eca2015_4e3_e = 0
        if pd.isna(lim_inf_eca2015_4e3_e) is not True or pd.isna(lim_sup_eca2015_4e3_e) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_4e3_e is not None and v < lim_inf_eca2015_4e3_e) or (lim_sup_eca2015_4e3_e is not None and v > lim_sup_eca2015_4e3_e):
                    n_inc_eca2015_4e3_e += 1
            porc_eca2015_4e3_e = round(100 * n_inc_eca2015_4e3_e / n_total_eca2015_4e3_e,2)
        else:
            porc_eca2015_4e3_e = None
            
    #Categoría ECA 2015 4-E3 M
    if ECA_2015_CAT_4E3_M is True:
        n_total_eca2015_4e3_m = len(valores_numericos)
    
        lim_inf_eca2015_4e3_m = grupo["lim_inf_eca_2015_4e3_m"].iloc[0] if "lim_inf_eca_2015_4e3_m" in grupo.columns else None
        lim_sup_eca2015_4e3_m = grupo["lim_sup_eca_2015_4e3_m"].iloc[0] if "lim_sup_eca_2015_4e3_m" in grupo.columns else None
        n_inc_eca2015_4e3_m = 0
        if pd.isna(lim_inf_eca2015_4e3_m) is not True or pd.isna(lim_sup_eca2015_4e3_m) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2015_4e3_m is not None and v < lim_inf_eca2015_4e3_m) or (lim_sup_eca2015_4e3_m is not None and v > lim_sup_eca2015_4e3_m):
                    n_inc_eca2015_4e3_m += 1
            porc_eca2015_4e3_m = round(100 * n_inc_eca2015_4e3_m / n_total_eca2015_4e3_m,2)
        else:
            porc_eca2015_4e3_m = None
            
    #################### Comparación con ECA 2017 ####################            
    #Categoría ECA 2017 1-A1
    if ECA_2017_CAT_1A1 is True:
        n_total_eca2017_1a1 = len(valores_numericos)
    
        lim_inf_eca2017_1a1 = grupo["lim_inf_eca_2017_1a1"].iloc[0] if "lim_inf_eca_2017_1a1" in grupo.columns else None
        lim_sup_eca2017_1a1 = grupo["lim_sup_eca_2017_1a1"].iloc[0] if "lim_sup_eca_2017_1a1" in grupo.columns else None
        n_inc_eca2017_1a1 = 0
        if pd.isna(lim_inf_eca2017_1a1) is not True or pd.isna(lim_sup_eca2017_1a1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_1a1 is not None and v < lim_inf_eca2017_1a1) or (lim_sup_eca2017_1a1 is not None and v > lim_sup_eca2017_1a1):
                    n_inc_eca2017_1a1 += 1
            porc_eca2017_1a1 = round(100 * n_inc_eca2017_1a1 / n_total_eca2017_1a1,2)
        else:
            porc_eca2017_1a1 = None
            
    #Categoría ECA 2017 1-A2
    if ECA_2017_CAT_1A2 is True:
        n_total_eca2017_1a2 = len(valores_numericos)
    
        lim_inf_eca2017_1a2 = grupo["lim_inf_eca_2017_1a2"].iloc[0] if "lim_inf_eca_2017_1a2" in grupo.columns else None
        lim_sup_eca2017_1a2 = grupo["lim_sup_eca_2017_1a2"].iloc[0] if "lim_sup_eca_2017_1a2" in grupo.columns else None
        n_inc_eca2017_1a2 = 0
        if pd.isna(lim_inf_eca2017_1a2) is not True or pd.isna(lim_sup_eca2017_1a2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_1a2 is not None and v < lim_inf_eca2017_1a2) or (lim_sup_eca2017_1a2 is not None and v > lim_sup_eca2017_1a2):
                    n_inc_eca2017_1a2 += 1
            porc_eca2017_1a2 = round(100 * n_inc_eca2017_1a2 / n_total_eca2017_1a2,0)
        else:
            porc_eca2017_1a2 = None
            
    #Categoría ECA 2017 1-A3
    if ECA_2017_CAT_1A3 is True:
        n_total_eca2017_1a3 = len(valores_numericos)
    
        lim_inf_eca2017_1a3 = grupo["lim_inf_eca_2017_1a3"].iloc[0] if "lim_inf_eca_2017_1a3" in grupo.columns else None
        lim_sup_eca2017_1a3 = grupo["lim_sup_eca_2017_1a3"].iloc[0] if "lim_sup_eca_2017_1a3" in grupo.columns else None
        n_inc_eca2017_1a3 = 0
        if pd.isna(lim_inf_eca2017_1a3) is not True or pd.isna(lim_sup_eca2017_1a3) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_1a3 is not None and v < lim_inf_eca2017_1a3) or (lim_sup_eca2017_1a3 is not None and v > lim_sup_eca2017_1a3):
                    n_inc_eca2017_1a3 += 1
            porc_eca2017_1a3 = round(100 * n_inc_eca2017_1a3 / n_total_eca2017_1a3,0)
        else:
            porc_eca2017_1a3 = None
            
    #Categoría ECA 2017 1-B1
    if ECA_2017_CAT_1B1 is True:
        n_total_eca2017_1b1 = len(valores_numericos)
    
        lim_inf_eca2017_1b1 = grupo["lim_inf_eca2017_1b1"].iloc[0] if "lim_inf_eca2017_1b1" in grupo.columns else None
        lim_sup_eca2017_1b1 = grupo["lim_sup_eca2017_1b1"].iloc[0] if "lim_sup_eca2017_1b1" in grupo.columns else None
        n_inc_eca2017_1b1 = 0
        if pd.isna(lim_inf_eca2017_1b1) is not True or pd.isna(lim_sup_eca2017_1b1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_1b1 is not None and v < lim_inf_eca2017_1b1) or (lim_sup_eca2017_1b1 is not None and v > lim_sup_eca2017_1b1):
                    n_inc_eca2017_1b1 += 1
            porc_eca2017_1b1 = round(100 * n_inc_eca2017_1b1 / n_total_eca2017_1b1,0)
        else:
            porc_eca2017_1b1 = None
            
    #Categoría ECA 2017 1-B2
    if ECA_2017_CAT_1B2 is True:
        n_total_eca2017_1b2 = len(valores_numericos)
    
        lim_inf_eca2017_1b2 = grupo["lim_inf_eca_2017_1b2"].iloc[0] if "lim_inf_eca_2017_1b2" in grupo.columns else None
        lim_sup_eca2017_1b2 = grupo["lim_sup_eca_2017_1b2"].iloc[0] if "lim_sup_eca_2017_1b2" in grupo.columns else None
        n_inc_eca2017_1b2 = 0
        if pd.isna(lim_inf_eca2017_1b2) is not True or pd.isna(lim_sup_eca2017_1b2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_1b2 is not None and v < lim_inf_eca2017_1b2) or (lim_sup_eca2017_1b2 is not None and v > lim_sup_eca2017_1b2):
                    n_inc_eca2017_1b2 += 1
            porc_eca2017_1b2 = round(100 * n_inc_eca2017_1b2 / n_total_eca2017_1b2,0)
        else:
            porc_eca2017_1b2 = None
            
    #Categoría ECA 2017 2-C1
    if ECA_2017_CAT_2C1 is True:
        n_total_eca2017_2c1 = len(valores_numericos)
    
        lim_inf_eca2017_2c1 = grupo["lim_inf_eca_2017_2c1"].iloc[0] if "lim_inf_eca_2017_2c1" in grupo.columns else None
        lim_sup_eca2017_2c1 = grupo["lim_sup_eca_2017_2c1"].iloc[0] if "lim_sup_eca_2017_2c1" in grupo.columns else None
        n_inc_eca2017_2c1 = 0
        if pd.isna(lim_inf_eca2017_2c1) is not True or pd.isna(lim_sup_eca2017_2c1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_2c1 is not None and v < lim_inf_eca2017_2c1) or (lim_sup_eca2017_2c1 is not None and v > lim_sup_eca2017_2c1):
                    n_inc_eca2017_2c1 += 1
            porc_eca2017_2c1 = round(100 * n_inc_eca2017_2c1 / n_total_eca2017_2c1,0)
            porc_eca2017_2c1 = None
            
    #Categoría ECA 2017 2-C2
    if ECA_2017_CAT_2C2 is True:
        n_total_eca2017_2c2 = len(valores_numericos)
    
        lim_inf_eca2017_2c2 = grupo["lim_inf_eca2017_2c2"].iloc[0] if "lim_inf_eca2017_2c2" in grupo.columns else None
        lim_sup_eca2017_2c2 = grupo["lim_sup_eca2017_2c2"].iloc[0] if "lim_sup_eca2017_2c2" in grupo.columns else None
        n_inc_eca2017_2c2 = 0
        if pd.isna(lim_inf_eca2017_2c2) is not True or pd.isna(lim_sup_eca2017_2c2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_2c2 is not None and v < lim_inf_eca2017_2c2) or (lim_sup_eca2017_2c2 is not None and v > lim_sup_eca2017_2c2):
                    n_inc_eca2017_2c2 += 1
            porc_eca2017_2c2 = round(100 * n_inc_eca2017_2c2 / n_total_eca2017_2c2,0)
        else:
            porc_eca2017_2c2 = None
            
    #Categoría ECA 2017 2-C3
    if ECA_2017_CAT_2C3 is True:
        n_total_eca2017_2c3 = len(valores_numericos)
    
        lim_inf_eca2017_2c3 = grupo["lim_inf_eca_2017_2c3"].iloc[0] if "lim_inf_eca_2017_2c3" in grupo.columns else None
        lim_sup_eca2017_2c3 = grupo["lim_sup_eca_2017_2c3"].iloc[0] if "lim_sup_eca_2017_2c3" in grupo.columns else None
        n_inc_eca2017_2c3 = 0
        if pd.isna(lim_inf_eca2017_2c3) is not True or pd.isna(lim_sup_eca2017_2c3) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_2c3 is not None and v < lim_inf_eca2017_2c3) or (lim_sup_eca2017_2c3 is not None and v > lim_sup_eca2017_2c3):
                    n_inc_eca2017_2c3 += 1
            porc_eca2017_2c3 = round(100 * n_inc_eca2017_2c3 / n_total_eca2017_2c3,0)
        else:
            porc_eca2017_2c3 = None
            
    #Categoría ECA 2017 2-C4
    if ECA_2017_CAT_2C4 is True:
        n_total_eca2017_2c4 = len(valores_numericos)
    
        lim_inf_eca2017_2c4 = grupo["lim_inf_eca_2017_2c4"].iloc[0] if "lim_inf_eca_2017_2c4" in grupo.columns else None
        lim_sup_eca2017_2c4 = grupo["lim_sup_eca_2017_2c4"].iloc[0] if "lim_sup_eca_2017_2c4" in grupo.columns else None
        n_inc_eca2017_2c4 = 0
        if pd.isna(lim_inf_eca2017_2c4) is not True or pd.isna(lim_sup_eca2017_2c4) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_2c4 is not None and v < lim_inf_eca2017_2c4) or (lim_sup_eca2017_2c4 is not None and v > lim_sup_eca2017_2c4):
                    n_inc_eca2017_2c4 += 1
            porc_eca2017_2c4 = round(100 * n_inc_eca2017_2c4 / n_total_eca2017_2c4,0)
        else:
            porc_eca2017_2c4 = None
            
    #Categoría ECA 2017 3-D1
    if ECA_2017_CAT_3D1 is True and ECA_2017_CAT_3D2 is False:
        n_total_eca2017_3d1 = len(valores_numericos)
    
        lim_inf_eca2017_3d1 = grupo["lim_inf_eca_2017_3d1"].iloc[0] if "lim_inf_eca_2017_3d1" in grupo.columns else None
        lim_sup_eca2017_3d1 = grupo["lim_sup_eca_2017_3d1"].iloc[0] if "lim_sup_eca_2017_3d1" in grupo.columns else None
        n_inc_eca2017_3d1 = 0
        if pd.isna(lim_inf_eca2017_3d1) is not True or pd.isna(lim_sup_eca2017_3d1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_3d1 is not None and v < lim_inf_eca2017_3d1) or (lim_sup_eca2017_3d1 is not None and v > lim_sup_eca2017_3d1):
                    n_inc_eca2017_3d1 += 1
            porc_eca2017_3d1 = round(100 * n_inc_eca2017_3d1 / n_total_eca2017_3d1,2)
        else:
            porc_eca2017_3d1 = None
            
    #Categoría ECA 2017 3-D2
    if ECA_2017_CAT_3D2 is True and ECA_2017_CAT_3D1 is False:
        n_total_eca2017_3d2 = len(valores_numericos)
    
        lim_inf_eca2017_3d2 = grupo["lim_inf_eca_2017_3d2"].iloc[0] if "lim_inf_eca_2017_3d2" in grupo.columns else None
        lim_sup_eca2017_3d2 = grupo["lim_sup_eca_2017_3d2"].iloc[0] if "lim_sup_eca_2017_3d2" in grupo.columns else None
        n_inc_eca2017_3d2 = 0
        if pd.isna(lim_inf_eca2017_3d2) is not True or pd.isna(lim_sup_eca2017_3d2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_3d2 is not None and v < lim_inf_eca2017_3d2) or (lim_sup_eca2017_3d2 is not None and v > lim_sup_eca2017_3d2):
                    n_inc_eca2017_3d2 += 1
            porc_eca2017_3d2 = round(100 * n_inc_eca2017_3d2 / n_total_eca2017_3d2,2)
        else:
            porc_eca2017_3d2 = None
    
    #Categoría ECA 2017 3-D1 y 3-D2
    if ECA_2017_CAT_3D1 is True and ECA_2017_CAT_3D2 is True:
        n_total = len(valores_numericos)
    
        # Categoría 3 – D1
        lim_inf_eca2017_3d1 = grupo["lim_inf_eca_2017_3d1"].iloc[0] if "lim_inf_eca_2017_3d1" in grupo.columns else None
        lim_sup_eca2017_3d1 = grupo["lim_sup_eca_2017_3d1"].iloc[0] if "lim_sup_eca_2017_3d1" in grupo.columns else None
        n_inc_eca2017_3d1 = 0
        if pd.isna(lim_inf_eca2017_3d1) is not True or pd.isna(lim_sup_eca2017_3d1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_3d1 is not None and v < lim_inf_eca2017_3d1) or (lim_sup_eca2017_3d1 is not None and v > lim_sup_eca2017_3d1):
                    n_inc_eca2017_3d1 += 1
            porc_eca2017_3d1 = round(100 * n_inc_eca2017_3d1 / n_total,2)
        else:
            porc_eca2017_3d1 = None
    
        # Categoría 3 – D2
        lim_inf_eca2017_3d2 = grupo["lim_inf_eca_2017_3d2"].iloc[0] if "lim_inf_eca_2017_3d2" in grupo.columns else None
        lim_sup_eca2017_3d2 = grupo["lim_sup_eca_2017_3d2"].iloc[0] if "lim_sup_eca_2017_3d2" in grupo.columns else None
        n_inc_eca2017_3d2 = 0
        if pd.isna(lim_inf_eca2017_3d2) is not True or pd.isna(lim_sup_eca2017_3d2) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_3d2 is not None and v < lim_inf_eca2017_3d2) or (lim_sup_eca2017_3d2 is not None and v > lim_sup_eca2017_3d2):
                    n_inc_eca2017_3d2 += 1
            porc_eca2017_3d2 = round(100 * n_inc_eca2017_3d2 / n_total,2)
        else:
            porc_eca2017_3d2 = None
            
    #Categoría ECA 2017 4E-1
    if ECA_2017_CAT_4E1 is True:
        n_total_eca2017_4e1 = len(valores_numericos)
    
        lim_inf_eca2017_4e1 = grupo["lim_inf_eca_2017_4e1"].iloc[0] if "lim_inf_eca_2017_4e1" in grupo.columns else None
        lim_sup_eca2017_4e1 = grupo["lim_sup_eca_2017_4e1"].iloc[0] if "lim_sup_eca_2017_4e1" in grupo.columns else None
        n_inc_eca2017_4e1 = 0
        if pd.isna(lim_inf_eca2017_4e1) is not True or pd.isna(lim_sup_eca2017_4e1) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_4e1 is not None and v < lim_inf_eca2017_4e1) or (lim_sup_eca2017_4e1 is not None and v > lim_sup_eca2017_4e1):
                    n_inc_eca2017_4e1 += 1
            porc_eca2017_4e1 = round(100 * n_inc_eca2017_4e1 / n_total_eca2017_4e1,0)
        else:
            porc_eca2017_4e1 = None
            
    #Categoría ECA 2017 4E-2 CYS
    if ECA_2017_CAT_4E2_CYS is True:
        n_total_eca2017_4e2_cys = len(valores_numericos)
    
        lim_inf_eca2017_4e2_cys = grupo["lim_inf_eca_2017_4e2_cys"].iloc[0] if "lim_inf_eca_2017_4e2_cys" in grupo.columns else None
        lim_sup_eca2017_4e2_cys = grupo["lim_sup_eca_2017_4e2_cys"].iloc[0] if "lim_sup_eca_2017_4e2_cys" in grupo.columns else None
        n_inc_eca2017_4e2_cys = 0
        if pd.isna(lim_inf_eca2017_4e2_cys) is not True or pd.isna(lim_sup_eca2017_4e2_cys) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_4e2_cys is not None and v < lim_inf_eca2017_4e2_cys) or (lim_sup_eca2017_4e2_cys is not None and v > lim_sup_eca2017_4e2_cys):
                    n_inc_eca2017_4e2_cys += 1
            porc_eca2017_4e2_cys = round(100 * n_inc_eca2017_4e2_cys / n_total_eca2017_4e2_cys,0)
        else:
            porc_eca2017_4e2_cys = None
            
    #Categoría ECA 2017 4E-2 S
    if ECA_2017_CAT_4E2_S is True:
        n_total_eca2017_4e2_s = len(valores_numericos)
    
        lim_inf_eca2017_4e2_s = grupo["lim_inf_eca_2017_4e2_s"].iloc[0] if "lim_inf_eca_2017_4e2_s" in grupo.columns else None
        lim_sup_eca2017_4e2_s = grupo["lim_sup_eca_2017_4e2_s"].iloc[0] if "lim_sup_eca_2017_4e2_s" in grupo.columns else None
        n_inc_eca2017_4e2_s = 0
        if pd.isna(lim_inf_eca2017_4e2_s) is not True or pd.isna(lim_sup_eca2017_4e2_s) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_4e2_s is not None and v < lim_inf_eca2017_4e2_s) or (lim_sup_eca2017_4e2_s is not None and v > lim_sup_eca2017_4e2_s):
                    n_inc_eca2017_4e2_s += 1
            porc_eca2017_4e2_s = round(100 * n_inc_eca2017_4e2_s / n_total_eca2017_4e2_s,0)
        else:
            porc_eca2017_4e2_s = None
            
    #Categoría ECA 2017 4E-3 E
    if ECA_2017_CAT_4E3_E is True:
        n_total_eca2017_4e3_e = len(valores_numericos)
    
        lim_inf_eca2017_4e3_e = grupo["lim_inf_eca_2017_4e3_e"].iloc[0] if "lim_inf_eca_2017_4e3_e" in grupo.columns else None
        lim_sup_eca2017_4e3_e = grupo["lim_sup_eca_2017_4e3_e"].iloc[0] if "lim_sup_eca_2017_4e3_e" in grupo.columns else None
        n_inc_eca2017_4e3_e = 0
        if pd.isna(lim_inf_eca2017_4e3_e) is not True or pd.isna(lim_sup_eca2017_4e3_e) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_4e3_e is not None and v < lim_inf_eca2017_4e3_e) or (lim_sup_eca2017_4e3_e is not None and v > lim_sup_eca2017_4e3_e):
                    n_inc_eca2017_4e3_e += 1
            porc_eca2017_4e3_e = round(100 * n_inc_eca2017_4e3_e / n_total_eca2017_4e3_e,0)
        else:
            porc_eca2017_4e3_e = None
            
    #Categoría ECA 2017 4E-3 M
    if ECA_2017_CAT_4E3_M is True:
        n_total_eca2017_4e3_m = len(valores_numericos)
    
        lim_inf_eca2017_4e3_m = grupo["lim_inf_eca_2017_4e3_m"].iloc[0] if "lim_inf_eca_2017_4e3_m" in grupo.columns else None
        lim_sup_eca2017_4e3_m = grupo["lim_sup_eca_2017_4e3_m"].iloc[0] if "lim_sup_eca_2017_4e3_m" in grupo.columns else None
        n_inc_eca2017_4e3_m = 0
        if pd.isna(lim_inf_eca2017_4e3_m) is not True or pd.isna(lim_sup_eca2017_4e3_m) is not True:
            for v in valores_numericos:
                if (lim_inf_eca2017_4e3_m is not None and v < lim_inf_eca2017_4e3_m) or (lim_sup_eca2017_4e3_m is not None and v > lim_sup_eca2017_4e3_m):
                    n_inc_eca2017_4e3_m += 1
            porc_eca2017_4e3_m = round(100 * n_inc_eca2017_4e3_m / n_total_eca2017_4e3_m,0)
        else:
            porc_eca2017_4e3_m = None
        
    #################### Comparación con LGA ####################
    # Categoría I
    if LGA_I is True:
        n_total_lga_i = len(valores_numericos)
    
        # Categoría I
        lim_inf_lga_i = grupo["lim_inf_lga_I"].iloc[0] if "lim_inf_lga_I" in grupo.columns else None
        lim_sup_lga_i = grupo["lim_sup_lga_I"].iloc[0] if "lim_sup_lga_I" in grupo.columns else None
        n_inc_lga_i = 0
        if pd.isna(lim_inf_lga_i) is not True or pd.isna(lim_sup_lga_i) is not True:
            for v in valores_numericos:
                if (lim_inf_lga_i is not None and v < lim_inf_lga_i) or (lim_sup_lga_i is not None and v > lim_sup_lga_i):
                    n_inc_lga_i += 1
            porc_lga_i = round(100 * n_inc_lga_i / n_total_lga_i,0)
        else:
            porc_lga_i = None
            
    # Categoría II
    if LGA_II is True:
        n_total_lga_ii = len(valores_numericos)
            
        lim_inf_lga_ii = grupo["lim_inf_lga_II"].iloc[0] if "lim_inf_lga_II" in grupo.columns else None
        lim_sup_lga_ii = grupo["lim_sup_lga_II"].iloc[0] if "lim_sup_lga_II" in grupo.columns else None
        n_inc_lga_ii = 0
        if pd.isna(lim_inf_lga_ii) is not True or pd.isna(lim_sup_lga_ii) is not True:
            for v in valores_numericos:
                if (lim_inf_lga_ii is not None and v < lim_inf_lga_ii) or (lim_sup_lga_ii is not None and v > lim_sup_lga_ii):
                    n_inc_lga_ii += 1
            porc_lga_ii = round(100 * n_inc_lga_ii / n_total_lga_ii,0)
        else:
            porc_lga_ii = None
            
    # Categoría III
    if LGA_III is True:
        n_total_lga_iii = len(valores_numericos)
            
        lim_inf_lga_iii = grupo["lim_inf_lga_III"].iloc[0] if "lim_inf_lga_III" in grupo.columns else None
        lim_sup_lga_iii = grupo["lim_sup_lga_III"].iloc[0] if "lim_sup_lga_III" in grupo.columns else None
        n_inc_lga_iii = 0
        if pd.isna(lim_inf_lga_iii) is not True or pd.isna(lim_sup_lga_iii) is not True:
            for v in valores_numericos:
                if (lim_inf_lga_iii is not None and v < lim_inf_lga_iii) or (lim_sup_lga_iii is not None and v > lim_sup_lga_iii):
                    n_inc_lga_iii += 1
            porc_lga_iii = round(100 * n_inc_lga_iii / n_total_lga_iii,0)
        else:
            porc_lga_iii = None
            
    # Categoría IV
    if LGA_IV is True:
        n_total_lga_iv = len(valores_numericos)  
        
        lim_inf_lga_iv = grupo["lim_inf_lga_IV"].iloc[0] if "lim_inf_lga_IV" in grupo.columns else None
        lim_sup_lga_iv = grupo["lim_sup_lga_IV"].iloc[0] if "lim_sup_lga_IV" in grupo.columns else None
        n_inc_lga_iv = 0
        if pd.isna(lim_inf_lga_iv) is not True or pd.isna(lim_sup_lga_iv) is not True:
            for v in valores_numericos:
                if (lim_inf_lga_iv is not None and v < lim_inf_lga_iv) or (lim_sup_lga_iv is not None and v > lim_sup_lga_iv):
                    n_inc_lga_iv += 1
            porc_lga_iv = round(100 * n_inc_lga_iv / n_total_lga_iv,0)
        else:
            porc_lga_iv = None
            
    # Categoría V
    if LGA_V is True:
        n_total_lga_v = len(valores_numericos)  
        
        lim_inf_lga_v = grupo["lim_inf_lga_V"].iloc[0] if "lim_inf_lga_V" in grupo.columns else None
        lim_sup_lga_v = grupo["lim_sup_lga_V"].iloc[0] if "lim_sup_lga_V" in grupo.columns else None
        n_inc_lga_v = 0
        if pd.isna(lim_inf_lga_v) is not True or pd.isna(lim_sup_lga_v) is not True:
            for v in valores_numericos:
                if (lim_inf_lga_v is not None and v < lim_inf_lga_v) or (lim_sup_lga_v is not None and v > lim_sup_lga_v):
                    n_inc_lga_v += 1
            porc_lga_v = round(100 * n_inc_lga_v / n_total_lga_v,0)
        else:
            porc_lga_v = None
            
    # Categoría VI
    if LGA_VI is True:
        n_total_lga_vi = len(valores_numericos)  
        
        lim_inf_lga_vi = grupo["lim_inf_lga_VI"].iloc[0] if "lim_inf_lga_VI" in grupo.columns else None
        lim_sup_lga_vi = grupo["lim_sup_lga_VI"].iloc[0] if "lim_sup_lga_VI" in grupo.columns else None
        n_inc_lga_vi = 0
        if pd.isna(lim_inf_lga_vi) is not True or pd.isna(lim_sup_lga_vi) is not True:
            for v in valores_numericos:
                if (lim_inf_lga_vi is not None and v < lim_inf_lga_vi) or (lim_sup_lga_vi is not None and v > lim_sup_lga_vi):
                    n_inc_lga_vi += 1
            porc_lga_vi = round(100 * n_inc_lga_vi / n_total_lga_vi,0)
        else:
            porc_lga_vi = None
    
        
    # ---- Texto final según casos ----
    ################## ECA 2017 CAT 1 A1 ##################
    if ECA_2017_CAT_1A1 is True:
        if pd.notna(lim_inf_eca2017_1a1) and pd.notna(lim_sup_eca2017_1a1):
            eca_formateado_1 = str(lim_inf_eca2017_1a1).replace(".", ",") + ' a '+ str(lim_sup_eca2017_1a1).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_1a1) and pd.notna(lim_sup_eca2017_1a1):
            eca_formateado_1 = str(lim_sup_eca2017_1a1).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_1a1) and pd.isna(lim_sup_eca2017_1a1):
            eca_formateado_1 = str(lim_inf_eca2017_1a1).replace(".", ",")
        
        if porc_eca2017_1a1 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 1 - A1 (aguas que pueden ser potabilizadas con desinfección) aplicable para este parámetro.")
        else:
            if porc_eca2017_1a1 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - A1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_1a1 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - A1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_1a1 = []                
                #if porc_eca2017_1a1 not in (None, 0, 100):
                parte1_eca2017_1a1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - A1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_1a1} ({str(porc_eca2017_1a1).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_1a1[0]}")
                    
    ################## ECA 2017 CAT 1 A2 ##################
    if ECA_2017_CAT_1A2 is True:
        if pd.notna(lim_inf_eca2017_1a2) and pd.notna(lim_sup_eca2017_1a2):
            eca_formateado_1 = str(lim_inf_eca2017_1a2).replace(".", ",") + ' a '+ str(lim_sup_eca2017_1a2).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_1a2) and pd.notna(lim_sup_eca2017_1a2):
            eca_formateado_1 = str(lim_sup_eca2017_1a2).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_1a2) and pd.isna(lim_sup_eca2017_1a2):
            eca_formateado_1 = str(lim_inf_eca2017_1a2).replace(".", ",")
            
        if porc_eca2017_1a2 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 1 - A2 (aguas que pueden ser potabilizadas con tratamiento convencional) aplicable para este parámetro.")
        else:
            if porc_eca2017_1a2 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - A2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_1a2 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - A2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_1a2 = []                
                #if porc_eca2017_1a2 not in (None, 0, 100):
                parte1_eca2017_1a2.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - A2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_1a2} ({str(porc_eca2017_1a2).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_1a2[0]}")
                    
    ################## ECA 2017 CAT 1 A3 ##################
    if ECA_2017_CAT_1A3 is True:
        if pd.notna(lim_inf_eca2017_1a3) and pd.notna(lim_sup_eca2017_1a3):
            eca_formateado_1 = str(lim_inf_eca2017_1a3).replace(".", ",") + ' a '+ str(lim_sup_eca2017_1a3).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_1a3) and pd.notna(lim_sup_eca2017_1a3):
            eca_formateado_1 = str(lim_sup_eca2017_1a3).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_1a3) and pd.isna(lim_sup_eca2017_1a3):
            eca_formateado_1 = str(lim_inf_eca2017_1a3).replace(".", ",")
            
        if porc_eca2017_1a3 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 1 - A3 (aguas que pueden ser potabilizadas con tratamiento avanzado) aplicable para este parámetro.")
        else:
            if porc_eca2017_1a3 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - A3 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_1a3 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - A3 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_1a3 = []                
                #if porc_eca2017_1a3 not in (None, 0, 100):
                parte1_eca2017_1a3.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - A3 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_1a3} ({str(porc_eca2017_1a3).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_1a3[0]}")
                    
    ################## ECA 2017 CAT 1 B1 ##################
    if ECA_2017_CAT_1B1 is True:
        if pd.notna(lim_inf_eca2017_1b1) and pd.notna(lim_sup_eca2017_1b1):
            eca_formateado_1 = str(lim_inf_eca2017_1b1).replace(".", ",") + ' a '+ str(lim_sup_eca2017_1b1).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_1b1) and pd.notna(lim_sup_eca2017_1b1):
            eca_formateado_1 = str(lim_sup_eca2017_1b1).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_1b1) and pd.isna(lim_sup_eca2017_1b1):
            eca_formateado_1 = str(lim_inf_eca2017_1b1).replace(".", ",")
            
        if porc_eca2017_1b1 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 1 - B1 (aguas superficiales destinadas para recreación de contacto primario) aplicable para este parámetro.")
        else:
            if porc_eca2017_1b1 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - B1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_1b1 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - B1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_1b1 = []                
                #if porc_eca2017_1b1 not in (None, 0, 100):
                parte1_eca2017_1b1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - B1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_1b1} ({str(porc_eca2017_1b1).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_1b1[0]}")
                    
    ################## ECA 2017 CAT 1 B2 ##################
    if ECA_2017_CAT_1B2 is True:
        if pd.notna(lim_inf_eca2017_1b2) and pd.notna(lim_sup_eca2017_1b2):
            eca_formateado_1 = str(lim_inf_eca2017_1b2).replace(".", ",") + ' a '+ str(lim_sup_eca2017_1b2).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_1b2) and pd.notna(lim_sup_eca2017_1b2):
            eca_formateado_1 = str(lim_sup_eca2017_1b2).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_1b2) and pd.isna(lim_sup_eca2017_1b2):
            eca_formateado_1 = str(lim_inf_eca2017_1b2).replace(".", ",")
            
        if porc_eca2017_1b2 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 1 - B2 (aguas superficiales destinadas para recreación de contacto secundario) aplicable para este parámetro.")
        else:
            if porc_eca2017_1b2 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - B2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_1b2 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - B2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_1b2 = []                
                #if porc_eca2017_1b2 not in (None, 0, 100):
                parte1_eca2017_1b2.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 1 - B2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_1b2} ({str(porc_eca2017_1b2).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_1b2[0]}")
    
    ################## ECA 2017 CAT 2 C1 ##################
    if ECA_2017_CAT_2C1 is True:
        if pd.notna(lim_inf_eca2017_2c1) and pd.notna(lim_sup_eca2017_2c1):
            eca_formateado_1 = str(lim_inf_eca2017_2c1).replace(".", ",") + ' a '+ str(lim_sup_eca2017_2c1).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_2c1) and pd.notna(lim_sup_eca2017_2c1):
            eca_formateado_1 = str(lim_sup_eca2017_2c1).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_2c1) and pd.isna(lim_sup_eca2017_2c1):
            eca_formateado_1 = str(lim_inf_eca2017_2c1).replace(".", ",")
            
        if porc_eca2017_2c1 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 2 - C1 (extracción y cultivo de moluscos, equinodermos y tunicados en aguas marino costeras) aplicable para este parámetro.")
        else:
            if porc_eca2017_2c1 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_2c1 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_2c1 = []                
               # if porc_eca2017_2c1 not in (None, 0, 100):
                parte1_eca2017_2c1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_2c1} ({str(porc_eca2017_2c1).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_2c1[0]}")
                    
    ################## ECA 2017 CAT 2 C2 ##################
    if ECA_2017_CAT_2C2 is True:
        if pd.notna(lim_inf_eca2017_2c2) and pd.notna(lim_sup_eca2017_2c2):
            eca_formateado_1 = str(lim_inf_eca2017_2c2).replace(".", ",") + ' a '+ str(lim_sup_eca2017_2c2).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_2c2) and pd.notna(lim_sup_eca2017_2c2):
            eca_formateado_1 = str(lim_sup_eca2017_2c2).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_2c2) and pd.isna(lim_sup_eca2017_2c2):
            eca_formateado_1 = str(lim_inf_eca2017_2c2).replace(".", ",")
            
        if porc_eca2017_2c2 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 2 - C2 (extracción y cultivo de otras especies hidrobiológicas en aguas marino costeras) aplicable para este parámetro.")
        else:
            if porc_eca2017_2c2 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_2c2 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_2c2 = []                
                #if porc_eca2017_2c2 not in (None, 0, 100):
                parte1_eca2017_2c2.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_2c2} ({str(porc_eca2017_2c2).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_2c2[0]}")
                    
    ################## ECA 2017 CAT 2 C3 ##################
    if ECA_2017_CAT_2C3 is True:
        if pd.notna(lim_inf_eca2017_2c3) and pd.notna(lim_sup_eca2017_2c3):
            eca_formateado_1 = str(lim_inf_eca2017_2c3).replace(".", ",") + ' a '+ str(lim_sup_eca2017_2c3).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_2c3) and pd.notna(lim_sup_eca2017_2c3):
            eca_formateado_1 = str(lim_sup_eca2017_2c3).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_2c3) and pd.isna(lim_sup_eca2017_2c3):
            eca_formateado_1 = str(lim_inf_eca2017_2c3).replace(".", ",")
            
        if porc_eca2017_2c3 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 2 - C3 (actividades marino portuarias, industriales o de saneamiento en aguas marino costeras) aplicable para este parámetro.")
        else:
            if porc_eca2017_2c3 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C3 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_2c3 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C3 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_2c3 = []                
                #if porc_eca2017_2c3 not in (None, 0, 100):
                parte1_eca2017_2c3.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C3 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_2c3} ({str(porc_eca2017_2c3).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_2c3[0]}")
                    
    ################## ECA 2017 CAT 2 C4 ##################
    if ECA_2017_CAT_2C4 is True:
        if pd.notna(lim_inf_eca2017_2c4) and pd.notna(lim_sup_eca2017_2c4):
            eca_formateado_1 = str(lim_inf_eca2017_2c4).replace(".", ",") + ' a '+ str(lim_sup_eca2017_2c4).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_2c4) and pd.notna(lim_sup_eca2017_2c4):
            eca_formateado_1 = str(lim_sup_eca2017_2c4).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_2c4) and pd.isna(lim_sup_eca2017_2c4):
            eca_formateado_1 = str(lim_inf_eca2017_2c4).replace(".", ",")
            
        if porc_eca2017_2c4 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 2 - C4 (extracción y cultivo de especies hidrobiológicas en lagos y lagunas) aplicable para este parámetro.")
        else:
            if porc_eca2017_2c4 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C4 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_2c4 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C4 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_2c4 = []                
                #if porc_eca2017_2c4 not in (None, 0, 100):
                parte1_eca2017_2c4.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 2 - C4 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_2c4} ({str(porc_eca2017_2c4).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_2c4[0]}")

    ################## ECA 2017 CAT 3 D1 ##################
    if ECA_2017_CAT_3D1 is True and ECA_2017_CAT_3D2 is False:
        if pd.notna(lim_inf_eca2017_3d1) and pd.notna(lim_sup_eca2017_3d1):
            eca_formateado_1 = str(lim_inf_eca2017_3d1).replace(".", ",") + ' a '+ str(lim_sup_eca2017_3d1).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_3d1) and pd.notna(lim_sup_eca2017_3d1):
            eca_formateado_1 = str(lim_sup_eca2017_3d1).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_3d1) and pd.isna(lim_sup_eca2017_3d1):
            eca_formateado_1 = str(lim_inf_eca2017_3d1).replace(".", ",")
            
        if porc_eca2017_3d1 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 - D1 (riego de vegetales) aplicable para este parámetro.")
        else:
            if porc_eca2017_3d1 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 - D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_3d1 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 - D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_3d1 = []                
                #if porc_eca2017_3d1 not in (None, 0, 100):
                parte1_eca2017_3d1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 - D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_3d1} ({str(porc_eca2017_3d1).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_3d1[0]}")
                    
    ################## ECA 2017 CAT 3 D2 ##################
    if ECA_2017_CAT_3D1 is False and ECA_2017_CAT_3D2 is True:
        if pd.notna(lim_inf_eca2017_3d2) and pd.notna(lim_sup_eca2017_3d2):
            eca_formateado_1 = str(lim_inf_eca2017_3d2).replace(".", ",") + ' a '+ str(lim_sup_eca2017_3d2).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_3d2) and pd.notna(lim_sup_eca2017_3d2):
            eca_formateado_1 = str(lim_sup_eca2017_3d2).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_3d2) and pd.isna(lim_sup_eca2017_3d2):
            eca_formateado_1 = str(lim_inf_eca2017_3d2).replace(".", ",")
            
        if porc_eca2017_3d2 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
        else:
            if porc_eca2017_3d2 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 - D2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_3d2 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 - D2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_3d2 = []                
                #if porc_eca2017_3d2 not in (None, 0, 100):
                parte1_eca2017_3d2.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 - D2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_3d2} ({str(porc_eca2017_3d2).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_3d2[0]}")
    
    ################## ECA 2017 CAT 3 D1 y D2##################
    if ECA_2017_CAT_3D1 is True and ECA_2017_CAT_3D2 is True:
        if pd.notna(lim_inf_eca2017_3d1) and pd.notna(lim_sup_eca2017_3d1):
            eca_formateado_1 = str(lim_inf_eca2017_3d1).replace(".", ",") + ' a '+ str(lim_sup_eca2017_3d1).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_3d1) and pd.notna(lim_sup_eca2017_3d1):
            eca_formateado_1 = str(lim_sup_eca2017_3d1).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_3d1) and pd.isna(lim_sup_eca2017_3d1):
            eca_formateado_1 = str(lim_inf_eca2017_3d1).replace(".", ",")
            
        if pd.notna(lim_inf_eca2017_3d2) and pd.notna(lim_sup_eca2017_3d2):
            eca_formateado_2 = str(lim_inf_eca2017_3d2).replace(".", ",") + ' a '+ str(lim_sup_eca2017_3d2).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_3d2) and pd.notna(lim_sup_eca2017_3d2):
            eca_formateado_2 = str(lim_sup_eca2017_3d2).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_3d2) and pd.isna(lim_sup_eca2017_3d2):
            eca_formateado_2 = str(lim_inf_eca2017_3d2).replace(".", ",")
            
        if porc_eca2017_3d1 is None and porc_eca2017_3d2 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 – D1 (riego de vegetales) y 3 - D2 (bebida de animales) aplicable para este parámetro.")
        else:
            if porc_eca2017_3d1 == 0 and porc_eca2017_3d2 == 0:
                texto.append(f' Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}) y 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2017.')
            elif porc_eca2017_3d1 == 100 and porc_eca2017_3d2 == 100:                
                texto.append(f' Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}) y 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.')
            elif porc_eca2017_3d1 == 0 and porc_eca2017_3d2 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017; y comparando con el ECA 2017 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")
            elif porc_eca2017_3d1 == 100 and porc_eca2017_3d2 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017; y comparando con el ECA 2017 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_3d1 == None and porc_eca2017_3d2 == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2017. Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 – D1 (riego de vegetales) aplicable para este parámetro.")
            elif porc_eca2017_3d1 == None and porc_eca2017_3d2 == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2017. Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 – D1 (riego de vegetales) aplicable para este parámetro.")
            elif porc_eca2017_3d1 == 0 and porc_eca2017_3d2 == None:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017. Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
            elif porc_eca2017_3d1 == 100 and porc_eca2017_3d2 == None:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017. Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
            else:
                parte1 = []
                parte2 = []
                if porc_eca2017_3d1 not in (None, 0, 100) and porc_eca2017_3d2 is None:
                    parte1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_3d1} ({str(porc_eca2017_3d1).replace('.', ',')} %) de los registros no cumplen con el valor establecido. Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
                    texto.append(f" {parte1[0]}")
                if porc_eca2017_3d1 is None and porc_eca2017_3d2 not in (None, 0, 100):
                    parte2.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2017_3d2} ({str(porc_eca2017_3d2).replace('.', ',')} %) de los registros no cumplen con el valor establecido. Cabe mencionar que no existe un ECA 2017 para agua para la categoría 3 – D1 (riego de vegetales) aplicable para este parámetro.")    
                    texto.append(f" {parte2[0]}")
                if porc_eca2017_3d1 not in (None, 0, 100) and porc_eca2017_3d2 not in (None, 0, 100):
                    parte1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_3d1} ({str(porc_eca2017_3d1).replace('.', ',')} %) de los registros no cumplen con el valor establecido; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2017_3d2} ({str(porc_eca2017_3d2).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2017_3d1 == 0 and porc_eca2017_3d2 not in (None, 0, 100):
                    parte1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2017_3d2} ({str(porc_eca2017_3d2).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2017_3d1 not in (None, 0, 100) and porc_eca2017_3d2 == 0:
                    parte1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_3d1} ({str(porc_eca2017_3d1).replace('.', ',')} %) de los registros no cumplen con el valor establecido; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2017_3d1 == 100 and porc_eca2017_3d2 not in (None, 0, 100):
                    parte1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2017_3d2} ({str(porc_eca2017_3d2).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2017_3d1 not in (None, 0, 100) and porc_eca2017_3d2 == 100:
                    parte1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_3d1} ({str(porc_eca2017_3d1).replace('.', ',')} %) de los registros no cumplen con el valor establecido; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                    
    ################## ECA 2017 CAT 4 E1 ##################
    if ECA_2017_CAT_4E1 is True:
        if pd.notna(lim_inf_eca2017_4e1) and pd.notna(lim_sup_eca2017_4e1):
            eca_formateado_1 = str(lim_inf_eca2017_4e1).replace(".", ",") + ' a '+ str(lim_sup_eca2017_4e1).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_4e1) and pd.notna(lim_sup_eca2017_4e1):
            eca_formateado_1 = str(lim_sup_eca2017_4e1).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_4e1) and pd.isna(lim_sup_eca2017_4e1):
            eca_formateado_1 = str(lim_inf_eca2017_4e1).replace(".", ",")
            
        if porc_eca2017_4e1 is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 4 - E1 (conservación del ambiente acuático para lagunas y lagos) aplicable para este parámetro.")
        else:
            if porc_eca2017_4e1 == 0:
                texto.append(f' Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.')
            elif porc_eca2017_4e1 == 100:
                texto.append(f' Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.')          
            else:
                parte1_eca2017_4e1 = []                
                #if porc_eca2017_4e1 not in (None, 0, 100):
                parte1_eca2017_4e1.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_4e1} ({str(porc_eca2017_4e1).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_4e1[0]}")
                    
    ################## ECA 2017 CAT 4 E2 CYS ##################
    if ECA_2017_CAT_4E2_CYS is True:
        if pd.notna(lim_inf_eca2017_4e2_cys) and pd.notna(lim_sup_eca2017_4e2_cys):
            eca_formateado_1 = str(lim_inf_eca2017_4e2_cys).replace(".", ",") + ' a '+ str(lim_sup_eca2017_4e2_cys).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_4e2_cys) and pd.notna(lim_sup_eca2017_4e2_cys):
            eca_formateado_1 = str(lim_sup_eca2017_4e2_cys).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_4e2_cys) and pd.isna(lim_sup_eca2017_4e2_cys):
            eca_formateado_1 = str(lim_inf_eca2017_4e2_cys).replace(".", ",")
            
        if porc_eca2017_4e2_cys is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 4 - E2 costa y sierra (conservación del ambiente acuático para ríos) aplicable para este parámetro.")
        else:
            if porc_eca2017_4e2_cys == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E2 costa y sierra ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_4e2_cys == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E2 costa y sierra ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_4e2_cys = []                
                #if porc_eca2017_4e2_cys not in (None, 0, 100):
                parte1_eca2017_4e2_cys.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E2 costa y sierra ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_4e2_cys} ({str(porc_eca2017_4e2_cys).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_4e2_cys[0]}")
                    
    ################## ECA 2017 CAT 4 E2 S ##################
    if ECA_2017_CAT_4E2_S is True:
        if pd.notna(lim_inf_eca2017_4e2_s) and pd.notna(lim_sup_eca2017_4e2_s):
            eca_formateado_1 = str(lim_inf_eca2017_4e2_s).replace(".", ",") + ' a '+ str(lim_sup_eca2017_4e2_s).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_4e2_s) and pd.notna(lim_sup_eca2017_4e2_s):
            eca_formateado_1 = str(lim_sup_eca2017_4e2_s).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_4e2_s) and pd.isna(lim_sup_eca2017_4e2_s):
            eca_formateado_1 = str(lim_inf_eca2017_4e2_s).replace(".", ",")
            
        if porc_eca2017_4e2_s is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 4 - E2 selva (conservación del ambiente acuático para ríos) aplicable para este parámetro.")
        else:
            if porc_eca2017_4e2_s == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E2 selva ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_4e2_s == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E2 selva ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_4e2_s = []                
                #if porc_eca2017_4e2_s not in (None, 0, 100):
                parte1_eca2017_4e2_s.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E2 selva ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_4e2_s} ({str(porc_eca2017_4e2_s).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_4e2_s[0]}")
                    
    ################## ECA 2017 CAT 4 E3 E ##################
    if ECA_2017_CAT_4E3_E is True:
        if pd.notna(lim_inf_eca2017_4e3_e) and pd.notna(lim_sup_eca2017_4e3_e):
            eca_formateado_1 = str(lim_inf_eca2017_4e3_e).replace(".", ",") + ' a '+ str(lim_sup_eca2017_4e3_e).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_4e3_e) and pd.notna(lim_sup_eca2017_4e3_e):
            eca_formateado_1 = str(lim_sup_eca2017_4e3_e).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_4e3_e) and pd.isna(lim_sup_eca2017_4e3_e):
            eca_formateado_1 = str(lim_inf_eca2017_4e3_e).replace(".", ",")
            
        if porc_eca2017_4e3_e is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 4 - E3 estuarios (conservación del ambiente acuático para ecosistemas costeros y marinos) aplicable para este parámetro.")
        else:
            if porc_eca2017_4e3_e == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E3 estuarios ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_4e3_e == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E3 estuarios ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_4e3_e = []                
                #if porc_eca2017_4e3_e not in (None, 0, 100):
                parte1_eca2017_4e3_e.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E3 estuarios ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_4e3_e} ({str(porc_eca2017_4e3_e).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_4e3_e[0]}")
                    
    ################## ECA 2017 CAT 4 E3 M ##################
    if ECA_2017_CAT_4E3_M is True:
        if pd.notna(lim_inf_eca2017_4e3_m) and pd.notna(lim_sup_eca2017_4e3_m):
            eca_formateado_1 = str(lim_inf_eca2017_4e3_m).replace(".", ",") + ' a '+ str(lim_sup_eca2017_4e3_m).replace(".", ",")
        elif pd.isna(lim_inf_eca2017_4e3_m) and pd.notna(lim_sup_eca2017_4e3_m):
            eca_formateado_1 = str(lim_sup_eca2017_4e3_m).replace(".", ",")
        elif pd.notna(lim_inf_eca2017_4e3_m) and pd.isna(lim_sup_eca2017_4e3_m):
            eca_formateado_1 = str(lim_inf_eca2017_4e3_m).replace(".", ",")
            
        if porc_eca2017_4e3_m is None:
            texto.append(f" Cabe mencionar que no existe un ECA 2017 para agua para la categoría 4 - E3 marinos (conservación del ambiente acuático para ecosistemas costeros y marinos) aplicable para este parámetro.")
        else:
            if porc_eca2017_4e3_m == 0:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E3 marinos ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2017.")
            elif porc_eca2017_4e3_m == 100:
                texto.append(f" Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E3 marinos ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2017.")          
            else:
                parte1_eca2017_4e3_m = []                
                #if porc_eca2017_4e3_m not in (None, 0, 100):
                parte1_eca2017_4e3_m.append(f"Al comparar los resultados obtenidos con el ECA 2017 para agua para la categoría 4 - E3 marinos ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2017_4e3_m} ({str(porc_eca2017_4e3_m).replace('.', ',')} %) de los registros no cumplen con el valor establecido.")
                texto.append(f" {parte1_eca2017_4e3_m[0]}")
                    
    ################## ECA 2008 CAT 1 A1 ##################
    if ECA_2008_CAT_1A1 is True:
        if pd.notna(lim_inf_eca2008_1a1) and pd.notna(lim_sup_eca2008_1a1):
            eca_formateado_1 = str(lim_inf_eca2008_1a1).replace(".", ",") + ' a '+ str(lim_sup_eca2008_1a1).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_1a1) and pd.notna(lim_sup_eca2008_1a1):
            eca_formateado_1 = str(lim_sup_eca2008_1a1).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_1a1) and pd.isna(lim_sup_eca2008_1a1):
            eca_formateado_1 = str(lim_inf_eca2008_1a1).replace(".", ",")
        
        if porc_eca2008_1a1 is None and porc_eca2008_1a1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 1 - A1 (aguas que pueden ser potabilizadas con desinfección) aplicable para este parámetro.")
        else:
            if porc_eca2008_1a1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - A1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_1a1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - A1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_1a1 = []                
                if porc_eca2008_1a1 not in (None, 0, 100):
                    parte1_eca2008_1a1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - A1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_1a1} ({str(porc_eca2008_1a1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_1a1[0]}")
                    
    ################## ECA 2008 CAT 1 A2 ##################
    if ECA_2008_CAT_1A2 is True:
        if pd.notna(lim_inf_eca2008_1a2) and pd.notna(lim_sup_eca2008_1a2):
            eca_formateado_1 = str(lim_inf_eca2008_1a2).replace(".", ",") + ' a '+ str(lim_sup_eca2008_1a2).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_1a2) and pd.notna(lim_sup_eca2008_1a2):
            eca_formateado_1 = str(lim_sup_eca2008_1a2).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_1a2) and pd.isna(lim_sup_eca2008_1a2):
            eca_formateado_1 = str(lim_inf_eca2008_1a2).replace(".", ",")
        
        if porc_eca2008_1a2 is None and porc_eca2008_1a2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 1 - A2 (aguas que pueden ser potabilizadas con tratamiento convencional) aplicable para este parámetro.")
        else:
            if porc_eca2008_1a2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - A2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_1a2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - A2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_1a2 = []                
                if porc_eca2008_1a2 not in (None, 0, 100):
                    parte1_eca2008_1a2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - A2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_1a2} ({str(porc_eca2008_1a2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_1a2[0]}")
                    
    ################## ECA 2008 CAT 1 A3 ##################
    if ECA_2008_CAT_1A3 is True:
        if pd.notna(lim_inf_eca2008_1a3) and pd.notna(lim_sup_eca2008_1a3):
            eca_formateado_1 = str(lim_inf_eca2008_1a3).replace(".", ",") + ' a '+ str(lim_sup_eca2008_1a3).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_1a3) and pd.notna(lim_sup_eca2008_1a3):
            eca_formateado_1 = str(lim_sup_eca2008_1a3).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_1a3) and pd.isna(lim_sup_eca2008_1a3):
            eca_formateado_1 = str(lim_inf_eca2008_1a3).replace(".", ",")
        
        if porc_eca2008_1a3 is None and porc_eca2008_1a3 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 1 - A3 (aguas que pueden ser potabilizadas con tratamiento avanzado) aplicable para este parámetro.")
        else:
            if porc_eca2008_1a3 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - A3 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_1a3 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - A3 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_1a3 = []                
                if porc_eca2008_1a3 not in (None, 0, 100):
                    parte1_eca2008_1a3.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - A3 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_1a3} ({str(porc_eca2008_1a3).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_1a3[0]}")
                    
    ################## ECA 2008 CAT 1 B1 ##################
    if ECA_2008_CAT_1B1 is True:
        if pd.notna(lim_inf_eca2008_1b1) and pd.notna(lim_sup_eca2008_1b1):
            eca_formateado_1 = str(lim_inf_eca2008_1b1).replace(".", ",") + ' a '+ str(lim_sup_eca2008_1b1).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_1b1) and pd.notna(lim_sup_eca2008_1b1):
            eca_formateado_1 = str(lim_sup_eca2008_1b1).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_1b1) and pd.isna(lim_sup_eca2008_1b1):
            eca_formateado_1 = str(lim_inf_eca2008_1b1).replace(".", ",")
        
        if porc_eca2008_1b1 is None and porc_eca2008_1b1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 1 - B1 (aguas superficiales destinadas para recreación de contacto primario) aplicable para este parámetro.")
        else:
            if porc_eca2008_1b1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - B1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_1b1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - B1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_1b1 = []                
                if porc_eca2008_1b1 not in (None, 0, 100):
                    parte1_eca2008_1b1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - B1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_1b1} ({str(porc_eca2008_1b1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_1b1[0]}")
                    
    ################## ECA 2008 CAT 1 B2 ##################
    if ECA_2008_CAT_1B2 is True:
        if pd.notna(lim_inf_eca2008_1b2) and pd.notna(lim_sup_eca2008_1b2):
            eca_formateado_1 = str(lim_inf_eca2008_1b2).replace(".", ",") + ' a '+ str(lim_sup_eca2008_1b2).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_1b2) and pd.notna(lim_sup_eca2008_1b2):
            eca_formateado_1 = str(lim_sup_eca2008_1b2).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_1b2) and pd.isna(lim_sup_eca2008_1b2):
            eca_formateado_1 = str(lim_inf_eca2008_1b2).replace(".", ",")
        
        if porc_eca2008_1b2 is None and porc_eca2008_1b2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 1 - B2 (aguas superficiales destinadas para recreación de contacto secundario) aplicable para este parámetro.")
        else:
            if porc_eca2008_1b2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - B2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_1b2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - B2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_1b2 = []                
                if porc_eca2008_1b2 not in (None, 0, 100):
                    parte1_eca2008_1b2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 1 - B2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_1b2} ({str(porc_eca2008_1b2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_1b2[0]}")
                    
    ################## ECA 2008 CAT 2 C1 ##################
    if ECA_2008_CAT_2C1 is True:
        if pd.notna(lim_inf_eca2008_2c1) and pd.notna(lim_sup_eca2008_2c1):
            eca_formateado_1 = str(lim_inf_eca2008_2c1).replace(".", ",") + ' a '+ str(lim_sup_eca2008_2c1).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_2c1) and pd.notna(lim_sup_eca2008_2c1):
            eca_formateado_1 = str(lim_sup_eca2008_2c1).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_2c1) and pd.isna(lim_sup_eca2008_2c1):
            eca_formateado_1 = str(lim_inf_eca2008_2c1).replace(".", ",")
        
        if porc_eca2008_2c1 is None and porc_eca2008_2c1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 2 - C1 (extracción y cultivo de moluscos, equinodermos y tunicados en aguas marino costeras) aplicable para este parámetro.")
        else:
            if porc_eca2008_2c1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 2 - C1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_2c1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 2 - C1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_2c1 = []                
                if porc_eca2008_2c1 not in (None, 0, 100):
                    parte1_eca2008_2c1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 2 - C1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_2c1} ({str(porc_eca2008_2c1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_2c1[0]}")
                    
    ################## ECA 2008 CAT 2 C2 ##################
    if ECA_2008_CAT_2C2 is True:
        if pd.notna(lim_inf_eca2008_2c2) and pd.notna(lim_sup_eca2008_2c2):
            eca_formateado_1 = str(lim_inf_eca2008_2c2).replace(".", ",") + ' a '+ str(lim_sup_eca2008_2c2).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_2c2) and pd.notna(lim_sup_eca2008_2c2):
            eca_formateado_1 = str(lim_sup_eca2008_2c2).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_2c2) and pd.isna(lim_sup_eca2008_2c2):
            eca_formateado_1 = str(lim_inf_eca2008_2c2).replace(".", ",")
        
        if porc_eca2008_2c2 is None and porc_eca2008_2c2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 2 - C2 (extracción y cultivo de otras especies hidrobiológicas en aguas marino costeras) aplicable para este parámetro.")
        else:
            if porc_eca2008_2c2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 2 - C2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_2c2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 2 - C2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_2c2 = []                
                if porc_eca2008_2c2 not in (None, 0, 100):
                    parte1_eca2008_2c2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 2 - C2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_2c2} ({str(porc_eca2008_2c2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_2c2[0]}")
                    
    ################## ECA 2008 CAT 2 C3 ##################
    if ECA_2008_CAT_2C3 is True:
        if pd.notna(lim_inf_eca2008_2c3) and pd.notna(lim_sup_eca2008_2c3):
            eca_formateado_1 = str(lim_inf_eca2008_2c3).replace(".", ",") + ' a '+ str(lim_sup_eca2008_2c3).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_2c3) and pd.notna(lim_sup_eca2008_2c3):
            eca_formateado_1 = str(lim_sup_eca2008_2c3).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_2c3) and pd.isna(lim_sup_eca2008_2c3):
            eca_formateado_1 = str(lim_inf_eca2008_2c3).replace(".", ",")
        
        if porc_eca2008_2c3 is None and porc_eca2008_2c3 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 2 - C3 (actividades marino portuarias, industriales o de saneamiento en aguas marino costeras) aplicable para este parámetro.")
        else:
            if porc_eca2008_2c3 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 2 - C3 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_2c3 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 2 - C3 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_2c3 = []                
                if porc_eca2008_2c3 not in (None, 0, 100):
                    parte1_eca2008_2c3.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 2 - C3 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_2c3} ({str(porc_eca2008_2c3).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_2c3[0]}")
                    
    ################## ECA 2008 CAT 3 D1 ##################
    if ECA_2008_CAT_3D1 is True and ECA_2008_CAT_3D2 is False:
        if pd.notna(lim_inf_eca2008_3d1) and pd.notna(lim_sup_eca2008_3d1):
            eca_formateado_1 = str(lim_inf_eca2008_3d1).replace(".", ",") + ' a '+ str(lim_sup_eca2008_3d1).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_3d1) and pd.notna(lim_sup_eca2008_3d1):
            eca_formateado_1 = str(lim_sup_eca2008_3d1).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_3d1) and pd.isna(lim_sup_eca2008_3d1):
            eca_formateado_1 = str(lim_inf_eca2008_3d1).replace(".", ",")
            
        if porc_eca2008_3d1 is None and porc_eca2008_3d1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 3 - D1 (riego de vegetales) aplicable para este parámetro.")
        else:
            if porc_eca2008_3d1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 - D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_3d1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 - D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_3d1 = []                
                if porc_eca2008_3d1 not in (None, 0, 100):
                    parte1_eca2008_3d1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 - D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_3d1} ({str(porc_eca2008_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_3d1[0]}")
                    
    ################## ECA 2008 CAT 3 D2 ##################
    if ECA_2008_CAT_3D1 is False and ECA_2008_CAT_3D2 is True:
        if pd.notna(lim_inf_eca2008_3d2) and pd.notna(lim_sup_eca2008_3d2):
            eca_formateado_1 = str(lim_inf_eca2008_3d2).replace(".", ",") + ' a '+ str(lim_sup_eca2008_3d2).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_3d2) and pd.notna(lim_sup_eca2008_3d2):
            eca_formateado_1 = str(lim_sup_eca2008_3d2).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_3d2) and pd.isna(lim_sup_eca2008_3d2):
            eca_formateado_1 = str(lim_inf_eca2008_3d2).replace(".", ",")
            
        if porc_eca2008_3d2 is None and porc_eca2008_3d2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
        else:
            if porc_eca2008_3d2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 - D2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_3d2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 - D2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_3d2 = []                
                if porc_eca2008_3d2 not in (None, 0, 100):
                    parte1_eca2008_3d2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 - D2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_3d2} ({str(porc_eca2008_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_3d2[0]}")
                    
    ################## ECA 2008 CAT 3 D1 y D2##################
    if ECA_2008_CAT_3D1 is True and ECA_2008_CAT_3D2 is True:
        if pd.notna(lim_inf_eca2008_3d1) and pd.notna(lim_sup_eca2008_3d1):
            eca_formateado_1 = str(lim_inf_eca2008_3d1).replace(".", ",") + ' a '+ str(lim_sup_eca2008_3d1).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_3d1) and pd.notna(lim_sup_eca2008_3d1):
            eca_formateado_1 = str(lim_sup_eca2008_3d1).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_3d1) and pd.isna(lim_sup_eca2008_3d1):
            eca_formateado_1 = str(lim_inf_eca2008_3d1).replace(".", ",")
            
        if pd.notna(lim_inf_eca2008_3d2) and pd.notna(lim_sup_eca2008_3d2):
            eca_formateado_2 = str(lim_inf_eca2008_3d2).replace(".", ",") + ' a '+ str(lim_sup_eca2008_3d2).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_3d2) and pd.notna(lim_sup_eca2008_3d2):
            eca_formateado_2 = str(lim_sup_eca2008_3d2).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_3d2) and pd.isna(lim_sup_eca2008_3d2):
            eca_formateado_2 = str(lim_inf_eca2008_3d2).replace(".", ",")
            
        if porc_eca2008_3d1 is None and porc_eca2008_3d2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 3 – D1 (riego de vegetales) y 3 - D2 (bebida de animales) aplicable para este parámetro.")
        else:
            if porc_eca2008_3d1 == 0 and porc_eca2008_3d2 == 0:
                texto.append(f' Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}) y 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2008.')
            elif porc_eca2008_3d1 == 100 and porc_eca2008_3d2 == 100:                
                texto.append(f' Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}) y 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.')
            elif porc_eca2008_3d1 == 0 and porc_eca2008_3d2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008; y comparando con el ECA 2008 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")
            elif porc_eca2008_3d1 == 100 and porc_eca2008_3d2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008; y comparando con el ECA 2008 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_3d1 == None and porc_eca2008_3d2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2008. Cabe mencionar que no existe un ECA 2008 para agua para la categoría 3 – D1 (riego de vegetales) aplicable para este parámetro.")
            elif porc_eca2008_3d1 == None and porc_eca2008_3d2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2008. Cabe mencionar que no existe un ECA 2008 para agua para la categoría 3 – D1 (riego de vegetales) aplicable para este parámetro.")
            elif porc_eca2008_3d1 == 0 and porc_eca2008_3d2 == None:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008. Cabe mencionar que no existe un ECA 2008 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
            elif porc_eca2008_3d1 == 100 and porc_eca2008_3d2 == None:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008. Cabe mencionar que no existe un ECA 2008 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
            else:
                parte1 = []
                parte2 = []
                if porc_eca2008_3d1 not in (None, 0, 100) and porc_eca2008_3d2 is None:
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_3d1} ({str(porc_eca2008_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido. Cabe mencionar que no existe un ECA 2008 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
                    texto.append(f" {parte1[0]}")
                if porc_eca2008_3d1 is None and porc_eca2008_3d2 not in (None, 0, 100):
                    parte2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2008_3d2} ({str(porc_eca2008_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido. Cabe mencionar que no existe un ECA 2008 para agua para la categoría 3 – D1 (riego de vegetales) aplicable para este parámetro.")    
                    texto.append(f" {parte2[0]}")
                if porc_eca2008_3d1 not in (None, 0, 100) and porc_eca2008_3d2 not in (None, 0, 100):
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_3d1} ({str(porc_eca2008_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2008_3d2} ({str(porc_eca2008_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2008_3d1 == 0 and porc_eca2008_3d2 not in (None, 0, 100):
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2008_3d2} ({str(porc_eca2008_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2008_3d1 not in (None, 0, 100) and porc_eca2008_3d2 == 0:
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_3d1} ({str(porc_eca2008_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2008_3d1 == 100 and porc_eca2008_3d2 not in (None, 0, 100):
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2008_3d2} ({str(porc_eca2008_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2008_3d1 not in (None, 0, 100) and porc_eca2008_3d2 == 100:
                    parte1.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_3d1} ({str(porc_eca2008_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                    
    ################## ECA 2008 CAT 4 E1 ##################
    if ECA_2008_CAT_4E1 is True:
        if pd.notna(lim_inf_eca2008_4e1) and pd.notna(lim_sup_eca2008_4e1):
            eca_formateado_1 = str(lim_inf_eca2008_4e1).replace(".", ",") + ' a '+ str(lim_sup_eca2008_4e1).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_4e1) and pd.notna(lim_sup_eca2008_4e1):
            eca_formateado_1 = str(lim_sup_eca2008_4e1).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_4e1) and pd.isna(lim_sup_eca2008_4e1):
            eca_formateado_1 = str(lim_inf_eca2008_4e1).replace(".", ",")
        
        if porc_eca2008_4e1 is None and porc_eca2008_4e1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 4 - E1 (conservación del ambiente acuático para lagunas y lagos) aplicable para este parámetro.")
        else:
            if porc_eca2008_4e1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_4e1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_4e1 = []                
                if porc_eca2008_4e1 not in (None, 0, 100):
                    parte1_eca2008_4e1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_4e1} ({str(porc_eca2008_4e1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_4e1[0]}")
                    
    ################## ECA 2008 CAT 4 E2 CYS ##################
    if ECA_2008_CAT_4E2_CYS is True:
        if pd.notna(lim_inf_eca2008_4e2_cys) and pd.notna(lim_sup_eca2008_4e2_cys):
            eca_formateado_1 = str(lim_inf_eca2008_4e2_cys).replace(".", ",") + ' a '+ str(lim_sup_eca2008_4e2_cys).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_4e2_cys) and pd.notna(lim_sup_eca2008_4e2_cys):
            eca_formateado_1 = str(lim_sup_eca2008_4e2_cys).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_4e2_cys) and pd.isna(lim_sup_eca2008_4e2_cys):
            eca_formateado_1 = str(lim_inf_eca2008_4e2_cys).replace(".", ",")
        
        if porc_eca2008_4e2_cys is None and porc_eca2008_4e2_cys is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 4 - E2 costa y sierra (conservación del ambiente acuático para ríos) aplicable para este parámetro.")
        else:
            if porc_eca2008_4e2_cys == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E2 costa y sierra ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_4e2_cys == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E2 costa y sierra ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_4e2_cys = []                
                if porc_eca2008_4e2_cys not in (None, 0, 100):
                    parte1_eca2008_4e2_cys.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E2 costa y sierra ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_4e2_cys} ({str(porc_eca2008_4e2_cys).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_4e2_cys[0]}")
                    
    ################## ECA 2008 CAT 4 E2 S ##################
    if ECA_2008_CAT_4E2_CYS is True:
        if pd.notna(lim_inf_eca2008_4e2_s) and pd.notna(lim_sup_eca2008_4e2_s):
            eca_formateado_1 = str(lim_inf_eca2008_4e2_s).replace(".", ",") + ' a '+ str(lim_sup_eca2008_4e2_s).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_4e2_s) and pd.notna(lim_sup_eca2008_4e2_s):
            eca_formateado_1 = str(lim_sup_eca2008_4e2_s).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_4e2_s) and pd.isna(lim_sup_eca2008_4e2_s):
            eca_formateado_1 = str(lim_inf_eca2008_4e2_s).replace(".", ",")
        
        if porc_eca2008_4e2_s is None and porc_eca2008_4e2_s is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 4 - E2 selva (conservación del ambiente acuático para ríos) aplicable para este parámetro.")
        else:
            if porc_eca2008_4e2_s == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E2 selva ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_4e2_s == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E2 selva ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_4e2_s = []                
                if porc_eca2008_4e2_s not in (None, 0, 100):
                    parte1_eca2008_4e2_s.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E2 selva ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_4e2_s} ({str(porc_eca2008_4e2_s).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_4e2_s[0]}")
                    
    ################## ECA 2008 CAT 4 E3 E ##################
    if ECA_2008_CAT_4E3_E is True:
        if pd.notna(lim_inf_eca2008_4e3_e) and pd.notna(lim_sup_eca2008_4e3_e):
            eca_formateado_1 = str(lim_inf_eca2008_4e3_e).replace(".", ",") + ' a '+ str(lim_sup_eca2008_4e3_e).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_4e3_e) and pd.notna(lim_sup_eca2008_4e3_e):
            eca_formateado_1 = str(lim_sup_eca2008_4e3_e).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_4e3_e) and pd.isna(lim_sup_eca2008_4e3_e):
            eca_formateado_1 = str(lim_inf_eca2008_4e3_e).replace(".", ",")
        
        if porc_eca2008_4e3_e is None and porc_eca2008_4e3_e is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 4 - E3 estuarios (conservación del ambiente acuático para ecosistemas costeros y marinos) aplicable para este parámetro.")
        else:
            if porc_eca2008_4e3_e == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E3 estuarios ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_4e3_e == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E3 estuarios ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_4e3_e = []                
                if porc_eca2008_4e3_e not in (None, 0, 100):
                    parte1_eca2008_4e3_e.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E3 estuarios ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_4e3_e} ({str(porc_eca2008_4e3_e).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_4e3_e[0]}")
                    
    ################## ECA 2008 CAT 4 E3 M ##################
    if ECA_2008_CAT_4E3_M is True:
        if pd.notna(lim_inf_eca2008_4e3_m) and pd.notna(lim_sup_eca2008_4e3_m):
            eca_formateado_1 = str(lim_inf_eca2008_4e3_m).replace(".", ",") + ' a '+ str(lim_sup_eca2008_4e3_m).replace(".", ",")
        elif pd.isna(lim_inf_eca2008_4e3_m) and pd.notna(lim_sup_eca2008_4e3_m):
            eca_formateado_1 = str(lim_sup_eca2008_4e3_m).replace(".", ",")
        elif pd.notna(lim_inf_eca2008_4e3_m) and pd.isna(lim_sup_eca2008_4e3_m):
            eca_formateado_1 = str(lim_inf_eca2008_4e3_m).replace(".", ",")
        
        if porc_eca2008_4e3_m is None and porc_eca2008_4e3_m is None:
            texto.append(f" Por otro lado, no existe un ECA 2008 para agua para la categoría 4 - E3 marinos (conservación del ambiente acuático para ecosistemas costeros y marinos) aplicable para este parámetro.")
        else:
            if porc_eca2008_4e3_m == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E3 marinos ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2008.")
            elif porc_eca2008_4e3_m == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E3 marinos ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2008.")          
            else:
                parte1_eca2008_4e3_m = []                
                if porc_eca2008_4e3_m not in (None, 0, 100):
                    parte1_eca2008_4e3_m.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2008 para agua para la categoría 4 - E3 marinos ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2008_4e3_m} ({str(porc_eca2008_4e3_m).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2008_4e3_m[0]}")
                    
    ################## ECA 2015 CAT 1 A1 ##################
    if ECA_2015_CAT_1A1 is True:
        if pd.notna(lim_inf_eca2015_1a1) and pd.notna(lim_sup_eca2015_1a1):
            eca_formateado_1 = str(lim_inf_eca2015_1a1).replace(".", ",") + ' a '+ str(lim_sup_eca2015_1a1).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_1a1) and pd.notna(lim_sup_eca2015_1a1):
            eca_formateado_1 = str(lim_sup_eca2015_1a1).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_1a1) and pd.isna(lim_sup_eca2015_1a1):
            eca_formateado_1 = str(lim_inf_eca2015_1a1).replace(".", ",")
        
        if porc_eca2015_1a1 is None and porc_eca2015_1a1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 1 - A1 (aguas que pueden ser potabilizadas con desinfección) aplicable para este parámetro.")
        else:
            if porc_eca2015_1a1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - A1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_1a1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - A1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_1a1 = []                
                if porc_eca2015_1a1 not in (None, 0, 100):
                    parte1_eca2015_1a1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - A1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_1a1} ({str(porc_eca2015_1a1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_1a1[0]}")
                    
    ################## ECA 2015 CAT 1 A2 ##################
    if ECA_2015_CAT_1A2 is True:
        if pd.notna(lim_inf_eca2015_1a2) and pd.notna(lim_sup_eca2015_1a2):
            eca_formateado_1 = str(lim_inf_eca2015_1a2).replace(".", ",") + ' a '+ str(lim_sup_eca2015_1a2).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_1a2) and pd.notna(lim_sup_eca2015_1a2):
            eca_formateado_1 = str(lim_sup_eca2015_1a2).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_1a2) and pd.isna(lim_sup_eca2015_1a2):
            eca_formateado_1 = str(lim_inf_eca2015_1a2).replace(".", ",")
        
        if porc_eca2015_1a2 is None and porc_eca2015_1a2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 1 - A2 (aguas que pueden ser potabilizadas con tratamiento convencional) aplicable para este parámetro.")
        else:
            if porc_eca2015_1a2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - A2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_1a2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - A2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_1a2 = []                
                if porc_eca2015_1a2 not in (None, 0, 100):
                    parte1_eca2015_1a2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - A2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_1a2} ({str(porc_eca2015_1a2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_1a2[0]}")
                    
    ################## ECA 2015 CAT 1 A3 ##################
    if ECA_2015_CAT_1A3 is True:
        if pd.notna(lim_inf_eca2015_1a3) and pd.notna(lim_sup_eca2015_1a3):
            eca_formateado_1 = str(lim_inf_eca2015_1a3).replace(".", ",") + ' a '+ str(lim_sup_eca2015_1a3).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_1a3) and pd.notna(lim_sup_eca2015_1a3):
            eca_formateado_1 = str(lim_sup_eca2015_1a3).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_1a3) and pd.isna(lim_sup_eca2015_1a3):
            eca_formateado_1 = str(lim_inf_eca2015_1a3).replace(".", ",")
        
        if porc_eca2015_1a3 is None and porc_eca2015_1a3 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 1 - A3 (aguas que pueden ser potabilizadas con tratamiento avanzado) aplicable para este parámetro.")
        else:
            if porc_eca2015_1a3 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - A3 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_1a3 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - A3 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_1a3 = []                
                if porc_eca2015_1a3 not in (None, 0, 100):
                    parte1_eca2015_1a3.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - A3 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_1a3} ({str(porc_eca2015_1a3).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_1a3[0]}")
                    
    ################## ECA 2015 CAT 1 B1 ##################
    if ECA_2015_CAT_1B1 is True:
        if pd.notna(lim_inf_eca2015_1b1) and pd.notna(lim_sup_eca2015_1b1):
            eca_formateado_1 = str(lim_inf_eca2015_1b1).replace(".", ",") + ' a '+ str(lim_sup_eca2015_1b1).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_1b1) and pd.notna(lim_sup_eca2015_1b1):
            eca_formateado_1 = str(lim_sup_eca2015_1b1).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_1b1) and pd.isna(lim_sup_eca2015_1b1):
            eca_formateado_1 = str(lim_inf_eca2015_1b1).replace(".", ",")
        
        if porc_eca2015_1b1 is None and porc_eca2015_1b1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 1 - B1 (aguas superficiales destinadas para recreación de contacto primario) aplicable para este parámetro.")
        else:
            if porc_eca2015_1b1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - B1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_1b1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - B1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_1b1 = []                
                if porc_eca2015_1b1 not in (None, 0, 100):
                    parte1_eca2015_1b1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - B1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_1b1} ({str(porc_eca2015_1b1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_1b1[0]}")
                    
    ################## ECA 2015 CAT 1 B2 ##################
    if ECA_2015_CAT_1B2 is True:
        if pd.notna(lim_inf_eca2015_1b2) and pd.notna(lim_sup_eca2015_1b2):
            eca_formateado_1 = str(lim_inf_eca2015_1b2).replace(".", ",") + ' a '+ str(lim_sup_eca2015_1b2).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_1b2) and pd.notna(lim_sup_eca2015_1b2):
            eca_formateado_1 = str(lim_sup_eca2015_1b2).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_1b2) and pd.isna(lim_sup_eca2015_1b2):
            eca_formateado_1 = str(lim_inf_eca2015_1b2).replace(".", ",")
        
        if porc_eca2015_1b2 is None and porc_eca2015_1b2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 1 - B2 (aguas superficiales destinadas para recreación de contacto secundario) aplicable para este parámetro.")
        else:
            if porc_eca2015_1b2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - B2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_1b2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - B2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_1b2 = []                
                if porc_eca2015_1b2 not in (None, 0, 100):
                    parte1_eca2015_1b2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 1 - B2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_1b2} ({str(porc_eca2015_1b2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_1b2[0]}")
                    
    ################## ECA 2015 CAT 2 C1 ##################
    if ECA_2015_CAT_2C1 is True:
        if pd.notna(lim_inf_eca2015_2c1) and pd.notna(lim_sup_eca2015_2c1):
            eca_formateado_1 = str(lim_inf_eca2015_2c1).replace(".", ",") + ' a '+ str(lim_sup_eca2015_2c1).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_2c1) and pd.notna(lim_sup_eca2015_2c1):
            eca_formateado_1 = str(lim_sup_eca2015_2c1).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_2c1) and pd.isna(lim_sup_eca2015_2c1):
            eca_formateado_1 = str(lim_inf_eca2015_2c1).replace(".", ",")
        
        if porc_eca2015_2c1 is None and porc_eca2015_2c1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 2 - C1 (extracción y cultivo de moluscos, equinodermos y tunicados en aguas marino costeras) aplicable para este parámetro.")
        else:
            if porc_eca2015_2c1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_2c1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_2c1 = []                
                if porc_eca2015_2c1 not in (None, 0, 100):
                    parte1_eca2015_2c1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_2c1} ({str(porc_eca2015_2c1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_2c1[0]}")
                    
    ################## ECA 2015 CAT 2 C2 ##################
    if ECA_2015_CAT_2C2 is True:
        if pd.notna(lim_inf_eca2015_2c2) and pd.notna(lim_sup_eca2015_2c2):
            eca_formateado_1 = str(lim_inf_eca2015_2c2).replace(".", ",") + ' a '+ str(lim_sup_eca2015_2c2).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_2c2) and pd.notna(lim_sup_eca2015_2c2):
            eca_formateado_1 = str(lim_sup_eca2015_2c2).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_2c2) and pd.isna(lim_sup_eca2015_2c2):
            eca_formateado_1 = str(lim_inf_eca2015_2c2).replace(".", ",")
        
        if porc_eca2015_2c2 is None and porc_eca2015_2c2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 2 - C2 (extracción y cultivo de otras especies hidrobiológicas en aguas marino costeras) aplicable para este parámetro.")
        else:
            if porc_eca2015_2c2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_2c2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_2c2 = []                
                if porc_eca2015_2c2 not in (None, 0, 100):
                    parte1_eca2015_2c2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_2c2} ({str(porc_eca2015_2c2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_2c2[0]}")
                    
    ################## ECA 2015 CAT 2 C3 ##################
    if ECA_2015_CAT_2C3 is True:
        if pd.notna(lim_inf_eca2015_2c3) and pd.notna(lim_sup_eca2015_2c3):
            eca_formateado_1 = str(lim_inf_eca2015_2c3).replace(".", ",") + ' a '+ str(lim_sup_eca2015_2c3).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_2c3) and pd.notna(lim_sup_eca2015_2c3):
            eca_formateado_1 = str(lim_sup_eca2015_2c3).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_2c3) and pd.isna(lim_sup_eca2015_2c3):
            eca_formateado_1 = str(lim_inf_eca2015_2c3).replace(".", ",")
        
        if porc_eca2015_2c3 is None and porc_eca2015_2c3 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 2 - C3 (actividades marino portuarias, industriales o de saneamiento en aguas marino costeras) aplicable para este parámetro.")
        else:
            if porc_eca2015_2c3 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C3 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_2c3 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C3 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_2c3 = []                
                if porc_eca2015_2c3 not in (None, 0, 100):
                    parte1_eca2015_2c3.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C3 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_2c3} ({str(porc_eca2015_2c3).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_2c3[0]}")
                    
    ################## ECA 2015 CAT 2 C4 ##################
    if ECA_2015_CAT_2C4 is True:
        if pd.notna(lim_inf_eca2015_2c4) and pd.notna(lim_sup_eca2015_2c4):
            eca_formateado_1 = str(lim_inf_eca2015_2c4).replace(".", ",") + ' a '+ str(lim_sup_eca2015_2c4).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_2c4) and pd.notna(lim_sup_eca2015_2c4):
            eca_formateado_1 = str(lim_sup_eca2015_2c4).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_2c4) and pd.isna(lim_sup_eca2015_2c4):
            eca_formateado_1 = str(lim_inf_eca2015_2c4).replace(".", ",")
        
        if porc_eca2015_2c4 is None and porc_eca2015_2c4 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 2 - C4 (extracción y cultivo de especies hidrobiológicas en lagos y lagunas) aplicable para este parámetro.")
        else:
            if porc_eca2015_2c4 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C4 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_2c4 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C4 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_2c4 = []                
                if porc_eca2015_2c4 not in (None, 0, 100):
                    parte1_eca2015_2c4.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 2 - C4 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_2c4} ({str(porc_eca2015_2c4).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_2c4[0]}")
                    
    ################## ECA 2015 CAT 3 D1 ##################
    if ECA_2015_CAT_3D1 is True and ECA_2015_CAT_3D2 is False:
        if pd.notna(lim_inf_eca2015_3d1) and pd.notna(lim_sup_eca2015_3d1):
            eca_formateado_1 = str(lim_inf_eca2015_3d1).replace(".", ",") + ' a '+ str(lim_sup_eca2015_3d1).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_3d1) and pd.notna(lim_sup_eca2015_3d1):
            eca_formateado_1 = str(lim_sup_eca2015_3d1).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_3d1) and pd.isna(lim_sup_eca2015_3d1):
            eca_formateado_1 = str(lim_inf_eca2015_3d1).replace(".", ",")
            
        if porc_eca2015_3d1 is None and porc_eca2015_3d1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 3 - D1 (riego de vegetales) aplicable para este parámetro.")
        else:
            if porc_eca2015_3d1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 - D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_3d1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 - D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_3d1 = []                
                if porc_eca2015_3d1 not in (None, 0, 100):
                    parte1_eca2015_3d1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 - D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_3d1} ({str(porc_eca2015_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_3d1[0]}")
                    
    ################## ECA 2015 CAT 3 D2 ##################
    if ECA_2015_CAT_3D1 is False and ECA_2015_CAT_3D2 is True:
        if pd.notna(lim_inf_eca2015_3d2) and pd.notna(lim_sup_eca2015_3d2):
            eca_formateado_1 = str(lim_inf_eca2015_3d2).replace(".", ",") + ' a '+ str(lim_sup_eca2015_3d2).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_3d2) and pd.notna(lim_sup_eca2015_3d2):
            eca_formateado_1 = str(lim_sup_eca2015_3d2).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_3d2) and pd.isna(lim_sup_eca2015_3d2):
            eca_formateado_1 = str(lim_inf_eca2015_3d2).replace(".", ",")
            
        if porc_eca2015_3d2 is None and porc_eca2015_3d2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
        else:
            if porc_eca2015_3d2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 - D2 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_3d2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 - D2 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_3d2 = []                
                if porc_eca2015_3d2 not in (None, 0, 100):
                    parte1_eca2015_3d2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 - D2 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_3d2} ({str(porc_eca2015_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_3d2[0]}")
                    
    ################## ECA 2015 CAT 3 D1 y D2##################
    if ECA_2015_CAT_3D1 is True and ECA_2015_CAT_3D2 is True:
        if pd.notna(lim_inf_eca2015_3d1) and pd.notna(lim_sup_eca2015_3d1):
            eca_formateado_1 = str(lim_inf_eca2015_3d1).replace(".", ",") + ' a '+ str(lim_sup_eca2015_3d1).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_3d1) and pd.notna(lim_sup_eca2015_3d1):
            eca_formateado_1 = str(lim_sup_eca2015_3d1).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_3d1) and pd.isna(lim_sup_eca2015_3d1):
            eca_formateado_1 = str(lim_inf_eca2015_3d1).replace(".", ",")
            
        if pd.notna(lim_inf_eca2015_3d2) and pd.notna(lim_sup_eca2015_3d2):
            eca_formateado_2 = str(lim_inf_eca2015_3d2).replace(".", ",") + ' a '+ str(lim_sup_eca2015_3d2).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_3d2) and pd.notna(lim_sup_eca2015_3d2):
            eca_formateado_2 = str(lim_sup_eca2015_3d2).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_3d2) and pd.isna(lim_sup_eca2015_3d2):
            eca_formateado_2 = str(lim_inf_eca2015_3d2).replace(".", ",")
            
        if porc_eca2015_3d1 is None and porc_eca2015_3d2 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 3 – D1 (riego de vegetales) y 3 - D2 (bebida de animales) aplicable para este parámetro.")
        else:
            if porc_eca2015_3d1 == 0 and porc_eca2015_3d2 == 0:
                texto.append(f' Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}) y 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2015.')
            elif porc_eca2015_3d1 == 100 and porc_eca2015_3d2 == 100:                
                texto.append(f' Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}) y 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.')
            elif porc_eca2015_3d1 == 0 and porc_eca2015_3d2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015; y comparando con el ECA 2015 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")
            elif porc_eca2015_3d1 == 100 and porc_eca2015_3d2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015; y comparando con el ECA 2015 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_3d1 == None and porc_eca2015_3d2 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2015. Cabe mencionar que no existe un ECA 2015 para agua para la categoría 3 – D1 (riego de vegetales) aplicable para este parámetro.")
            elif porc_eca2015_3d1 == None and porc_eca2015_3d2 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 - D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2015. Cabe mencionar que no existe un ECA 2015 para agua para la categoría 3 – D1 (riego de vegetales) aplicable para este parámetro.")
            elif porc_eca2015_3d1 == 0 and porc_eca2015_3d2 == None:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015. Cabe mencionar que no existe un ECA 2015 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
            elif porc_eca2015_3d1 == 100 and porc_eca2015_3d2 == None:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015. Cabe mencionar que no existe un ECA 2015 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
            else:
                parte1 = []
                parte2 = []
                if porc_eca2015_3d1 not in (None, 0, 100) and porc_eca2015_3d2 is None:
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_3d1} ({str(porc_eca2015_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido. Cabe mencionar que no existe un ECA 2015 para agua para la categoría 3 - D2 (bebida de animales) aplicable para este parámetro.")
                    texto.append(f" {parte1[0]}")
                if porc_eca2015_3d1 is None and porc_eca2015_3d2 not in (None, 0, 100):
                    parte2.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2015_3d2} ({str(porc_eca2015_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido. Cabe mencionar que no existe un ECA 2015 para agua para la categoría 3 – D1 (riego de vegetales) aplicable para este parámetro.")    
                    texto.append(f" {parte2[0]}")
                if porc_eca2015_3d1 not in (None, 0, 100) and porc_eca2015_3d2 not in (None, 0, 100):
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_3d1} ({str(porc_eca2015_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2015_3d2} ({str(porc_eca2015_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2015_3d1 == 0 and porc_eca2015_3d2 not in (None, 0, 100):
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2015_3d2} ({str(porc_eca2015_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2015_3d1 not in (None, 0, 100) and porc_eca2015_3d2 == 0:
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_3d1} ({str(porc_eca2015_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2015_3d1 == 100 and porc_eca2015_3d2 not in (None, 0, 100):
                    parte1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que {n_inc_eca2015_3d2} ({str(porc_eca2015_3d2).replace('.',',')} %) de los registros no cumplen con el valor establecido.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                if porc_eca2015_3d1 not in (None, 0, 100) and porc_eca2015_3d2 == 100:
                    parte1.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_3d1} ({str(porc_eca2015_3d1).replace('.',',')} %) de los registros no cumplen con el valor establecido; y")
                    parte2.append(f"al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 3 – D2 ({eca_formateado_2} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")    
                    texto.append(f" {parte1[0]} {parte2[0]}")
                    
    ################## ECA 2015 CAT 4 E1 ##################
    if ECA_2015_CAT_4E1 is True:
        if pd.notna(lim_inf_eca2015_4e1) and pd.notna(lim_sup_eca2015_4e1):
            eca_formateado_1 = str(lim_inf_eca2015_4e1).replace(".", ",") + ' a '+ str(lim_sup_eca2015_4e1).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_4e1) and pd.notna(lim_sup_eca2015_4e1):
            eca_formateado_1 = str(lim_sup_eca2015_4e1).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_4e1) and pd.isna(lim_sup_eca2015_4e1):
            eca_formateado_1 = str(lim_inf_eca2015_4e1).replace(".", ",")
        
        if porc_eca2015_4e1 is None and porc_eca2015_4e1 is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 4 - E1 (conservación del ambiente acuático para lagunas y lagos) aplicable para este parámetro.")
        else:
            if porc_eca2015_4e1 == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E1 ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_4e1 == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E1 ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_4e1 = []                
                if porc_eca2015_4e1 not in (None, 0, 100):
                    parte1_eca2015_4e1.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E1 ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_4e1} ({str(porc_eca2015_4e1).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_4e1[0]}")
                    
    ################## ECA 2015 CAT 4 E2 CYS ##################
    if ECA_2015_CAT_4E2_CYS is True:
        if pd.notna(lim_inf_eca2015_4e2_cys) and pd.notna(lim_sup_eca2015_4e2_cys):
            eca_formateado_1 = str(lim_inf_eca2015_4e2_cys).replace(".", ",") + ' a '+ str(lim_sup_eca2015_4e2_cys).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_4e2_cys) and pd.notna(lim_sup_eca2015_4e2_cys):
            eca_formateado_1 = str(lim_sup_eca2015_4e2_cys).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_4e2_cys) and pd.isna(lim_sup_eca2015_4e2_cys):
            eca_formateado_1 = str(lim_inf_eca2015_4e2_cys).replace(".", ",")
        
        if porc_eca2015_4e2_cys is None and porc_eca2015_4e2_cys is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 4 - E2 costa y sierra (conservación del ambiente acuático para ríos) aplicable para este parámetro.")
        else:
            if porc_eca2015_4e2_cys == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E2 costa y sierra ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_4e2_cys == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E2 costa y sierra ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_4e2_cys = []                
                if porc_eca2015_4e2_cys not in (None, 0, 100):
                    parte1_eca2015_4e2_cys.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E2 costa y sierra ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_4e2_cys} ({str(porc_eca2015_4e2_cys).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_4e2_cys[0]}")
                    
    ################## ECA 2015 CAT 4 E2 S ##################
    if ECA_2015_CAT_4E2_CYS is True:
        if pd.notna(lim_inf_eca2015_4e2_s) and pd.notna(lim_sup_eca2015_4e2_s):
            eca_formateado_1 = str(lim_inf_eca2015_4e2_s).replace(".", ",") + ' a '+ str(lim_sup_eca2015_4e2_s).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_4e2_s) and pd.notna(lim_sup_eca2015_4e2_s):
            eca_formateado_1 = str(lim_sup_eca2015_4e2_s).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_4e2_s) and pd.isna(lim_sup_eca2015_4e2_s):
            eca_formateado_1 = str(lim_inf_eca2015_4e2_s).replace(".", ",")
        
        if porc_eca2015_4e2_s is None and porc_eca2015_4e2_s is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 4 - E2 selva (conservación del ambiente acuático para ríos) aplicable para este parámetro.")
        else:
            if porc_eca2015_4e2_s == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E2 selva ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_4e2_s == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E2 selva ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_4e2_s = []                
                if porc_eca2015_4e2_s not in (None, 0, 100):
                    parte1_eca2015_4e2_s.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E2 selva ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_4e2_s} ({str(porc_eca2015_4e2_s).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_4e2_s[0]}")
                    
    ################## ECA 2015 CAT 4 E3 E ##################
    if ECA_2015_CAT_4E3_E is True:
        if pd.notna(lim_inf_eca2015_4e3_e) and pd.notna(lim_sup_eca2015_4e3_e):
            eca_formateado_1 = str(lim_inf_eca2015_4e3_e).replace(".", ",") + ' a '+ str(lim_sup_eca2015_4e3_e).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_4e3_e) and pd.notna(lim_sup_eca2015_4e3_e):
            eca_formateado_1 = str(lim_sup_eca2015_4e3_e).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_4e3_e) and pd.isna(lim_sup_eca2015_4e3_e):
            eca_formateado_1 = str(lim_inf_eca2015_4e3_e).replace(".", ",")
        
        if porc_eca2015_4e3_e is None and porc_eca2015_4e3_e is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 4 - E3 estuarios (conservación del ambiente acuático para ecosistemas costeros y marinos) aplicable para este parámetro.")
        else:
            if porc_eca2015_4e3_e == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E3 estuarios ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_4e3_e == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E3 estuarios ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_4e3_e = []                
                if porc_eca2015_4e3_e not in (None, 0, 100):
                    parte1_eca2015_4e3_e.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E3 estuarios ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_4e3_e} ({str(porc_eca2015_4e3_e).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_4e3_e[0]}")
                    
    ################## ECA 2015 CAT 4 E3 M ##################
    if ECA_2015_CAT_4E3_M is True:
        if pd.notna(lim_inf_eca2015_4e3_m) and pd.notna(lim_sup_eca2015_4e3_m):
            eca_formateado_1 = str(lim_inf_eca2015_4e3_m).replace(".", ",") + ' a '+ str(lim_sup_eca2015_4e3_m).replace(".", ",")
        elif pd.isna(lim_inf_eca2015_4e3_m) and pd.notna(lim_sup_eca2015_4e3_m):
            eca_formateado_1 = str(lim_sup_eca2015_4e3_m).replace(".", ",")
        elif pd.notna(lim_inf_eca2015_4e3_m) and pd.isna(lim_sup_eca2015_4e3_m):
            eca_formateado_1 = str(lim_inf_eca2015_4e3_m).replace(".", ",")
        
        if porc_eca2015_4e3_m is None and porc_eca2015_4e3_m is None:
            texto.append(f" Por otro lado, no existe un ECA 2015 para agua para la categoría 4 - E3 marinos (conservación del ambiente acuático para ecosistemas costeros y marinos) aplicable para este parámetro.")
        else:
            if porc_eca2015_4e3_m == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E3 marinos ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con el ECA 2015.")
            elif porc_eca2015_4e3_m == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E3 marinos ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con el ECA 2015.")          
            else:
                parte1_eca2015_4e3_m = []                
                if porc_eca2015_4e3_m not in (None, 0, 100):
                    parte1_eca2015_4e3_m.append(f"Por otro lado, al comparar los resultados obtenidos con el ECA 2015 para agua para la categoría 4 - E3 marinos ({eca_formateado_1} {unidad}), se observa que {n_inc_eca2015_4e3_m} ({str(porc_eca2015_4e3_m).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_eca2015_4e3_m[0]}")
                    
    ################## LGA I ##################
    if LGA_I is True:
        if pd.notna(lim_inf_lga_i) and pd.notna(lim_sup_lga_i):
            eca_formateado_1 = str(lim_inf_lga_i).replace(".", ",") + ' a '+ str(lim_sup_lga_i).replace(".", ",")
        elif pd.isna(lim_inf_lga_i) and pd.notna(lim_sup_lga_i):
            eca_formateado_1 = str(lim_sup_lga_i).replace(".", ",")
        elif pd.notna(lim_inf_lga_i) and pd.isna(lim_sup_lga_i):
            eca_formateado_1 = str(lim_inf_lga_i).replace(".", ",")
        
        if porc_lga_i is None and porc_lga_i is None:
            texto.append(f" Por otro lado, no existe un valor en la LGA para la categoría I (aguas de abastecimiento doméstico con simple desinfección) aplicable para este parámetro.")
        else:
            if porc_lga_i == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría I ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con la LGA.")
            elif porc_lga_i == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría I ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con la LGA.")          
            else:
                parte1_lgai = []                
                if porc_lga_i not in (None, 0, 100):
                    parte1_lgai.append(f"Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría I ({eca_formateado_1} {unidad}), se observa que {n_inc_lga_i} ({str(porc_lga_i).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lgai[0]}")
                    
    ################## LGA II ##################
    if LGA_II is True:
        if pd.notna(lim_inf_lga_ii) and pd.notna(lim_sup_lga_ii):
            eca_formateado_1 = str(lim_inf_lga_ii).replace(".", ",") + ' a '+ str(lim_sup_lga_ii).replace(".", ",")
        elif pd.isna(lim_inf_lga_ii) and pd.notna(lim_sup_lga_ii):
            eca_formateado_1 = str(lim_sup_lga_ii).replace(".", ",")
        elif pd.notna(lim_inf_lga_ii) and pd.isna(lim_sup_lga_ii):
            eca_formateado_1 = str(lim_inf_lga_ii).replace(".", ",")
            
        if porc_lga_ii is None and porc_lga_ii is None:
            texto.append(f" Por otro lado, no existe un valor en la LGA para la categoría II (aguas de abastecimiento doméstico con tratamiento equivalente a procesos combinados de mezcla y coagulación, sedimentación, filtración y coloración) aplicable para este parámetro.")
        else:
            if porc_lga_ii == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría II ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con la LGA.")
            elif porc_lga_ii == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría II ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con la LGA.")          
            else:
                parte1_lgaii = []                
                if porc_lga_ii not in (None, 0, 100):
                    parte1_lgaii.append(f"Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría II ({eca_formateado_1} {unidad}), se observa que {n_inc_lga_ii} ({str(porc_lga_ii).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lgaii[0]}")
                    
    ################## LGA III ##################
    if LGA_III is True:
        if pd.notna(lim_inf_lga_iii) and pd.notna(lim_sup_lga_iii):
            eca_formateado_1 = str(lim_inf_lga_iii).replace(".", ",") + ' a '+ str(lim_sup_lga_iii).replace(".", ",")
        elif pd.isna(lim_inf_lga_iii) and pd.notna(lim_sup_lga_iii):
            eca_formateado_1 = str(lim_sup_lga_iii).replace(".", ",")
        elif pd.notna(lim_inf_lga_iii) and pd.isna(lim_sup_lga_iii):
            eca_formateado_1 = str(lim_inf_lga_iii).replace(".", ",")
            
        if porc_lga_iii is None and porc_lga_iii is None:
            texto.append(f" Por otro lado, no existe un valor en la LGA para la categoría III (aguas para riego de vegetales de consumo crudo y bebida de animales) aplicable para este parámetro.")
        else:
            if porc_lga_iii == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría III ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con la LGA.")
            elif porc_lga_iii == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría III ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con la LGA.")          
            else:
                parte1_lgaiii = []                
                if porc_lga_iii not in (None, 0, 100):
                    parte1_lgaiii.append(f"Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría III ({eca_formateado_1} {unidad}), se observa que {n_inc_lga_iii} ({str(porc_lga_iii).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lgaiii[0]}")
                    
    ################## LGA IV ##################
    if LGA_IV is True:
        if pd.notna(lim_inf_lga_iv) and pd.notna(lim_sup_lga_iv):
            eca_formateado_1 = str(lim_inf_lga_iv).replace(".", ",") + ' a '+ str(lim_sup_lga_iv).replace(".", ",")
        elif pd.isna(lim_inf_lga_iv) and pd.notna(lim_sup_lga_iv):
            eca_formateado_1 = str(lim_sup_lga_iv).replace(".", ",")
        elif pd.notna(lim_inf_lga_iv) and pd.isna(lim_sup_lga_iv):
            eca_formateado_1 = str(lim_inf_lga_iv).replace(".", ",")
            
        if porc_lga_iv is None and porc_lga_iv is None:
            texto.append(f" Por otro lado, no existe un valor en la LGA para la categoría IV (aguas de zonas recreativas de contacto primario) aplicable para este parámetro.")
        else:
            if porc_lga_iv == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría IV ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con la LGA.")
            elif porc_lga_iv == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría IV ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con la LGA.")          
            else:
                parte1_lgaiv = []                
                if porc_lga_iv not in (None, 0, 100):
                    parte1_lgaiv.append(f"Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría IV ({eca_formateado_1} {unidad}), se observa que {n_inc_lga_iv} ({str(porc_lga_iv).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lgaiv[0]}")
                    
    ################## LGA V ##################
    if LGA_V is True:
        if pd.notna(lim_inf_lga_v) and pd.notna(lim_sup_lga_v):
            eca_formateado_1 = str(lim_inf_lga_v).replace(".", ",") + ' a '+ str(lim_sup_lga_v).replace(".", ",")
        elif pd.isna(lim_inf_lga_v) and pd.notna(lim_sup_lga_v):
            eca_formateado_1 = str(lim_sup_lga_v).replace(".", ",")
        elif pd.notna(lim_inf_lga_v) and pd.isna(lim_sup_lga_v):
            eca_formateado_1 = str(lim_inf_lga_v).replace(".", ",")
            
        if porc_lga_v is None and porc_lga_v is None:
            texto.append(f" Por otro lado, no existe un valor en la LGA para la categoría V (aguas de zonas de pesca de mariscos bivalvos) aplicable para este parámetro.")
        else:
            if porc_lga_v == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría V ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con la LGA.")
            elif porc_lga_v == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría V ({eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con la LGA.")          
            else:
                parte1_lgav = []                
                if porc_lga_v not in (None, 0, 100):
                    parte1_lgav.append(f"Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría V ({eca_formateado_1} {unidad}), se observa que {n_inc_lga_v} ({str(porc_lga_v).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lgav[0]}")
                    
    ################## LGA VI ##################
    if LGA_VI is True:
        if pd.notna(lim_inf_lga_vi) and pd.notna(lim_sup_lga_vi):
            eca_formateado_1 = str(lim_inf_lga_vi).replace(".", ",") + ' a '+ str(lim_sup_lga_vi).replace(".", ",")
        elif pd.isna(lim_inf_lga_vi) and pd.notna(lim_sup_lga_vi):
            eca_formateado_1 = str(lim_sup_lga_vi).replace(".", ",")
        elif pd.notna(lim_inf_lga_vi) and pd.isna(lim_sup_lga_vi):
            eca_formateado_1 = str(lim_inf_lga_vi).replace(".", ",")
            
        if porc_lga_vi is None and porc_lga_vi is None:
            texto.append(f" Por otro lado, no existe un valor en la LGA para la categoría VI (aguas de zonas de preservación de fauna acuática y pesca recreativa o comercial) aplicable para este parámetro.")
        else:
            if porc_lga_vi == 0:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría VI ({eca_formateado_1} {unidad}), se observa que todos los registros cumplen con la LGA.")
            elif porc_lga_vi == 100:
                texto.append(f" Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría VI (a{eca_formateado_1} {unidad}), se observa que todos los registros no cumplen con la LGA.")          
            else:
                parte1_lgavi = []                
                if porc_lga_vi not in (None, 0, 100):
                    parte1_lgavi.append(f"Por otro lado, al comparar los resultados obtenidos con la LGA para la categoría VI ({eca_formateado_1} {unidad}), se observa que {n_inc_lga_vi} ({str(porc_lga_vi).replace('.',',')} %) de los registros no cumplen con el valor establecido.")
                    texto.append(f" {parte1_lgavi[0]}")
                    
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


