from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from datetime import date, datetime

from VIEWS.Loggin_S import Ui_MainWindow as Ui_LoginWindow
from VIEWS.RegisterAtt_S import Ui_MainWindow as Ui_RegisterAttWindow
from VIEWS.Gym_S import Ui_MainWindow as Ui_GymWindow

from MODELS.persona import Persona
from MODELS.empleado import Empleado

#Tiempo en el que se mostrara la informacion de asistencia
tiempoDeEspera=10000

class vistascontroller:
    def __init__(self, gym_controller):
        self.gym_controller = gym_controller
        self.login_window = None
        self.gym_window = None
        self.registro_window = None
        self.cerrando_sesion = False
        
    def mostrar_login(self):
        if self.login_window is None:
            self.login_window = LoginWindow(self.gym_controller, self)
        else:
            self.login_window.ui.le_usuario.clear()
            self.login_window.ui.le_contrasea.clear()
            self.login_window.ui.le_usuario.setFocus()
        self.login_window.show()
        
    def mostrar_ventana_principal(self, empleado):
        if self.gym_window is None:
            self.gym_window = GymWindow(self.gym_controller, empleado, self)
        self.gym_window.show()
        
    def mostrar_registro_asistencia(self, desde_login=False):
        parent_window = self.login_window if desde_login else self.gym_window
        
        if self.registro_window and self.registro_window.isVisible():
            self.registro_window.raise_()
            self.registro_window.activateWindow()
        else:
            self.registro_window = RegisterAttWindow(
                self.gym_controller, 
                parent_window, 
                self, 
                desde_login
            )
            self.registro_window.show()
        
    def cerrar_login(self):
        if self.login_window:
            self.login_window.close()
            self.login_window = None
            
    def cerrar_ventana_principal(self):
        self.cerrar_ventanas_hijas()
        if self.gym_window:
            self.gym_window.close()
            self.gym_window = None
            
    def cerrar_registro_asistencia(self):
        if self.registro_window:
            self.registro_window.close()
            self.registro_window = None
    
    def cerrar_ventanas_hijas(self):
        self.cerrar_registro_asistencia()
    
    def cerrar_sesion(self):
        respuesta = QMessageBox.question(
            None,
            "Cerrar Sesión", 
            "¿Está seguro de que desea cerrar sesión?\nSe cerrarán todas las ventanas abiertas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.cerrando_sesion = True
            self.cerrar_ventanas_hijas()
            self.cerrar_ventana_principal()
            self.mostrar_login()
            self.cerrando_sesion = False
            return True
        return False
    
    def verificar_y_cerrar_hijas(self):
        if self.gym_window is None:
            self.cerrar_ventanas_hijas()

class LoginWindow(QMainWindow):
    def __init__(self, gym_controller, vistas_controller):
        super().__init__()
        self.gym_controller = gym_controller
        self.vistas_controller = vistas_controller
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        
        self.ui.bt_loggin.clicked.connect(self.iniciar_sesion)
        self.ui.le_contrasea.returnPressed.connect(self.iniciar_sesion)
        self.ui.btn_registrarAs.clicked.connect(self.ir_a_registro_asistencia)
        
        self.setWindowTitle("Gym Soft - Login")
        self.setFixedSize(self.width(), self.height())
    
    def iniciar_sesion(self):
        try:
            usuario = self.ui.le_usuario.text().strip()
            contraseña = self.ui.le_contrasea.text().strip()
            
            print(f"Intentando login con usuario: {usuario}")
            
            if not usuario or not contraseña:
                QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
                return
            
            cod_emple = int(usuario)
            print(f"Buscando empleado: {cod_emple}")
            
            empleado = self.verificar_empleado(cod_emple)
            print(f"Resultado búsqueda: {empleado}")
            
            if empleado:
                QMessageBox.information(self, "Éxito", f"Bienvenido/a {empleado.persona.nombre_completo}")
                self.vistas_controller.cerrar_login()
                self.vistas_controller.mostrar_ventana_principal(empleado)
            else:
                QMessageBox.critical(self, "Error", "Credenciales no válidas")
                self.limpiar_formulario()
                
        except ValueError:
            QMessageBox.critical(self, "Error", "El ID debe ser un número")
            self.limpiar_formulario()
        except Exception as e:
            print(f"Error en login: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def verificar_empleado(self, cod_emple):
        query = """
        SELECT e.CodEmple, p.Nombre, p.ApellidoPA, p.ApellidoMA 
        FROM Empleado e 
        JOIN Persona p ON e.IDPersona = p.ID 
        WHERE e.CodEmple = %s AND p.Activo = TRUE
        """
        
        resultado = self.gym_controller.db.fetch_one(query, (cod_emple,))
        
        if resultado:
            persona = Persona(
                nombre=resultado['Nombre'],
                apellido_pa=resultado['ApellidoPA'],
                apellido_ma=resultado['ApellidoMA']
            )
            
            empleado = Empleado(
                cod_emple=resultado['CodEmple'],
                persona=persona
            )
            return empleado
        
        return None
    
    def ir_a_registro_asistencia(self):
        self.vistas_controller.mostrar_registro_asistencia(desde_login=True)
        self.hide()
    
    def limpiar_formulario(self):
        self.ui.le_contrasea.clear()
        self.ui.le_usuario.setFocus()

class GymWindow(QMainWindow):
    def __init__(self, gym_controller, empleado, vistas_controller):
        super().__init__()
        self.gym_controller = gym_controller
        self.empleado = empleado
        self.vistas_controller = vistas_controller
        self.ui = Ui_GymWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Gym Soft - Sistema de Gestión")
        self.configurar_interfaz_empleado()
        
        self.ui.btn_registrarAs.clicked.connect(self.ir_a_registro_asistencia_desde_principal)
        self.ui.bt_cerrarSe.clicked.connect(self.cerrar_sesion)
    
    def configurar_interfaz_empleado(self):
        print(f"Empleado logueado: {self.empleado.persona.nombre_completo}")
        titulo_actual = self.windowTitle()
        self.setWindowTitle(f"{titulo_actual} - {self.empleado.persona.nombre_completo}")
    
    def ir_a_registro_asistencia_desde_principal(self):
        if (self.vistas_controller.registro_window and 
            self.vistas_controller.registro_window.isVisible()):
            self.vistas_controller.registro_window.raise_()
            self.vistas_controller.registro_window.activateWindow()
        else:
            self.vistas_controller.mostrar_registro_asistencia(desde_login=False)
    
    def cerrar_sesion(self):
        self.vistas_controller.cerrar_sesion()
    
    def closeEvent(self, event):
        if self.vistas_controller.cerrando_sesion:
            event.accept()
            return
            
        respuesta = QMessageBox.question(
            self, 
            "Cerrar Aplicación", 
            "¿Está seguro de que desea salir del sistema?\nSe cerrarán todas las ventanas abiertas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.vistas_controller.cerrar_ventanas_hijas()
            self.vistas_controller.cerrar_ventana_principal()
            self.gym_controller.db.disconnect()
            event.accept()
        else:
            event.ignore()

class RegisterAttWindow(QMainWindow):
    def __init__(self, gym_controller, parent_window, vistas_controller, desde_login=False):
        super().__init__()
        self.gym_controller = gym_controller
        self.parent_window = parent_window
        self.vistas_controller = vistas_controller
        self.desde_login = desde_login
        self.ui = Ui_RegisterAttWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Gym Soft - Registro de Asistencia")
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.WindowType.Window)
        
        self.ui.bt_aceptar.clicked.connect(self.procesar_codigo)
        self.ui.le_codigo.returnPressed.connect(self.procesar_codigo)
        
        self.timer_restaurar = QTimer()
        self.timer_restaurar.setSingleShot(True)
        self.timer_restaurar.timeout.connect(self.restaurar_interfaz)
        
        self.estado_original()
    
    def estado_original(self):
        self.ui.frame_superior.setMaximumSize(16777215, 180)
        self.ui.frame_inferior.setMaximumSize(16777215, 0)
        self.ui.lb_nombre.setText("Nombre")
        self.ui.lb_info.setText("Información")
        self.ui.le_codigo.clear()
        self.ui.le_codigo.setFocus()
    
    def procesar_codigo(self):
        codigo_texto = self.ui.le_codigo.text().strip()
        
        if not codigo_texto:
            QMessageBox.warning(self, "Error", "Por favor ingrese un código")
            return
        
        try:
            codigo = int(codigo_texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
            self.ui.le_codigo.clear()
            self.ui.le_codigo.setFocus()
            return
        
        cliente = self.gym_controller.buscar_cliente_por_codigo(codigo)
        
        if not cliente:
            QMessageBox.warning(self, "Error", "Cliente no encontrado")
            self.ui.le_codigo.clear()
            self.ui.le_codigo.setFocus()
            return
        
        membresia = self.gym_controller.obtener_membresia_activa_cliente(cliente.cod_cli)
        
        sede_id = cliente.sede_inscrito.id if cliente.sede_inscrito and cliente.sede_inscrito.id else 1
        resultado = self.gym_controller.registrar_asistencia_cliente(cliente.cod_cli, sede_id)
        
        if resultado['success']:
            mensaje_tipo = "ENTRADA" if resultado['tipo'] == 'entrada' else "SALIDA"
            QMessageBox.information(self, "Éxito", f"{mensaje_tipo} registrada\n{resultado['mensaje']}")
            self.mostrar_informacion_cliente(cliente, membresia)
        else:
            QMessageBox.warning(self, "Error", resultado['mensaje'])
    
    def mostrar_informacion_cliente(self, cliente, membresia):
        nombre_completo = f"{cliente.persona.nombre} {cliente.persona.apellido_pa} {cliente.persona.apellido_ma}"
        self.ui.lb_nombre.setText(nombre_completo)
        
        if membresia and membresia.fecha_venc:
            try:
                if isinstance(membresia.fecha_venc, datetime):
                    fecha_venc_date = membresia.fecha_venc.date()
                else:
                    fecha_venc_date = membresia.fecha_venc
                
                dias_restantes = (fecha_venc_date - date.today()).days
                
                if dias_restantes > 0:
                    info_texto = f"Membresía {membresia.tipo}. Días restantes: {dias_restantes}"
                else:
                    info_texto = f"Membresía {membresia.tipo}. ¡Expirada!"
            except Exception as e:
                print(f"Error calculando días restantes: {e}")
                info_texto = f"Membresía {membresia.tipo}"
        elif membresia:
            info_texto = f"Membresía {membresia.tipo}"
        else:
            info_texto = "No tiene membresía activa"
        
        self.ui.lb_info.setText(info_texto)
        
        self.ui.frame_superior.setMaximumSize(16777215, 0)
        self.ui.frame_inferior.setMaximumSize(16777215, 16777215)
        
        self.timer_restaurar.start(tiempoDeEspera)
    
    def restaurar_interfaz(self):
        self.estado_original()
    
    def closeEvent(self, event):
        if self.timer_restaurar.isActive():
            self.timer_restaurar.stop()
        
        if not self.desde_login:
            self.vistas_controller.verificar_y_cerrar_hijas()
        
        if self.desde_login:
            if self.parent_window:
                self.parent_window.show()
        
        if self.vistas_controller.registro_window == self:
            self.vistas_controller.registro_window = None
        
        event.accept()