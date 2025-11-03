CREATE DATABASE IF NOT EXISTS `GYM`;
USE `GYM`;

-- ============================================
-- TABLAS BASE
-- ============================================

CREATE TABLE `Direccion`(
	ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Calle VARCHAR(200) NOT NULL,
    Ciudad VARCHAR(50) NOT NULL,
    EstadoP VARCHAR(50) NOT NULL,
    CP INT NOT NULL
)ENGINE=InnoDB;

CREATE TABLE `Sede`(
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(70) UNIQUE NOT NULL,
    HoraAbre TIME NOT NULL,
    HoraCierra TIME NOT NULL,
    IDDireccion INT NOT NULL,
    Telefono VARCHAR(20),
    FOREIGN KEY (IDDireccion) REFERENCES Direccion(ID)
)ENGINE=InnoDB;

-- Tabla base para datos personales (herencia)
CREATE TABLE `Persona`(
	ID INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(30) NOT NULL,
    ApellidoPA VARCHAR(30) NOT NULL,
    ApellidoMA VARCHAR(30) NOT NULL,
    Email VARCHAR(45) NOT NULL,
    Telefono VARCHAR(20),
    Activo BOOLEAN DEFAULT TRUE
)ENGINE=InnoDB;

-- ============================================
-- TABLAS DE EXTENSIÓN (HERENCIA)
-- ============================================

CREATE TABLE `Empleado`(
    CodEmple INT PRIMARY KEY AUTO_INCREMENT,
    IDPersona INT UNIQUE NOT NULL,
	IDSede INT,
    FechaContrat DATE NOT NULL,
    Salario DECIMAL(10,2) NOT NULL,
    Rol VARCHAR(30) NOT NULL,
    FOREIGN KEY (IDPersona) REFERENCES Persona(ID) ON DELETE CASCADE,
    FOREIGN KEY (IDSede) REFERENCES Sede(ID)
)ENGINE=InnoDB;

CREATE TABLE `Cliente`(
    CodCli INT PRIMARY KEY AUTO_INCREMENT,
    IDPersona INT UNIQUE NOT NULL,
    IDSedeInscrito INT,
    Genero ENUM('Masculino', 'Femenino') NOT NULL,
    FechaNac DATE NOT NULL,
    FechaInscri DATETIME NOT NULL,
    FOREIGN KEY (IDPersona) REFERENCES Persona(ID) ON DELETE CASCADE,
    FOREIGN KEY (IDSedeInscrito) REFERENCES Sede(ID)
)ENGINE=InnoDB;

-- ============================================
-- TABLAS OPERATIVAS
-- ============================================

CREATE TABLE `Membresia`(
    CodMem INT PRIMARY KEY AUTO_INCREMENT,
    IDCliente INT NOT NULL,
    Tipo ENUM('Visitante','Semanal','Mensual','Anual') NOT NULL DEFAULT 'Mensual',
    Precio DECIMAL(8,2) NOT NULL,
    FechaInicio DATETIME NOT NULL,
    FechaVenc DATETIME NOT NULL,
    DiasValidez INT GENERATED ALWAYS AS (DATEDIFF(FechaVenc, FechaInicio)) STORED,
    Estado ENUM('Activa', 'Inactiva', 'Expirada', 'Pausada') NOT NULL DEFAULT 'Activa',
    FOREIGN KEY (IDCliente) REFERENCES Cliente(CodCli) ON DELETE CASCADE
)ENGINE=InnoDB;

CREATE TABLE `Pago`(
    Folio INT PRIMARY KEY AUTO_INCREMENT,
    IDCliente INT NOT NULL,
    IDEmpleado INT,
    IDMembresia INT NOT NULL,
    Monto DECIMAL(10,2) NOT NULL,
    MontoPagado DECIMAL(10,2) NOT NULL,
    Cambio DECIMAL(10,2) GENERATED ALWAYS AS (MontoPagado - Monto) STORED,
    Metodo ENUM('Efectivo', 'Tarjeta', 'Transferencia') NOT NULL,
    FechaPago DATETIME NOT NULL,
    Concepto VARCHAR(100) NOT NULL,
    Estado ENUM('Completado', 'Pendiente', 'Cancelado') NOT NULL,
    Referencia VARCHAR(50),
    FOREIGN KEY (IDCliente) REFERENCES Cliente(CodCli),
    FOREIGN KEY (IDEmpleado) REFERENCES Empleado(CodEmple),
    FOREIGN KEY (IDMembresia) REFERENCES Membresia(CodMem)
)ENGINE=InnoDB;

CREATE TABLE `Asistencia`(
    ID INT PRIMARY KEY AUTO_INCREMENT,
    IDCliente INT NOT NULL,
    IDSede INT NOT NULL,
    Fecha DATE NOT NULL,
    HoraEntrada TIME NOT NULL,
    HoraSalida TIME,
    FOREIGN KEY (IDCliente) REFERENCES Cliente(CodCli),
    FOREIGN KEY (IDSede) REFERENCES Sede(ID)
)ENGINE=InnoDB;

CREATE TABLE `Inventario`(
    CodigoBarras INT PRIMARY KEY AUTO_INCREMENT,
    IDSede INT,
    Nombre VARCHAR(100) NOT NULL,
    Categoria ENUM('Bebida', 'Suplemento', 'Accesorio', 'Ropa', 'Equipo') NOT NULL,
    Tipo VARCHAR(50) NOT NULL,
    Descripcion TEXT,
    PrecioVenta DECIMAL(8,2) NOT NULL,
    PrecioCompra DECIMAL(8,2),
    Cantidad INT NOT NULL,
    StockMinimo INT DEFAULT 5,
    FechaCaducidad DATE,
    Activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (IDSede) REFERENCES Sede(ID)
)ENGINE=InnoDB;

CREATE TABLE `Prestamo_Equipo`(
    ID INT PRIMARY KEY AUTO_INCREMENT,
    IDCliente INT NOT NULL,
    IDEquipo INT NOT NULL,
    IDEmpleado INT NOT NULL,
    FechaPrestamo DATETIME NOT NULL,
    FechaDevolucion DATETIME,
    Estado ENUM('Prestado', 'Devuelto', 'Atrasado') DEFAULT 'Prestado',
    Observaciones TEXT,
    FOREIGN KEY (IDCliente) REFERENCES Cliente(CodCli),
    FOREIGN KEY (IDEquipo) REFERENCES Inventario(CodigoBarras),
    FOREIGN KEY (IDEmpleado) REFERENCES Empleado(CodEmple)
)ENGINE=InnoDB;

-- ============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ============================================

-- Índices en Persona
CREATE INDEX idx_persona_activo ON Persona(Activo);
CREATE INDEX idx_persona_email ON Persona(Email);

-- Índices en Cliente
CREATE INDEX idx_cliente_sede ON Cliente(IDSedeInscrito);
CREATE INDEX idx_cliente_fecha_inscr ON Cliente(FechaInscri);

-- Índices en Empleado
CREATE INDEX idx_empleado_sede ON Empleado(IDSede);
CREATE INDEX idx_empleado_rol ON Empleado(Rol);

-- Índices en Membresía
CREATE INDEX idx_membresia_cliente ON Membresia(IDCliente);
CREATE INDEX idx_membresia_estado ON Membresia(Estado);
CREATE INDEX idx_membresia_vencimiento ON Membresia(FechaVenc);
CREATE INDEX idx_membresia_tipo ON Membresia(Tipo);

-- Índices en Pago
CREATE INDEX idx_pago_cliente ON Pago(IDCliente);
CREATE INDEX idx_pago_fecha ON Pago(FechaPago);
CREATE INDEX idx_pago_estado ON Pago(Estado);
CREATE INDEX idx_pago_membresia ON Pago(IDMembresia);

-- Índices en Asistencia
CREATE INDEX idx_asistencia_cliente ON Asistencia(IDCliente);
CREATE INDEX idx_asistencia_fecha ON Asistencia(Fecha);
CREATE INDEX idx_asistencia_sede ON Asistencia(IDSede);

-- Índices en Inventario
CREATE INDEX idx_inventario_sede ON Inventario(IDSede);
CREATE INDEX idx_inventario_categoria ON Inventario(Categoria);
CREATE INDEX idx_inventario_stock ON Inventario(Cantidad);
CREATE INDEX idx_inventario_activo ON Inventario(Activo);

-- Índices en Préstamo
CREATE INDEX idx_prestamo_cliente ON Prestamo_Equipo(IDCliente);
CREATE INDEX idx_prestamo_estado ON Prestamo_Equipo(Estado);
CREATE INDEX idx_prestamo_fecha ON Prestamo_Equipo(FechaPrestamo);