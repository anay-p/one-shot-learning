import cv2
import numpy as np
import os

# Take roll no from user
roll_no = input("Please enter your roll no: ")

# Define confidence limit for face detector
confidence_limit = 0.8

# Start capturing the webcam and create a window for displaying its output
capture = cv2.VideoCapture(0)
cv2.namedWindow("Register", cv2.WINDOW_AUTOSIZE)

# Load SSD model for face detection
net = cv2.dnn.readNetFromCaffe(
    os.path.join(os.path.expanduser("~"), ".deepface/weights/deploy.prototxt"),
    os.path.join(os.path.expanduser("~"), ".deepface/weights/res10_300x300_ssd_iter_140000.caffemodel")
)

while True:
    # Read a frame from the webcam, flip it and make a copy of it
    _, frame = capture.read()
    frame = cv2.flip(frame, 1)
    frame_copy = np.copy(frame)

    # Initialize a variable to store the no of faces detected in the frame
    no_of_faces = 0

    # Store the height and width of the frame
    h, w = frame.shape[:2]

    # Create a blob from the frame and pass it to the face detector model
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    # Loop through all the detections
    for i in range(detections.shape[2]):
        # Store the confidence level and ignore detection if the it is lower than the confidence limit
        confidence = detections[0, 0, i, 2]
        if confidence < confidence_limit:
            continue

        # Increment the no of faces by one
        no_of_faces += 1

        # Get the coordinates for the detected face
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
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
        print("User not registered.")
        break
    elif key == ord(' '):
        # If the spacebar key is pressed and only one face is detected, save the copied frame as a JPEG with
        # roll no as the name and exit loop otherwise continue
        if no_of_faces == 0:
            print("No face detected!")
        elif no_of_faces == 1:
            if not os.path.exists("data"):
                os.makedirs("data")
            cv2.imwrite(f"data/{roll_no}.jpg", frame_copy)
            print("Face registered successfully!")
            break
        else:
            print("More than one face detected!")

    # Display the frame on the window
    cv2.imshow("Register", frame)

# Turn the webcam off and destroy the window
capture.release()
cv2.destroyWindow("Register")
