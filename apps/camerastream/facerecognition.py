import cv2
import pickle
from PIL import Image, ImageDraw

import face_recognition
import numpy as np
import dlib

import time


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


def start():
    startTime = time.time()
    lastTime = time.time()
    print(f'\rSetting GEN HOLL cameras up..\tTime: {time.ctime()}', end="")
    process_this_frame = 30
    # if camera.login != '' or camera.password != '':
    #     url = cv2.VideoCapture(f'rtsp://{camera.ip}:{camera.port}//user={camera.login}_password={camera.password}_channel=1_stream=0.sdp?real_stream')
    # else:
    #     url = cv2.VideoCapture(f'rtsp://{camera.ip}:{camera.port}/h264_ulaw.sdp')
    # print(url)
    url = 'rtsp://192.168.1.87:8080/h264_ulaw.sdp' # Camera URL rtsp://192.168.1.87:8080/h264_ulaw.sdp
    cap = cv2.VideoCapture(url)
    while 1 > 0:
        
        if startTime + 5 * 60 < time.time():
            exit(0)
        ret, frame = cap.read()
        if ret:
            process_this_frame = process_this_frame + 1

            if process_this_frame % 31 == 0:
                img = cv2.resize(frame, (0, 0), fx=0.55, fy=0.55)
                
                counts_of_predict = 0
                predictions = predict(img, model_path="apps/camerastream/trained_model.clf") #Model trained on photo
                if predictions != []:
                    for name, (top, right, bottom, left) in predictions:
                        if name != "unknown":
                            if lastTime + 5 < time.time():
                                print("\n", name, time.ctime())
                                return name
                        elif name == "unknown":
                            img_save = cv2.imwrite('Unknown.png', img)

