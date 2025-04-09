from flask import Flask, render_template, send_from_directory, redirect, request, url_for, flash, jsonify
import os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'changeme_admin_password'

UPLOAD_FOLDER = 'static'
METADATA_FILE = 'metadata.json'

@app.route("/")
def index():
    metadata = {}
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE) as f:
            metadata = json.load(f)
    directories = [d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))]
    files_by_dir = {
        d: os.listdir(os.path.join(UPLOAD_FOLDER, d))
        for d in directories
    }
    return render_template("index.html", files_by_dir=files_by_dir, metadata=metadata)

@app.route("/static/<path:filename>")
def static_file(filename):
    return send_from_directory("static", filename)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") != "changeme":
            flash("Invalid password.")
            return redirect(url_for("admin"))

        action = request.form.get("action")
        folder = request.form.get("folder")
        file = request.files.get("file")

        if action == "upload" and file and folder:
            folder_path = os.path.join(UPLOAD_FOLDER, folder)
            os.makedirs(folder_path, exist_ok=True)
            filename = secure_filename(file.filename)
            file.save(os.path.join(folder_path, filename))
            flash("File uploaded.")
        elif action == "delete":
            path = request.form.get("path")
            full_path = os.path.join(UPLOAD_FOLDER, path)
            if os.path.exists(full_path):
                os.remove(full_path)
                flash("File deleted.")
        elif action == "update_metadata":
            key = request.form.get("meta_key")
            value = request.form.get("meta_value")
            meta_file = METADATA_FILE
            if os.path.exists(meta_file):
                with open(meta_file, "r") as f:
                    data = json.load(f)
            else:
                data = {}
            data[key] = value
            with open(meta_file, "w") as f:
                json.dump(data, f, indent=2)
            flash("Metadata updated.")
        return redirect(url_for("admin"))

    existing_dirs = os.listdir(UPLOAD_FOLDER)
    return render_template("admin.html", folders=existing_dirs)
