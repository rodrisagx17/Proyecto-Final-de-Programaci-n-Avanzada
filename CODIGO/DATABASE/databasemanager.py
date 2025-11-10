import pymysql
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, host: str = "localhost", user: str = "root", 
                password: str = "", database: str = "", port: int = 3306) -> bool:
        try:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.connection.cursor()
            print(f"Conexión exitosa a: {database}")
            return True
        except pymysql.Error as e:
            print(f"Error al conectar: {e}")
            return False

    def disconnect(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Conexión cerrada")

    def cerrar_conexion(self) -> None:
        self.disconnect()

    def commit(self) -> None:
        if self.connection:
            self.connection.commit()

    def rollback(self) -> None:
        if self.connection:
            self.connection.rollback()

    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Ejecuta query sin retornar resultados (INSERT, UPDATE, DELETE)"""
        try:
            self.cursor.execute(query, params or ())
            self.commit()
            return True
        except pymysql.Error as e:
            print(f"Error en query: {e}")
            self.rollback()
            return False

    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Ejecuta SELECT y retorna todos los resultados"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error en fetch: {e}")
            return []

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Ejecuta SELECT y retorna un solo resultado"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except pymysql.Error as e:
            print(f"Error en fetch: {e}")
            return None

    def get_last_id(self) -> int:
        """Retorna el último ID insertado"""
        return self.cursor.lastrowid if self.cursor else 0
