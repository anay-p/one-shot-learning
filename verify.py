import cv2
import numpy as np
import os
from deepface import DeepFace
import sys

roll_no = input("Please enter your roll no: ")
if not os.path.isfile(f"data/{roll_no}.jpg"):
    print("This roll no is not registered.")
    sys.exit()

confidence_limit = 0.8

capture = cv2.VideoCapture(0)
cv2.namedWindow("Face detector", cv2.WINDOW_AUTOSIZE)

net = cv2.dnn.readNetFromCaffe(
    os.path.join(os.path.expanduser("~"), ".deepface/weights/deploy.prototxt"),
    os.path.join(os.path.expanduser("~"), ".deepface/weights/res10_300x300_ssd_iter_140000.caffemodel")
)

while True:
    _, frame = capture.read()
    frame_flip = cv2.flip(frame, 1)
    frame_flip_copy = np.copy(frame_flip)

    no_of_faces = 0

    h, w = frame_flip.shape[:2]
    blob = cv2.dnn.blobFromImage(frame_flip, 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence < confidence_limit:
            continue

        no_of_faces += 1

        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        start_x, start_y, end_x, end_y = box.astype("int")

        text = f"{confidence * 100:.2f}%"
        y = start_y - 10 if start_y - 10 > 10 else start_y + 10
        cv2.rectangle(frame_flip, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
        cv2.putText(frame_flip, text, (start_x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord(' '):
        if no_of_faces == 0:
            print("No face detected!")
        elif no_of_faces == 1:
            face = cv2.imread(f"data/{roll_no}.jpg")
            result = DeepFace.verify(face, frame_flip_copy, "Facenet512", "ssd", "euclidean_l2")
            print(f"{result['distance']} (threshold: {result['threshold']})")
            if result["verified"]:
                print("Verified!")
            else:
                print("Not verified!")
            break
        else:
            print("More than one face detected!")

    cv2.imshow("Face detector", frame_flip)

capture.release()
cv2.destroyWindow("Face detector")
