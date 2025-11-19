from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import QTimer, Qt
from datetime import date, datetime, timedelta
from typing import Optional

from VIEWS.Loggin_S import Ui_MainWindow as Ui_LoginWindow
from VIEWS.RegisterAtt_S import Ui_MainWindow as Ui_RegisterAttWindow
from VIEWS.Gym_S import Ui_MainWindow as Ui_GymWindow
from VIEWS.RegisterWindow import Ui_MainWindow as Ui_RegisterWindow
from VIEWS.ModifyWindow import Ui_MainWindow as Ui_ModifyWindow
from VIEWS.UpdateMemb import Ui_MainWindow as Ui_UpdateMembWindow
from VIEWS.DeleteWindow import Ui_MainWindow as Ui_DeleteWindow
from VIEWS.RegisterEmployed import Ui_MainWindow as Ui_RegisterEmployedWindow
from VIEWS.ModifyEmployed import Ui_MainWindow as Ui_ModifyEmployedWindow
from VIEWS.DeleteEmployed import Ui_MainWindow as Ui_DeleteEmployedWindow
from VIEWS.RegisterPrestamo import Ui_MainWindow as Ui_RegisterPrestamo
from VIEWS.RegisterInventario import Ui_MainWindow as Ui_RegisterInventario
from VIEWS.ModifyInventario import Ui_MainWindow as Ui_ModifyInventario
from VIEWS.DeleteInventario import Ui_MainWindow as Ui_DeleteInventario


from MODELS.persona import Persona
from MODELS.empleado import Empleado
from MODELS.cliente import Cliente
from MODELS.membresia import Membresia
from MODELS.pago import Pago
from MODELS.inventario import Inventario
from MODELS.prestamo_equipo import PrestamoEquipo

tiempoDeEspera = 8000

# ========== CONFIGURACIÓN DE PRECIOS DE MEMBRESÍAS ==========
PRECIOS_MEMBRESIAS = {
    "Visitante": 50.00,
    "Semanal": 150.00,
    "Mensual": 400.00,
    "Anual": 4500.00
}

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
        
        self.registro_empleado_window = None
        self.modify_empleado_window = None
        self.delete_empleado_window = None
        self.registro_cliente_window = None
        self.modify_window = None
        self.update_memb_window = None
        self.delete_window = None
        self.registro_prestamo_window = None
        self.registro_inventario_window = None
        self.modify_inventario_window = None
        self.delete_inventario_window = None
        
        self.configurar_conexiones()
        
        self.setWindowTitle("Gym Soft - Sistema de Gestión")
        self.configurar_interfaz_empleado()
        
        self.cargar_clientes()
        self.cargar_empleados()
        
        self.ui.stackedWidget.currentChanged.connect(self.cargar_datos_pagina)
    
    def configurar_conexiones(self):
        self.ui.pb_modificarClient.clicked.connect(self.abrir_modificar_cliente)
        self.ui.pb_actualizarMemb.clicked.connect(self.abrir_actualizar_membresia)
        self.ui.pb_eliminarClient.clicked.connect(self.abrir_eliminar_cliente)

        self.ui.pb_addEmpleado.clicked.connect(self.abrir_registro_empleado)
        self.ui.pb_modificarEmpleados.clicked.connect(self.abrir_modificar_empleado)
        self.ui.pb_eliminarEmpleados.clicked.connect(self.abrir_eliminar_empleado)
        
        self.ui.pb_buscarElemento.clicked.connect(self.buscar_elemento_prestamo)
        self.ui.le_codigoPrestamo.returnPressed.connect(self.buscar_elemento_prestamo)
        self.ui.pb_registrarPrestamo.clicked.connect(self.abrir_registro_prestamo)
        self.ui.pb_addElemento.clicked.connect(self.abrir_registro_inventario)
        self.ui.pb_modificarElemento.clicked.connect(self.abrir_modificar_inventario)
        self.ui.pb_eliminarElemento.clicked.connect(self.abrir_eliminar_inventario)

        self.ui.btn_registrarAs.clicked.connect(self.ir_a_registro_asistencia_desde_principal)
        self.ui.bt_aceptarAsistencia.clicked.connect(self.registrar_asistencia_integrada)
        self.ui.le_codigoAsistencia.returnPressed.connect(self.registrar_asistencia_integrada)

        self.ui.bt_cerrarSe.clicked.connect(self.cerrar_sesion)
        self.ui.pb_addCliente.clicked.connect(self.abrir_registro_cliente)
        self.ui.pb_buscarClientAsistencia.clicked.connect(self.buscar_asistencias_cliente)
        self.ui.le_codigoClienteBuscarAsistencia.returnPressed.connect(self.buscar_asistencias_cliente)

        self.timer_asistencia = QTimer()
        self.timer_asistencia.setSingleShot(True)
        self.timer_asistencia.timeout.connect(self.restaurar_interfaz_asistencia)

    def abrir_registro_cliente(self):
        try:
            self.registro_cliente_window = RegisterWindow(self.gym_controller, self, self.empleado)
            self.registro_cliente_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario: {str(e)}")
    
    def abrir_modificar_cliente(self):
        try:
            if self.modify_window is not None and self.modify_window.isVisible():
                self.modify_window.raise_()
                self.modify_window.activateWindow()
                return
                
            self.modify_window = ModifyWindow(self.gym_controller, self)
            self.modify_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de modificación: {str(e)}")

    def abrir_actualizar_membresia(self):
        try:
            if self.update_memb_window is not None and self.update_memb_window.isVisible():
                self.update_memb_window.raise_()
                self.update_memb_window.activateWindow()
                return
                
            self.update_memb_window = UpdateMembWindow(self.gym_controller, self, self.empleado)
            self.update_memb_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de actualización de membresía: {str(e)}")

    def abrir_eliminar_cliente(self):
        try:
            if self.delete_window is not None and self.delete_window.isVisible():
                self.delete_window.raise_()
                self.delete_window.activateWindow()
                return
                
            self.delete_window = DeleteWindow(self.gym_controller, self)
            self.delete_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de eliminación: {str(e)}")

    def abrir_registro_empleado(self):
        try:
            # VERIFICAR SI LA VENTANA YA ESTÁ ABIERTA
            if self.registro_empleado_window is not None and self.registro_empleado_window.isVisible():
                self.registro_empleado_window.raise_()
                self.registro_empleado_window.activateWindow()
                return
                
            self.registro_empleado_window = RegisterEmployedWindow(self.gym_controller, self)
            self.registro_empleado_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario: {str(e)}")
    
    def abrir_modificar_empleado(self):
        try:
            if self.modify_empleado_window is not None and self.modify_empleado_window.isVisible():
                self.modify_empleado_window.raise_()
                self.modify_empleado_window.activateWindow()
                return
                
            self.modify_empleado_window = ModifyEmployedWindow(self.gym_controller, self)
            self.modify_empleado_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de modificación: {str(e)}")

    def abrir_eliminar_empleado(self):
        try:
            if self.delete_empleado_window is not None and self.delete_empleado_window.isVisible():
                self.delete_empleado_window.raise_()
                self.delete_empleado_window.activateWindow()
                return
                
            self.delete_empleado_window = DeleteEmployedWindow(self.gym_controller, self)
            self.delete_empleado_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de eliminación: {str(e)}")

    def configurar_interfaz_empleado(self):
        print(f"Empleado logueado: {self.empleado.persona.nombre_completo}")
        titulo_actual = self.windowTitle()
        self.setWindowTitle(f"{titulo_actual} - {self.empleado.persona.nombre_completo}")

    def cargar_clientes(self):
        try:
            clientes = self.gym_controller.obtener_clientes()
            
            self.ui.tb_clientesRegistrados.setRowCount(len(clientes))
            
            for row, cliente in enumerate(clientes):
                # Obtener membresía activa
                membresia_activa = self.gym_controller.obtener_membresia_activa_cliente(cliente.cod_cli)
                
                # Datos básicos del cliente
                self.ui.tb_clientesRegistrados.setItem(row, 0, QTableWidgetItem(str(cliente.cod_cli)))
                self.ui.tb_clientesRegistrados.setItem(row, 1, QTableWidgetItem(cliente.persona.nombre_completo))
                self.ui.tb_clientesRegistrados.setItem(row, 2, QTableWidgetItem(str(cliente.persona.edad)))
                self.ui.tb_clientesRegistrados.setItem(row, 3, QTableWidgetItem(cliente.genero))
                self.ui.tb_clientesRegistrados.setItem(row, 4, QTableWidgetItem(cliente.persona.email))
                self.ui.tb_clientesRegistrados.setItem(row, 5, QTableWidgetItem(cliente.persona.telefono or ""))
                self.ui.tb_clientesRegistrados.setItem(row, 6, QTableWidgetItem(cliente.fecha_nac.strftime("%Y-%m-%d") if cliente.fecha_nac else ""))
                self.ui.tb_clientesRegistrados.setItem(row, 7, QTableWidgetItem(cliente.fecha_inscri.strftime("%Y-%m-%d %H:%M") if cliente.fecha_inscri else ""))
                
                if membresia_activa:
                    self.ui.tb_clientesRegistrados.setItem(row, 8, QTableWidgetItem(str(membresia_activa.cod_mem)))
                    self.ui.tb_clientesRegistrados.setItem(row, 9, QTableWidgetItem(membresia_activa.tipo))
                    self.ui.tb_clientesRegistrados.setItem(row, 10, QTableWidgetItem(membresia_activa.fecha_inicio.strftime("%Y-%m-%d %H:%M")))
                    self.ui.tb_clientesRegistrados.setItem(row, 11, QTableWidgetItem(membresia_activa.fecha_venc.strftime("%Y-%m-%d %H:%M")))
                    
                    if hasattr(membresia_activa, 'dias_validez') and membresia_activa.dias_validez is not None:
                        dias_validez = str(membresia_activa.dias_validez)
                    else:
                        if membresia_activa.fecha_inicio and membresia_activa.fecha_venc:
                            dias_validez = str((membresia_activa.fecha_venc - membresia_activa.fecha_inicio).days)
                        else:
                            dias_validez = "N/A"
                    
                    self.ui.tb_clientesRegistrados.setItem(row, 12, QTableWidgetItem(dias_validez))
                    
                    from datetime import datetime
                    estado_mostrar = membresia_activa.estado
                    
                    if (membresia_activa.estado == 'Activa' and 
                        membresia_activa.fecha_venc and 
                        membresia_activa.fecha_venc < datetime.now()):
                        estado_mostrar = "Expirada"
                    
                    self.ui.tb_clientesRegistrados.setItem(row, 13, QTableWidgetItem(estado_mostrar))
                else:
                    self.ui.tb_clientesRegistrados.setItem(row, 8, QTableWidgetItem("N/A"))
                    self.ui.tb_clientesRegistrados.setItem(row, 9, QTableWidgetItem("Sin membresía"))
                    self.ui.tb_clientesRegistrados.setItem(row, 10, QTableWidgetItem("N/A"))
                    self.ui.tb_clientesRegistrados.setItem(row, 11, QTableWidgetItem("N/A"))
                    self.ui.tb_clientesRegistrados.setItem(row, 12, QTableWidgetItem("N/A"))
                    self.ui.tb_clientesRegistrados.setItem(row, 13, QTableWidgetItem("N/A"))
            
            self.ui.lb_totalClientes.setText(f"Total de Clientes: {len(clientes)}")
            
            self.ui.tb_clientesRegistrados.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error al cargar clientes: {e}")
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los clientes: {str(e)}")
    
    def cargar_empleados(self):
        try:
            empleados = self.gym_controller.obtener_empleados()
            
            self.ui.tb_empleados.setRowCount(len(empleados))
            
            for row, empleado in enumerate(empleados):
                self.ui.tb_empleados.setItem(row, 0, QTableWidgetItem(str(empleado.cod_emple)))
                self.ui.tb_empleados.setItem(row, 1, QTableWidgetItem(empleado.persona.nombre_completo))
                self.ui.tb_empleados.setItem(row, 2, QTableWidgetItem(str(empleado.persona.edad)))
                self.ui.tb_empleados.setItem(row, 3, QTableWidgetItem(empleado.persona.email))
                self.ui.tb_empleados.setItem(row, 4, QTableWidgetItem(empleado.persona.telefono or ""))
                self.ui.tb_empleados.setItem(row, 5, QTableWidgetItem(empleado.fecha_contrat.strftime("%Y-%m-%d") if empleado.fecha_contrat else ""))
                self.ui.tb_empleados.setItem(row, 6, QTableWidgetItem(f"${empleado.salario:.2f}" if empleado.salario else ""))
                self.ui.tb_empleados.setItem(row, 7, QTableWidgetItem(empleado.rol))
            
            self.ui.lb_empleadosRegistrados.setText(f"EMPLEADOS REGISTRADOS: {len(empleados)}")
            self.ui.lb_totalEmpleados.setText(f"Total de Empleados: {len(empleados)}")
            
            self.ui.tb_empleados.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error al cargar empleados: {e}")
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los empleados: {str(e)}")

    def buscar_asistencias_cliente(self):
        try:
            codigo_texto = self.ui.le_codigoClienteBuscarAsistencia.text().strip()
            if not codigo_texto:
                QMessageBox.warning(self, "Advertencia", "Por favor ingrese un código de cliente")
                return
            
            cliente_id = int(codigo_texto)
            
            cliente = self.gym_controller.buscar_cliente_por_codigo(cliente_id)
            if not cliente:
                QMessageBox.warning(self, "Cliente no encontrado", "El código de cliente no existe")
                return
            
            asistencias = self.gym_controller.obtener_asistencias_cliente(cliente_id)
            
            self.ui.tb_asistencias.setRowCount(0)
            
            for row, asistencia in enumerate(asistencias):
                self.ui.tb_asistencias.insertRow(row)
                self.ui.tb_asistencias.setItem(row, 0, QTableWidgetItem(str(asistencia.id)))
                self.ui.tb_asistencias.setItem(row, 1, QTableWidgetItem(str(asistencia.cliente.cod_cli)))
                self.ui.tb_asistencias.setItem(row, 2, QTableWidgetItem(asistencia.sede.nombre))
                self.ui.tb_asistencias.setItem(row, 3, QTableWidgetItem(asistencia.fecha.strftime("%Y-%m-%d")))
                self.ui.tb_asistencias.setItem(row, 4, QTableWidgetItem(str(asistencia.hora_entrada)))
                self.ui.tb_asistencias.setItem(row, 5, QTableWidgetItem(str(asistencia.hora_salida) if asistencia.hora_salida else "En curso"))
            
            self.ui.tb_asistencias.resizeColumnsToContents()
            
            QMessageBox.information(self, "Búsqueda completada", 
                                   f"Se encontraron {len(asistencias)} asistencias para el cliente {cliente_id}")
            
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las asistencias: {str(e)}")
    
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

    def cargar_datos_pagina(self, index):
        try:
            pagina_actual = self.ui.stackedWidget.widget(index)
            
            if pagina_actual == self.ui.page_4:
                self.cargar_inventario()
                self.cargar_prestamos()
            elif pagina_actual == self.ui.page_2:
                self.cargar_clientes()
            elif pagina_actual == self.ui.page_3:
                self.cargar_empleados()
        except Exception as e:
            print(f"Error al cargar datos de página: {e}")


    def cargar_inventario(self):
        try:
            inventarios = self.gym_controller.obtener_inventario_completo()
            
            self.ui.tb_elementosRegistrados.setRowCount(len(inventarios))
            
            for row, inventario in enumerate(inventarios):
                self.ui.tb_elementosRegistrados.setItem(row, 0, QTableWidgetItem(str(inventario.codigo_barras)))
                self.ui.tb_elementosRegistrados.setItem(row, 1, QTableWidgetItem(inventario.sede.nombre if inventario.sede else "N/A"))
                self.ui.tb_elementosRegistrados.setItem(row, 2, QTableWidgetItem(inventario.nombre))
                self.ui.tb_elementosRegistrados.setItem(row, 3, QTableWidgetItem(inventario.categoria))
                self.ui.tb_elementosRegistrados.setItem(row, 4, QTableWidgetItem(inventario.descripcion or ""))
                self.ui.tb_elementosRegistrados.setItem(row, 5, QTableWidgetItem(f"${inventario.precio_venta:.2f}"))
                self.ui.tb_elementosRegistrados.setItem(row, 6, QTableWidgetItem(str(inventario.cantidad)))
                self.ui.tb_elementosRegistrados.setItem(row, 7, QTableWidgetItem(inventario.fecha_caducidad.strftime("%Y-%m-%d") if inventario.fecha_caducidad else "N/A"))
                self.ui.tb_elementosRegistrados.setItem(row, 8, QTableWidgetItem("Sí" if inventario.activo else "No"))
            
            self.ui.lb_totalClientes_2.setText(f"Elementos en inventario: {len(inventarios)}")
            
            self.ui.tb_elementosRegistrados.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error al cargar inventario: {e}")
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los elementos de inventario: {str(e)}")

    def cargar_prestamos(self):
        try:
            prestamos = self.gym_controller.obtener_prestamos_completos()
            
            self.ui.tb_prestamos.setRowCount(len(prestamos))
            
            for row, prestamo in enumerate(prestamos):
                self.ui.tb_prestamos.setItem(row, 0, QTableWidgetItem(str(prestamo.id)))
                self.ui.tb_prestamos.setItem(row, 1, QTableWidgetItem(str(prestamo.equipo.codigo_barras)))
                self.ui.tb_prestamos.setItem(row, 2, QTableWidgetItem(str(prestamo.cliente.cod_cli)))
                self.ui.tb_prestamos.setItem(row, 3, QTableWidgetItem(prestamo.fecha_prestamo.strftime("%Y-%m-%d %H:%M")))
                self.ui.tb_prestamos.setItem(row, 4, QTableWidgetItem(prestamo.fecha_devolucion.strftime("%Y-%m-%d %H:%M") if prestamo.fecha_devolucion else "Pendiente"))
                self.ui.tb_prestamos.setItem(row, 5, QTableWidgetItem(prestamo.estado))
                self.ui.tb_prestamos.setItem(row, 6, QTableWidgetItem(prestamo.observaciones or ""))
            
            self.ui.tb_prestamos.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error al cargar préstamos: {e}")
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los préstamos: {str(e)}")

    def buscar_elemento_prestamo(self):
        try:
            codigo_texto = self.ui.le_codigoPrestamo.text().strip()
            if not codigo_texto:
                self.cargar_prestamos()
                return
            
            codigo_elemento = int(codigo_texto)
            prestamos = self.gym_controller.buscar_prestamos_por_elemento(codigo_elemento)
            
            self.ui.tb_prestamos.setRowCount(len(prestamos))
            
            for row, prestamo in enumerate(prestamos):
                self.ui.tb_prestamos.setItem(row, 0, QTableWidgetItem(str(prestamo.id)))
                self.ui.tb_prestamos.setItem(row, 1, QTableWidgetItem(str(prestamo.equipo.codigo_barras)))
                self.ui.tb_prestamos.setItem(row, 2, QTableWidgetItem(str(prestamo.cliente.cod_cli)))
                self.ui.tb_prestamos.setItem(row, 3, QTableWidgetItem(prestamo.fecha_prestamo.strftime("%Y-%m-%d %H:%M")))
                self.ui.tb_prestamos.setItem(row, 4, QTableWidgetItem(prestamo.fecha_devolucion.strftime("%Y-%m-%d %H:%M") if prestamo.fecha_devolucion else "Pendiente"))
                self.ui.tb_prestamos.setItem(row, 5, QTableWidgetItem(prestamo.estado))
                self.ui.tb_prestamos.setItem(row, 6, QTableWidgetItem(prestamo.observaciones or ""))
            
            QMessageBox.information(self, "Búsqueda completada", 
                                f"Se encontraron {len(prestamos)} préstamos para el elemento {codigo_elemento}")
            
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los préstamos: {str(e)}")

    def abrir_registro_prestamo(self):
        try:
            self.registro_prestamo_window = RegisterPrestamoWindow(self.gym_controller, self, self.empleado)
            self.registro_prestamo_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario de préstamo: {str(e)}")

    def abrir_registro_inventario(self):
        try:
            self.registro_inventario_window = RegisterInventarioWindow(self.gym_controller, self)
            self.registro_inventario_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario de inventario: {str(e)}")

    def registrar_asistencia_integrada(self):
        codigo_texto = self.ui.le_codigoAsistencia.text().strip()
        
        if not codigo_texto:
            QMessageBox.warning(self, "Error", "Por favor ingrese un código")
            return
        
        try:
            codigo = int(codigo_texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
            self.ui.le_codigoAsistencia.clear()
            self.ui.le_codigoAsistencia.setFocus()
            return
        
        cliente = self.gym_controller.buscar_cliente_por_codigo(codigo)
        
        if not cliente:
            QMessageBox.warning(self, "Error", "Cliente no encontrado")
            self.ui.le_codigoAsistencia.clear()
            self.ui.le_codigoAsistencia.setFocus()
            return
        
        membresia = self.gym_controller.obtener_membresia_activa_cliente(cliente.cod_cli)
        
        sede_id = cliente.sede_inscrito.id if cliente.sede_inscrito and cliente.sede_inscrito.id else 1
        resultado = self.gym_controller.registrar_asistencia_cliente(cliente.cod_cli, sede_id)
        
        if resultado['success']:
            mensaje_tipo = "ENTRADA" if resultado['tipo'] == 'entrada' else "SALIDA"
            QMessageBox.information(self, "Éxito", f"{mensaje_tipo} registrada\n{resultado['mensaje']}")
            self.mostrar_informacion_cliente_asistencia(cliente, membresia)
        else:
            QMessageBox.warning(self, "Error", resultado['mensaje'])

    def mostrar_informacion_cliente_asistencia(self, cliente, membresia):
        nombre_completo = f"{cliente.persona.nombre} {cliente.persona.apellido_pa} {cliente.persona.apellido_ma}"
        self.ui.lb_nombreAs.setText(nombre_completo)
        
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
        
        self.ui.lb_infoAs.setText(info_texto)
        
        self.ui.frame_superiorAs.setMaximumSize(16777215, 0)
        self.ui.frame_inferior_2.setMaximumSize(16777215, 16777215)
        self.timer_asistencia.start(tiempoDeEspera)

    def restaurar_interfaz_asistencia(self):
        self.ui.frame_superiorAs.setMaximumSize(16777215, 180)
        self.ui.frame_inferior_2.setMaximumSize(16777215, 0)
        self.ui.lb_nombreAs.setText("Nombre")
        self.ui.lb_infoAs.setText("Información")
        self.ui.le_codigoAsistencia.clear()
        self.ui.le_codigoAsistencia.setFocus()

    def abrir_modificar_inventario(self):
        try:
            if (hasattr(self, 'modify_inventario_window') and 
                self.modify_inventario_window is not None and 
                self.modify_inventario_window.isVisible()):
                self.modify_inventario_window.raise_()
                self.modify_inventario_window.activateWindow()
                return
                
            self.modify_inventario_window = ModifyInventarioWindow(self.gym_controller, self)
            self.modify_inventario_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario de modificación: {str(e)}")

    def abrir_eliminar_inventario(self):
        try:
            if (hasattr(self, 'delete_inventario_window') and 
                self.delete_inventario_window is not None and 
                self.delete_inventario_window.isVisible()):
                self.delete_inventario_window.raise_()
                self.delete_inventario_window.activateWindow()
                return
                
            self.delete_inventario_window = DeleteInventarioWindow(self.gym_controller, self)
            self.delete_inventario_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario de eliminación: {str(e)}")

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

class RegisterWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None, empleado=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.empleado = empleado
        self.ui = Ui_RegisterWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Registrar Nuevo Cliente")
        self.setFixedSize(self.width(), self.height())
        
        fecha_18_anios = date.today() - timedelta(days=365*18)
        self.ui.de_fechaNac.setDate(fecha_18_anios)
        self.ui.de_fechaNac.setMaximumDate(date.today())
        
        self.ui.cb_tipoMemb.currentTextChanged.connect(self.actualizar_precio_y_fechas)
        self.ui.btnPagar.clicked.connect(self.registrar_cliente)
        
        self.actualizar_precio_y_fechas()
        
        self.ui.rb_masculino.setChecked(True)
        
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
    
    def actualizar_precio_y_fechas(self):
        tipo_membresia = self.ui.cb_tipoMemb.currentText()
        precio = PRECIOS_MEMBRESIAS.get(tipo_membresia, 0.00)
        self.ui.lb_precio.setText(f"${precio:.2f}")
        
        fecha_inicio = datetime.now()
        fecha_vencimiento = fecha_inicio
        
        if tipo_membresia == "Visitante":
            fecha_vencimiento = fecha_inicio + timedelta(days=1)
        elif tipo_membresia == "Semanal":
            fecha_vencimiento = fecha_inicio + timedelta(weeks=1)
        elif tipo_membresia == "Mensual":
            fecha_vencimiento = fecha_inicio + timedelta(days=30)
        elif tipo_membresia == "Anual":
            fecha_vencimiento = fecha_inicio + timedelta(days=365)
        
        self.ui.lb_fechaInicio.setText(fecha_inicio.strftime("%Y-%m-%d %H:%M"))
        self.ui.lb_fechaVenc.setText(fecha_vencimiento.strftime("%Y-%m-%d %H:%M"))
    
    def registrar_cliente(self):
        try:
            if not self.validar_campos():
                return
            
            nombre = self.ui.le_nombre.text().strip()
            apellido_pa = self.ui.le_apellidoPA.text().strip()
            apellido_ma = self.ui.le_apellidoMA.text().strip()
            genero = "Masculino" if self.ui.rb_masculino.isChecked() else "Femenino"
            fecha_nac = self.ui.de_fechaNac.date().toPyDate()
            email = self.ui.le_email.text().strip()
            telefono = self.ui.le_telefono.text().strip()
            
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            
            persona = Persona(
                nombre=nombre,
                apellido_pa=apellido_pa,
                apellido_ma=apellido_ma,
                edad=edad,
                email=email,
                telefono=telefono
            )
            
            sedes = self.gym_controller.obtener_sedes()
            sede_inscrito = sedes[0] if sedes else None
            
            cliente = Cliente(
                persona=persona,
                sede_inscrito=sede_inscrito,
                genero=genero,
                fecha_nac=fecha_nac,
                fecha_inscri=datetime.now()
            )
            
            cliente_id = self.gym_controller.crear_cliente(cliente)
            if not cliente_id:
                QMessageBox.critical(self, "Error", "No se pudo registrar el cliente")
                return
            
            cliente.cod_cli = cliente_id
            
            tipo_membresia = self.ui.cb_tipoMemb.currentText()
            precio = float(self.ui.lb_precio.text().replace('$', ''))
            fecha_inicio = datetime.now()
            
            if tipo_membresia == "Visitante":
                fecha_venc = fecha_inicio + timedelta(days=1)
            elif tipo_membresia == "Semanal":
                fecha_venc = fecha_inicio + timedelta(weeks=1)
            elif tipo_membresia == "Mensual":
                fecha_venc = fecha_inicio + timedelta(days=30)
            elif tipo_membresia == "Anual":
                fecha_venc = fecha_inicio + timedelta(days=365)
            
            membresia = Membresia(
                cliente=cliente,
                tipo=tipo_membresia,
                precio=precio,
                fecha_inicio=fecha_inicio,
                fecha_venc=fecha_venc,
                estado='Activa'
            )
            
            membresia_id = self.gym_controller.crear_membresia(membresia)
            if not membresia_id:
                QMessageBox.critical(self, "Error", "No se pudo registrar la membresía")
                return
            
            membresia.cod_mem = membresia_id
            
            pago = Pago(
                cliente=cliente,
                empleado=self.empleado,
                membresia=membresia,
                monto=precio,
                monto_pagado=precio,
                metodo='Efectivo',
                fecha_pago=datetime.now(),
                concepto=f"Membresía {tipo_membresia} - {nombre} {apellido_pa}",
                estado='Completado',
                referencia=f"MEM{membresia_id:06d}"
            )
            
            if self.gym_controller.registrar_pago(pago):
                QMessageBox.information(self, "Éxito", 
                    f"Cliente registrado exitosamente!\n"
                    f"Código de cliente: {cliente_id}\n"
                    f"Membresía: {tipo_membresia}\n"
                    f"Total pagado: ${precio:.2f}")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el pago")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar cliente: {str(e)}")
    
    def validar_campos(self):
        campos_obligatorios = [
            (self.ui.le_nombre, "Nombre"),
            (self.ui.le_apellidoPA, "Apellido Paterno"),
            (self.ui.le_apellidoMA, "Apellido Materno"),
            (self.ui.le_email, "Email"),
            (self.ui.le_telefono, "Teléfono")
        ]
        
        for campo, nombre in campos_obligatorios:
            if not campo.text().strip():
                QMessageBox.warning(self, "Campo requerido", 
                                           f"El campo {nombre} es obligatorio")
                campo.setFocus()
                return False
        
        email = self.ui.le_email.text().strip()
        if '@' not in email or '.' not in email:
            QMessageBox.warning(self, "Email inválido", 
                                       "Por favor ingrese un email válido")
            self.ui.le_email.setFocus()
            return False
            
        fecha_nac = self.ui.de_fechaNac.date().toPyDate()
        edad_minima = date.today() - timedelta(days=365*15)
        if fecha_nac > edad_minima:
            QMessageBox.warning(self, "Edad inválida", 
                                       "El cliente debe tener al menos 15 años")
            self.ui.de_fechaNac.setFocus()
            return False
            
        return True
    
    def closeEvent(self, event):
        if hasattr(self.parent(), 'cargar_clientes'):
            self.parent().cargar_clientes()
        event.accept()

class ModifyWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.cliente_actual = None
        self.ui = Ui_ModifyWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Modificar Cliente")
        self.setFixedSize(self.width(), self.height())
        
        self.ui.pb_buscar.clicked.connect(self.buscar_cliente)
        self.ui.btnModificar.clicked.connect(self.modificar_cliente)
        
        self.ui.groupBox.setEnabled(False)
        self.ui.btnModificar.setEnabled(False)
    
    def buscar_cliente(self):
        try:
            codigo_texto = self.ui.le_codigoCliente.text().strip()
            if not codigo_texto:
                QMessageBox.warning(self, "Advertencia", "Por favor ingrese un código de cliente")
                return
            
            cliente_id = int(codigo_texto)
            cliente = self.gym_controller.buscar_cliente_por_codigo(cliente_id)
            
            if not cliente:
                QMessageBox.warning(self, "Cliente no encontrado", "El código de cliente no existe")
                return
            
            self.cliente_actual = cliente
            self.mostrar_datos_cliente(cliente)
            self.ui.groupBox.setEnabled(True)
            self.ui.btnModificar.setEnabled(True)
            
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar cliente: {str(e)}")
    
    def mostrar_datos_cliente(self, cliente):
        self.ui.le_nombre.setText(cliente.persona.nombre)
        self.ui.le_apellidoPA.setText(cliente.persona.apellido_pa)
        self.ui.le_apellidoMA.setText(cliente.persona.apellido_ma)
        self.ui.le_email.setText(cliente.persona.email)
        self.ui.le_telefono.setText(cliente.persona.telefono or "")
    
    def modificar_cliente(self):
        try:
            if not self.cliente_actual:
                QMessageBox.warning(self, "Advertencia", "No hay cliente seleccionado")
                return
            
            nombre = self.ui.le_nombre.text().strip()
            apellido_pa = self.ui.le_apellidoPA.text().strip()
            apellido_ma = self.ui.le_apellidoMA.text().strip()
            email = self.ui.le_email.text().strip()
            telefono = self.ui.le_telefono.text().strip()
            
            if not nombre or not apellido_pa or not apellido_ma or not email:
                QMessageBox.warning(self, "Campos requeridos", "Nombre, apellidos y email son obligatorios")
                return
            
            self.cliente_actual.persona.nombre = nombre
            self.cliente_actual.persona.apellido_pa = apellido_pa
            self.cliente_actual.persona.apellido_ma = apellido_ma
            self.cliente_actual.persona.email = email
            self.cliente_actual.persona.telefono = telefono

            if self.actualizar_cliente_en_db(self.cliente_actual):
                QMessageBox.information(self, "Éxito", "Cliente modificado correctamente")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "No se pudo modificar el cliente")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar cliente: {str(e)}")
    
    def actualizar_cliente_en_db(self, cliente):
        query_persona = """
        UPDATE Persona 
        SET Nombre = %s, ApellidoPA = %s, ApellidoMA = %s, Email = %s, Telefono = %s
        WHERE ID = %s
        """
        return self.gym_controller.db.execute_query(query_persona, (
            cliente.persona.nombre,
            cliente.persona.apellido_pa,
            cliente.persona.apellido_ma,
            cliente.persona.email,
            cliente.persona.telefono,
            cliente.persona.id
        ))
    
class UpdateMembWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None, empleado=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.empleado = empleado
        self.cliente_actual = None
        self.membresia_actual = None
        self.ui = Ui_UpdateMembWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Gestionar Membresía")
        self.setFixedSize(self.width(), self.height())
        
        self.ui.pb_pagar.clicked.connect(self.buscar_cliente)
        self.ui.cb_tipoMemb.currentTextChanged.connect(self.actualizar_precio_y_fechas)
        self.ui.btn_pagar.clicked.connect(self.gestionar_membresia)
        
        # Inicializar precios y fechas
        self.actualizar_precio_y_fechas()
        
        self.ui.groupBox.setEnabled(False)
        self.ui.btn_pagar.setEnabled(False)
    
    def buscar_cliente(self):
        try:
            codigo_texto = self.ui.le_codigoCliente.text().strip()
            if not codigo_texto:
                QMessageBox.warning(self, "Advertencia", "Por favor ingrese un código de cliente")
                return
            
            cliente_id = int(codigo_texto)
            cliente = self.gym_controller.buscar_cliente_por_codigo(cliente_id)
            
            if not cliente:
                QMessageBox.warning(self, "Cliente no encontrado", "El código de cliente no existe")
                return
            
            self.cliente_actual = cliente
            self.membresia_actual = self.gym_controller.obtener_membresia_activa_cliente(cliente_id)
            
            if not self.membresia_actual:
                # Cliente sin membresía - permitir crear una nueva
                self.ui.btn_pagar.setText("Crear Membresía")
                self.ui.groupBox.setTitle("Crear Nueva Membresía")
                self.limpiar_formulario()
                QMessageBox.information(self, "Cliente sin membresía", 
                                      "Este cliente no tiene membresía activa. Puede crear una nueva membresía.")
            else:
                self.ui.btn_pagar.setText("Actualizar Membresía")
                self.ui.groupBox.setTitle("Actualizar Membresía Existente")
                self.mostrar_datos_membresia(self.membresia_actual)
                QMessageBox.information(self, "Membresía encontrada", 
                                      f"Cliente tiene membresía {self.membresia_actual.tipo} - Estado: {self.membresia_actual.estado}")
            
            self.ui.groupBox.setEnabled(True)
            self.ui.btn_pagar.setEnabled(True)
            
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar cliente: {str(e)}")
    
    def limpiar_formulario(self):
        self.ui.cb_tipoMemb.setCurrentText("Mensual")
        self.ui.cb_estadoMemb.setCurrentText("Activa")
        self.actualizar_precio_y_fechas()
    
    def mostrar_datos_membresia(self, membresia):
        self.ui.cb_tipoMemb.setCurrentText(membresia.tipo)
        self.ui.cb_estadoMemb.setCurrentText(membresia.estado)
        
        self.ui.lb_precioValue.setText(f"${membresia.precio:.2f}")
        
        if membresia.fecha_inicio:
            self.ui.lb_fechaInicioValue.setText(membresia.fecha_inicio.strftime("%Y-%m-%d %H:%M"))
        if membresia.fecha_venc:
            self.ui.lb_fechaVencValue.setText(membresia.fecha_venc.strftime("%Y-%m-%d %H:%M"))
    
    def actualizar_precio_y_fechas(self):
        tipo_membresia = self.ui.cb_tipoMemb.currentText()
        precio = PRECIOS_MEMBRESIAS.get(tipo_membresia, 0.00)
        
        if not self.membresia_actual:
            self.ui.lb_precioValue.setText(f"${precio:.2f}")
        
        fecha_inicio = datetime.now()
        fecha_vencimiento = fecha_inicio
        
        if tipo_membresia == "Visitante":
            fecha_vencimiento = fecha_inicio + timedelta(days=1)
        elif tipo_membresia == "Semanal":
            fecha_vencimiento = fecha_inicio + timedelta(weeks=1)
        elif tipo_membresia == "Mensual":
            fecha_vencimiento = fecha_inicio + timedelta(days=30)
        elif tipo_membresia == "Anual":
            fecha_vencimiento = fecha_inicio + timedelta(days=365)
        
        if not self.membresia_actual:
            self.ui.lb_fechaInicioValue.setText(fecha_inicio.strftime("%Y-%m-%d %H:%M"))
            self.ui.lb_fechaVencValue.setText(fecha_vencimiento.strftime("%Y-%m-%d %H:%M"))
    
    def gestionar_membresia(self):
        try:
            if not self.cliente_actual:
                QMessageBox.warning(self, "Advertencia", "No hay cliente seleccionado")
                return
            
            tipo_membresia = self.ui.cb_tipoMemb.currentText()
            estado = self.ui.cb_estadoMemb.currentText()
            
            if self.membresia_actual:
                precio = float(self.ui.lb_precioValue.text().replace('$', ''))
                
                fecha_inicio = self.membresia_actual.fecha_inicio
                fecha_venc = self.membresia_actual.fecha_venc
                
                if tipo_membresia != self.membresia_actual.tipo:
                    fecha_inicio = datetime.now()
                    if tipo_membresia == "Visitante":
                        fecha_venc = fecha_inicio + timedelta(days=1)
                    elif tipo_membresia == "Semanal":
                        fecha_venc = fecha_inicio + timedelta(weeks=1)
                    elif tipo_membresia == "Mensual":
                        fecha_venc = fecha_inicio + timedelta(days=30)
                    elif tipo_membresia == "Anual":
                        fecha_venc = fecha_inicio + timedelta(days=365)
                
                query = """
                UPDATE Membresia 
                SET Tipo = %s, Precio = %s, FechaInicio = %s, FechaVenc = %s, Estado = %s
                WHERE CodMem = %s
                """
                if self.gym_controller.db.execute_query(query, (
                    tipo_membresia,
                    precio,
                    fecha_inicio,
                    fecha_venc,
                    estado,
                    self.membresia_actual.cod_mem
                )):
                    QMessageBox.information(self, "Éxito", "Membresía actualizada correctamente")
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo actualizar la membresía")
            
            else:
                precio = PRECIOS_MEMBRESIAS.get(tipo_membresia, 0.00)
                fecha_inicio = datetime.now()
                
                if tipo_membresia == "Visitante":
                    fecha_venc = fecha_inicio + timedelta(days=1)
                elif tipo_membresia == "Semanal":
                    fecha_venc = fecha_inicio + timedelta(weeks=1)
                elif tipo_membresia == "Mensual":
                    fecha_venc = fecha_inicio + timedelta(days=30)
                elif tipo_membresia == "Anual":
                    fecha_venc = fecha_inicio + timedelta(days=365)
                
                membresia = Membresia(
                    cliente=self.cliente_actual,
                    tipo=tipo_membresia,
                    precio=precio,
                    fecha_inicio=fecha_inicio,
                    fecha_venc=fecha_venc,
                    estado=estado
                )
                
                membresia_id = self.gym_controller.crear_membresia(membresia)
                if not membresia_id:
                    QMessageBox.critical(self, "Error", "No se pudo crear la membresía")
                    return
                
                membresia.cod_mem = membresia_id
                
                pago = Pago(
                    cliente=self.cliente_actual,
                    empleado=self.empleado,
                    membresia=membresia,
                    monto=precio,
                    monto_pagado=precio,
                    metodo='Efectivo',
                    fecha_pago=datetime.now(),
                    concepto=f"Membresía {tipo_membresia} - {self.cliente_actual.persona.nombre} {self.cliente_actual.persona.apellido_pa}",
                    estado='Completado',
                    referencia=f"MEM{membresia_id:06d}"
                )
                
                if self.gym_controller.registrar_pago(pago):
                    QMessageBox.information(self, "Éxito", 
                        f"Membresía creada exitosamente!\n"
                        f"Tipo: {tipo_membresia}\n"
                        f"Total pagado: ${precio:.2f}")
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", "Membresía creada pero no se pudo registrar el pago")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al gestionar membresía: {str(e)}")
    
    def buscar_cliente(self):
        try:
            codigo_texto = self.ui.le_codigoCliente.text().strip()
            if not codigo_texto:
                QMessageBox.warning(self, "Advertencia", "Por favor ingrese un código de cliente")
                return
            
            cliente_id = int(codigo_texto)
            cliente = self.gym_controller.buscar_cliente_por_codigo(cliente_id)
            
            if not cliente:
                QMessageBox.warning(self, "Cliente no encontrado", "El código de cliente no existe")
                return
            
            self.cliente_actual = cliente
            self.membresia_actual = self.gym_controller.obtener_membresia_activa_cliente(cliente_id)
            
            if not self.membresia_actual:
                QMessageBox.warning(self, "Membresía no encontrada", "El cliente no tiene una membresía activa")
                return
            
            self.mostrar_datos_membresia(self.membresia_actual)
            self.ui.groupBox.setEnabled(True)
            self.ui.btn_pagar.setEnabled(True)
            
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar cliente: {str(e)}")
    
    def mostrar_datos_membresia(self, membresia):
        self.ui.cb_tipoMemb.setCurrentText(membresia.tipo)
        self.ui.cb_estadoMemb.setCurrentText(membresia.estado)
        self.actualizar_precio_y_fechas()
    
    def actualizar_precio_y_fechas(self):
        tipo_membresia = self.ui.cb_tipoMemb.currentText()
        precio = PRECIOS_MEMBRESIAS.get(tipo_membresia, 0.00)
        self.ui.lb_precioValue.setText(f"${precio:.2f}")
        
        fecha_inicio = datetime.now()
        fecha_vencimiento = fecha_inicio
        
        if tipo_membresia == "Visitante":
            fecha_vencimiento = fecha_inicio + timedelta(days=1)
        elif tipo_membresia == "Semanal":
            fecha_vencimiento = fecha_inicio + timedelta(weeks=1)
        elif tipo_membresia == "Mensual":
            fecha_vencimiento = fecha_inicio + timedelta(days=30)
        elif tipo_membresia == "Anual":
            fecha_vencimiento = fecha_inicio + timedelta(days=365)
        
        self.ui.lb_fechaInicioValue.setText(fecha_inicio.strftime("%Y-%m-%d %H:%M"))
        self.ui.lb_fechaVencValue.setText(fecha_vencimiento.strftime("%Y-%m-%d %H:%M"))
    
    def actualizar_membresia(self):
        try:
            if not self.membresia_actual:
                QMessageBox.warning(self, "Advertencia", "No hay membresía seleccionada")
                return
            
            tipo_membresia = self.ui.cb_tipoMemb.currentText()
            estado = self.ui.cb_estadoMemb.currentText()
            precio = PRECIOS_MEMBRESIAS.get(tipo_membresia, 0.00)
            fecha_inicio = datetime.now()
            
            if tipo_membresia == "Visitante":
                fecha_venc = fecha_inicio + timedelta(days=1)
            elif tipo_membresia == "Semanal":
                fecha_venc = fecha_inicio + timedelta(weeks=1)
            elif tipo_membresia == "Mensual":
                fecha_venc = fecha_inicio + timedelta(days=30)
            elif tipo_membresia == "Anual":
                fecha_venc = fecha_inicio + timedelta(days=365)
            
            query = """
            UPDATE Membresia 
            SET Tipo = %s, Precio = %s, FechaInicio = %s, FechaVenc = %s, Estado = %s
            WHERE CodMem = %s
            """
            if self.gym_controller.db.execute_query(query, (
                tipo_membresia,
                precio,
                fecha_inicio,
                fecha_venc,
                estado,
                self.membresia_actual.cod_mem
            )):
                QMessageBox.information(self, "Éxito", "Membresía actualizada correctamente")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar la membresía")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar membresía: {str(e)}")

class DeleteWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.parent = parent
        self.cliente_actual = None
        self.ui = Ui_DeleteWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Eliminar Cliente")
        self.setFixedSize(self.width(), self.height())

        self.ui.btnBuscar.clicked.connect(self.buscar_cliente)
        self.ui.btnEliminar.clicked.connect(self.eliminar_cliente)

        self.ui.groupDatos.setEnabled(False)
        self.ui.btnEliminar.setEnabled(False)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

    def buscar_cliente(self):
        try:
            codigo_texto = self.ui.le_codigoCliente.text().strip()
            if not codigo_texto:
                QMessageBox.warning(self, "Advertencia", "Por favor ingrese un código de cliente")
                return

            cliente_id = int(codigo_texto)
            cliente = self.gym_controller.buscar_cliente_por_codigo(cliente_id)
            
            if not cliente:
                QMessageBox.warning(self, "Cliente no encontrado", "El código de cliente no existe")
                return

            self.cliente_actual = cliente
            self.mostrar_datos_cliente(cliente)
            self.ui.groupDatos.setEnabled(True)
            self.ui.btnEliminar.setEnabled(True)

        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar cliente: {str(e)}")

    def mostrar_datos_cliente(self, cliente):
        self.ui.lblNombreValue.setText(cliente.persona.nombre_completo)
        self.ui.lb_edadValue.setText(str(cliente.persona.edad))
        self.ui.lblGeneroValue.setText(cliente.genero)
        self.ui.lb_emailValue.setText(cliente.persona.email)
        self.ui.lb_telefonoValue.setText(cliente.persona.telefono or "No proporcionado")
        self.ui.lblFechaNacValue.setText(cliente.fecha_nac.strftime("%Y-%m-%d") if cliente.fecha_nac else "N/A")
        self.ui.lb_fechaInscriValue.setText(cliente.fecha_inscri.strftime("%Y-%m-%d %H:%M") if cliente.fecha_inscri else "N/A")

    def eliminar_cliente(self):
        try:
            if not self.cliente_actual:
                QMessageBox.warning(self, "Advertencia", "No hay cliente seleccionado")
                return

            respuesta = QMessageBox.question(
                self,
                "Tipo de Eliminación",
                f"¿Cómo desea eliminar al cliente {self.cliente_actual.persona.nombre_completo}?\n\n"
                "• 'Sí' - Eliminación COMPLETA (borra todos los registros)\n"
                "• 'No' - Eliminación LÓGICA (solo marca como inactivo)\n"
                "• 'Cancelar' - No eliminar",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                confirmacion = QMessageBox.critical(
                    self,
                    "¡CONFIRMACIÓN DE ELIMINACIÓN!",
                    "¿ESTÁ ABSOLUTAMENTE SEGURO?\n\n"
                    "Esta acción:\n"
                    "• Eliminará TODOS los registros del cliente\n"
                    "• Borrará membresías, pagos, asistencias y préstamos\n"
                    "• NO SE PUEDE DESHACER\n\n"
                    "¿Continuar?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if confirmacion == QMessageBox.StandardButton.Yes:
                    if hasattr(self.gym_controller, 'eliminar_cliente_completo'):
                        exito = self.gym_controller.eliminar_cliente_completo(self.cliente_actual.cod_cli)
                    else:
                        exito = self.gym_controller.eliminar_cliente(self.cliente_actual.cod_cli)
                    
                    if exito:
                        QMessageBox.information(self, "Éxito", "Cliente eliminado completamente")
                        self.close()
                    else:
                        QMessageBox.critical(self, "Error", 
                                           "No se pudo eliminar el cliente completamente.\n"
                                           "Puede que tenga registros vinculados.\n"
                                           "Intente con eliminación lógica.")

            elif respuesta == QMessageBox.StandardButton.No:
                if hasattr(self.gym_controller, 'eliminar_cliente_logico'):
                    exito = self.gym_controller.eliminar_cliente_logico(self.cliente_actual.cod_cli)
                else:
                    query = "UPDATE Persona SET Activo = FALSE WHERE ID = %s"
                    exito = self.gym_controller.db.execute_query(query, (self.cliente_actual.persona.id,))

                if exito:
                    QMessageBox.information(self, "Éxito", "Cliente marcado como inactivo")
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo marcar el cliente como inactivo")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar cliente: {str(e)}")

    def closeEvent(self, event):
        if hasattr(self.parent, 'cargar_clientes'):
            self.parent.cargar_clientes()
        event.accept()

class RegisterEmployedWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.parent = parent
        self.ui = Ui_RegisterEmployedWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Registrar Empleado")
        self.setFixedSize(self.width(), self.height())
        
        self.ui.le_salario.setPlaceholderText("Ej: 5000.00")
        
        self.ui.btnGuardar.clicked.connect(self.registrar_empleado)
        
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
    
    def registrar_empleado(self):
        try:
            if not self.validar_campos():
                return
            
            nombre = self.ui.le_nombre.text().strip()
            apellido_pa = self.ui.le_apellidoPA.text().strip()
            apellido_ma = self.ui.le_apellidoMa.text().strip()
            edad_texto = self.ui.le_edad.text().strip()
            email = self.ui.le_email.text().strip()
            telefono = self.ui.le_telefono.text().strip()
            rol = self.ui.le_rol.text().strip()
            salario_texto = self.ui.le_salario.text().strip()

            try:
                edad = int(edad_texto)
                if edad < 18 or edad > 100:
                    QMessageBox.warning(self, "Edad inválida", "La edad debe estar entre 18 y 100 años")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "La edad debe ser un número válido")
                return
            
            salario = 0.00
            if salario_texto:
                try:
                    salario = float(salario_texto)
                    if salario < 0:
                        QMessageBox.warning(self, "Salario inválido", "El salario no puede ser negativo")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Error", "El salario debe ser un número válido")
                    return
            
            persona = Persona(
                nombre=nombre,
                apellido_pa=apellido_pa,
                apellido_ma=apellido_ma,
                edad=edad,
                email=email,
                telefono=telefono
            )
            
            sedes = self.gym_controller.obtener_sedes()
            sede = sedes[0] if sedes else None
            
            empleado = Empleado(
                persona=persona,
                sede=sede,
                fecha_contrat=date.today(),
                salario=salario,
                rol=rol
            )
            
            empleado_id = self.gym_controller.crear_empleado(empleado)
            if empleado_id:
                QMessageBox.information(self, "Éxito", 
                    f"Empleado registrado exitosamente.\n"
                    f"Código de empleado: {empleado_id}\n"
                    f"Salario: ${salario:.2f}")
                self.close()
                if self.parent and hasattr(self.parent, 'cargar_empleados'):
                    self.parent.cargar_empleados()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el empleado")
                
        except Exception as e:
            print(f"Error completo al registrar empleado: {e}")
            QMessageBox.critical(self, "Error", f"Error al registrar empleado: {str(e)}")
    
    def validar_campos(self):
        campos_obligatorios = [
            (self.ui.le_nombre, "Nombre"),
            (self.ui.le_apellidoPA, "Apellido Paterno"),
            (self.ui.le_apellidoMa, "Apellido Materno"),
            (self.ui.le_edad, "Edad"),
            (self.ui.le_email, "Email"),
            (self.ui.le_rol, "Rol")
        ]
        
        for campo, nombre in campos_obligatorios:
            if not campo.text().strip():
                QMessageBox.warning(self, "Campo requerido", f"El campo {nombre} es obligatorio")
                campo.setFocus()
                return False
        
        email = self.ui.le_email.text().strip()
        if '@' not in email or '.' not in email:
            QMessageBox.warning(self, "Email inválido", "Por favor ingrese un email válido")
            self.ui.le_email.setFocus()
            return False
            
        return True

    def closeEvent(self, event):
        if hasattr(self.parent, 'cargar_empleados'):
            self.parent.cargar_empleados()
        event.accept()

class ModifyEmployedWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.parent = parent
        self.empleado_actual = None
        self.ui = Ui_ModifyEmployedWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Modificar Empleado")
        self.setFixedSize(self.width(), self.height())
        
        self.ui.btn_buscar.clicked.connect(self.buscar_empleado)
        self.ui.btnModificar.clicked.connect(self.modificar_empleado)
        
        self.ui.groupBox.setEnabled(False)
        self.ui.btnModificar.setEnabled(False)
    
    def buscar_empleado(self):
        try:
            codigo_texto = self.ui.le_codigoEmple.text().strip()
            if not codigo_texto:
                QMessageBox.warning(self, "Advertencia", "Por favor ingrese un código de empleado")
                return
            
            empleado_id = int(codigo_texto)
            empleado = self.buscar_empleado_por_codigo(empleado_id)
            
            if not empleado:
                QMessageBox.warning(self, "Empleado no encontrado", "El código de empleado no existe")
                return
            
            self.empleado_actual = empleado
            self.mostrar_datos_empleado(empleado)
            self.ui.groupBox.setEnabled(True)
            self.ui.btnModificar.setEnabled(True)
            
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar empleado: {str(e)}")
    
    def buscar_empleado_por_codigo(self, codigo: int) -> Optional[Empleado]:
        query = """
        SELECT e.*, p.Nombre, p.ApellidoPA, p.ApellidoMA, p.Edad, p.Email, p.Telefono
        FROM Empleado e
        JOIN Persona p ON e.IDPersona = p.ID
        WHERE e.CodEmple = %s AND p.Activo = TRUE
        """
        resultado = self.gym_controller.db.fetch_one(query, (codigo,))
        
        if resultado:
            persona = Persona(
                id=resultado['IDPersona'],
                nombre=resultado['Nombre'],
                apellido_pa=resultado['ApellidoPA'],
                apellido_ma=resultado['ApellidoMA'],
                edad=resultado['Edad'],
                email=resultado['Email'],
                telefono=resultado['Telefono']
            )
            
            empleado = Empleado(
                cod_emple=resultado['CodEmple'],
                persona=persona,
                fecha_contrat=resultado['FechaContrat'],
                salario=resultado['Salario'],
                rol=resultado['Rol']
            )
            return empleado
        
        return None
    
    def mostrar_datos_empleado(self, empleado):
        self.ui.le_nombre.setText(empleado.persona.nombre)
        self.ui.le_apellidoPA.setText(empleado.persona.apellido_pa)
        self.ui.le_apellidoMA.setText(empleado.persona.apellido_ma)
        self.ui.le_email.setText(empleado.persona.email)
        self.ui.le_telefono.setText(empleado.persona.telefono or "")
        self.ui.le_salario.setText(str(empleado.salario))
    
    def modificar_empleado(self):
        try:
            if not self.empleado_actual:
                QMessageBox.warning(self, "Advertencia", "No hay empleado seleccionado")
                return
            
            nombre = self.ui.le_nombre.text().strip()
            apellido_pa = self.ui.le_apellidoPA.text().strip()
            apellido_ma = self.ui.le_apellidoMA.text().strip()
            email = self.ui.le_email.text().strip()
            telefono = self.ui.le_telefono.text().strip()
            salario_texto = self.ui.le_salario.text().strip()
            
            if not nombre or not apellido_pa or not apellido_ma or not email:
                QMessageBox.warning(self, "Campos requeridos", "Nombre, apellidos y email son obligatorios")
                return
            
            try:
                salario = float(salario_texto)
            except ValueError:
                QMessageBox.warning(self, "Error", "El salario debe ser un número válido")
                return
            
            self.empleado_actual.persona.nombre = nombre
            self.empleado_actual.persona.apellido_pa = apellido_pa
            self.empleado_actual.persona.apellido_ma = apellido_ma
            self.empleado_actual.persona.email = email
            self.empleado_actual.persona.telefono = telefono
            self.empleado_actual.salario = salario
            
            if self.actualizar_empleado_en_db(self.empleado_actual):
                QMessageBox.information(self, "Éxito", "Empleado modificado correctamente")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "No se pudo modificar el empleado")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar empleado: {str(e)}")
    
    def actualizar_empleado_en_db(self, empleado):
        query_persona = """
        UPDATE Persona 
        SET Nombre = %s, ApellidoPA = %s, ApellidoMA = %s, Email = %s, Telefono = %s
        WHERE ID = %s
        """
        persona_actualizada = self.gym_controller.db.execute_query(query_persona, (
            empleado.persona.nombre,
            empleado.persona.apellido_pa,
            empleado.persona.apellido_ma,
            empleado.persona.email,
            empleado.persona.telefono,
            empleado.persona.id
        ))
        
        query_empleado = """
        UPDATE Empleado 
        SET Salario = %s
        WHERE CodEmple = %s
        """
        empleado_actualizado = self.gym_controller.db.execute_query(query_empleado, (
            empleado.salario,
            empleado.cod_emple
        ))
        
        return persona_actualizada and empleado_actualizado

    def closeEvent(self, event):
        if hasattr(self.parent, 'cargar_empleados'):
            self.parent.cargar_empleados()
        event.accept()

class DeleteEmployedWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.parent = parent
        self.empleado_actual = None
        self.ui = Ui_DeleteEmployedWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Eliminar Empleado")
        self.setFixedSize(self.width(), self.height())
        
        self.ui.btnBuscar.clicked.connect(self.buscar_empleado)
        self.ui.btnEliminar.clicked.connect(self.eliminar_empleado)
        
        self.ui.groupDatos.setEnabled(False)
        self.ui.btnEliminar.setEnabled(False)
    
    def buscar_empleado(self):
        try:
            codigo_texto = self.ui.le_codigoEmpleado.text().strip()
            if not codigo_texto:
                QMessageBox.warning(self, "Advertencia", "Por favor ingrese un código de empleado")
                return
            
            empleado_id = int(codigo_texto)
            empleado = self.buscar_empleado_por_codigo(empleado_id)
            
            if not empleado:
                QMessageBox.warning(self, "Empleado no encontrado", "El código de empleado no existe")
                return
            
            self.empleado_actual = empleado
            self.mostrar_datos_empleado(empleado)
            self.ui.groupDatos.setEnabled(True)
            self.ui.btnEliminar.setEnabled(True)
            
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar empleado: {str(e)}")
    
    def buscar_empleado_por_codigo(self, codigo: int) -> Optional[Empleado]:
        query = """
        SELECT e.*, p.Nombre, p.ApellidoPA, p.ApellidoMA, p.Edad, p.Email, p.Telefono
        FROM Empleado e
        JOIN Persona p ON e.IDPersona = p.ID
        WHERE e.CodEmple = %s AND p.Activo = TRUE
        """
        resultado = self.gym_controller.db.fetch_one(query, (codigo,))
        
        if resultado:
            persona = Persona(
                id=resultado['IDPersona'],
                nombre=resultado['Nombre'],
                apellido_pa=resultado['ApellidoPA'],
                apellido_ma=resultado['ApellidoMA'],
                edad=resultado['Edad'],
                email=resultado['Email'],
                telefono=resultado['Telefono']
            )
            
            empleado = Empleado(
                cod_emple=resultado['CodEmple'],
                persona=persona,
                fecha_contrat=resultado['FechaContrat'],
                salario=resultado['Salario'],
                rol=resultado['Rol']
            )
            return empleado
        
        return None
    
    def mostrar_datos_empleado(self, empleado):
        self.ui.lblNombreValue.setText(empleado.persona.nombre_completo)
        self.ui.lblEdadValue.setText(str(empleado.persona.edad))
        self.ui.lblEmailValue.setText(empleado.persona.email)
        self.ui.lblTelefonoValue.setText(empleado.persona.telefono or "No proporcionado")
        self.ui.lblFechaNacValue.setText(empleado.fecha_contrat.strftime("%Y-%m-%d") if empleado.fecha_contrat else "N/A")
        self.ui.lblSalarioValue.setText(f"${empleado.salario:.2f}")
        self.ui.lblRolValue.setText(empleado.rol)
    
    def eliminar_empleado(self):
        try:
            if not self.empleado_actual:
                QMessageBox.warning(self, "Advertencia", "No hay empleado seleccionado")
                return
            
            respuesta = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar al empleado {self.empleado_actual.persona.nombre_completo}?\nEsta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                # Eliminar empleado (esto eliminará en cascada la persona por la FK)
                query = "DELETE FROM Empleado WHERE CodEmple = %s"
                if self.gym_controller.db.execute_query(query, (self.empleado_actual.cod_emple,)):
                    QMessageBox.information(self, "Éxito", "Empleado eliminado correctamente")
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo eliminar el empleado")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar empleado: {str(e)}")

    def closeEvent(self, event):
        if hasattr(self.parent, 'cargar_empleados'):
            self.parent.cargar_empleados()
        event.accept()
    
class RegisterInventarioWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.parent = parent
        self.ui = Ui_RegisterInventario()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Registrar Elemento de Inventario")
        self.setFixedSize(self.width(), self.height())
        
        fecha_un_anio = date.today() + timedelta(days=365)
        self.ui.de_fechaNac.setDate(fecha_un_anio)
        
        self.ui.btnPagar.clicked.connect(self.registrar_inventario)
        
        self.cargar_sedes()
        
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
    
    def cargar_sedes(self):
        try:
            sedes = self.gym_controller.obtener_sedes()
            pass
        except Exception as e:
            print(f"Error al cargar sedes: {e}")
    
    def registrar_inventario(self):
        try:
            if not self.validar_campos():
                return
            
            nombre = self.ui.le_nombre.text().strip()
            categoria = self.ui.comboBox.currentText()
            descripcion = self.ui.le_apellidoMA.text().strip()
            precio_venta_texto = self.ui.le_email.text().strip()
            cantidad_texto = self.ui.le_telefono.text().strip()
            fecha_caducidad = self.ui.de_fechaNac.date().toPyDate()
            activo = self.ui.checkBox.isChecked()
            
            try:
                precio_venta = float(precio_venta_texto)
                cantidad = int(cantidad_texto)
            except ValueError:
                QMessageBox.warning(self, "Error", "Precio y cantidad deben ser números válidos")
                return
            
            sedes = self.gym_controller.obtener_sedes()
            sede = sedes[0] if sedes else None
            
            inventario = Inventario(
                sede=sede,
                nombre=nombre,
                categoria=categoria,
                tipo=categoria,
                descripcion=descripcion,
                precio_venta=precio_venta,
                precio_compra=0.0,
                cantidad=cantidad,
                stock_minimo=5,
                fecha_caducidad=fecha_caducidad,
                activo=activo
            )
            
            # Registrar en la base de datos
            inventario_id = self.gym_controller.agregar_inventario(inventario)
            if inventario_id:
                QMessageBox.information(self, "Éxito", 
                    f"Elemento registrado exitosamente!\n"
                    f"Código de barras: {inventario_id}\n"
                    f"Nombre: {nombre}\n"
                    f"Categoría: {categoria}")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el elemento")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar elemento: {str(e)}")
    
    def validar_campos(self):
        campos_obligatorios = [
            (self.ui.le_nombre, "Nombre"),
            (self.ui.le_email, "Precio"),
            (self.ui.le_telefono, "Cantidad")
        ]
        
        for campo, nombre in campos_obligatorios:
            if not campo.text().strip():
                QMessageBox.warning(self, "Campo requerido", 
                                           f"El campo {nombre} es obligatorio")
                campo.setFocus()
                return False
        
        try:
            float(self.ui.le_email.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Error", "El precio debe ser un número válido")
            self.ui.le_email.setFocus()
            return False
            
        try:
            int(self.ui.le_telefono.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Error", "La cantidad debe ser un número válido")
            self.ui.le_telefono.setFocus()
            return False
            
        return True
    
    def closeEvent(self, event):
        if hasattr(self.parent, 'cargar_inventario'):
            self.parent.cargar_inventario()
        event.accept()

class RegisterPrestamoWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None, empleado=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.parent = parent
        self.empleado = empleado
        self.ui = Ui_RegisterPrestamo()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Registrar Préstamo de Equipo")
        self.setFixedSize(self.width(), self.height())
        
        fecha_manana = date.today() + timedelta(days=1)
        self.ui.de_fechaDev.setDate(fecha_manana)
        
        self.ui.btnRegistrar.clicked.connect(self.registrar_prestamo)
        
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
    
    def registrar_prestamo(self):
        try:
            if not self.validar_campos():
                return
            
            codigo_equipo_texto = self.ui.le_codEquipo.text().strip()
            codigo_cliente_texto = self.ui.le_codCliente.text().strip()
            fecha_devolucion = self.ui.de_fechaDev.date().toPyDate()
            estado = self.ui.cb_estado.currentText()
            
            try:
                codigo_equipo = int(codigo_equipo_texto)
                codigo_cliente = int(codigo_cliente_texto)
            except ValueError:
                QMessageBox.warning(self, "Error", "Los códigos deben ser números válidos")
                return
            
            equipo = self.gym_controller.buscar_elemento_por_codigo(codigo_equipo)
            if not equipo:
                QMessageBox.warning(self, "Error", "El código de equipo no existe")
                return
            
            cliente = self.gym_controller.buscar_cliente_por_codigo(codigo_cliente)
            if not cliente:
                QMessageBox.warning(self, "Error", "El código de cliente no existe")
                return
            
            if equipo.cantidad <= 0:
                QMessageBox.warning(self, "Error", "No hay stock disponible de este equipo")
                return
            
            prestamo = PrestamoEquipo(
                cliente=cliente,
                equipo=equipo,
                empleado=self.empleado,
                fecha_prestamo=datetime.now(),
                fecha_devolucion=datetime.combine(fecha_devolucion, datetime.min.time()),
                estado=estado,
                observaciones="Préstamo registrado desde sistema"
            )
            
            prestamo_id = self.gym_controller.registrar_prestamo(prestamo)
            if prestamo_id:
                nueva_cantidad = equipo.cantidad - 1
                if self.gym_controller.actualizar_stock(equipo.codigo_barras, nueva_cantidad):
                    QMessageBox.information(self, "Éxito", 
                        f"Préstamo registrado exitosamente!\n"
                        f"ID de préstamo: {prestamo_id}\n"
                        f"Equipo: {equipo.nombre}\n"
                        f"Cliente: {cliente.persona.nombre_completo}\n"
                        f"Fecha de devolución: {fecha_devolucion}")
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", "Préstamo registrado pero no se pudo actualizar el stock")
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el préstamo")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar préstamo: {str(e)}")
    
    def validar_campos(self):
        campos_obligatorios = [
            (self.ui.le_codEquipo, "Código de equipo"),
            (self.ui.le_codCliente, "Código de cliente")
        ]
        
        for campo, nombre in campos_obligatorios:
            if not campo.text().strip():
                QMessageBox.warning(self, "Campo requerido", 
                                           f"El campo {nombre} es obligatorio")
                campo.setFocus()
                return False
        
        try:
            int(self.ui.le_codEquipo.text().strip())
            int(self.ui.le_codCliente.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Error", "Los códigos deben ser números válidos")
            return False
            
        return True
    
    def closeEvent(self, event):
        if hasattr(self.parent, 'cargar_prestamos'):
            self.parent.cargar_prestamos()
        if hasattr(self.parent, 'cargar_inventario'):
            self.parent.cargar_inventario()
        event.accept()

    def configurar_conexiones(self):
        self.ui.pb_modificarClient.clicked.connect(self.abrir_modificar_cliente)
        self.ui.pb_actualizarMemb.clicked.connect(self.abrir_actualizar_membresia)
        self.ui.pb_eliminarClient.clicked.connect(self.abrir_eliminar_cliente)

        self.ui.pb_addEmpleado.clicked.connect(self.abrir_registro_empleado)
        self.ui.pb_modificarEmpleados.clicked.connect(self.abrir_modificar_empleado)
        self.ui.pb_eliminarEmpleados.clicked.connect(self.abrir_eliminar_empleado)
        
        self.ui.pb_buscarElemento.clicked.connect(self.buscar_elemento_prestamo)
        self.ui.le_codigoPrestamo.returnPressed.connect(self.buscar_elemento_prestamo)
        self.ui.pb_registrarPrestamo.clicked.connect(self.abrir_registro_prestamo)
        self.ui.pb_addElemento.clicked.connect(self.abrir_registro_inventario)
        self.ui.pb_modificarElemento.clicked.connect(self.abrir_modificar_inventario)
        self.ui.pb_eliminarElemento.clicked.connect(self.abrir_eliminar_inventario)

        self.ui.btn_registrarAs.clicked.connect(self.ir_a_registro_asistencia_desde_principal)
        self.ui.bt_aceptarAsistencia.clicked.connect(self.registrar_asistencia_integrada)
        self.ui.le_codigoAsistencia.returnPressed.connect(self.registrar_asistencia_integrada)

        self.ui.bt_cerrarSe.clicked.connect(self.cerrar_sesion)
        self.ui.pb_addCliente.clicked.connect(self.abrir_registro_cliente)
        self.ui.pb_buscarClientAsistencia.clicked.connect(self.buscar_asistencias_cliente)
        self.ui.le_codigoClienteBuscarAsistencia.returnPressed.connect(self.buscar_asistencias_cliente)

        self.ui.stackedWidget.currentChanged.connect(self.cargar_datos_pagina)

    def abrir_modificar_inventario(self):
        try:
            if (hasattr(self, 'modify_inventario_window') and 
                self.modify_inventario_window is not None and 
                self.modify_inventario_window.isVisible()):
                self.modify_inventario_window.raise_()
                self.modify_inventario_window.activateWindow()
                return
                
            self.modify_inventario_window = ModifyInventarioWindow(self.gym_controller, self)
            self.modify_inventario_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario de modificación: {str(e)}")

    def abrir_eliminar_inventario(self):
        try:
            if (hasattr(self, 'delete_inventario_window') and 
                self.delete_inventario_window is not None and 
                self.delete_inventario_window.isVisible()):
                self.delete_inventario_window.raise_()
                self.delete_inventario_window.activateWindow()
                return
                
            self.delete_inventario_window = DeleteInventarioWindow(self.gym_controller, self)
            self.delete_inventario_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario de eliminación: {str(e)}")

class ModifyInventarioWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.parent = parent
        self.elemento_actual = None
        self.ui = Ui_ModifyInventario()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Modificar Elemento de Inventario")
        self.setFixedSize(self.width(), self.height())
        
        self.ui.btn_buscar.clicked.connect(self.buscar_elemento)
        self.ui.btnMoficar.clicked.connect(self.modificar_elemento)
        
        self.ui.groupBox.setEnabled(False)
        self.ui.btnMoficar.setEnabled(False)
        
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
    
    def buscar_elemento(self):
        try:
            codigo_texto = self.ui.le_codigoEle.text().strip()
            
            if not codigo_texto:
                QMessageBox.warning(self, "Advertencia", "Por favor ingrese un código de elemento")
                return
            
            try:
                codigo = int(codigo_texto)
            except ValueError:
                QMessageBox.warning(self, "Error", "El código debe ser un número válido")
                return
            
            print(f"Buscando elemento con código: {codigo}")
            
            elemento = self.gym_controller.buscar_elemento_por_codigo(codigo)
            
            if not elemento:
                QMessageBox.warning(self, "Elemento no encontrado", "El código de elemento no existe")
                return
            
            self.elemento_actual = elemento
            self.mostrar_datos_elemento(elemento)
            self.ui.groupBox.setEnabled(True)
            self.ui.btnMoficar.setEnabled(True)
            
        except Exception as e:
            print(f"Error completo en buscar_elemento: {e}")
            QMessageBox.critical(self, "Error", f"Error al buscar elemento: {str(e)}")
    
    def mostrar_datos_elemento(self, elemento):
        self.ui.le_nombre.setText(elemento.nombre)
        
        index = self.ui.cb_bebida.findText(elemento.categoria)
        if index >= 0:
            self.ui.cb_bebida.setCurrentIndex(index)
        
        self.ui.le_descripcion.setText(elemento.descripcion or "")
        
        if elemento.fecha_caducidad:
            self.ui.de_fechaCad.setDate(elemento.fecha_caducidad)
        
        self.ui.le_precio.setText(str(elemento.precio_venta))
        self.ui.le_cantidad.setText(str(elemento.cantidad))
        self.ui.cb_activo.setChecked(elemento.activo)
    
    def modificar_elemento(self):
        try:
            if not self.elemento_actual:
                QMessageBox.warning(self, "Advertencia", "No hay elemento seleccionado")
                return
            
            nombre = self.ui.le_nombre.text().strip()
            categoria = self.ui.cb_bebida.currentText().strip()  # ComboBox
            descripcion = self.ui.le_descripcion.text().strip()
            precio_texto = self.ui.le_precio.text().strip()
            cantidad_texto = self.ui.le_cantidad.text().strip()
            activo = self.ui.cb_activo.isChecked()
            
            if not nombre or not categoria:
                QMessageBox.warning(self, "Campos requeridos", "Nombre y categoría son obligatorios")
                return
            
            try:
                precio = float(precio_texto) if precio_texto else 0.0
                cantidad = int(cantidad_texto) if cantidad_texto else 0
            except ValueError:
                QMessageBox.warning(self, "Error", "Precio y cantidad deben ser números válidos")
                return
            
            fecha_caducidad = self.ui.de_fechaCad.date().toPyDate()
            
            query = """
            UPDATE Inventario 
            SET Nombre = %s, Categoria = %s, Descripcion = %s, PrecioVenta = %s, 
                Cantidad = %s, FechaCaducidad = %s, Activo = %s
            WHERE CodigoBarras = %s
            """
            if self.gym_controller.db.execute_query(query, (
                nombre,
                categoria,
                descripcion,
                precio,
                cantidad,
                fecha_caducidad,
                activo,
                self.elemento_actual.codigo_barras
            )):
                QMessageBox.information(self, "Éxito", "Elemento modificado correctamente")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "No se pudo modificar el elemento")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar elemento: {str(e)}")
    
    def closeEvent(self, event):
        if hasattr(self.parent, 'cargar_inventario'):
            self.parent.cargar_inventario()
        event.accept()

class DeleteInventarioWindow(QMainWindow):
    def __init__(self, gym_controller, parent=None):
        super().__init__(parent)
        self.gym_controller = gym_controller
        self.parent = parent
        self.elemento_actual = None
        self.ui = Ui_DeleteInventario()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Eliminar Elemento de Inventario")
        self.setFixedSize(self.width(), self.height())
        
        self.ui.btnBuscar.clicked.connect(self.buscar_elemento)
        self.ui.btnEliminar.clicked.connect(self.eliminar_elemento)
        
        self.ui.groupDatos.setEnabled(False)
        self.ui.btnEliminar.setEnabled(False)
        
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
    
    def buscar_elemento(self):
        try:
            codigo_texto = self.ui.le_codigoElemento.text().strip()
            
            if not codigo_texto:
                QMessageBox.warning(self, "Advertencia", "Por favor ingrese un código de elemento")
                return
            
            try:
                codigo = int(codigo_texto)
            except ValueError:
                QMessageBox.warning(self, "Error", "El código debe ser un número válido")
                return
            
            elemento = self.gym_controller.buscar_elemento_por_codigo(codigo)
            
            if not elemento:
                QMessageBox.warning(self, "Elemento no encontrado", "El código de elemento no existe")
                return
            
            self.elemento_actual = elemento
            self.mostrar_datos_elemento(elemento)
            self.ui.groupDatos.setEnabled(True)
            self.ui.btnEliminar.setEnabled(True)
            
        except Exception as e:
            print(f"Error completo en buscar_elemento (eliminar): {e}")
            QMessageBox.critical(self, "Error", f"Error al buscar elemento: {str(e)}")
    
    def mostrar_datos_elemento(self, elemento):
        self.ui.lblNombreValue.setText(elemento.nombre)
        
        index = self.ui.lblCategoriaValue.findText(elemento.categoria)
        if index >= 0:
            self.ui.lblCategoriaValue.setCurrentIndex(index)
        
        self.ui.lblDescripcionValue.setText(elemento.descripcion or "Sin descripción")
        
        if elemento.fecha_caducidad:
            self.ui.de_fechaCad.setDate(elemento.fecha_caducidad)
        
        self.ui.lblPrecioValue.setText(f"{elemento.precio_venta:.2f}")
        self.ui.lblCantidadValue.setText(str(elemento.cantidad))
        self.ui.cb_activo.setChecked(elemento.activo)
    
    def eliminar_elemento(self):
        try:
            if not self.elemento_actual:
                QMessageBox.warning(self, "Advertencia", "No hay elemento seleccionado")
                return
            
            respuesta = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar el elemento?\n\n"
                f"Nombre: {self.elemento_actual.nombre}\n"
                f"Categoría: {self.elemento_actual.categoria}\n"
                f"Cantidad: {self.elemento_actual.cantidad}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                query = "UPDATE Inventario SET Activo = FALSE WHERE CodigoBarras = %s"
                if self.gym_controller.db.execute_query(query, (self.elemento_actual.codigo_barras,)):
                    QMessageBox.information(self, "Éxito", "Elemento eliminado correctamente")
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo eliminar el elemento")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar elemento: {str(e)}")
    
    def closeEvent(self, event):
        if hasattr(self.parent, 'cargar_inventario'):
            self.parent.cargar_inventario()
        event.accept()