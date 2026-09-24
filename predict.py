import os
import json
import numpy as np
import tensorflow as tf
from PIL import Image

IMAGE_SIZE = (224, 224)

class PlantDiseasePredictor:
    def __init__(self, model_path="models/plant_disease_mobilenetv2.keras", class_names_path="class_names.json"):
        if not os.path.exists(model_path) and os.path.exists("models/plant_disease_mobilenetv2.h5"):
            model_path = "models/plant_disease_mobilenetv2.h5"

        self.model = tf.keras.models.load_model(model_path, compile=False)

        with open(class_names_path, "r") as f:
            self.class_names = json.load(f)

    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        image = image.convert("RGB")
        image = image.resize(IMAGE_SIZE)
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

    def predict(self, image: Image.Image):
        processed_img = self.preprocess_image(image)
        predictions = self.model.predict(processed_img, verbose=0)
        
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        disease_name = self.class_names[predicted_class_idx]
        
        return disease_name, confidence