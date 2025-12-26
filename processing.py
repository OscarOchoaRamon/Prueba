import pandas as pd


def load_data(file):
    """
    Loads data from the uploaded Excel file.
    Expects sheets 'datos' and 'eca'.
    """
    try:
        xls = pd.ExcelFile(file)
        if "datos" not in xls.sheet_names:
             return None, "Error: El archivo debe contener la hoja 'datos'."
             
        df_datos = pd.read_excel(xls, "datos")
        
        # Check for 'eca' or 'lmp'
        if "eca" in xls.sheet_names:
            df_eca = pd.read_excel(xls, "eca")
        elif "lmp" in xls.sheet_names:
            df_eca = pd.read_excel(xls, "lmp")
        else:
            return None, "Error: El archivo debe contener una hoja 'eca' o 'lmp'."
            
        return (df_datos, df_eca), None
    except Exception as e:
        return None, f"Error al leer el archivo: {e}"

def clean_data(df):
    """
    Optimized cleaning of the 'valor' column.
    Handles '<' symbols and converts to numeric.
    """
    # Create a copy to avoid SettingWithCopy warnings
    df = df.copy()
    
    # Ensure 'valor' is string for string operations
    # Using astype(str) might turn NaNs into "nan", so we handle that.
    # But since we are looking for '<', we can coerce non-strings safely.
    
    # Vectorized detection of '<'
    # valid strings are those that are actually strings.
    # We'll operate on a series mask.
    
    # Force conversion to string to check for '<', but handle NaNs first if needed?
    # Actually, pandas str accessor handles NaNs as NaNs usually.
    
    # We need to handle potential mixed types. 
    # Let's coerce everything to string first for the check.
    s_values = df['valor'].astype(str)
    
    # Mask for values containing '<'
    mask_less = s_values.str.contains('<', na=False)
    
    # 1. Handle values with '<'
    # Remove '<', convert to float, divide by 2.
    # We perform this only on the subset, but vectorization is preserved on the subset.
    if mask_less.any():
        clean_values = s_values.loc[mask_less].str.replace('<', '', regex=False)
        # Convert to numeric, coerce errors to NaN just in case
        numeric_values = pd.to_numeric(clean_values, errors='coerce')
        df.loc[mask_less, 'valor'] = numeric_values / 2.0
        
    # 2. Handle values without '<'
    # Convert original values to numeric directly
    # We use to_numeric on the inverse mask
    # Note: df.loc[~mask_less, 'valor'] might contain things that were already floats.
    # pd.to_numeric handles them fine.
    df.loc[~mask_less, 'valor'] = pd.to_numeric(df.loc[~mask_less, 'valor'], errors='coerce')
    
    # Final cleanup: ensure the column is fully float
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    
    # Drop rows where value is NaN (if that's the business rule from the original script)
    # The original script did: df = df.dropna(subset=["valor"])
    df = df.dropna(subset=['valor'])
    
    # Create 'parametro_unidad'
    df['parametro_unidad'] = df['parametro'].astype(str) + " (" + df['unidad'].astype(str) + ")"
    
    # Ensure fecha is datetime
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    return df

def merge_data(df_datos, df_eca):
    """
    Merges measurement data with regulation limits.
    """
    # Merge on parametro and unidad
    # how='left' keeps all measurements
    df_merged = df_datos.merge(df_eca, on=['parametro', 'unidad'], how='left')
    
    return df_merged

def get_regulation_columns(df):
    """
    Dynamically identifies regulation columns (limits).
    Assumes they start with 'lim_'.
    """
    return [col for col in df.columns if col.startswith('lim_')]

def get_regulation_groups(df):
    """
    Groups regulation columns into friendly standard names.
    Example: 'lim_inf_eca_2017_3d1' -> 'ECA 2017 3D1'
    Returns a dict: {'Standard Name': ['col1', 'col2']}
    """
    limit_cols = get_regulation_columns(df)
    groups = {}
    
    for col in limit_cols:
        # Generate friendly name
        # Remove prefix
        name = col.replace('lim_inf_', '').replace('lim_sup_', '').replace('lim_', '')
        # Replace underscores with spaces and uppercase
        friendly_name = name.replace('_', ' ').upper()
        
        # Clean up some common artifacts if needed or keep it simple
        if friendly_name not in groups:
            groups[friendly_name] = []
        groups[friendly_name].append(col)
        
    return groups
