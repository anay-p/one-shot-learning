import cv2
from deepface import DeepFace
from deepface.commons import functions
import pickle

fd_model = "ssd"
fr_model = "Facenet512"

def yesno(prompt, default=None):
    yes_list = ["y", "Y"]
    no_list = ["n", "N"]
    if default == "y":
        prompt += " [Y/n] "
        yes_list.append("")
    elif default == "n":
        prompt += " [y/N] "
        no_list.append("")
    else:
        prompt += " [y/n] "
    while True:
        ans = input(prompt)
        if ans in yes_list:
            ans = True
            break
        elif ans in no_list:
            ans = False
            break
        else:
            print("Please give a valid answer ('y' for yes or 'n' for no)")
    return ans

representations = {}

while True:
    roll_no = input("Please enter your roll no: ")
    name = input("Please enter your name: ")

    capture = cv2.VideoCapture(0)
    frame_width = 1280
    frame_height = 720
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    cv2.namedWindow("Register", cv2.WINDOW_AUTOSIZE)

    while True:
        _, frame = capture.read()
        frame = cv2.flip(frame, 1)

        try:
            extracted_faces = functions.extract_faces(frame, target_size=functions.find_target_size(fr_model), detector_backend=fd_model)
        except ValueError:
            extracted_faces = []

        for face, coordinates, _ in extracted_faces:
            x, y, w, h = coordinates.values()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Register", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("User not registered")
            break
        elif key == ord(' '):
            if len(extracted_faces) == 1:
                if yesno("Would you like to continue with this image?", "n"):
                    embedding = DeepFace.represent(face, fr_model, detector_backend="skip")[0]["embedding"]
                    print(name, roll_no)
                    representations[roll_no] = embedding
                    print("User registered")
                    break

    capture.release()
    cv2.destroyWindow("Register")

    if not yesno("Would you like to register another user?", "y"):
        break

if len(representations) != 0:
    with open(f"representations.pkl", "wb") as f:
        pickle.dump(representations, f)
