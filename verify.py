import cv2
from deepface import DeepFace
from deepface.commons import functions, distance
import pickle
from datetime import datetime
import sys
import pymysql

fd_model = "ssd"
fr_model = "Facenet512"
dst_metric = "euclidean_l2"
# fr_thresh = distance.findThreshold(fr_model, dst_metric)
fr_thresh = 0.9

def euclidean_l2(repr1, repr2):
    return distance.findEuclideanDistance(distance.l2_normalize(repr1), distance.l2_normalize(repr2))

try:
    with open("representations.pkl", "rb") as f:
        representations = pickle.load(f)
except FileNotFoundError:
    print("No users registered")
    sys.exit()

DeepFace.represent("test.jpg", fr_model, detector_backend=fd_model)

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="1234",
    database="Cyborg",
    autocommit=True
)
cursor = connection.cursor()

capture = cv2.VideoCapture(0)
frame_width = 1280
frame_height = 720
capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cv2.namedWindow("Verify", cv2.WINDOW_AUTOSIZE)

room_locked = True

while True:
    _, frame = capture.read()
    frame = cv2.flip(frame, 1)

    try:
        extracted_faces = functions.extract_faces(frame, target_size=functions.find_target_size(fr_model), detector_backend=fd_model)
    except (ValueError, cv2.error):
        extracted_faces = []

    recognized_faces = []

    for face, coordinates, _ in extracted_faces:
        embedding = DeepFace.represent(face, fr_model, detector_backend="skip")[0]["embedding"]
        distances = {roll_no: euclidean_l2(embedding, repr) for roll_no, repr in representations.items()}
        match = min(distances, key=lambda roll_no: distances[roll_no])
        x, y, w, h = coordinates.values()
        # text = f"{distances[match]:.3f}/{fr_thresh}"
        if distances[match] < fr_thresh:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, match, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
            # cv2.putText(frame, text, (x, y-35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
            recognized_faces.append(match)
        else:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # cv2.putText(frame, text, (x, y-35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

    if room_locked:
        cv2.putText(frame, "ROOM LOCKED", (frame_width-230, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, "ROOM UNLOCKED", (frame_width-275, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("Verify", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('o'):
        if len(recognized_faces) != 0:
            print("ROOM UNLOCK AUTHORIZED")
            cursor.execute(f"INSERT INTO `entries` (`Time`, `Roll No`, `Action`) VALUES (\"{datetime.now()}\", \"{recognized_faces[0]}\", \"UNLOCK\")")
            room_locked = False
        else:
            print("CANNOT UNLOCK: NOT AUTHORIZED")
    elif key == ord('c'):
        if len(recognized_faces) != 0:
            print("ROOM LOCK AUTHORIZED")
            cursor.execute(f"INSERT INTO `entries` (`Time`, `Roll No`, `Action`) VALUES (\"{datetime.now()}\", \"{recognized_faces[0]}\", \"LOCK\")")
            room_locked = True
        else:
            print("CANNOT LOCK: NOT AUTHORIZED")

cursor.close()
connection.close()
