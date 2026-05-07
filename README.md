# RE_PIPELINE — Pipeline de Datos: Ingesta, Limpieza y Carga a Oracle

---

## Descripción

Este proyecto implementa un pipeline de datos en tres etapas: **ingesta**, **limpieza/transformación** y **carga a base de datos**. El objetivo es automatizar el proceso de preparación de un dataset CSV desde su recepción hasta dejarlo persistido en Oracle Database, asegurando calidad, consistencia y trazabilidad.

---

## Estructura del Proyecto

```
RE_PIPELINE/
│
├── data/
│   ├── landing/        # Archivos CSV crudos recién recibidos
│   ├── raw/            # Archivos ingestados (con timestamp)
│   └── processed/      # Dataset limpio y transformado
│
├── scripts/
│   ├── ingesta.py      # Etapa 1: mueve CSV de landing → raw
│   ├── clean_data.py   # Etapa 2: limpia y transforma raw → processed
│   └── subida.py       # Etapa 3: carga el CSV procesado a Oracle Database
│
├── wallet/             # Credenciales Oracle Wallet (NO subir a git)
├── .env                # Variables de entorno con credenciales (NO subir a git)
├── .env.example        # Plantilla de variables de entorno (sin valores)
└── README.md
```

---

## Requisitos

- Python 3.8 o superior
- pandas
- oracledb
- python-dotenv

Instalar dependencias:

```bash
pip install pandas oracledb python-dotenv
```

---

## Configuración de Credenciales

Las credenciales de conexión a Oracle se gestionan mediante un archivo `.env` en la raíz del proyecto. **Nunca subir este archivo al repositorio.**

Crea tu `.env` basándote en la plantilla:

```bash
cp .env.example .env
```

Contenido del `.env`:

```env
DB_USER=ADMIN
DB_PASSWORD=TuContraseñaAqui
DB_DSN=midb_high
WALLET_DIR=./wallet
```

| Variable | Descripción |
|---|---|
| `DB_USER` | Usuario de Oracle (usualmente `ADMIN`) |
| `DB_PASSWORD` | Contraseña del usuario |
| `DB_DSN` | Alias de conexión definido en `wallet/tnsnames.ora` (ej: `midb_high`) |
| `WALLET_DIR` | Ruta a la carpeta descomprimida del Oracle Wallet |

> **Nota:** El alias `DB_DSN` se obtiene abriendo `wallet/tnsnames.ora`. Busca el nombre antes del primer `=` (ej: `midb_high`, `midb_medium`, `midb_low`).

---

## Uso

Ejecutar los scripts en orden desde la raíz del proyecto:

### Etapa 1 – Ingesta

Mueve cualquier archivo CSV desde `data/landing/` hacia `data/raw/`, renombrándolo con la fecha de ingesta.

```bash
python scripts/ingesta.py
```

### Etapa 2 – Limpieza y Transformación

Lee el archivo más reciente de `data/raw/`, aplica el flujo de limpieza y guarda el resultado en `data/processed/`.

```bash
python scripts/clean_data.py
```

### Etapa 3 – Carga a Oracle Database

Lee el CSV procesado desde `data/processed/`, crea la tabla `VR_SESSIONS` en Oracle (falla si ya existe) e inserta los datos en lotes de 1.000 filas.

```bash
python scripts/subida.py
```

> **Importante:** Si la tabla `VR_SESSIONS` ya existe en la base de datos, el script termina con error. Elimínala manualmente antes de volver a ejecutar.

---

## Transformaciones Aplicadas

### Limpieza

| Problema | Acción |
|---|---|
| Registros duplicados | Eliminados con `drop_duplicates()` |
| Valores nulos en columnas críticas | Filas eliminadas con `dropna()` |
| Age fuera de rango (< 18 o > 80) | Filas eliminadas |
| Duration fuera de rango (< 1 o > 120 min) | Filas eliminadas |
| MotionSickness fuera de escala (1–10) | Filas eliminadas |
| ImmersionLevel fuera de escala (1–5) | Filas eliminadas |

### Estandarización

| Campo | Transformación |
|---|---|
| `Gender` | `.str.strip().str.title()` — elimina espacios y normaliza capitalización |
| `VRHeadset` | `.str.strip().str.title()` — ídem |
| `Duration` | Redondeado a 2 decimales |

### Columnas Derivadas

| Columna | Descripción |
|---|---|
| `AgeGroup` | Grupo etario: Joven / Adulto joven / Adulto / Adulto mayor |
| `SessionCategory` | Duración de sesión: Corta (< 15 min) / Media / Larga (> 35 min) |
| `HighImmersion` | `True` si `ImmersionLevel >= 4` |
| `SevereSickness` | `True` si `MotionSickness >= 7` |

### Mapeo de Tipos a Oracle

| Tipo Python/pandas | Tipo Oracle |
|---|---|
| `int` | `NUMBER(10)` |
| `float` | `NUMBER(15,4)` |
| `bool` | `NUMBER(1)` — convertido a 0/1 |
| `object` (texto) | `VARCHAR2(255)` |

---

## Control de Versiones

Se utilizó Git para registrar el avance del proyecto. Ejemplos de commits:

```
feat: agregar script de ingesta con selección dinámica de CSV
feat: implementar limpieza y transformación del dataset VR
feat: agregar script de carga a Oracle con wallet y .env
docs: actualizar README con etapa de subida y configuración de credenciales
```

---

## Archivos ignorados por Git

Asegúrate de que tu `.gitignore` incluya lo siguiente:

```
.env
wallet/
```

---

## Decisiones Técnicas

- **Rutas relativas resueltas desde la raíz del proyecto** mediante `os.chdir()` al inicio de cada script, garantizando portabilidad.
- **Selección dinámica del archivo** en ingesta con `glob`, permitiendo procesar cualquier CSV sin modificar el código.
- **Columnas derivadas** diseñadas para facilitar análisis segmentados por perfil de usuario y tipo de sesión.
- **Credenciales externalizadas en `.env`** mediante `python-dotenv`, evitando exponer información sensible en el código fuente.
- **Conexión a Oracle mediante Wallet**, compatible con Oracle Autonomous Database en la nube (OCI).
- **Inserción en lotes de 1.000 filas** con `executemany()` para optimizar el rendimiento en inserciones masivas.
- **Verificación post-carga** comparando el conteo de filas del CSV contra el conteo en la tabla Oracle.
- **Registro de cambios en consola** en cada etapa del pipeline para facilitar la trazabilidad del proceso.