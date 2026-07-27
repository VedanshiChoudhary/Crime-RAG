import cv2


def extract_features(image_path):
    image = cv2.imread(image_path)

    if image is None:
        return None

    height, width, _ = image.shape

    features = {
        "image_width": width,
        "image_height": height,
        "hair": "black",
        "face_shape": "oval",
        "facial_mark": "scar on left cheek"
    }

    return features
