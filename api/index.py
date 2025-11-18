from flask import Flask,render_template
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
CONNECTION_STRING = os.getenv("CONNECTION_STRING")
app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'


@app.route('/sensor')
def sensor():
    # Connect to the database
    try:
        connection = psycopg2.connect(CONNECTION_STRING)
        print("Connection successful!")
        
        # Create a cursor to execute SQL queries
        cursor = connection.cursor()
        
        # Example query
        cursor.execute("select * from sensores;")
        result = cursor.fetchone()
        print("Current Time:", result)

        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("Connection closed.")
        return f"Connection successful! {result}"

    except Exception as e:
        print(f"Failed to connect: {e}")
        return f"Failed to connect: {e}"

@app.route("/sensor/<int:sensor_id>")
def get_sensor(sensor_id):
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        cur = conn.cursor()

        # Get the latest 10 values
        cur.execute("""
            SELECT value, created_at
            FROM sensores
            WHERE sensor_id = %s
            ORDER BY created_at DESC
            LIMIT 10;
        """, (sensor_id,))
        rows = cur.fetchall()

        # Convert to lists for graph
        values = [r[0] for r in rows][::-1]        # reverse for chronological order
        timestamps = [r[1].strftime('%Y-%m-%d %H:%M:%S') for r in rows][::-1]
        
        return render_template("sensor.html", sensor_id=sensor_id, values=values, timestamps=timestamps, rows=rows)

    except Exception as e:
        return f"<h3>Error: {e}</h3>"

    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/pagina')
def pagina():
    return render_template("pagina.html", user="Miguel")

@app.route('/dashboard')
def dashboard():
    sensor_ids = []
    conn = None
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        cur = conn.cursor()
        
        # Obtener IDs de sensores
        cur.execute("SELECT DISTINCT sensor_id FROM sensores ORDER BY sensor_id ASC;")
        sensor_ids = [row[0] for row in cur.fetchall()]
        
        cur.close()
    except Exception as e:
        print(f"Error al cargar datos del dashboard: {e}")
        
    finally:
        if conn:
            conn.close()

    # Usar render_template para cargar dashboard.html
    # La variable 'sensor_ids' es accesible en el HTML.
    return render_template("dashboard.html", sensor_ids=sensor_ids)

@app.route("/sensor/<int:sensor_id>")
def get_sensor(sensor_id):
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        cur = conn.cursor()

        # Get the latest 10 values
        cur.execute("""
            SELECT value, created_at
            FROM sensores
            WHERE sensor_id = %s
            ORDER BY created_at DESC
            LIMIT 10;
        """, (sensor_id,))
        rows = cur.fetchall()

        # Convert to lists for graph
        values = [r[0] for r in rows][::-1]        # reverse for chronological order
        timestamps = [r[1].strftime('%Y-%m-%d %H:%M:%S') for r in rows][::-1]
        
        return jsonify(sensor_id=sensor_id, values=values, timestamps=timestamps)
        
    except Exception as e:
        return f"<h3>Error: {e}</h3>"

    finally:
        if 'conn' in locals():
            conn.close()
