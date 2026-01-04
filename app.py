import os
from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
import time

app = Flask(__name__)

# Read MySQL config from environment variables
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")
MYSQL_DB = os.environ.get("MYSQL_DB", "devops")

def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

def init_db():
    retries = 10
    while retries > 0:
        try:
            print("⏳ Trying to connect to MySQL...")
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message TEXT
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ MySQL connected & table ready")
            return
        except Error as e:
            print(f"❌ MySQL not ready yet: {e}")
            retries -= 1
            time.sleep(5)

    raise Exception("❌ Could not connect to MySQL after retries")

@app.route("/")
def hello():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT message FROM messages")
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("index.html", messages=messages)
    except Error as e:
        return f"Database error: {e}"

@app.route("/submit", methods=["POST"])
def submit():
    new_message = request.form.get("new_message")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (message) VALUES (%s)",
            (new_message,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": new_message})
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
