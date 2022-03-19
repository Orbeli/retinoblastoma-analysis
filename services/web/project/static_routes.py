from flask import Flask, render_template, send_from_directory


app = Flask(__name__)
app.config.from_object("project.config.Config")


def static_css_files(filename):
    return send_from_directory(app.config["STATIC_CSS"], filename)


def static_js_files(filename):
    return send_from_directory(app.config["STATIC_JS"], filename)


def media_files(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)
