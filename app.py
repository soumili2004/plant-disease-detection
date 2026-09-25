import io
import re
import streamlit as st
from PIL import Image
from gtts import gTTS
from predict import PlantDiseasePredictor
from pdf_generator import generate_pdf_report

# 1. Page Configuration
st.set_page_config(
    page_title="AgriGuard | AI Plant Doctor",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for UI
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
        <div class="header-subtitle">Instant Leaf Disease Detection & English Voice Remedies</div>
    </div>
""", unsafe_allow_html=True)

# 4. Sidebar Information
with st.sidebar:
    st.markdown("## 🌿 **AgriGuard Controls**")
    st.caption("AI-Powered Botanical Health Engine")
    st.info("""
        **Powered by MobileNetV2 & Gemini Vision**
        
        Identifies 38 plant conditions across crops like Tomato, Potato, Apple, and Pepper, with dynamic fallback for unknown species.
    """)
    st.caption("🚀 Version 2.7 | Disease-Specific Voice Diagnostics")

# 5. Full Specialized Database for Plant Conditions
REMEDIES = {
    # Apple
    "apple_apple_scab": {
        "organic": "Apply neem oil, sulfur spray, or liquid copper. Prune affected branches and rake fallen leaves to stop spore germination.",
        "chemical": "Spray fungicides containing captan, myclobutanil, or mancozeb at green-tip stage."
    },
    "apple_black_rot": {
        "organic": "Prune out dead wood, Cankers, and infected twigs. Remove mummified fruit from trees.",
        "chemical": "Apply fungicides containing captan or thiophanate-methyl starting at petal fall."
    },
    "apple_cedar_apple_rust": {
        "organic": "Remove nearby cedar galls. Spray copper or sulfur fungicide during early spring growth.",
        "chemical": "Spray myclobutanil or propiconazole at pink-bud stage."
    },
    # Cherry
    "cherry_powdery_mildew": {
        "organic": "Spray potassium bicarbonate, neem oil, or sulfur. Improve air circulation around the canopy.",
        "chemical": "Apply myclobutanil, quinoxyfen, or tebuconazole fungicides."
    },
    # Corn
    "corn_cercospora_leaf_spot_gray_leaf_spot": {
        "organic": "Rotate crops with non-grass species. Apply bio-fungicides containing Bacillus subtilis.",
        "chemical": "Spray azoxystrobin, pyraclostrobin, or propiconazole at first sign of lesions."
    },
    "corn_common_rust": {
        "organic": "Plant resistant corn hybrids. Apply sulfur-based sprays early in infestation.",
        "chemical": "Apply triazole or strobilurin-based foliar fungicides."
    },
    "corn_northern_leaf_blight": {
        "organic": "Incorporate crop residues into soil post-harvest. Use copper-based bio-pesticides.",
        "chemical": "Apply azoxystrobin or propiconazole at tasseling stage."
    },
    # Grape
    "grape_black_rot": {
        "organic": "Prune vines to increase sunlight exposure. Remove mummified grapes and destroy infected shoots.",
        "chemical": "Spray mancozeb, captan, or ziram during early bloom."
    },
    "grape_esca_black_measles": {
        "organic": "Remove infected trunk tissue and apply pruning wound sealants.",
        "chemical": "Apply preventive lime-sulfur or systemic fungicides after pruning."
    },
    "grape_leaf_blight_isariopsis_leaf_spot": {
        "organic": "Spray copper hydroxide or sulfur spray. Remove infected lower leaves.",
        "chemical": "Apply mancozeb or copper-based broad spectrum fungicides."
    },
    # Peach
    "peach_bacterial_spot": {
        "organic": "Spray copper fungicides early during dormancy. Avoid excessive nitrogen fertilization.",
        "chemical": "Apply oxytetracycline or copper hydroxide sprays."
    },
    # Pepper
    "pepper_bell_bacterial_spot": {
        "organic": "Spray copper octanoate or copper soap. Avoid handling plants when foliage is wet.",
        "chemical": "Apply copper hydroxide mixed with mancozeb for enhanced control."
    },
    # Potato
    "potato_early_blight": {
        "organic": "Mulch base to avoid soil splash. Apply copper fungicide or Bacillus subtilis.",
        "chemical": "Apply chlorothalonil, mancozeb, or azoxystrobin."
    },
    "potato_late_blight": {
        "organic": "Destroy infected foliage immediately. Spray fixed copper defensively.",
        "chemical": "Apply systemic fungicides containing cymoxanil, fluazinam, or chlorothalonil."
    },
    # Strawberry
    "strawberry_leaf_scorch": {
        "organic": "Remove old infected leaves post-harvest. Spray neem oil or copper sulfate.",
        "chemical": "Apply captan, thiophanate-methyl, or myclobutanil."
    },
    # Tomato
    "tomato_bacterial_spot": {
        "organic": "Apply copper-based sprays mixed with neem oil. Practice strict 3-year crop rotation.",
        "chemical": "Apply copper hydroxide combined with mancozeb."
    },
    "tomato_early_blight": {
        "organic": "Prune lower leaves touching soil. Apply potassium bicarbonate or copper fungicide.",
        "chemical": "Apply chlorothalonil, mancozeb, or difenoconazole."
    },
    "tomato_late_blight": {
        "organic": "Remove infected plants immediately to save crop. Spray fixed copper defensively.",
        "chemical": "Spray systemic fungicides containing chlorothalonil or cymoxanil."
    },
    "tomato_leaf_mold": {
        "organic": "Increase greenhouse ventilation and reduce humidity. Spray liquid copper.",
        "chemical": "Apply difenoconazole, chlorothalonil, or mancozeb."
    },
    "tomato_septoria_leaf_spot": {
        "organic": "Remove infected bottom leaves. Apply neem oil or copper fungicide.",
        "chemical": "Apply chlorothalonil or mancozeb at first sign of leaf spots."
    },
    "tomato_spider_mites_two_spotted_spider_mite": {
        "organic": "Spray insecticidal soap, neem oil, or introduce predatory mites (Phytoseiulus).",
        "chemical": "Apply abamectin, bifenazate, or spiromesifen miticides."
    },
    "tomato_target_spot": {
        "organic": "Improve air movement between plants. Apply copper fungicides.",
        "chemical": "Apply azoxystrobin, chlorothalonil, or pyraclostrobin."
    },
    "tomato_yellow_leaf_curl_virus": {
        "organic": "Use yellow sticky traps. Cover plants with fine mesh net. Spray neem oil for whiteflies.",
        "chemical": "Spray systemic insecticides like imidacloprid to target vector whiteflies."
    },
    "tomato_mosaic_virus": {
        "organic": "Remove infected plants immediately. Wash hands and tools with milk or trisodium phosphate.",
        "chemical": "No chemical cure exists for viral infection. Control weed hosts and pests."
    }
}

def get_remedy(class_name):
    """Fuzzy key search to ensure specific remedies match any variation of class names."""
    # Standardize string for lookup: tomato___early_blight -> tomato_early_blight
    clean_key = re.sub(r'[^a-zA-Z0-9]', '_', class_name).lower()
    clean_key = re.sub(r'_+', '_', clean_key).strip('_')

    # 1. Exact or Partial Dictionary Match
    for key, remedy in REMEDIES.items():
        if key in clean_key or clean_key in key:
            return remedy

    # 2. Healthy Condition Match
    if "healthy" in clean_key:
        return {
            "organic": "No treatment required. Maintain regular watering, adequate sunlight, and soil aeration.",
            "chemical": "No chemical intervention needed."
        }

    # 3. Categorical Fallbacks (Specific to disease types)
    if "bacterial" in clean_key:
        return {
            "organic": "Apply copper soap spray. Avoid overhead watering to prevent bacterial spread.",
            "chemical": "Spray copper hydroxide mixed with mancozeb."
        }
    elif "virus" in clean_key:
        return {
            "organic": "Remove and burn infected plants. Control sap-sucking vector insects with neem oil.",
            "chemical": "Apply systemic insecticides to eliminate pest vectors."
        }
    elif "mildew" in clean_key or "rust" in clean_key or "blight" in clean_key:
        return {
            "organic": "Prune affected foliage. Apply neem oil, sulfur spray, or bio-fungicides.",
            "chemical": "Apply broad-spectrum foliar fungicides like chlorothalonil or azoxystrobin."
        }
    else:
        return {
            "organic": "Apply neem oil or copper fungicide. Ensure balanced soil nutrients and good air drainage.",
            "chemical": "Apply a general-purpose agricultural fungicide suitable for your crop."
        }

# 6. Helper Functions for Audio Processing
def clean_text_for_speech(text: str) -> str:
    """Removes Markdown symbols and extra formatting for clean English TTS synthesis."""
    text = re.sub(r'[\*#_~`]', '', text)
    text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_audio_bytes(text: str) -> io.BytesIO:
    """Generates an English MP3 audio stream in memory using gTTS."""
    clean_script = clean_text_for_speech(text)
    tts = gTTS(text=clean_script, lang='en', slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp

# 7. Load Predictor Engine
@st.cache_resource
def load_predictor():
    return PlantDiseasePredictor()

try:
    predictor = load_predictor()
    model_loaded = True
except Exception as e:
    model_loaded = False
    st.error("❌ Predictor load error. Ensure model and class files exist.")

# 8. Upload and Main Interface
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
            disease_name, confidence, is_unknown, gemini_result = predictor.predict(image)

            st.markdown("---")
            st.markdown("## 📊 Analysis Findings")

            if is_unknown:
                st.warning("⚠️ Low confidence detection! This leaf appears to be outside our trained dataset.")
                st.markdown("### 🤖 AI Gemini Vision Diagnosis")
                st.info(gemini_result)
                
                organic_text = clean_text_for_speech(gemini_result)
                chemical_text = "Consult a local agricultural extension officer."
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
                    st.success("🟢 **Optimal Plant Health Detected!**")

                # Retrieve specific remedy dynamically
                treatment = get_remedy(disease_name)
                organic_text = treatment["organic"]
                chemical_text = treatment["chemical"]

                # Render UI Tabs
                tab1, tab2 = st.tabs(["🌱 Organic / Bio Remedies", "🧪 Chemical Control"])
                with tab1:
                    st.info(organic_text)
                with tab2:
                    st.warning(chemical_text)

                class_name = disease_name

            # 9. English Voice Output Generation
            st.markdown("---")
            st.markdown("### 🔊 Voice Remedies (English)")
            
            try:
                audio_stream = create_audio_bytes(organic_text)
                st.audio(audio_stream, format="audio/mp3")
            except Exception as audio_err:
                st.caption(f"Audio playback currently unavailable: {str(audio_err)}")

            st.markdown("---")
            
            # 10. Generate PDF Report
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