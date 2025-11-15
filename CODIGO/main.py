import sys
import os
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
os.environ['QT_SCALE_FACTOR'] = '1'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from DATABASE.databasemanager import DatabaseManager
from CONTROLLERS.gymcontroller import GymController
from CONTROLLERS.vistascontroller import vistascontroller

def main():
    #Configuración de la base de datos
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'gyms',
        'port': 3306
    }
    
    #Inicializamos la app PyQt6
    app = QApplication(sys.argv)
    
    #Configuraramos high DPI scaling
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    #Inicializamos el DatabaseManager y controladores
    db_manager = DatabaseManager()
    
    if db_manager.connect(**db_config):
        gym_controller = GymController(db_manager)
        vistas_controller = vistascontroller(gym_controller)
        
        #Mostramos la ventana de login
        vistas_controller.mostrar_login()
        
        #Ejecutamos la app
        sys.exit(app.exec())
        
    else:
        print("No se pudo conectar a la base de datos")
        sys.exit(1)

if __name__ == "__main__":
    main()