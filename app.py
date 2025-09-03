from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE = 'hemodialysis.db'

def init_db():
    """Inicializar base de datos con datos de ejemplo"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Crear tabla de pacientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            documento TEXT UNIQUE NOT NULL,
            tipo_documento TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            fecha_nacimiento DATE NOT NULL,
            genero TEXT NOT NULL,
            telefono TEXT,
            eps TEXT,
            fecha_inicio_hd DATE NOT NULL,
            causa_erc TEXT,
            comorbilidades TEXT,
            activo BOOLEAN DEFAULT 1,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Crear tabla de laboratorios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS laboratorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            fecha DATETIME NOT NULL,
            hemoglobina REAL,
            ferritina REAL,
            tsat REAL,
            calcio REAL,
            fosforo REAL,
            pth REAL,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    # Crear tabla de alertas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            resuelta BOOLEAN DEFAULT 0,
            prioridad INTEGER DEFAULT 1,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    # Insertar datos de ejemplo si no existen
    cursor.execute("SELECT COUNT(*) FROM pacientes")
    if cursor.fetchone()[0] == 0:
        # Pacientes de ejemplo
        pacientes_ejemplo = [
            ('12345678', 'CC', 'María Elena', 'González López', '1965-03-15', 
             'F', '3001234567', 'Nueva EPS', '2022-06-10', 'Diabetes Mellitus tipo 2', 
             'Hipertensión arterial, Diabetes tipo 2'),
            ('87654321', 'CC', 'Carlos Andrés', 'Rodríguez Martín', '1958-08-22', 
             'M', '3109876543', 'Sanitas EPS', '2021-11-05', 'Nefropatía hipertensiva', 
             'Hipertensión arterial, Cardiopatía isquémica'),
            ('45678912', 'CC', 'Ana Lucia', 'Pérez Silva', '1972-12-03', 
             'F', '3156789012', 'SURA EPS', '2023-01-18', 'Glomerulonefritis crónica', 
             'Anemia crónica')
        ]

        cursor.executemany("""
            INSERT INTO pacientes (documento, tipo_documento, nombres, apellidos, 
            fecha_nacimiento, genero, telefono, eps, fecha_inicio_hd, causa_erc, comorbilidades)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pacientes_ejemplo)

        # Laboratorios de ejemplo
        laboratorios_ejemplo = [
            (1, '2024-01-15', 10.2, 280, 22, 9.1, 4.8, 220),
            (1, '2024-02-15', 9.8, 320, 25, 9.3, 5.2, 195),
            (2, '2024-01-15', 11.1, 450, 28, 8.9, 4.5, 180),
            (2, '2024-02-15', 10.9, 420, 26, 9.0, 4.7, 165),
            (3, '2024-01-15', 9.5, 180, 18, 9.2, 5.1, 280),
            (3, '2024-02-15', 10.1, 240, 21, 9.4, 4.9, 250)
        ]

        cursor.executemany("""
            INSERT INTO laboratorios (paciente_id, fecha, hemoglobina, ferritina, 
            tsat, calcio, fosforo, pth) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, laboratorios_ejemplo)

        # Alertas de ejemplo
        alertas_ejemplo = [
            (1, 'MODERADA', 'ANEMIA', 'Hemoglobina: 10.2 g/dl. Evaluar incremento de AEE.', 3),
            (2, 'PREVENTIVA', 'ACCESO_VASCULAR', 'Seguimiento rutinario programado.', 1),
            (3, 'CRITICA', 'ANEMIA', 'Hemoglobina: 9.5 g/dl. Considerar ajuste urgente.', 4)
        ]

        cursor.executemany("""
            INSERT INTO alertas (paciente_id, tipo, categoria, mensaje, prioridad)
            VALUES (?, ?, ?, ?, ?)
        """, alertas_ejemplo)

    conn.commit()
    conn.close()

def get_db():
    """Obtener conexión a base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Rutas principales
@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Servir archivos estáticos"""
    return send_from_directory('static', filename)

# API Routes
@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Obtener todos los pacientes"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, documento, tipo_documento, nombres, apellidos, 
                   genero, eps, fecha_inicio_hd, causa_erc, activo,
                   (julianday('now') - julianday(fecha_nacimiento)) / 365.25 as edad,
                   (julianday('now') - julianday(fecha_inicio_hd)) / 30.44 as tiempo_dialisis_meses
            FROM pacientes WHERE activo = 1
            ORDER BY nombres, apellidos
        """)

        patients = []
        for row in cursor.fetchall():
            patients.append({
                'id': row['id'],
                'documento': f"{row['tipo_documento']} {row['documento']}",
                'nombres': row['nombres'],
                'apellidos': row['apellidos'],
                'edad': int(row['edad']) if row['edad'] else 0,
                'genero': row['genero'],
                'eps': row['eps'],
                'fecha_inicio_hd': row['fecha_inicio_hd'],
                'causa_erc': row['causa_erc'],
                'activo': bool(row['activo']),
                'tiempo_dialisis_meses': int(row['tiempo_dialisis_meses']) if row['tiempo_dialisis_meses'] else 0
            })

        conn.close()
        return jsonify(patients)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['POST'])
def create_patient():
    """Crear nuevo paciente"""
    try:
        data = request.get_json()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pacientes (documento, tipo_documento, nombres, apellidos, 
            fecha_nacimiento, genero, telefono, eps, fecha_inicio_hd, causa_erc, comorbilidades)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['documento'], data['tipo_documento'], data['nombres'], data['apellidos'],
            data['fecha_nacimiento'], data['genero'], data.get('telefono'),
            data.get('eps'), data['fecha_inicio_hd'], data.get('causa_erc'),
            data.get('comorbilidades')
        ))

        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({'id': patient_id, 'message': 'Paciente creado exitosamente'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Obtener alertas activas"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id, a.paciente_id, a.tipo, a.categoria, a.mensaje, 
                   a.fecha_creacion, a.prioridad,
                   p.nombres || ' ' || p.apellidos as paciente_nombre
            FROM alertas a
            JOIN pacientes p ON a.paciente_id = p.id
            WHERE a.resuelta = 0
            ORDER BY a.prioridad DESC, a.fecha_creacion DESC
            LIMIT 50
        """)

        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row['id'],
                'paciente_id': row['paciente_id'],
                'tipo': row['tipo'],
                'categoria': row['categoria'],
                'mensaje': row['mensaje'],
                'fecha_creacion': row['fecha_creacion'],
                'paciente_nombre': row['paciente_nombre'],
                'prioridad': row['prioridad']
            })

        conn.close()
        return jsonify(alerts)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Obtener paciente específico con laboratorios"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Datos del paciente
        cursor.execute("""
            SELECT *, (julianday('now') - julianday(fecha_nacimiento)) / 365.25 as edad
            FROM pacientes WHERE id = ? AND activo = 1
        """, (patient_id,))

        patient_row = cursor.fetchone()
        if not patient_row:
            return jsonify({'error': 'Paciente no encontrado'}), 404

        # Laboratorios
        cursor.execute("""
            SELECT * FROM laboratorios 
            WHERE paciente_id = ? 
            ORDER BY fecha DESC LIMIT 5
        """, (patient_id,))

        labs = [dict(row) for row in cursor.fetchall()]

        patient = {
            'id': patient_row['id'],
            'documento': f"{patient_row['tipo_documento']} {patient_row['documento']}",
            'nombres': patient_row['nombres'],
            'apellidos': patient_row['apellidos'],
            'edad': int(patient_row['edad']) if patient_row['edad'] else 0,
            'genero': patient_row['genero'],
            'eps': patient_row['eps'],
            'laboratorios': labs
        }

        conn.close()
        return jsonify(patient)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Inicializar base de datos
    init_db()

    # Ejecutar aplicación
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
