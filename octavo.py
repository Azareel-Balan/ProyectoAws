from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:proyecto2@prueba.cn2w6gu2q9i3.us-east-1.rds.amazonaws.com/prueba'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definición de modelos
class Alumno(db.Model):
    __tablename__ = 'alumnos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(50), nullable=False, unique=True)
    promedio = db.Column(db.Float, nullable=False)
    fotoPerfilUrl = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)

class Profesor(db.Model):
    __tablename__ = 'profesores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numeroEmpleado = db.Column(db.String(50), nullable=False, unique=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    horasClase = db.Column(db.Integer, nullable=False)

# Crear las tablas en la base de datos al inicio de la aplicación
with app.app_context():
    db.create_all()

# Validaciones de campos
def validate_alumno(data):
    required_fields = ['nombres', 'apellidos', 'matricula', 'promedio', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"El campo {field} es requerido y no puede estar vacío."
    if not isinstance(data['promedio'], (int, float)) or data['promedio'] < 0 or data['promedio'] > 10:
        return False, "El promedio debe ser un número entre 0 y 10."
    return True, ""

def validate_profesor(data):
    required_fields = ['nombres', 'apellidos', 'numeroEmpleado', 'horasClase']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"El campo {field} es requerido y no puede estar vacío."
    if not isinstance(data['horasClase'], int) or data['horasClase'] < 0:
        return False, "Las horas de clase deben ser un número entero positivo."
    return True, ""

# Endpoints de alumnos
@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    alumnos = Alumno.query.all()
    return jsonify([{
        'id': alumno.id,
        'nombres': alumno.nombres,
        'apellidos': alumno.apellidos,
        'matricula': alumno.matricula,
        'promedio': alumno.promedio,
        'fotoPerfilUrl': alumno.fotoPerfilUrl
    } for alumno in alumnos]), 200

@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404
    return jsonify({
        'id': alumno.id,
        'nombres': alumno.nombres,
        'apellidos': alumno.apellidos,
        'matricula': alumno.matricula,
        'promedio': alumno.promedio,
        'fotoPerfilUrl': alumno.fotoPerfilUrl
    }), 200

@app.route('/alumnos', methods=['POST'])
def create_alumno():
    data = request.get_json()
    is_valid, error_message = validate_alumno(data)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    nuevo_alumno = Alumno(
        nombres=data['nombres'],
        apellidos=data['apellidos'],
        matricula=data['matricula'],
        promedio=data['promedio'],
        password=data['password']
    )
    try:
        db.session.add(nuevo_alumno)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Matrícula ya existente"}), 400
    return jsonify({
        'id': nuevo_alumno.id,
        'nombres': nuevo_alumno.nombres,
        'apellidos': nuevo_alumno.apellidos,
        'matricula': nuevo_alumno.matricula,
        'promedio': nuevo_alumno.promedio
    }), 201

@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    data = request.get_json()
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404
    is_valid, error_message = validate_alumno(data)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    alumno.nombres = data.get('nombres', alumno.nombres)
    alumno.apellidos = data.get('apellidos', alumno.apellidos)
    alumno.matricula = data.get('matricula', alumno.matricula)
    alumno.promedio = data.get('promedio', alumno.promedio)
    alumno.password = data.get('password', alumno.password)
    db.session.commit()
    return jsonify({
        'id': alumno.id,
        'nombres': alumno.nombres,
        'apellidos': alumno.apellidos,
        'matricula': alumno.matricula,
        'promedio': alumno.promedio
    }), 200

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404
    db.session.delete(alumno)
    db.session.commit()
    return '', 200

# Endpoint para enviar email
@app.route('/alumnos/<int:id>/email', methods=['POST'])
def send_email(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404
    
    # Simulación de envío de email
    email_sent = True  # Cambia esto según la lógica real de envío de email

    if email_sent:
        return jsonify({"message": "Email enviado exitosamente"}), 200
    else:
        return jsonify({"error": "Error al enviar el email"}), 500

# Endpoints de profesores
@app.route('/profesores', methods=['GET'])
def get_profesores():
    profesores = Profesor.query.all()
    return jsonify([{
        'id': profesor.id,
        'nombres': profesor.nombres,
        'apellidos': profesor.apellidos,
        'numeroEmpleado': profesor.numeroEmpleado,
        'horasClase': profesor.horasClase
    } for profesor in profesores]), 200

@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor(id):
    profesor = Profesor.query.get(id)
    if not profesor:
        return jsonify({"error": "Profesor no encontrado"}), 404
    return jsonify({
        'id': profesor.id,
        'nombres': profesor.nombres,
        'apellidos': profesor.apellidos,
        'numeroEmpleado': profesor.numeroEmpleado,
        'horasClase': profesor.horasClase
    }), 200

@app.route('/profesores', methods=['POST'])
def create_profesor():
    data = request.get_json()
    is_valid, error_message = validate_profesor(data)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    nuevo_profesor = Profesor(
        nombres=data['nombres'],
        apellidos=data['apellidos'],
        numeroEmpleado=data['numeroEmpleado'],
        horasClase=data['horasClase']
    )
    try:
        db.session.add(nuevo_profesor)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Número de empleado ya existente"}), 400
    return jsonify({
        'id': nuevo_profesor.id,
        'nombres': nuevo_profesor.nombres,
        'apellidos': nuevo_profesor.apellidos,
        'numeroEmpleado': nuevo_profesor.numeroEmpleado,
        'horasClase': nuevo_profesor.horasClase
    }), 201

@app.route('/profesores/<int:id>', methods=['PUT'])
def update_profesor(id):
    data = request.get_json()
    profesor = Profesor.query.get(id)
    if not profesor:
        return jsonify({"error": "Profesor no encontrado"}), 404
    is_valid, error_message = validate_profesor(data)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    profesor.nombres = data.get('nombres', profesor.nombres)
    profesor.apellidos = data.get('apellidos', profesor.apellidos)
    profesor.numeroEmpleado = data.get('numeroEmpleado', profesor.numeroEmpleado)
    profesor.horasClase = data.get('horasClase', profesor.horasClase)
    db.session.commit()
    return jsonify({
        'id': profesor.id,
        'nombres': profesor.nombres,
        'apellidos': profesor.apellidos,
        'numeroEmpleado': profesor.numeroEmpleado,
        'horasClase': profesor.horasClase
    }), 200

@app.route('/profesores/<int:id>', methods=['DELETE'])
def delete_profesor(id):
    profesor = Profesor.query.get(id)
    if not profesor:
        return jsonify({"error": "Profesor no encontrado"}), 404
    db.session.delete(profesor)
    db.session.commit()
    return '', 200

# Manejo de errores generales
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Error interno del servidor"}), 500

# Ejecución de la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
