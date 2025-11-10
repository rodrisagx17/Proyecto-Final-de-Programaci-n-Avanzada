from DATABASE.databasemanager import DatabaseManager
from CONTROLLERS.gymcontroller import GymController
from MODELS.sede import Sede
from MODELS.cliente import Cliente
from datetime import datetime

def main():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'gym',
        'port': 3306
    }
    
    db_manager = DatabaseManager()
    
    if db_manager.connect(**db_config):
        gym = GymController(db_manager)
        
        try:
            # Ejemplo para obtener sedes existentes
            sedes = gym.obtener_sedes()
            print(f"Sedes disponibles: {len(sedes)}")
            
            # Ejemplo para obtener clientes
            clientes = gym.obtener_clientes()
            print(f"Clientes registrados: {len(clientes)}")
            
            # Ejemplo para CREAR nueva sede si no hay
            if not sedes:
                sede = Sede(
                    nombre="GYM WARRIOR Z25",
                    hora_abre="07:00",
                    hora_cierra="22:00",
                    direccion="Zaragoza #25",
                    telefono="8123456789",
                    ciudad="Monterrey",
                    estado="Nuevo León",
                    cp=64000
                )
                sede_id = gym.crear_sede(sede)
                print(f"Sede creada con ID: {sede_id}")
                sedes = gym.obtener_sedes()  # Recargar sedes
            
            # Ejemplo para crear nuevo cliente
            if sedes:
                cliente = Cliente(
                    identificacion="CURP123456",
                    nombre="María",
                    apellido_paterno="Gómez",
                    apellido_materno="López",
                    telefono="8118765432",
                    genero="Femenino",
                    fecha_nacimiento=datetime(1992, 8, 15),
                    fecha_inscripcion=datetime.now(),
                    sede_inscrito=sedes[0],
                    activo=True
                )
                
                nuevo_id = gym.crear_cliente(cliente)
                if nuevo_id:
                    print(f"Cliente creado con ID: {nuevo_id}")
                else:
                    print("Error al crear cliente")
            
        except Exception as e:
            print(f"Error en la aplicación: {e}")
        finally:
            db_manager.disconnect()
    else:
        print("No se pudo conectar a la base de datos")

if __name__ == "__main__":
    main()
