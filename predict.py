import os
import json
import numpy as np
import tensorflow as tf
from PIL import Image
from google import genai

IMAGE_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.65  # 65% threshold

class PlantDiseasePredictor:
    def __init__(self, model_path="models/plant_disease_mobilenetv2.keras", class_names_path="class_names.json"):
        if not os.path.exists(model_path) and os.path.exists("models/plant_disease_mobilenetv2.h5"):
            model_path = "models/plant_disease_mobilenetv2.h5"

        self.model = tf.keras.models.load_model(model_path, compile=False)
        with open(class_names_path, "r") as f:
            self.class_names = json.load(f)
            
        # Try retrieving API key from environment variables or Streamlit secrets
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets.get("GEMINI_API_KEY")
            except Exception:
                api_key = None

        self.gemini_client = genai.Client(api_key=api_key) if api_key else None

    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        image = image.convert("RGB").resize(IMAGE_SIZE)
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        return np.expand_dims(img_array, axis=0)

    def predict_with_gemini(self, image: Image.Image) -> str:
        """Fallback to Gemini Vision for unknown/unseen leaf images."""
        if not self.gemini_client:
            return "Unknown Leaf (Confidence too low and Gemini API key not configured in secrets)."

        prompt = (
            "Analyze this plant leaf image carefully. "
            "1. Identify the plant type.\n"
            "2. Identify if there is any disease or pest issue (or if it's healthy).\n"
            "3. Provide brief organic and chemical remedies.\n"
            "Keep the output concise and structured."
        )
        
        try:
            # Updated to standard stable model ID
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[image, prompt]
            )
            return response.text
        except Exception as e:
            return f"Gemini API Analysis Error: {str(e)}"

    def predict(self, image: Image.Image):
        processed_img = self.preprocess_image(image)
        predictions = self.model.predict(processed_img, verbose=0)
        
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        # If confidence is high, return the MobileNetV2 diagnosis
        if confidence >= CONFIDENCE_THRESHOLD:
            disease_name = self.class_names[predicted_class_idx]
            return disease_name, confidence, False, None
        
        # Otherwise, fall back to Gemini for out-of-dataset images
        gemini_analysis = self.predict_with_gemini(image)
        return "Unknown / Out-of-Dataset Leaf", confidence, True, gemini_analysis