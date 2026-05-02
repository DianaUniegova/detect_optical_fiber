from flask import Flask, request, session, render_template, jsonify, redirect, url_for
from db.db import Database

app = Flask(__name__)
app.secret_key = 'nanoSUPER_secret_KEY_123456'  # Required for session management
db = Database()

@app.route('/', methods=['GET'])
def ret():
    print("Welcome to the Flask API!")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return jsonify({"error": "Missing fields"}), 400

        if db.verify_user(username, password):
            return redirect(url_for('home'))
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "Missing fields", 400

        if len(password) < 6:
            return "Password too short", 400

        success = db.add_user(username, password)

        if success:
            return redirect(url_for('login'))
        else:
            return "User already exists", 409

    return render_template("register.html")

@app.route('/home', methods=['GET'])
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)