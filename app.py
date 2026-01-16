from flask import Flask, render_template, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database connection configuration
DB_HOST = "192.168.100.227"
DB_PORT = "5437"
DB_NAME = "prueba"
DB_USER = "athena"
DB_PASS = "athena"

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list/alumnos', methods=['GET'])
def list_alumnos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT cedula, nombre, apellidos FROM "consulata_Institucion".alumnos')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        alumnos = [{'cedula': r[0], 'nombre': r[1], 'apellidos': r[2]} for r in rows]
        return jsonify(alumnos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list/cursos', methods=['GET'])
def list_cursos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT paralelo FROM "consulata_Institucion".cursos')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        cursos = [{'paralelo': r[0]} for r in rows]
        return jsonify(cursos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insert/alumnos', methods=['POST'])
def insert_alumnos():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO "consulata_Institucion".alumnos (nombre, apellidos, cedula) VALUES (%s, %s, %s)',
            (data['nombre'], data['apellidos'], data['cedula'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Alumno insertado correctamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insert/cursos', methods=['POST'])
def insert_cursos():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO "consulata_Institucion".cursos (paralelo, "DC_tutor") VALUES (%s, %s)',
            (data['paralelo'], data['dc_tutor'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Curso insertado correctamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insert/alumnos_cursos', methods=['POST'])
def insert_alumnos_cursos():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Calculate next ID
        cur.execute('SELECT COALESCE(MAX("ID_tabla"), 0) + 1 FROM "consulata_Institucion".alumnos_cursos')
        next_id = cur.fetchone()[0]
        
        cur.execute(
            'INSERT INTO "consulata_Institucion".alumnos_cursos (paralelo, cedula_alumnos, "ID_tabla") VALUES (%s, %s, %s)',
            (data['paralelo'], data['cedula_alumnos'], next_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': f'Relación Alumno-Curso insertada correctamente con ID {next_id}'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
