import os
from project import web_routes, static_routes
import cv2
import numpy as np
from dataclasses import dataclass
import statistics
from werkzeug.utils import secure_filename
from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    make_response,
    redirect,
    url_for,
    render_template
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)

# Web Routes
app.add_url_rule('/', view_func=web_routes.home)
app.add_url_rule('/analysis', view_func=web_routes.analysis)

# Static Routes
app.add_url_rule('/static/css/<path:filename>',
                 view_func=static_routes.static_css_files)
app.add_url_rule('/static/js/<path:filename>',
                 view_func=static_routes.static_js_files)
app.add_url_rule('/media/<path:filename>', view_func=static_routes.media_files)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email

face_cascade = cv2.CascadeClassifier(f'{app.config["HAARCASCADE"]}/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(f'{app.config["HAARCASCADE"]}/haarcascade_eye.xml')

@dataclass
class FaceRoi:
    x: int
    y: int
    w: int
    h: int


@dataclass
class EyeRoi:
    x: int
    y: int
    w: int
    h: int


class Recognize:

    @classmethod
    def _recognize_face_roi(self, image, img):
        # Returns a tuple in cases that cannot define faces ROI
        face = face_cascade.detectMultiScale(image, 1.1, 10)
        if type(face) is tuple:
            print("Erro ao definir face")
            return False

        # Drawing rectangle around the face
        for(x, y,  w,  h) in face:
            face = FaceRoi(
                x=x,
                y=y,
                w=w,
                h=h
            )
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 3)
            print(f'\n\nX: {x}\nY: {y}\nW: {w}\nH: {h}')

        print("Sucesso ao definir Face")
        return face

    @classmethod
    def _recognize_eye_roi(self, image, face: FaceRoi, img, kernel):
        roi_face_gray = image[face.y:(face.y+face.h), face.x:(face.x+face.w)]
        roi_face_color = img[face.y:(face.y+face.h), face.x:(face.x+face.w)]
        eyes_roi = eye_cascade.detectMultiScale(roi_face_gray, 1.1, 10)
        eyes_list = []
        if type(eyes_roi) is tuple:
            print("Erro ao definir olhos")
            return False

        for (x_eye, y_eye, w_eye, h_eye) in eyes_roi:
            if x_eye == 74:
                continue
            eye = EyeRoi(
                x=x_eye,
                y=y_eye,
                w=w_eye,
                h=h_eye
            )
            eyes_list.append(eye)

            print(f'\n\nx_eye: {x_eye}\ny_eye: {y_eye}\nw_eye: {w_eye}\nh_eye: {h_eye}')
        
        
        # TRATA QUANDO TEM MAIS DE 3 ROIS
        if len(eyes_list) >= 3:
            print(f'\n\nEYES LIST: {len(eyes_list)}')
            # remove roi que estejam discrepantes
            roi_edge_list = []
            for eye in eyes_list:
                edge = eye.w
                roi_edge_list.append(edge)
            
            to_remove_list = []

            for edge in roi_edge_list:
                variacao_edge = (edge-statistics.mean(roi_edge_list))/edge*100
                print(f"\nVARIATION: {type(variacao_edge)}")
                print(f"\nEDGE VARIATION: {abs(variacao_edge)}")
                if int(abs(variacao_edge)) > 40:
                    print('\nREMOVER')
                    to_remove_list.append(edge)
                    roi_edge_list.remove(edge)
            
            
            for eye in eyes_list:
                if eye.w in to_remove_list:
                    eyes_list.remove(eye)

        white_pixels_list = []
        for eye in eyes_list:
            cv2.rectangle(
                roi_face_color,
                (eye.x, eye.y),
                (eye.x+eye.w, eye.y+eye.h),
                (0, 255, 0),
                2
            )
            roi_eye_gray = roi_face_gray[eye.y:eye.y+eye.h, eye.x:eye.x+eye.w]
            roi_eye_color = roi_face_color[eye.y:eye.y+eye.h, eye.x:eye.x+eye.w]
            roi_bgr = cv2.cvtColor(roi_eye_gray, cv2.COLOR_GRAY2BGR)
            _, thresh = cv2.threshold(roi_eye_gray, 92, 255, cv2.THRESH_BINARY_INV)
            morph_close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            morph_open = cv2.morphologyEx(morph_close, cv2.MORPH_OPEN, kernel)

            n_white_pix = np.sum(morph_open == 255)
            white_pixels_list.append(n_white_pix)
            print(f"n_white_pix {n_white_pix}")

        print("Sucesso ao definir olhos")
        return face, white_pixels_list


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
        path = f'{app.config["MEDIA_FOLDER"]}/{filename}'

        img = cv2.imread(path)

        kernel = np.ones((3, 3), np.uint8)
        # Creating an object faces
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        recognizer = Recognize()
        recognized_face_roi = recognizer._recognize_face_roi(gray_img, img)
        recognized_face_roi, white_pixels_list = recognizer._recognize_eye_roi(
            image=gray_img, 
            face=recognized_face_roi,
            img=img,
            kernel=kernel
        )

        max_value = max(white_pixels_list)
        min_value = min(white_pixels_list)
        percent_variation = (max_value-min_value)/max_value*100
        print(f"\npercent_variation {percent_variation}\n")
        ret = {"percent_variation": percent_variation}

        r = make_response(ret)
        r.mimetype = 'application/json'
        return r
    return f"""
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """
