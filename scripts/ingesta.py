import os
import shutil
import glob
from datetime import datetime

# Buscar cualquier CSV en landing/
archivos = glob.glob("data/landing/*.csv")

if archivos:
    origen = archivos[0]  # toma el primero que encuentre
    destino = f"data/raw/ingesta_{datetime.now().strftime('%Y-%m-%d')}.csv"
    shutil.move(origen, destino)
    print(f"Exito! datos movidos hacia {destino}")
else:
    print(f"Error! no se ha encontrado ningún archivo CSV en data/landing/")