import cv2
from deepface import DeepFace
from deepface.commons import functions, distance
import pickle
from datetime import datetime
import sys
import pymysql
from constants import *

def euclidean_l2(repr1, repr2):
    return distance.findEuclideanDistance(distance.l2_normalize(repr1), distance.l2_normalize(repr2))

try:
    with open("representations.pkl", "rb") as f:
        representations = pickle.load(f)
except FileNotFoundError:
    print("No users registered")
    sys.exit()

DeepFace.represent("test.jpg", FR_MODEL_NAME, detector_backend=FD_MODEL_NAME)

connection = pymysql.connect(
    host="localhost",
    user=DB_USERNAME,
    password=DB_PASSWORD,
    database="cyborg",
    autocommit=True
)
cursor = connection.cursor()

capture = cv2.VideoCapture(0)
frame_width = 1280
frame_height = 720
capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cv2.namedWindow("Verify", cv2.WINDOW_AUTOSIZE)

cursor.execute("SELECT * FROM `entries` ORDER BY `Time` DESC LIMIT 1")
room_locked = True if cursor.fetchone()[2] == "LOCK" else False

while True:
    _, frame = capture.read()
    frame = cv2.flip(frame, 1)

    try:
        extracted_faces = functions.extract_faces(frame, target_size=functions.find_target_size(FR_MODEL_NAME), detector_backend=FD_MODEL_NAME)
    except (ValueError, cv2.error):
        extracted_faces = []

    recognized_faces = []

    for face, coordinates, _ in extracted_faces:
        embedding = DeepFace.represent(face, FR_MODEL_NAME, detector_backend="skip")[0]["embedding"]
        distances = {roll_no: euclidean_l2(embedding, repr) for roll_no, repr in representations.items()}
        match = min(distances, key=lambda roll_no: distances[roll_no])
        x, y, w, h = coordinates.values()
        # text = f"{distances[match]:.3f}/{FR_MODEL_THRESH}"
        if distances[match] < FR_MODEL_THRESH:
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
