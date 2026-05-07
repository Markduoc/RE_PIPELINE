import pandas as pd
import os

# Ajustar ruta
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs("data/reports", exist_ok=True)

# Cargar el archivo que ya limpiaste
df = pd.read_csv("data/processed/dataset_limpio.csv")
errores = []

# Validaciones Estructurales 
# 1. Unicidad de UserID
if df["UserID"].duplicated().any():
    for id_duplicado in df[df["UserID"].duplicated()]["UserID"]:
        errores.append({"ID": id_duplicado, "Capa": "Estructural", "Error": "UserID duplicado"})

# 2. Verificar que no haya nulos (doble chequeo)
if df.isnull().values.any():
    errores.append({"ID": "Global", "Capa": "Estructural", "Error": "Se detectaron valores nulos tras la limpieza"})

# Validaciones Semánticas 
# 1. Coherencia HighImmersion vs Nivel
incoherentes = df[(df["HighImmersion"] == True) & (df["ImmersionLevel"] < 4)]
for _, fila in incoherentes.iterrows():
    errores.append({"ID": fila["UserID"], "Capa": "Semántica", "Error": "HighImmersion True pero Nivel < 4"})

# 2. Coherencia SevereSickness vs Motion
mareo_error = df[(df["SevereSickness"] == True) & (df["MotionSickness"] < 7)]
for _, fila in mareo_error.iterrows():
    errores.append({"ID": fila["UserID"], "Capa": "Semántica", "Error": "SevereSickness True pero Motion < 7"})

# Generar reporte
pd.DataFrame(errores).to_csv("data/reports/reporte_errores.csv", index=False)
print(f"Validación lista. Reporte creado con {len(errores)} observaciones.")