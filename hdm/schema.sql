-- Esquema de base de datos D1 para Cloudflare
-- Archivo: schema.sql

-- Tabla de pacientes
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento TEXT UNIQUE NOT NULL,
    tipo_documento TEXT NOT NULL CHECK (tipo_documento IN ('CC', 'TI', 'CE', 'PS', 'RC')),
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    genero TEXT NOT NULL CHECK (genero IN ('M', 'F')),
    telefono TEXT,
    direccion TEXT,
    eps TEXT,
    fecha_inicio_hd DATE NOT NULL,
    causa_erc TEXT,
    comorbilidades TEXT,
    activo BOOLEAN DEFAULT 1,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de sesiones de diálisis
CREATE TABLE IF NOT EXISTS sesiones_dialisis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    fecha DATETIME NOT NULL,
    turno TEXT NOT NULL CHECK (turno IN ('LMV_MAÑANA', 'LMV_TARDE', 'LMV_NOCHE', 'MJS_MAÑANA', 'MJS_TARDE', 'MJS_NOCHE')),
    peso_pre REAL,
    peso_post REAL,
    peso_seco REAL,
    qb INTEGER,
    tiempo_sesion INTEGER,
    uf_programada REAL,
    uf_real REAL,
    kt_v REAL,
    pru REAL,
    presion_arterial_pre TEXT,
    presion_arterial_post TEXT,
    medicamentos_iv TEXT,
    complicaciones TEXT,
    observaciones TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
);

-- Tabla de laboratorios
CREATE TABLE IF NOT EXISTS laboratorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    fecha DATETIME NOT NULL,
    -- Anemia
    hemoglobina REAL,
    hematocrito REAL,
    ferritina REAL,
    tsat REAL,
    hierro_serico REAL,
    pcr REAL,
    -- Función renal y adecuación
    urea_pre REAL,
    urea_post REAL,
    creatinina REAL,
    albumina REAL,
    -- Mineral óseo
    calcio REAL,
    fosforo REAL,
    pth REAL,
    vitamina_d REAL,
    fosfatasa_alcalina REAL,
    -- Otros
    potasio REAL,
    sodio REAL,
    bicarbonato REAL,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
);

-- Tabla de accesos vasculares
CREATE TABLE IF NOT EXISTS accesos_vasculares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    tipo_acceso TEXT NOT NULL CHECK (tipo_acceso IN ('FAV_NATIVA', 'FAV_PROTESICA', 'CATETER_TEMPORAL', 'CATETER_PERMANENTE')),
    localizacion TEXT,
    fecha_creacion DATE,
    fecha_evaluacion DATE NOT NULL,
    -- Parámetros físicos
    fremito TEXT CHECK (fremito IN ('PRESENTE', 'AUSENTE', 'DISMINUIDO', 'AUMENTADO')),
    soplo TEXT CHECK (soplo IN ('NORMAL', 'ANORMAL', 'AUSENTE')),
    qa_flujo REAL,
    presion_intraacceso REAL,
    recirculacion REAL,
    -- Estado y complicaciones
    estado TEXT CHECK (estado IN ('FUNCIONAL', 'DISFUNCIONAL', 'TROMBOSADO')),
    complicaciones TEXT,
    fecha_ultima_intervencion DATE,
    riesgo_disfuncion REAL,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
);

-- Tabla de medicamentos
CREATE TABLE IF NOT EXISTS medicamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    tipo TEXT CHECK (tipo IN ('AEE', 'HIERRO_IV', 'QUELANTE', 'VITAMINA_D')),
    dosis TEXT,
    via TEXT CHECK (via IN ('IV', 'SC', 'VO')),
    frecuencia TEXT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    activo BOOLEAN DEFAULT 1,
    indicacion TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
);

-- Tabla de alertas
CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('CRITICA', 'MODERADA', 'PREVENTIVA')),
    categoria TEXT CHECK (categoria IN ('ANEMIA', 'MINERAL_OSEO', 'ACCESO_VASCULAR', 'ADECUACION')),
    mensaje TEXT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion DATETIME,
    resuelta BOOLEAN DEFAULT 0,
    prioridad INTEGER DEFAULT 1 CHECK (prioridad BETWEEN 1 AND 5),
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_pacientes_documento ON pacientes(documento);
CREATE INDEX IF NOT EXISTS idx_pacientes_activo ON pacientes(activo);
CREATE INDEX IF NOT EXISTS idx_sesiones_paciente_fecha ON sesiones_dialisis(paciente_id, fecha);
CREATE INDEX IF NOT EXISTS idx_laboratorios_paciente_fecha ON laboratorios(paciente_id, fecha);
CREATE INDEX IF NOT EXISTS idx_accesos_paciente ON accesos_vasculares(paciente_id);
CREATE INDEX IF NOT EXISTS idx_alertas_activas ON alertas(resuelta, prioridad);
CREATE INDEX IF NOT EXISTS idx_alertas_paciente ON alertas(paciente_id, resuelta);

-- Insertar datos de ejemplo
INSERT OR IGNORE INTO pacientes (
    documento, tipo_documento, nombres, apellidos, fecha_nacimiento, 
    genero, telefono, eps, fecha_inicio_hd, causa_erc, comorbilidades
) VALUES 
('12345678', 'CC', 'María Elena', 'González López', '1965-03-15', 
 'F', '3001234567', 'Nueva EPS', '2022-06-10', 'Diabetes Mellitus tipo 2', 'Hipertensión arterial, Diabetes tipo 2'),
('87654321', 'CC', 'Carlos Andrés', 'Rodríguez Martín', '1958-08-22', 
 'M', '3109876543', 'Sanitas EPS', '2021-11-05', 'Nefropatía hipertensiva', 'Hipertensión arterial, Cardiopatía isquémica'),
('45678912', 'CC', 'Ana Lucia', 'Pérez Silva', '1972-12-03', 
 'F', '3156789012', 'SURA EPS', '2023-01-18', 'Glomerulonefritis crónica', 'Anemia crónica');

-- Insertar laboratorios de ejemplo
INSERT OR IGNORE INTO laboratorios (
    paciente_id, fecha, hemoglobina, ferritina, tsat, calcio, fosforo, pth
) VALUES 
(1, '2024-01-15', 10.2, 280, 22, 9.1, 4.8, 220),
(1, '2024-02-15', 9.8, 320, 25, 9.3, 5.2, 195),
(2, '2024-01-15', 11.1, 450, 28, 8.9, 4.5, 180),
(2, '2024-02-15', 10.9, 420, 26, 9.0, 4.7, 165),
(3, '2024-01-15', 9.5, 180, 18, 9.2, 5.1, 280),
(3, '2024-02-15', 10.1, 240, 21, 9.4, 4.9, 250);

-- Insertar sesiones de diálisis de ejemplo
INSERT OR IGNORE INTO sesiones_dialisis (
    paciente_id, fecha, turno, peso_pre, peso_post, peso_seco, 
    qb, tiempo_sesion, uf_programada, uf_real, kt_v, pru
) VALUES 
(1, '2024-02-20', 'LMV_MAÑANA', 72.5, 69.8, 69.0, 400, 240, 2.7, 2.7, 1.4, 72),
(1, '2024-02-22', 'LMV_MAÑANA', 71.8, 69.5, 69.0, 400, 240, 2.3, 2.3, 1.5, 75),
(2, '2024-02-20', 'MJS_TARDE', 78.2, 75.0, 74.5, 420, 240, 3.2, 3.2, 1.3, 70),
(2, '2024-02-22', 'MJS_TARDE', 77.8, 74.8, 74.5, 420, 240, 3.0, 3.0, 1.4, 73),
(3, '2024-02-20', 'LMV_TARDE', 65.5, 63.2, 62.8, 380, 240, 2.3, 2.3, 1.2, 68),
(3, '2024-02-22', 'LMV_TARDE', 64.8, 62.9, 62.8, 380, 240, 1.9, 1.9, 1.3, 71);

-- Insertar accesos vasculares de ejemplo
INSERT OR IGNORE INTO accesos_vasculares (
    paciente_id, tipo_acceso, localizacion, fecha_creacion, fecha_evaluacion,
    fremito, soplo, qa_flujo, presion_intraacceso, recirculacion, estado, riesgo_disfuncion
) VALUES 
(1, 'FAV_NATIVA', 'Radiocefálica izquierda', '2022-04-15', '2024-02-15', 'PRESENTE', 'NORMAL', 850, 45, 5, 'FUNCIONAL', 0.2),
(2, 'FAV_NATIVA', 'Braquiocefálica derecha', '2021-09-10', '2024-02-15', 'PRESENTE', 'NORMAL', 920, 42, 7, 'FUNCIONAL', 0.15),
(3, 'CATETER_PERMANENTE', 'Yugular interna derecha', '2023-01-10', '2024-02-15', 'NO_APLICA', 'NO_APLICA', 0, 0, 0, 'FUNCIONAL', 0.3);

-- Insertar alertas de ejemplo
INSERT OR IGNORE INTO alertas (
    paciente_id, tipo, categoria, mensaje, prioridad
) VALUES 
(1, 'MODERADA', 'ANEMIA', 'Hemoglobina: 10.2 g/dl. Evaluar incremento de AEE.', 3),
(2, 'PREVENTIVA', 'ACCESO_VASCULAR', 'Flujo de acceso: 920 ml/min. Seguimiento rutinario.', 1),
(3, 'CRITICA', 'ANEMIA', 'Hemoglobina: 9.5 g/dl. Considerar ajuste urgente de tratamiento.', 4);