import os
import shutil
from datetime import datetime

#Definir rutas de los archivos
origen = "data/landing/dataset_retinopatia_simulado.csv"
destino = f"data/raw/ingesta_{datetime.now().strftime('%Y-%m-%d')}.csv"

#control de errores
if os.path.exists(origen):
    shutil.move(origen, destino)
    print(f"Exito! datos movidos hacia {destino}")
else:
    print(f"Error! no se ha encontrado el archivo de origen")