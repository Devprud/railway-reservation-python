from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.dirname(__file__), 'railway.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        # Bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                train TEXT,
                travel_class TEXT,
                payment TEXT
            )
        ''')
        # Passengers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passengers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER,
                name TEXT,
                age INTEGER,
                FOREIGN KEY (booking_id) REFERENCES bookings(id)
            )
        ''')
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        return jsonify(success=True, message="Registration successful!")
    except sqlite3.IntegrityError:
        return jsonify(success=False, message="Username already exists.")

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            return jsonify(success=True, message="Login successful!")
        else:
            return jsonify(success=False, message="Invalid username or password.")
    except Exception as e:
        print("Login error:", e)
        return jsonify(success=False, message="Server error."), 500

@app.route('/api/book', methods=['POST'])
def book():
    data = request.get_json()
    username = data.get('username', 'guest')  # should be set from frontend!
    train = data.get('train')
    travel_class = data.get('travelClass')
    payment = data.get('payment')
    passengers = data.get('passengers', [])

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO bookings (username, train, travel_class, payment) VALUES (?, ?, ?, ?)",
                   (username, train, travel_class, payment))
    booking_id = cursor.lastrowid
    for p in passengers:
        cursor.execute("INSERT INTO passengers (booking_id, name, age) VALUES (?, ?, ?)",
                       (booking_id, p['name'], p['age']))
    db.commit()
    return jsonify(success=True, message="Booking successful!")

@app.route('/api/bookings')
def get_bookings():
    username = request.args.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM bookings WHERE username=?", (username,))
    bookings = []
    for row in cursor.fetchall():
        booking_id = row[0]
        cursor2 = db.cursor()
        cursor2.execute("SELECT name, age FROM passengers WHERE booking_id=?", (booking_id,))
        passengers = [{"name": p[0], "age": p[1]} for p in cursor2.fetchall()]
        bookings.append({
            "train": row[2],
            "travel_class": row[3],
            "payment": row[4],
            "passengers": passengers
        })
    return jsonify(success=True, bookings=bookings)

@app.route('/api/delete_account', methods=['POST'])
def delete_account():
    data = request.get_json()
    username = data.get('username')
    db = get_db()
    cursor = db.cursor()
    # Delete bookings and passengers
    cursor.execute("SELECT id FROM bookings WHERE username=?", (username,))
    booking_ids = [row[0] for row in cursor.fetchall()]
    for bid in booking_ids:
        cursor.execute("DELETE FROM passengers WHERE booking_id=?", (bid,))
    cursor.execute("DELETE FROM bookings WHERE username=?", (username,))
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    db.commit()
    return jsonify(success=True, message="Account and all bookings deleted.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
