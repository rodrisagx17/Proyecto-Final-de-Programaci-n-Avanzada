from DATABASE.databasemanager import DatabaseManager
from CONTROLLERS.gymcontroller import GymController
from MODELS.direccion import Direccion
from MODELS.persona import Persona
from MODELS.sede import Sede
from MODELS.cliente import Cliente
from datetime import datetime

def main():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'gyms',
        'port': 3306
    }
    
    db_manager = DatabaseManager()
    
    if db_manager.connect(**db_config):
        gym = GymController(db_manager)
        
        try:
            # Obtener sedes existentes
            sedes = gym.obtener_sedes()
            print(f"Sedes disponibles: {len(sedes)}")
            
            # Obtener clientes
            clientes = gym.obtener_clientes()
            print(f"Clientes registrados: {len(clientes)}")
            
            # Crear nueva sede si no hay
            if not sedes:
                direccion = Direccion(
                    calle="Zaragoza #25",
                    ciudad="Monterrey",
                    estado="Nuevo León",
                    cp=64000
                )
                sede = Sede(
                    nombre="GYM WARRIOR Z25",
                    hora_abre="07:00",
                    hora_cierra="22:00",
                    direccion=direccion,
                    telefono="8123456789"
                )
                sede_id = gym.crear_sede(sede)
                print(f"Sede creada con ID: {sede_id}")
                sedes = gym.obtener_sedes()
            
            # Crear nuevo cliente
            if sedes:
                persona = Persona(
                    nombre="María",
                    apellido_pa="Gómez",
                    apellido_ma="López",
                    email="maria@email.com",
                    telefono="8118765432"
                )
                cliente = Cliente(
                    persona=persona,
                    sede_inscrito=sedes[0],
                    genero="Femenino",
                    fecha_nac=datetime(1992, 8, 15),
                    fecha_inscri=datetime.now()
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
