from flask import render_template

def home():
    return render_template("index.html")

def analysis():
    return render_template("analysis.html")