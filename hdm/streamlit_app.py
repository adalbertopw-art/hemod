from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'dialisis_secret_key_2023'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dialisis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos de base de datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # nefrologo, enfermeria, medico
    name = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identificacion = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    sexo = db.Column(db.String(10), nullable=False)
    fecha_ingreso = db.Column(db.DateTime, nullable=False)
    turnos = db.Column(db.String(200), nullable=False)  # JSON con turnos asignados
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Paciente {self.nombre}>'

class Laboratorio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    hb = db.Column(db.Float)  # Hemoglobina
    hto = db.Column(db.Float)  # Hematocrito
    ferritina = db.Column(db.Float)
    tsat = db.Column(db.Float)  # Saturación de transferrina
    fosforo = db.Column(db.Float)
    calcio = db.Column(db.Float)
    pth = db.Column(db.Float)  # Hormona paratiroidea
    albumin = db.Column(db.Float)
    kt_v = db.Column(db.Float)  # Kt/V
    usuario_registro = db.Column(db.String(100), nullable=False)

    paciente = db.relationship('Paciente', backref=db.backref('laboratorios', lazy=True))

class Tratamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tipo = db.Column(db.String(20), nullable=False)  # ESA, Hierro, Calcio, etc.
    dosis = db.Column(db.Float, nullable=False)
    frecuencia = db.Column(db.String(50), nullable=False)
    usuario_registro = db.Column(db.String(100), nullable=False)

    paciente = db.relationship('Paciente', backref=db.backref('tratamientos', lazy=True))

class AccesoVascular(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tipo = db.Column(db.String(50), nullable=False)  # FAV, Catéter, etc.
    localizacion = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), nullable=False)  # Funcionando, Problemas, etc.
    usuario_registro = db.Column(db.String(100), nullable=False)

    paciente = db.relationship('Paciente', backref=db.backref('accesos_vascular', lazy=True))

class HistorialCambios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tabla_afectada = db.Column(db.String(50), nullable=False)
    registro_id = db.Column(db.Integer, nullable=False)
    accion = db.Column(db.String(10), nullable=False)  # INSERT, UPDATE, DELETE
    usuario = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    datos_anteriores = db.Column(db.Text)
    datos_nuevos = db.Column(db.Text)

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para requerir roles específicos
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if user.role not in roles:
                flash('No tiene permisos para acceder a esta página', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rutas de la aplicación
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session['user_name'] = user.name

            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Ha cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Obtener pacientes con alertas
    pacientes = Paciente.query.filter_by(activo=True).all()
    pacientes_con_alertas = []

    for paciente in pacientes:
        alertas = obtener_alertas_paciente(paciente.id)
        if alertas:
            pacientes_con_alertas.append({
                'paciente': paciente,
                'alertas': alertas
            })

    return render_template('dashboard.html', pacientes_alertas=pacientes_con_alertas)

@app.route('/pacientes')
@login_required
def pacientes():
    vista = request.args.get('vista', 'tarjetas')
    pacientes = Paciente.query.filter_by(activo=True).all()
    return render_template('pacientes.html', pacientes=pacientes, vista=vista)

@app.route('/paciente/<int:id>')
@login_required
def paciente_detalle(id):
    paciente = Paciente.query.get_or_404(id)
    laboratorios = Laboratorio.query.filter_by(paciente_id=id).order_by(Laboratorio.fecha.desc()).all()
    tratamientos = Tratamiento.query.filter_by(paciente_id=id).order_by(Tratamiento.fecha.desc()).all()
    accesos = AccesoVascular.query.filter_by(paciente_id=id).order_by(AccesoVascular.fecha.desc()).all()

    # Obtener recomendaciones
    recomendaciones_anemia = generar_recomendaciones_anemia(id)
    recomendaciones_hueso = generar_recomendaciones_hueso(id)

    return render_template('paciente_detalle.html', 
                         paciente=paciente, 
                         laboratorios=laboratorios,
                         tratamientos=tratamientos,
                         accesos=accesos,
                         recomendaciones_anemia=recomendaciones_anemia,
                         recomendaciones_hueso=recomendaciones_hueso)

@app.route('/paciente/nuevo', methods=['GET', 'POST'])
@login_required
@role_required(['nefrologo', 'enfermeria'])
def paciente_nuevo():
    if request.method == 'POST':
        try:
            # Procesar datos del formulario
            identificacion = request.form['identificacion']
            nombre = request.form['nombre']
            edad = int(request.form['edad'])
            sexo = request.form['sexo']
            fecha_ingreso = datetime.strptime(request.form['fecha_ingreso'], '%Y-%m-%d')

            # Procesar turnos
            turnos = {}
            dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado']
            turnos_disponibles = ['manana', 'tarde', 'noche']

            for dia in dias:
                turnos[dia] = request.form.get(f'turno_{dia}', 'no_asignado')

            # Crear nuevo paciente
            nuevo_paciente = Paciente(
                identificacion=identificacion,
                nombre=nombre,
                edad=edad,
                sexo=sexo,
                fecha_ingreso=fecha_ingreso,
                turnos=json.dumps(turnos)
            )

            db.session.add(nuevo_paciente)
            db.session.commit()

            # Registrar en historial
            registro_historial('Paciente', nuevo_paciente.id, 'INSERT', session['username'], 
                              datos_nuevos=str(nuevo_paciente.__dict__))

            flash('Paciente creado exitosamente', 'success')
            return redirect(url_for('pacientes'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear paciente: {str(e)}', 'danger')

    return render_template('paciente_form.html', paciente=None)

@app.route('/laboratorio/nuevo/<int:paciente_id>', methods=['POST'])
@login_required
@role_required(['nefrologo', 'enfermeria'])
def laboratorio_nuevo(paciente_id):
    try:
        # Obtener datos del formulario
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
        hb = float(request.form['hb']) if request.form['hb'] else None
        hto = float(request.form['hto']) if request.form['hto'] else None
        ferritina = float(request.form['ferritina']) if request.form['ferritina'] else None
        tsat = float(request.form['tsat']) if request.form['tsat'] else None
        fosforo = float(request.form['fosforo']) if request.form['fosforo'] else None
        calcio = float(request.form['calcio']) if request.form['calcio'] else None
        pth = float(request.form['pth']) if request.form['pth'] else None
        albumin = float(request.form['albumin']) if request.form['albumin'] else None
        kt_v = float(request.form['kt_v']) if request.form['kt_v'] else None

        # Crear nuevo registro de laboratorio
        nuevo_lab = Laboratorio(
            paciente_id=paciente_id,
            fecha=fecha,
            hb=hb,
            hto=hto,
            ferritina=ferritina,
            tsat=tsat,
            fosforo=fosforo,
            calcio=calcio,
            pth=pth,
            albumin=albumin,
            kt_v=kt_v,
            usuario_registro=session['username']
        )

        db.session.add(nuevo_lab)
        db.session.commit()

        # Registrar en historial
        registro_historial('Laboratorio', nuevo_lab.id, 'INSERT', session['username'], 
                          datos_nuevos=str(nuevo_lab.__dict__))

        flash('Laboratorio registrado exitosamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar laboratorio: {str(e)}', 'danger')

    return redirect(url_for('paciente_detalle', id=paciente_id))

@app.route('/tratamiento/nuevo/<int:paciente_id>', methods=['POST'])
@login_required
@role_required(['nefrologo'])
def tratamiento_nuevo(paciente_id):
    try:
        # Obtener datos del formulario
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
        tipo = request.form['tipo']
        dosis = float(request.form['dosis'])
        frecuencia = request.form['frecuencia']

        # Crear nuevo tratamiento
        nuevo_tratamiento = Tratamiento(
            paciente_id=paciente_id,
            fecha=fecha,
            tipo=tipo,
            dosis=dosis,
            frecuencia=frecuencia,
            usuario_registro=session['username']
        )

        db.session.add(nuevo_tratamiento)
        db.session.commit()

        # Registrar en historial
        registro_historial('Tratamiento', nuevo_tratamiento.id, 'INSERT', session['username'], 
                          datos_nuevos=str(nuevo_tratamiento.__dict__))

        flash('Tratamiento registrado exitosamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar tratamiento: {str(e)}', 'danger')

    return redirect(url_for('paciente_detalle', id=paciente_id))

@app.route('/acceso/nuevo/<int:paciente_id>', methods=['POST'])
@login_required
@role_required(['nefrologo', 'enfermeria'])
def acceso_nuevo(paciente_id):
    try:
        # Obtener datos del formulario
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
        tipo = request.form['tipo']
        localizacion = request.form['localizacion']
        estado = request.form['estado']

        # Crear nuevo acceso vascular
        nuevo_acceso = AccesoVascular(
            paciente_id=paciente_id,
            fecha=fecha,
            tipo=tipo,
            localizacion=localizacion,
            estado=estado,
            usuario_registro=session['username']
        )

        db.session.add(nuevo_acceso)
        db.session.commit()

        # Registrar en historial
        registro_historial('AccesoVascular', nuevo_acceso.id, 'INSERT', session['username'], 
                          datos_nuevos=str(nuevo_acceso.__dict__))

        flash('Acceso vascular registrado exitosamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar acceso vascular: {str(e)}', 'danger')

    return redirect(url_for('paciente_detalle', id=paciente_id))

@app.route('/historial')
@login_required
@role_required(['nefrologo'])
def historial():
    cambios = HistorialCambios.query.order_by(HistorialCambios.fecha.desc()).all()
    return render_template('historial.html', cambios=cambios)

# Funciones auxiliares
def obtener_alertas_paciente(paciente_id):
    alertas = []

    # Obtener el último laboratorio
    ultimo_lab = Laboratorio.query.filter_by(paciente_id=paciente_id).order_by(Laboratorio.fecha.desc()).first()

    if not ultimo_lab:
        return ["No hay datos de laboratorio"]

    # Verificar valores fuera de rango
    if ultimo_lab.hb and (ultimo_lab.hb < 10 or ultimo_lab.hb > 12):
        alertas.append(f"Hemoglobina fuera de rango: {ultimo_lab.hb} g/dL")

    if ultimo_lab.ferritina and ultimo_lab.ferritina < 200:
        alertas.append(f"Ferritina baja: {ultimo_lab.ferritina} ng/mL")

    if ultimo_lab.tsat and ultimo_lab.tsat < 20:
        alertas.append(f"TSAT bajo: {ultimo_lab.tsat}%")

    if ultimo_lab.fosforo and (ultimo_lab.fosforo < 3.5 or ultimo_lab.fosforo > 5.5):
        alertas.append(f"Fósforo fuera de rango: {ultimo_lab.fosforo} mg/dL")

    if ultimo_lab.calcio and (ultimo_lab.calcio < 8.4 or ultimo_lab.calcio > 10.2):
        alertas.append(f"Calcio fuera de rango: {ultimo_lab.calcio} mg/dL")

    if ultimo_lab.pth and (ultimo_lab.pth < 150 or ultimo_lab.pth > 600):
        alertas.append(f"PTH fuera de rango: {ultimo_lab.pth} pg/mL")

    return alertas

def generar_recomendaciones_anemia(paciente_id):
    recomendaciones = []

    # Obtener el último laboratorio
    ultimo_lab = Laboratorio.query.filter_by(paciente_id=paciente_id).order_by(Laboratorio.fecha.desc()).first()

    if not ultimo_lab:
        return ["No hay datos suficientes para generar recomendaciones"]

    # Recomendaciones basadas en ACM de Fresenius
    if ultimo_lab.hb and ultimo_lab.hb < 10:
        recomendaciones.append("Ajustar dosis de ESA para incrementar hemoglobina")
    elif ultimo_lab.hb and ultimo_lab.hb > 12:
        recomendaciones.append("Reducir dosis de ESA para disminuir hemoglobina")

    if ultimo_lab.ferritina and ultimo_lab.ferritina < 200:
        recomendaciones.append("Suplementar hierro intravenoso")

    if ultimo_lab.tsat and ultimo_lab.tsat < 20:
        recomendaciones.append("Evaluar suplementación adicional de hierro")

    # Obtener tratamientos actuales de ESA
    tratamientos_esa = Tratamiento.query.filter_by(
        paciente_id=paciente_id, 
        tipo='ESA'
    ).order_by(Tratamiento.fecha.desc()).all()

    if not tratamientos_esa:
        recomendaciones.append("Considerar iniciar terapia con ESA")

    return recomendaciones if recomendaciones else ["Parámetros dentro de rangos objetivos"]

def generar_recomendaciones_hueso(paciente_id):
    recomendaciones = []

    # Obtener el último laboratorio
    ultimo_lab = Laboratorio.query.filter_by(paciente_id=paciente_id).order_by(Laboratorio.fecha.desc()).first()

    if not ultimo_lab:
        return ["No hay datos suficientes para generar recomendaciones"]

    # Recomendaciones basadas en KDIGO
    if ultimo_lab.fosforo and ultimo_lab.fosforo > 5.5:
        recomendaciones.append("Iniciar o ajustar quelantes de fósforo")
        recomendaciones.append("Reforzar educación sobre restricción dietética de fósforo")

    if ultimo_lab.calcio and ultimo_lab.calcio > 10.2:
        recomendaciones.append("Evaluar uso de calcimiméticos")
        recomendaciones.append("Considerar reducir o suspender suplementos de calcio")

    if ultimo_lab.pth and ultimo_lab.pth > 600:
        recomendaciones.append("Considerar tratamiento con calcimiméticos o vitamina D activa")

    if ultimo_lab.pth and ultimo_lab.pth < 150:
        recomendaciones.append("Evaluar posible adinamia ósea")
        recomendaciones.append("Considerar ajuste de terapia con vitamina D")

    return recomendaciones if recomendaciones else ["Parámetros de MBD dentro de rangos objetivos"]

def registro_historial(tabla, registro_id, accion, usuario, datos_anteriores=None, datos_nuevos=None):
    cambio = HistorialCambios(
        tabla_afectada=tabla,
        registro_id=registro_id,
        accion=accion,
        usuario=usuario,
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos
    )
    db.session.add(cambio)
    db.session.commit()

# Inicializar base de datos con datos de ejemplo
def init_db():
    with app.app_context():
        db.create_all()

        # Crear usuarios por defecto si no existen
        if not User.query.filter_by(username='nefrologo').first():
            nefrologo = User(username='nefrologo', name='Dr. Nefrólogo', role='nefrologo')
            nefrologo.set_password('nefro123')
            db.session.add(nefrologo)

        if not User.query.filter_by(username='enfermeria').first():
            enfermeria = User(username='enfermeria', name='Enfermera Principal', role='enfermeria')
            enfermeria.set_password('enfermeria123')
            db.session.add(enfermeria)

        if not User.query.filter_by(username='medico').first():
            medico = User(username='medico', name='Dr. General', role='medico')
            medico.set_password('medico123')
            db.session.add(medico)

        db.session.commit()

        # Crear pacientes de ejemplo si no existen
        if not Paciente.query.first():
            # Crear 5 pacientes de ejemplo
            pacientes_ejemplo = [
                {
                    'identificacion': '123456789',
                    'nombre': 'Juan Pérez',
                    'edad': 65,
                    'sexo': 'Masculino',
                    'fecha_ingreso': datetime(2022, 1, 15),
                    'turnos': json.dumps({
                        'lunes': 'manana', 'martes': 'no_asignado', 
                        'miercoles': 'tarde', 'jueves': 'no_asignado',
                        'viernes': 'noche', 'sabado': 'no_asignado'
                    })
                },
                {
                    'identificacion': '987654321',
                    'nombre': 'María García',
                    'edad': 58,
                    'sexo': 'Femenino',
                    'fecha_ingreso': datetime(2022, 3, 22),
                    'turnos': json.dumps({
                        'lunes': 'no_asignado', 'martes': 'tarde', 
                        'miercoles': 'no_asignado', 'jueves': 'manana',
                        'viernes': 'no_asignado', 'sabado': 'noche'
                    })
                }
            ]

            for datos in pacientes_ejemplo:
                paciente = Paciente(**datos)
                db.session.add(paciente)

            db.session.commit()

            # Agregar algunos datos de laboratorio
            laboratorios_ejemplo = [
                {
                    'paciente_id': 1,
                    'fecha': datetime(2023, 10, 15),
                    'hb': 9.5,
                    'ferritina': 180,
                    'tsat': 18,
                    'fosforo': 6.2,
                    'calcio': 8.8,
                    'pth': 450,
                    'usuario_registro': 'nefrologo'
                },
                {
                    'paciente_id': 2,
                    'fecha': datetime(2023, 10, 16),
                    'hb': 11.8,
                    'ferritina': 350,
                    'tsat': 25,
                    'fosforo': 4.8,
                    'calcio': 9.2,
                    'pth': 280,
                    'usuario_registro': 'nefrologo'
                }
            ]

            for datos in laboratorios_ejemplo:
                lab = Laboratorio(**datos)
                db.session.add(lab)

            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
