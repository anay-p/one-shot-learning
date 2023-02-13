import cv2
import numpy as np
import os
from deepface import DeepFace
from deepface.detectors import FaceDetector

# Take roll no from user
roll_no = input("Please enter your roll no: ")

# Check if the user's JPEG exists and exit if it doesn't
if not os.path.isfile(f"data/{roll_no}.jpg"):
    print("This roll no is not registered.")
else:
    # Load SSD model for face detection and set threshold
    net = cv2.dnn.readNetFromCaffe(
        os.path.join(os.path.expanduser("~"), ".deepface/weights/deploy.prototxt"),
        os.path.join(os.path.expanduser("~"), ".deepface/weights/res10_300x300_ssd_iter_140000.caffemodel")
    )
    thresh = 0.8

    # Test image is passed to load and initialize the models
    DeepFace.represent("data/test.jpg", "Facenet512", detector_backend="ssd")

    # Start capturing the webcam, set its width and height, and create a window for displaying its output
    capture = cv2.VideoCapture(0)
    frame_width = 1280
    frame_height = 720
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    cv2.namedWindow("Verify", cv2.WINDOW_AUTOSIZE)

    while True:
        # Read a frame from the webcam, flip it and make a copy of it
        _, frame = capture.read()
        frame = cv2.flip(frame, 1)
        frame_copy = np.copy(frame)

        # Initialize a variable to store the no of faces detected in the frame
        no_of_faces = 0

        # Create a blob from the frame and pass it to the face detector model
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        # Loop through all the detections
        for i in range(detections.shape[2]):
            # Retrieve the confidence level and ignore detection if the it is lower than the threshold
            confidence = detections[0, 0, i, 2]
            if confidence < thresh:
                continue

            # Increment the no of faces by one
            no_of_faces += 1

            # Get the coordinates for the detected face
            box = detections[0, 0, i, 3:7] * np.array([frame_width, frame_height, frame_width, frame_height])
            start_x, start_y, end_x, end_y = box.astype("int")

            # Create an outline around the detected face and display the confidence percentage on the frame
            text = f"{confidence * 100:.2f}%"
            y = start_y - 10 if start_y - 10 > 10 else start_y + 10
            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
            cv2.putText(frame, text, (start_x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        # Get keypress input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            # Exit loop if 'q' is pressed
            print("Exiting.")
            break
        elif key == ord(' '):
            # If the spacebar key is pressed and only one face is detected, try to verify else continue
            if no_of_faces == 0:
                print("No face detected!")
            elif no_of_faces == 1:
                # User's JPEG and webcam frame are passed to verify if they contain the same person's face
                # Model is chosen as a modified FaceNet which returns 512 dimensional vector rather
                # than the usual 128 dimensional vector
                # The face detector chosen is SSD, the same as the one used in this file.
                face = cv2.imread(f"data/{roll_no}.jpg")
                result = DeepFace.verify(face, frame_copy, "Facenet512", "ssd", "euclidean_l2")

                # The distance between the two images, time taken by the model and verification status
                # are all printed
                print(f"Distance: {result['distance']} (threshold: {result['threshold']})")
                print(f"Time taken: {result['time']}s")
                if result["verified"]:
                    print("Verified!")
                else:
                    print("Not verified!")
                break
            else:
                print("More than one face detected!")

        # Display the frame on the window
        cv2.imshow("Verify", frame)

    # Turn the webcam off and destroy the window
    capture.release()
    cv2.destroyWindow("Verify")
