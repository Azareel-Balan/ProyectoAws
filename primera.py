from flask import Flask, request, jsonify

app = Flask(__name__)

# Arrays en memoria para almacenar los objetos
alumnos = []
profesores = []

# Funciones de validación
def validar_alumno(data):
    required_fields = ['id', 'nombres', 'apellidos', 'matricula', 'promedio']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"El campo {field} es obligatorio y no puede estar vacío."
    if not isinstance(data['promedio'], (int, float)):
        return False, "El promedio debe ser un número."
    return True, ""

def validar_profesor(data):
    required_fields = ['id', 'numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"El campo {field} es obligatorio y no puede estar vacío."
    if not isinstance(data['horasClase'], int):
        return False, "Las horas de clase deben ser un número entero."
    return True, ""

# Endpoints para alumnos
@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    return jsonify(alumnos), 200

@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = next((a for a in alumnos if a['id'] == id), None)
    if alumno is None:
        return jsonify({"error": "Alumno no encontrado"}), 404
    return jsonify(alumno), 200

@app.route('/alumnos', methods=['POST'])
def create_alumno():
    data = request.get_json()
    is_valid, message = validar_alumno(data)
    if not is_valid:
        return jsonify({"error": message}), 400
    alumnos.append(data)
    return jsonify(data), 201

@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    data = request.get_json()
    is_valid, message = validar_alumno(data)
    if not is_valid:
        return jsonify({"error": message}), 400
    alumno = next((a for a in alumnos if a['id'] == id), None)
    if alumno is None:
        return jsonify({"error": "Alumno no encontrado"}), 404
    alumno.update(data)
    return jsonify(alumno), 200

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    global alumnos
    alumno = next((a for a in alumnos if a['id'] == id), None)
    if alumno is None:
        return jsonify({"error": "Alumno no encontrado"}), 404
    alumnos = [a for a in alumnos if a['id'] != id]
    return '', 200

# Endpoints para profesores
@app.route('/profesores', methods=['GET'])
def get_profesores():
    return jsonify(profesores), 200

@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor(id):
    profesor = next((p for p in profesores if p['id'] == id), None)
    if profesor is None:
        return jsonify({"error": "Profesor no encontrado"}), 404
    return jsonify(profesor), 200

@app.route('/profesores', methods=['POST'])
def create_profesor():
    data = request.get_json()
    is_valid, message = validar_profesor(data)
    if not is_valid:
        return jsonify({"error": message}), 400
    profesores.append(data)
    return jsonify(data), 201

@app.route('/profesores/<int:id>', methods=['PUT'])
def update_profesor(id):
    data = request.get_json()
    is_valid, message = validar_profesor(data)
    if not is_valid:
        return jsonify({"error": message}), 400
    profesor = next((p for p in profesores if p['id'] == id), None)
    if profesor is None:
        return jsonify({"error": "Profesor no encontrado"}), 404
    profesor.update(data)
    return jsonify(profesor), 200

@app.route('/profesores/<int:id>', methods=['DELETE'])
def delete_profesor(id):
    global profesores
    profesor = next((p for p in profesores if p['id'] == id), None)
    if profesor is None:
        return jsonify({"error": "Profesor no encontrado"}), 404
    profesores = [p for p in profesores if p['id'] != id]
    return '', 200

# Manejo de métodos no soportados
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Método no permitido"}), 405

# Manejo de rutas no encontradas
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ruta no encontrada"}), 404

if __name__ == '__main__':
    app.run(debug=True)
