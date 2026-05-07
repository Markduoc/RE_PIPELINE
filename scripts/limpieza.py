import os
import glob
import pandas as pd
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ─────────────────────────────────────────────
# 1. LOCALIZAR EL ARCHIVO MÁS RECIENTE EN raw/
# ─────────────────────────────────────────────
archivos = sorted(glob.glob("data/raw/ingesta_*.csv"), reverse=True)

if not archivos:
    print("Error: no se encontró ningún archivo en data/raw/")
    exit(1)

ruta_entrada = archivos[0]
print(f"Archivo a procesar: {ruta_entrada}")

# ─────────────────────────────────────────────
# 2. CARGAR DATOS
# ─────────────────────────────────────────────
df = pd.read_csv(ruta_entrada)

print(f"\n── Estado ANTES de la limpieza ──")
print(f"  Filas:       {len(df)}")
print(f"  Columnas:    {list(df.columns)}")
print(f"  Nulos:\n{df.isnull().sum().to_string()}")
print(f"  Duplicados:  {df.duplicated().sum()}")

# ─────────────────────────────────────────────
# 3. LIMPIEZA
# ─────────────────────────────────────────────

# 3.1 Eliminar duplicados exactos
filas_antes = len(df)
df = df.drop_duplicates()
print(f"\n[Limpieza] Duplicados eliminados: {filas_antes - len(df)}")

# 3.2 Eliminar filas con nulos en columnas críticas
columnas_criticas = ["UserID", "Age", "Gender", "VRHeadset", "Duration",
                     "MotionSickness", "ImmersionLevel"]
filas_antes = len(df)
df = df.dropna(subset=columnas_criticas)
print(f"[Limpieza] Filas con nulos eliminadas: {filas_antes - len(df)}")

# 3.3 Filtrar valores fuera de rango
# Age: se esperan usuarios adultos entre 18 y 80 años
filas_antes = len(df)
df = df[df["Age"].between(18, 80)]
print(f"[Limpieza] Filas con Age fuera de rango eliminadas: {filas_antes - len(df)}")

# Duration: sesiones entre 1 y 120 minutos
filas_antes = len(df)
df = df[df["Duration"].between(1, 120)]
print(f"[Limpieza] Filas con Duration fuera de rango eliminadas: {filas_antes - len(df)}")

# MotionSickness e ImmersionLevel son escalas 1–10 y 1–5
filas_antes = len(df)
df = df[df["MotionSickness"].between(1, 10)]
df = df[df["ImmersionLevel"].between(1, 5)]
print(f"[Limpieza] Filas con escalas fuera de rango eliminadas: {filas_antes - len(df)}")

# ─────────────────────────────────────────────
# 4. ESTANDARIZACIÓN
# ─────────────────────────────────────────────

# 4.1 Estandarizar texto: sin espacios extra, capitalización consistente
df["Gender"]    = df["Gender"].str.strip().str.title()
df["VRHeadset"] = df["VRHeadset"].str.strip().str.title()

# 4.2 Redondear Duration a 2 decimales (limpieza numérica)
df["Duration"] = df["Duration"].round(2)

# 4.3 Resetear índice tras eliminaciones
df = df.reset_index(drop=True)

# ─────────────────────────────────────────────
# 5. TRANSFORMACIONES (columnas derivadas)
# ─────────────────────────────────────────────

# 5.1 Grupo etario
def grupo_etario(edad):
    if edad < 25:
        return "Joven"
    elif edad < 40:
        return "Adulto joven"
    elif edad < 55:
        return "Adulto"
    else:
        return "Adulto mayor"

df["AgeGroup"] = df["Age"].apply(grupo_etario)

# 5.2 Categoría de duración de sesión
def categoria_duracion(min):
    if min < 15:
        return "Corta"
    elif min < 35:
        return "Media"
    else:
        return "Larga"

df["SessionCategory"] = df["Duration"].apply(categoria_duracion)

# 5.3 Indicador de alta inmersión (ImmersionLevel >= 4)
df["HighImmersion"] = df["ImmersionLevel"] >= 4

# 5.4 Indicador de mareo severo (MotionSickness >= 7)
df["SevereSickness"] = df["MotionSickness"] >= 7

# 6. GUARDAR (Tu código original)
os.makedirs("data/processed", exist_ok=True)
ruta_salida = "data/processed/dataset_limpio.csv"
df.to_csv(ruta_salida, index=False)

print(f"\nArchivo guardado en: {ruta_salida}")
print("✓ Limpieza y transformación completada exitosamente.")

# --- NUEVO: BORRAR EL ARCHIVO DE RAW TRAS EL PROCESAMIENTO ---
try:
    os.remove(ruta_entrada)
    print(f"🗑️ Archivo temporal eliminado de raw: {ruta_entrada}")
except Exception as e:
    print(f"⚠️ No se pudo eliminar el archivo de raw: {e}")