import gdown
import os

def get_weights(path, url):
    """Downloads the file at the path from the url it if does not already exist"""
    if not os.path.isfile(path):
        gdown.download(url, path)

# Define absolute path to ~/.deepface/weights and create it if it does not already exist
weights_dir = os.path.join(os.path.expanduser("~"), ".deepface/weights")
os.makedirs(weights_dir, exist_ok=True)

# Download the weights for FaceNet512 and SDD if they aren't already present
get_weights(
    os.path.join(weights_dir, "facenet512_weights.h5"),
    "https://github.com/serengil/deepface_models/releases/download/v1.0/facenet512_weights.h5"
)
get_weights(
    os.path.join(weights_dir, "deploy.prototxt"),
    "https://github.com/opencv/opencv/raw/3.4.0/samples/dnn/face_detector/deploy.prototxt"
)
get_weights(
    os.path.join(weights_dir, "res10_300x300_ssd_iter_140000.caffemodel"),
    "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
)

print("Done!")
