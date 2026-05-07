import os
import pandas as pd
import oracledb

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CHECK .ENV
from dotenv import load_dotenv

load_dotenv()

DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN      = os.getenv("DB_DSN")
WALLET_DIR  = os.getenv("WALLET_DIR")
TABLA       = "VR_SESSIONS"
WALLET_DIR = os.path.abspath(WALLET_DIR) 

# Validar que todas las variables estén definidas
faltantes = [k for k, v in {"DB_USER": DB_USER, "DB_PASSWORD": DB_PASSWORD,
                              "DB_DSN": DB_DSN, "WALLET_DIR": WALLET_DIR}.items() if not v]
if faltantes:
    print(f"Error: faltan variables de entorno: {faltantes}")
    exit(1)
    
# 1. LEER EL CSV PROCESADO
ruta_csv = "data/processed/dataset_limpio.csv"

if not os.path.exists(ruta_csv):
    print(f"Error: no se encontró el archivo {ruta_csv}")
    print("Asegúrate de ejecutar limpieza.py antes de subida.py")
    exit(1)

df = pd.read_csv(ruta_csv)
print(f"CSV cargado: {len(df)} filas, {len(df.columns)} columnas")


# 2. MAPEO DE TIPOS Python → Oracle SQL
def tipo_oracle(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "NUMBER(10)"
    elif pd.api.types.is_float_dtype(dtype):
        return "NUMBER(15,4)"
    elif pd.api.types.is_bool_dtype(dtype):
        return "NUMBER(1)"          # Oracle no tiene BOOLEAN nativo en SQL
    else:
        return "VARCHAR2(255)"


# 3. CONECTAR A ORACLE CON WALLET
print(f"\nConectando a Oracle como {DB_USER}...")

try:
    connection = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
        config_dir=WALLET_DIR,
        wallet_location=WALLET_DIR,
        wallet_password=None        # solo si tu wallet tiene contraseña adicional
    )
    print("Conexión exitosa.")
except Exception as e:
    print(f"Error de conexión: {e}")
    exit(1)

cursor = connection.cursor()


# 4. VERIFICAR QUE LA TABLA NO EXISTA (fail on conflict)
cursor.execute(
    "SELECT COUNT(*) FROM user_tables WHERE table_name = :1",
    [TABLA.upper()]
)
existe = cursor.fetchone()[0]

if existe:
    print(f"\nError: la tabla '{TABLA}' ya existe en la base de datos.")
    print("Elimínala manualmente o cambia el nombre en TABLA si deseas empezar de cero.")
    cursor.close()
    connection.close()
    exit(1)


# 5. CREAR LA TABLA SEGÚN LAS COLUMNAS DEL CSV
columnas_sql = ",\n    ".join(
    f"{col.upper()} {tipo_oracle(df[col].dtype)}"
    for col in df.columns
)
ddl = f"CREATE TABLE {TABLA} (\n    {columnas_sql}\n)"

print(f"\nCreando tabla '{TABLA}'...")
cursor.execute(ddl)
print("Tabla creada.")

# 6. INSERTAR DATOS EN LOTES
BATCH_SIZE = 1000

# Convertir booleanos a 0/1 para Oracle
df_oracle = df.copy()
for col in df_oracle.select_dtypes(include="bool").columns:
    df_oracle[col] = df_oracle[col].astype(int)

placeholders = ", ".join(f":{i+1}" for i in range(len(df.columns)))
insert_sql = f"INSERT INTO {TABLA} VALUES ({placeholders})"

filas = [tuple(row) for row in df_oracle.itertuples(index=False, name=None)]
total = len(filas)
insertadas = 0

print(f"\nInsertando {total} filas en lotes de {BATCH_SIZE}...")

for i in range(0, total, BATCH_SIZE):
    lote = filas[i:i + BATCH_SIZE]
    cursor.executemany(insert_sql, lote)
    connection.commit()
    insertadas += len(lote)
    print(f"  {insertadas}/{total} filas insertadas")


# 7. VERIFICACIÓN FINAL
cursor.execute(f"SELECT COUNT(*) FROM {TABLA}")
count_db = cursor.fetchone()[0]
print(f"\n── Verificación ──")
print(f"  Filas en CSV:          {total}")
print(f"  Filas en Oracle:       {count_db}")
print(f"  ¿Coinciden?            {'✓ Sí' if count_db == total else '✗ No — revisar'}")

cursor.close()
connection.close()
print(f"\n✓ Subida completada exitosamente. Tabla: {TABLA}")