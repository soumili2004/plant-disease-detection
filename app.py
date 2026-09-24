import streamlit as st
from PIL import Image
from predict import PlantDiseasePredictor
from pdf_generator import generate_pdf_report

# 1. Page Configuration
st.set_page_config(
    page_title="AgriGuard | AI Plant Doctor",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for a Catchy UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }
    .header-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .header-title {
        color: #4E8A1B;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .header-subtitle {
        color: #B2BEC3;
        font-size: 1.1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
        color: #4E8A1B !important;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #11998e, #38ef7d);
        color: #000000 !important;
        font-weight: bold;
        font-size: 1.1rem;
        border-radius: 12px;
        padding: 12px 24px;
        border: none;
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #4E8A1B;
        border-radius: 15px;
        padding: 10px;
        background: rgba(255, 255, 255, 0.02);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header Banner
st.markdown("""
    <div class="header-card">
        <div class="header-title">🌿 AgriGuard AI</div>
        <div class="header-subtitle">Instant Leaf Disease Detection & Biological Remedies</div>
    </div>
""", unsafe_allow_html=True)

# 4. Sidebar Information
with st.sidebar:
    st.markdown("## 🌿 **AgriGuard AI**")
    st.caption("AI-Powered Botanical Health Engine")
    st.info("""
        **Powered by MobileNetV2 & Gemini Vision**
        
        Identifies 38 plant conditions across crops like Tomato, Potato, Apple, and Pepper, with dynamic fallback for unknown species.
    """)
    st.markdown("---")
    st.caption("🚀 Version 2.0 | Multi-Modal Diagnostics")

# 5. Database of Remedies for 38 PlantVillage Classes
REMEDIES = {
    "Apple___Apple_scab": {
        "organic": "Apply neem oil, liquid copper fungicide, or sulfur spray. Rake and burn fallen leaves.",
        "chemical": "Spray fungicides containing captan, myclobutanil, or mancozeb during early bloom."
    },
    "Apple___Black_rot": {
        "organic": "Prune out dead wood during winter. Remove all mummified fruit from the tree and ground.",
        "chemical": "Apply captan or thiophanate-methyl fungicides starting at petal fall."
    },
    "Apple___Cedar_apple_rust": {
        "organic": "Prune galls from nearby cedar hosts. Apply sulfur or copper fungicides early in spring.",
        "chemical": "Spray myclobutanil or propiconazole at pink-bud stage."
    },
    "Apple___healthy": {"organic": "No treatment required.", "chemical": "No chemical intervention needed."},
    "Potato___Early_blight": {
        "organic": "Mulch around base to prevent splashback. Apply Bacillus subtilis or copper fungicide.",
        "chemical": "Apply chlorothalonil, mancozeb, or azoxystrobin."
    },
    "Potato___Late_blight": {
        "organic": "Destroy infected foliage immediately. Apply fixed copper sprays regularly.",
        "chemical": "Apply systemic fungicides containing cymoxanil or chlorothalonil."
    },
    "Potato___healthy": {"organic": "No treatment required.", "chemical": "No chemical intervention needed."},
    "Tomato___Bacterial_spot": {
        "organic": "Spray copper fungicides. Avoid working with plants while foliage is wet.",
        "chemical": "Apply copper hydroxide mixed with mancozeb."
    },
    "Tomato___Early_blight": {
        "organic": "Prune lower leaves touching soil. Apply copper fungicide or potassium bicarbonate.",
        "chemical": "Apply chlorothalonil or mancozeb fungicides."
    },
    "Tomato___Late_blight": {
        "organic": "Remove infected plants immediately. Apply copper sprays defensively.",
        "chemical": "Spray fungicides containing chlorothalonil or cymoxanil."
    },
    "Tomato___healthy": {"organic": "No treatment required.", "chemical": "No chemical intervention needed."}
}

def get_remedy(class_name):
    if class_name in REMEDIES:
        return REMEDIES[class_name]
    if "healthy" in class_name.lower():
        return {
            "organic": "No treatment required. Maintain proper watering and soil nutrition.",
            "chemical": "No chemical intervention needed."
        }
    lower_name = class_name.lower()
    if "bacterial" in lower_name:
        return {
            "organic": "Apply fixed copper sprays mixed with liquid soap. Avoid overhead watering.",
            "chemical": "Apply copper hydroxide combined with mancozeb."
        }
    elif "virus" in lower_name:
        return {
            "organic": "Remove infected plants immediately. Control sap-sucking insects with neem oil.",
            "chemical": "Apply systemic insecticides to control vector insects."
        }
    else:
        return {
            "organic": "Apply neem oil or copper-based organic fungicides. Prune affected leaves.",
            "chemical": "Apply broad-spectrum foliar fungicides suitable for your crop."
        }

# 6. Load Predictor Engine
@st.cache_resource
def load_predictor():
    return PlantDiseasePredictor()

try:
    predictor = load_predictor()
    model_loaded = True
except Exception as e:
    model_loaded = False
    st.error("❌ Predictor load error. Ensure model and class files exist.")

# 7. Upload and Interface Section
st.subheader("🔍 Upload Leaf Sample")
uploaded_file = st.file_uploader("Drop a clear leaf image below (PNG, JPG, JPEG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and model_loaded:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(image, caption="Uploaded Leaf Sample", use_container_width=True)
    with col2:
        st.markdown("### Sample Ready")
        st.write("Click below to run neural network & vision analysis.")
        run_analysis = st.button("⚡ Run AI Diagnosis")

    if run_analysis:
        with st.spinner("🔍 Processing image..."):
            # Unpack all 4 values from predict.py
            disease_name, confidence, is_unknown, gemini_result = predictor.predict(image)

            st.markdown("---")
            st.markdown("## 📊 Analysis Findings")

            if is_unknown:
                st.warning("⚠️ Low confidence detection! This leaf appears to be outside our trained dataset.")
                st.markdown("### 🤖 AI Gemini Vision Diagnosis")
                st.info(gemini_result)
                
                organic_text = "Refer to the AI Gemini Vision Diagnosis provided above."
                chemical_text = "Consult a local agricultural expert."
                class_name = "Unknown / Out-of-Dataset Leaf"
            else:
                formatted_label = disease_name.replace("___", " - ").replace("_", " ")

                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric(label="Diagnosed Condition", value=formatted_label)
                with res_col2:
                    st.metric(label="Model Confidence", value=f"{confidence * 100:.2f}%")

                st.markdown("---")
                st.subheader("🛠️ Prescription & Action Plan")

                if "healthy" in disease_name.lower():
                    st.balloons()
                    organic_text = "No treatment required. Maintain regular watering and sunlight."
                    chemical_text = "No chemical intervention needed."
                    st.success("🟢 **Optimal Plant Health Detected!**")
                else:
                    treatment = get_remedy(disease_name)
                    organic_text = treatment["organic"]
                    chemical_text = treatment["chemical"]

                    tab1, tab2 = st.tabs(["🌱 Organic / Bio Remedies", "🧪 Chemical Control"])
                    with tab1:
                        st.info(organic_text)
                    with tab2:
                        st.warning(chemical_text)

                class_name = disease_name

            st.markdown("---")
            
            # Generate PDF Report
            pdf_bytes = generate_pdf_report(
                disease_name=class_name,
                confidence=confidence,
                organic_remedy=organic_text,
                chemical_remedy=chemical_text,
                leaf_image=image
            )

            st.download_button(
                label="📥 Export Full PDF Report",
                data=pdf_bytes,
                file_name=f"AgriGuard_Report_{class_name}.pdf",
                mime="application/pdf"
            )