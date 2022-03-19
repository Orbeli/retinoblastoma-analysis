import os

from werkzeug.utils import secure_filename
from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    redirect,
    url_for,
    render_template
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/analysis", methods=["GET"])
def analysis():
    return render_template("analysis.html")


# Static Routes
@app.route("/static/css/<path:filename>")
def static_css_files(filename):
    return send_from_directory(app.config["STATIC_CSS"], filename)


# Static Routes
@app.route("/static/js/<path:filename>")
def static_js_files(filename):
    return send_from_directory(app.config["STATIC_JS"], filename)


@app.route("/media/<path:filename>")
def media_files(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return f"""
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """
