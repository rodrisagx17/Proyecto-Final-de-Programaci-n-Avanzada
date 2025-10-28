"""_summary_"""

import mysql.connector


class DatabaseManager:
    # Constructor
    def __init__(self):
        self.connection = None
        self.cursor = None

    # Conexión a la base de datos MySQL
    def connect(
        self,
        host: str = "localhost",
        user: str = "root",
        password: str = "",
        database: str = "",
        port=3306,
    ):
        # Establecer la conexión
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, password=password, database=database, port=port
            )
            self.cursor = self.connection.cursor()
            print(f"Conexión exitosa a la base de datos MySQL: {database}")
        except mysql.connector.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    # Desconexión de la base de datos
    def disconnect(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión cerrada")

    # Cerrar la conexión
    def cerrar_conexion(self) -> None:
        self.disconnect()

    # Confirmar los cambios en la base de datos
    def commit(self) -> None:
        if self.connection:
            self.connection.commit()

    # Revertir los cambios en la base de datos
    def rollback(self) -> None:
        if self.connection:
            self.connection.rollback()
