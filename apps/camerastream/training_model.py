from sklearn import neighbors
import os.path
import pickle
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
import math

def start():
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG'}

    train_dir = "D:/Users/User/GitHub/allrussianhackaton/media"
    model_save_path = "trained_model.clf"
    n_neighbors = 2
    knn_algo = 'ball_tree'
    verbose = True

    """
            <train_dir>/
            ├── <person1>/
            │   ├── <somename1>.jpeg
            │   ├── <somename2>.jpeg
            │   ├── ...
            ├── <person2>/
            │   ├── <somename1>.jpeg
            │   └── <somename2>.jpeg
            └── ...
    """



    X = []
    y = []

    print("[!] Start train...")

    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
            
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)
            
            print("[#] READ " + str(img_path))

            if len(face_bounding_boxes) != 1:
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(class_dir)
    print("[#] Reading all directories.")

    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    print("[!] Model was trained!")

    with open(model_save_path, 'wb') as f:
        pickle.dump(knn_clf, f)

    print("[@] Model save.")

start()