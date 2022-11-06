import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    STATIC_CSS = f"{os.getenv('APP_FOLDER')}/project/static/css"
    STATIC_JS = f"{os.getenv('APP_FOLDER')}/project/static/js"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/project/media"
    HAARCASCADE = f"{os.getenv('APP_FOLDER')}/project/haarcascade"
