from matplotlib import pyplot as plt
from operator import itemgetter
from .facerecognition import start
from PIL import Image, ImageDraw
from .models import *
import cv2
import pytesseract
import time
import os
import re
import pkg_resources
import pickle
import face_recognition
import numpy as np
import dlib
import time

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe "
carplate_haar_cascade = cv2.CascadeClassifier ('apps\camerastream\haarcascade_russian_plate_number.xml')

#####Setting function for identifying the vehicle number#####
def carplate_detect(image,carplate_haar_cascade):
    carplate_overlay = image.copy() 
    carplate_rects = carplate_haar_cascade.detectMultiScale(carplate_overlay,scaleFactor=1.1, minNeighbors=5)
    for x,y,w,h in carplate_rects: 
        cv2.rectangle(carplate_overlay, (x,y), (x+w,y+h), (255,0,0), 5) 
    return carplate_overlay

#Function to get only the license plate area itself
def carplate_extract (image,carplate_haar_cascade): 
    carplate_rects = carplate_haar_cascade.detectMultiScale (image, scaleFactor = 1.1, minNeighbors = 5)
    carplate_img = []
    for x, y, w, h in carplate_rects: 
        carplate_img = image [y + 15: y + h-10, x + 15: x + w-20] 
    return carplate_img

#Zoom function for further processing 
def enlarge_img(image, scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    return resized_image

def detection(img, carplate_haar_cascade):
    img_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    try:
        carplate_extract_img = carplate_extract(img_rgb,carplate_haar_cascade)
        if not np.array_equal([],carplate_extract_img):
            carplate_extract_img = enlarge_img(carplate_extract_img, 150)   
            return carplate_extract_img
        else:
            return []
    except:
        return []

def predict_car(img):

    img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    config="-c tessedit_char_whitelist=ABCEHKMOPTXY0123456789 --psm 7"
    data = (pytesseract.image_to_string(img, config=config))
    data = data.upper().replace(" ", "").strip()

    if len(data)>=6:
        data = (data[0:6])
        
        buk = itemgetter(0, 4, 5)(data)
        chis = itemgetter(1, 2, 3)(data)
        chis = (''.join(chis))
        buk = (''.join(buk))
        buk = buk.replace('0','O')
        chis = chis.replace('O','0')
        data = buk[0]+chis+buk[1:3]
        
        result = re.findall(r"[A-Z]\d\d\d[A-Z][A-Z]", data)
        if len(result) != 1:
            return None
        if result[0] == data:
            print(data)
            return data
        else:
            return None

def predict(X_frame, knn_clf=None, model_path=None, distance_threshold=0.5):

    if knn_clf is None and model_path is None:
        raise Exception("Download model recognition")


    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    X_face_locations = face_recognition.face_locations(X_frame)


    if len(X_face_locations) == 0:
        return []

    faces_encodings = face_recognition.face_encodings(X_frame, known_face_locations=X_face_locations)

    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]


def show_prediction_labels_on_image(frame, predictions):

    pil_image = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_image)

    for name, (top, right, bottom, left) in predictions:
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2
        draw.rectangle(((left, top), (right, bottom)), outline=(127, 99, 69))

        name = name.encode("UTF-8")

        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(127, 99, 69), outline=(127, 99, 69))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    del draw

    opencvimage = np.array(pil_image)
    return opencvimage

def main(ip, port, location):
    startTime = time.time()
    lastTime = time.time()
    # print(f'rtsp://{camera.ip}:{camera.port}/h264_ulaw.sdp')
    process_this_frame = 30
    url = f'rtsp://{ip}:{port}/h264_ulaw.sdp'
    vid = cv2.VideoCapture(url)
    while(vid.isOpened()):
        ret, frame = vid.read()
        if ret:
            process_this_frame = process_this_frame + 1

            if process_this_frame % 31 == 0:
                img = cv2.resize(frame, (0, 0), fx=0.55, fy=0.55)
                
                predictions = predict(img, model_path="apps/camerastream/trained_model.clf") #Model trained on photo
                if predictions != []:
                    for name, (top, right, bottom, left) in predictions:
                        if name != "unknown":
                            if lastTime + 5 < time.time():
                                print("\n", name, time.ctime())
                                new_entry = EntryPersonLog(date=str(time.ctime()), location=location, name=name, )
                                new_entry.save()

                        elif name == "unknown":
                            img_save = cv2.imwrite('Unknown.png', img)
                img_rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

                # detected_carplate_img = carplate_detect(img_rgb, carplate_haar_cascade)

                carplate_extract_img = carplate_extract(img_rgb, carplate_haar_cascade)
                if not np.array_equal([],carplate_extract_img):
                    try:
                        carplate_extract_img = enlarge_img(carplate_extract_img, 150)
                        result = predict_car(carplate_extract_img)
                        if (result != None) and (result != 'None') and (result != name):
                            new_entry = EntryCarLog(date=str(time.ctime()), location=location, number=result)
                            new_entry.save()
                    except:
                        print("...")
                else:
                    pass
        
        
    