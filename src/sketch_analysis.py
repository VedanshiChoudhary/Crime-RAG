from image_features import extract_features

image_path = input("Enter sketch image path: ")

features = extract_features(image_path)

if features is None:
    print("❌ Image not found!")
else:
    print("\n===== Extracted Features =====")

    for key, value in features.items():
        print(f"{key}: {value}")
