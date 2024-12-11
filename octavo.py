from flask_sqlalchemy import SQLAlchemy
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from boto3.dynamodb.conditions import Key
from flask import Flask, jsonify, request
import os
import boto3
import random
import string
import uuid
import time
app = Flask(__name__)

BASE_URL = "http://127.0.0.1:5000"

# Database
endpoint = "prueba.cn2w6gu2q9i3.us-east-1.rds.amazonaws.com"
username = "admin"
password = "proyecto2"
database_name = "prueba"


app.config['SQLALCHEMY_DATABASE_URI'] = (
  f'mysql+pymysql://{username}:{password}@{endpoint}:3306/{database_name}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# AWS Credenciales y Bucket 
AWS_ACCESS_KEY_ID = 'ASIARABZEU3KZEK4TSXQ'
AWS_SECRET_ACCESS_KEY = 'KUNulhQfQ4t6jLMoALtPZFJdIv8i3JHOOAbLl0VH'
AWS_SESSION_TOKEN = 'IQoJb3JpZ2luX2VjEOX//////////wEaCXVzLXdlc3QtMiJHMEUCIQDRcjcokq0hh/wkGHlXmh1gFvGeHaardzOz+S+ss/2KCgIgbTd3QovG97Uq9D70ZdFPPOJcrQD4elxSEzN4xrm0tqgqvwIInv//////////ARAAGgwwNjg4MzkzMTkyNTMiDN2NUGgqrqS95A88nCqTAoYSv1O+YxQwS57ih6BI48H++aNedK8ZFLJjsRcWxPxYdmTNgttjtHfNnZQB/Fv/7aPl9yjHVDzoZFjI9g1rvpTw5V+VL3luNKdl3ccLw2zICwO7CDHJzQxs3oNI7Nk9XJLi/5kU+yhQ3bMvg7+ZjSIjsaDt8C+9xIGRqQPbxM3/krkOr7y/2k+TlBRPFrHvizHHqC7iVC4S+4Vd9HsOAANm5xjFkCTtXyrr7kf2+8Vyf2v4i/ffpBgzjI+3vXceVurt6aBWp6WmSqwKM0yUH0BgzGDILuN2cjEjK6RJdiGOSUjsLBTi+EJ7MeyTps3asZhdlGIDxnclUL1t17+8Akg6HrRl+wS5j0wZmZNzlsVBldIjMO2r5LoGOp0BnW9ZkgdDduq22oZlXDL7YT2kPPHndW5/Zkq0LjxsuX8YvaJQ+PvwOhshZzTigyQI08AYIGT3rW7xpLAWK0E+BA5U3Wo4xq1fTe11uea3G+dKaJQbDdULcTgxDaGKZ414RJbiTE4iCOWZJn+cBFMDQOuM3Hs3J++ZTRS1HsxZ3epb6Hk/ya2cXd7JnWoH4xC8PXhlz1cmC1LtwF39yg=='
AWS_REGION = 'us-east-1'  
BUCKET_NAME = 'miproyecto2'

# AWS S3 
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION
)

# Client DynamoDB
dynamodb_client = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION
)
dynamodb_table = dynamodb_client.Table('sesiones-alumnos')
def generate_session_string(length=128):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Configuración de SNS
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:068839319253:proyec'

# Inicialización del cliente de SNS(llaves)
sns_client = boto3.client(
    'sns',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION
)

# Modelos
class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=True)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    promedio = db.Column(db.Float, nullable=True)
    password = db.Column(db.String(100), nullable=False)
    fotoPerfilUrl = db.Column(db.String(300), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "matricula": self.matricula,
            "promedio": self.promedio,
            "password": self.password,
            "fotoPerfilUrl": self.fotoPerfilUrl
        }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


class Profesor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=True)
    numeroEmpleado = db.Column(db.Integer, unique=True, nullable=False)
    horasClase = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "numeroEmpleado": self.numeroEmpleado,
            "horasClase": int(self.horasClase),  
        }


# Inicialización de base de datos
with app.app_context():
    db.create_all()

# Validación de funciones
def validate_alumno(data):
    return (
            isinstance(data.get('nombres'), str) and len(data['nombres']) > 0 and
            isinstance(data.get('matricula'), str) and len(data['matricula']) > 0 and
            (data.get('promedio') is None or isinstance(data['promedio'], (int, float))) and
            isinstance(data.get('password'), str) and len(data['password']) > 0
    )

def validate_profesor(data):
    return (
            isinstance(data.get('nombres'), str) and len(data['nombres']) > 0 and
            isinstance(data.get('numeroEmpleado'), int) and data['numeroEmpleado'] > 0 and
            isinstance(data.get('horasClase'), (int, float)) and data['horasClase'] >= 0
    )

# ROUTES de alumnos
@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    alumnos = Alumno.query.all()
    return jsonify([alumno.to_dict() for alumno in alumnos]), 200

@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno not found"}), 404
    return jsonify(alumno.to_dict()), 200

@app.route('/alumnos', methods=['POST'])
def create_alumno():
    data = request.get_json()
    if not validate_alumno(data):
        return jsonify({"error": "Invalid data"}), 400
    alumno = Alumno(**data)
    db.session.add(alumno)
    db.session.commit()
    return jsonify(alumno.to_dict()), 201

import logging

@app.route('/alumnos/<int:id>/fotoPerfil', methods=['POST'])
def upload_foto_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno not found"}), 404

    if 'foto' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    files = request.files
    if isinstance(files['foto'], tuple):
        return jsonify({"error": "Expected file, but got tuple instead"}), 400

    file = files['foto']

    if not file or not hasattr(file, 'filename') or not file.filename:
        return jsonify({"error": "Invalid file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    try:
        # Nombre del archivo S3
        filename = f"alumnos/{id}/{file.filename}"
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            filename,
            ExtraArgs={'ACL':'public-read'}
        )

        # URL publica
        fotoPerfilUrl = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"

    # Actualización en la base de datos
        alumno.fotoPerfilUrl = fotoPerfilUrl

        db.session.commit()

        return jsonify({"fotoPerfilUrl": fotoPerfilUrl}), 200

    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Error with AWS credentials: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno not found"}), 404

    data = request.get_json()
    if not validate_alumno(data):
        return jsonify({"error": "Invalid data"}), 400

    alumno.nombres = data.get('nombres', alumno.nombres)
    alumno.apellidos = data.get('apellidos', alumno.apellidos)
    alumno.matricula = data.get('matricula', alumno.matricula)
    alumno.promedio = data.get('promedio', alumno.promedio)
    alumno.password = data.get('password', alumno.password)

    db.session.commit()
    return jsonify(alumno.to_dict()), 200

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno not found"}), 404

    # Foto de perfil si existe
    if alumno.fotoPerfilUrl:
        try:
            filename = alumno.fotoPerfilUrl.split(f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/")[1]
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        except Exception as e:
            return jsonify({"error": f"Failed to delete profile picture: {str(e)}"}), 500

    # Verificar alumno
    db.session.delete(alumno)
    db.session.commit()
    return jsonify({"message": "Alumno deleted successfully"}), 200

@app.route('/alumnos/<int:id>/session/login', methods=['POST'])
def session_login(id):
    data = request.get_json()
    password = data.get('password')

    # Verificar base de datos
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno not found"}), 404

    # Verificar contraseña
    if alumno.password != password:
        return jsonify({"error": "Invalid password"}), 400

    # Información de session
    session_id = str(uuid.uuid4())
    session_string = generate_session_string()
    timestamp = int(time.time())

    # Session DynamoDB
    try:
        dynamodb_table.put_item(
            Item={
                "id": session_id,
                "fecha": timestamp,
                "alumnoId": id,
                "active": True,
                "sessionString": session_string
            }
        )
        return jsonify({"session_id": session_id, "sessionString": session_string}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to create session: {str(e)}"}), 500

@app.route('/alumnos/<int:id>/session/verify', methods=['POST'])
def session_verify(id):
    data = request.get_json()
    session_string = data.get('sessionString')

    # Session DynamoDB
    try:
        response = dynamodb_table.scan(
            FilterExpression=Key('alumnoId').eq(id) & Key('sessionString').eq(session_string)
        )
        if not response['Items']:
            return jsonify({"error": "Invalid session"}), 400

        session = response['Items'][0]
        if session['active']:
            return jsonify({"message": "Session is valid"}), 200
        else:
            return jsonify({"error": "Session is inactive"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to verify session: {str(e)}"}), 500

@app.route('/alumnos/<int:id>/session/logout', methods=['POST'])
def session_logout(id):
    data = request.get_json()
    session_string = data.get('sessionString')

    try:
        response = dynamodb_table.scan(
            FilterExpression=Key('alumnoId').eq(id) & Key('sessionString').eq(session_string)
        )
        if not response['Items']:
            return jsonify({"error": "Invalid session"}), 400

        session_id = response['Items'][0]['id']
        dynamodb_table.update_item(
            Key={'id': session_id},
            UpdateExpression="SET active = :inactive",
            ExpressionAttributeValues={':inactive': False}
        )
        return jsonify({"message": "Session terminated"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to logout: {str(e)}"}), 500

# ROUTES de profesores
@app.route('/profesores', methods=['GET'])
def get_profesores():
    profesores = Profesor.query.all()
    return jsonify([profesor.to_dict() for profesor in profesores]), 200

@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor(id):
    profesor = Profesor.query.get(id)
    if not profesor:
        return jsonify({"error": "Profesor not found"}), 404
    return jsonify(profesor.to_dict()), 200

@app.route('/profesores', methods=['POST'])
def create_profesor():
    data = request.get_json()
    if not validate_profesor(data):
        return jsonify({"error": "Invalid data"}), 400
    profesor = Profesor(**data)
    db.session.add(profesor)
    db.session.commit()
    return jsonify(profesor.to_dict()), 201

@app.route('/profesores/<int:id>', methods=['PUT'])
def update_profesor(id):
    profesor = Profesor.query.get(id)
    if not profesor:
        return jsonify({"error": "Profesor not found"}), 404
    data = request.get_json()
    if not validate_profesor(data):
        return jsonify({"error": "Invalid data"}), 400
    profesor.nombres = data['nombres']
    profesor.apellidos = data.get('apellidos', profesor.apellidos)
    profesor.numeroEmpleado = data['numeroEmpleado']
    profesor.horasClase = data['horasClase']
    db.session.commit()
    return jsonify(profesor.to_dict()), 200

@app.route('/profesores/<int:id>', methods=['DELETE'])
def delete_profesor(id):
    profesor = Profesor.query.get(id)
    if not profesor:
        return jsonify({"error": "Profesor not found"}), 404
    db.session.delete(profesor)
    db.session.commit()
    return jsonify({"message": "Profesor deleted"}), 200

@app.route('/alumnos/<int:id>/email', methods=['POST'])
def send_email_to_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno not found"}), 404
    message = (
        f"Información del Alumno:\n"
        f"Nombre: {alumno.nombres} {alumno.apellidos}\n"
        f"Matrícula: {alumno.matricula}\n"
        f"Promedio: {alumno.promedio}\n"
    )

    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=f"Notificación para {alumno.nombres} {alumno.apellidos}"
        )
        return jsonify({"message": "Notificación enviada exitosamente", "response": response}), 200
    except Exception as e:
        return jsonify({"error": f"No se pudo enviar la notificación: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
