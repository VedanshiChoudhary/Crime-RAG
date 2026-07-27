import cv2
import os


def analyze_image(image_path):

    print("\nLoading image...")

    if not os.path.exists(image_path):
        return None


    image = cv2.imread(image_path)

    if image is None:
        return None


    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    # Face detector
    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )


    faces = face_detector.detectMultiScale(
    gray,
    scaleFactor=1.05,
    minNeighbors=3,
    minSize=(30, 30)
)



    features = {
        "image_width": image.shape[1],
        "image_height": image.shape[0],
        "faces_detected": len(faces),
        "hair": "black",
        "face_shape": "oval",
        "facial_mark": "unknown"
    }


    if len(faces) > 0:
        features["face_detected"] = "yes"
    else:
        features["face_detected"] = "no"


    return features



if __name__ == "__main__":

    path = input(
        "Enter image path: "
    )


    result = analyze_image(path)


    if result is None:
        print("❌ Image not found")

    else:
        print("\n===== AI Sketch Analysis =====")

        for key, value in result.items():
            print(
                f"{key}: {value}"
            )
