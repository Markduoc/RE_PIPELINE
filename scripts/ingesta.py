import os
import shutil
import glob
from datetime import datetime

# Buscar cualquier CSV en landing/
archivos = glob.glob("data/landing/*.csv")

if archivos:
    archivos_viejos = glob.glob("data/raw/ingesta_*.csv")
    for viejo in archivos_viejos:
        os.remove(viejo)
        print(f"Limpiando archivo antiguo de raw: {viejo}")
    origen = archivos[0]  # toma el primero que encuentre
    destino = f"data/raw/ingesta_{datetime.now().strftime('%Y-%m-%d')}.csv"
    os.makedirs("data/raw", exist_ok=True)
    shutil.move(origen, destino)
    print(f"Exito, datos movidos hacia {destino}")
else:
    print(f"Error,no se ha encontrado ningún archivo CSV en data/landing/")