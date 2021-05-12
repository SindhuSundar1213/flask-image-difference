
from skimage.metrics import structural_similarity as ssim
import imutils
import cv2
import os
import base64
import numpy as np
import urllib
from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


def dummy_process_image(pic1):
    print (pic1)
    gr1 = cv2.cvtColor(pic1, cv2.COLOR_BGR2GRAY)
    return cv2.imwrite("NEW.png",pic1)

@app.route('/', methods=['POST'])
def upload_image():
    if 'file1' not in request.files or 'file2' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        pic1 = secure_filename(file1.filename)
        pic2 = secure_filename(file2.filename)
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'], pic1))
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], pic2))
        ls = []
        p1 = os.path.join(app.config['UPLOAD_FOLDER'],pic1)
        p2 = os.path.join(app.config['UPLOAD_FOLDER'],pic2)
        ls.append(pic1)
        ls.append(pic2)

        cvpic1 = cv2.imread(p1)
        cvpic2 = cv2.imread(p2)
        #We will get the grayscale image for the Pictures Here.
        gr1 = cv2.cvtColor(cv2.imread(p1), cv2.COLOR_BGR2GRAY)
        newpath=os.path.join(app.config['UPLOAD_FOLDER'], "Grayscale1.png")
        cv2.imwrite(newpath,gr1)
        ls.append("Grayscale1.png")

        gr2 = cv2.cvtColor(cv2.imread(p2), cv2.COLOR_BGR2GRAY)
        newpath=os.path.join(app.config['UPLOAD_FOLDER'], "Grayscale2.png")
        cv2.imwrite(newpath,gr2)
        ls.append("Grayscale2.png")

        # Difference in the Grayscale images will be measured and printed here
        (score, diff) = ssim(gr1, gr2, full=True)
        diff = (diff * 255).astype("uint8")
        print("SSIM (percentage of similarity between the images): ", score * 100)

        tsh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cont = cv2.findContours(tsh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cont = imutils.grab_contours(cont)

        newpath=os.path.join(app.config['UPLOAD_FOLDER'], "DifferenceImage.png")
        cv2.imwrite(newpath,diff)
        ls.append("DifferenceImage.png")

        newpath=os.path.join(app.config['UPLOAD_FOLDER'], "Threshold.png")
        cv2.imwrite(newpath,tsh)
        ls.append("Threshold.png")

        for item in cont:
            (x, y, w, h) = cv2.boundingRect(item)
            cv2.rectangle(cvpic1, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(cvpic2, (x, y), (x + w, y + h), (0, 0, 255), 2)

        newpath=os.path.join(app.config['UPLOAD_FOLDER'], "BoundingBoxesPic1.png")
        cv2.imwrite(newpath,cvpic1)
        ls.append("BoundingBoxesPic1.png")

        newpath=os.path.join(app.config['UPLOAD_FOLDER'], "BoundingBoxesPic2.png")
        cv2.imwrite(newpath,cvpic2)
        ls.append("BoundingBoxesPic2.png")

        return render_template('upload.html', filename=ls)
    else:
        flash('Allowed image types are -> png, jpg, jpeg')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run()


def process_image(pic1, pic2):
    gr1 = cv2.cvtColor(pic1, cv2.COLOR_BGR2GRAY)
    gr2 = cv2.cvtColor(pic2, cv2.COLOR_BGR2GRAY)

    (score, diff) = ssim(gr1, gr2, full=True)
    diff = (diff * 255).astype("uint8")
    print("SSIM (percentage of similarity between the images): ", score*100)

    tsh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cont = cv2.findContours(tsh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cont = imutils.grab_contours(cont)

    for item in cont:
        (x, y, w, h) = cv2.boundingRect(item)
        cv2.rectangle(pic1, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.rectangle(pic2, (x, y), (x + w, y + h), (0, 0, 255), 2)

    ls = []
    ls.append(pic1)
    ls.append(pic2)
    ls.append(gr1)
    #ls.append(gr2)
    #ls.append(diff)
    #ls.append(tsh)

    return ls
