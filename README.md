# RE_PIPELINE — Pipeline de Datos: Limpieza y Transformación

---

## Descripción

Este proyecto implementa un pipeline de datos en dos etapas: **ingesta** y **limpieza/transformación**. El objetivo es automatizar el proceso de preparación de un dataset CSV desde su recepción hasta dejarlo listo para análisis, asegurando calidad, consistencia y trazabilidad.

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
│   └── clean_data.py   # Etapa 2: limpia y transforma raw → processed
│
└── README.md
```

---

## Requisitos

- Python 3.8 o superior
- pandas

Instalar dependencias:

```bash
pip install pandas
```

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

---

## Control de Versiones

Se utilizó Git para registrar el avance del proyecto. Ejemplos de commits:

```
feat: agregar script de ingesta con selección dinámica de CSV
feat: implementar limpieza y transformación del dataset VR
docs: actualizar README con estructura y transformaciones aplicadas
```

---

## Decisiones Técnicas

- **Rutas relativas resueltas desde la raíz del proyecto** mediante `os.chdir()` al inicio de cada script, garantizando portabilidad.
- **Selección dinámica del archivo** en ingesta con `glob`, permitiendo procesar cualquier CSV sin modificar el código.
- **Columnas derivadas** diseñadas para facilitar análisis segmentados por perfil de usuario y tipo de sesión.
- **Registro de cambios en consola** en cada etapa del pipeline para facilitar la trazabilidad del proceso.