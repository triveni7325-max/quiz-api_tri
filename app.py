from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# ==============================
# DATABASE CONNECTION
# ==============================
def get_connection():
    conn = sqlite3.connect("quiz.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==============================
# CREATE TABLE
# ==============================
def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_table()

# =====================================================
# WEB PAGE
# =====================================================
@app.route("/", methods=["GET", "POST"])
def category():

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        if name.strip() != "":
            cur.execute("INSERT INTO category (name) VALUES (?)", (name,))
            conn.commit()
        return redirect("/")

    cur.execute("SELECT * FROM category ORDER BY id DESC")
    categories = cur.fetchall()
    conn.close()

    return render_template("category.html", categories=categories)

# =====================================================
# API ROUTES
# =====================================================

@app.route("/api/categories", methods=["GET"])
def api_categories():

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM category ORDER BY id DESC")
    categories = cur.fetchall()
    conn.close()

    data = []
    for cat in categories:
        data.append({
            "id": cat["id"],
            "name": cat["name"]
        })

    return jsonify(data)

@app.route("/api/category/add", methods=["POST"])
def api_add_category():

    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    name = data["name"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO category (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Category Added Successfully"})

# =====================================================
# PRODUCTION SERVER
# =====================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)