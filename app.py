from flask import Flask, request, session, render_template, jsonify, redirect, url_for
from db.db import Database
import os
from werkzeug.utils import secure_filename
from services.image_service import process_image
from services.video_service import process_video


app = Flask(__name__)
app.secret_key = 'nanoSUPER_secret_KEY_123456'  # Required for session management
db = Database()

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "mp4", "avi"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']

        if file.filename == '':
            return "No selected file", 400

        if not allowed_file(file.filename):
            return "File type not allowed", 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # визначаємо тип
        ext = filename.rsplit(".", 1)[1].lower()

        if ext in ["png", "jpg", "jpeg"]:
            result = process_image(file_path)

        elif ext in ["mp4", "avi"]:
            result = process_video(file_path)

        return jsonify(result)
    
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)