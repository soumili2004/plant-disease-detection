import sys
import os
from PIL import Image
from predict import PlantDiseasePredictor

def test_single_image(image_path):
    # Check if image file exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found at '{image_path}'")
        return

    print("Loading model and class mappings...")
    try:
        predictor = PlantDiseasePredictor()
    except Exception as e:
        print(f"❌ Error loading predictor: {e}")
        return

    # Load image and predict
    print(f"Analyzing image: {image_path}...")
    image = Image.open(image_path)
    disease_name, confidence = predictor.predict(image)

    # Format class output
    formatted_label = disease_name.replace("___", " - ").replace("_", " ")

    print("\n" + "=" * 40)
    print("      DIAGNOSIS RESULT")
    print("=" * 40)
    print(f" Condition : {formatted_label}")
    print(f" Confidence: {confidence * 100:.2f}%")
    print("=" * 40 + "\n")

if __name__ == "__main__":
    # Check if image path argument is provided via command line
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        # Fallback default image path (pointing to an image inside your validation directory)
        print("No image path provided. Searching for a sample image in validation set...")
        val_dir = os.path.join("dataset", "val")
        if not os.path.exists(val_dir):
            val_dir = os.path.join("dataset", "validation")
        
        # Pick the first image found in the validation folder
        img_path = None
        for root, dirs, files in os.walk(val_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(root, file)
                    break
            if img_path:
                break

    if img_path:
        test_single_image(img_path)
    else:
        print("❌ Could not find any test images. Pass an image path manually.")