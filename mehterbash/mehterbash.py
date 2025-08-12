from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Veritabanı dosya adı
DB_FILE = os.getenv("DB_FILE", "mehterbash.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Tablo oluşturma
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        info TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command TEXT NOT NULL,
        target TEXT NOT NULL,
        enabled INTEGER NOT NULL,
        interval INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------------------
# AGENT CRUD
# ------------------------------
@app.route("/agents", methods=["GET"])
def get_agents():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM agents")
    agents = [{"id": row["id"], "name": row["id"]} for row in c.fetchall()]
    conn.close()
    return jsonify(agents)

@app.route("/agents", methods=["POST"])
def add_agent():
    data = request.json
    agent_id = data.get("id")
    if not agent_id:
        return jsonify({"error": "id gerekli"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO agents (id, info) VALUES (?, ?)", (agent_id, ""))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Agent zaten var"}), 400
    conn.close()
    return jsonify({"status": "ok"})

# ------------------------------
# TASK CRUD
# ------------------------------
@app.route("/tasks/<agent_id>/list", methods=["GET"])
def get_tasks(agent_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, command, target, enabled, interval FROM tasks WHERE target = ?", (agent_id,)
    )
    tasks = [
        {
            "id": row["id"],
            "command": row["command"],
            "target": row["target"],
            "enabled": bool(row["enabled"]),
            "interval": row["interval"],
        }
        for row in c.fetchall()
    ]
    conn.close()
    return jsonify(tasks)

@app.route("/add_task", methods=["POST"])
def add_task():
    data = request.json
    command = data.get("command")
    target = data.get("target")
    enabled = int(data.get("enabled", True))
    interval = int(data.get("interval", 0))

    if not command or not target:
        return jsonify({"error": "Eksik parametre"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (command, target, enabled, interval) VALUES (?, ?, ?, ?)",
        (command, target, enabled, interval),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/task/<agent_id>/<int:task_id>/<action>", methods=["POST"])
def toggle_task(agent_id, task_id, action):
    if action not in ["enable", "disable"]:
        return jsonify({"error": "Geçersiz işlem"}), 400

    enabled = 1 if action == "enable" else 0

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET enabled = ? WHERE id = ? AND target = ?", (enabled, task_id, agent_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

# ------------------------------
# TEST ENDPOINT
# ------------------------------
@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "mehterbash orchestrator çalışıyor"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
