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
    /* Main Background & Fonts */
    .main {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }
    
    /* Header Card */
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
        text-shadow: 0 0 10px rgba(78, 205, 196, 0.3);
    }

    .header-subtitle {
        color: #B2BEC3;
        font-size: 1.1rem;
    }

    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
        color: #4E8A1B !important;
    }

    /* Custom Buttons */
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
        box-shadow: 0 4px 15px rgba(56, 239, 125, 0.4);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(56, 239, 125, 0.6);
    }
    
    /* File Uploader Container */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #4E8A1B;
        border-radius: 15px;
        padding: 10px;
        background: rgba(255, 255, 255, 0.02);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Catchy Header Banner
st.markdown("""
    <div class="header-card">
        <div class="header-title">🌿 AgriGuard AI</div>
        <div class="header-subtitle">Instant Leaf Disease Detection & Biological Remedies</div>
    </div>
""", unsafe_allow_html=True)

# 4. Sidebar Information (Fixed image render using Native Emojis)
with st.sidebar:
    st.markdown("## 🌿 **AgriGuard AI**")
    st.caption("AI-Powered Botanical Health Engine")
    
    st.info("""
        **Powered by MobileNetV2**
        
        This deep learning system identifies 38 different plant conditions across crops like Tomato, Potato, Apple, and Pepper.
    """)
    st.markdown("---")
    st.caption("🚀 Version 2.0 | High-Speed Inference Engine")

# 5. Comprehensive Database of Remedies for 38 PlantVillage Classes
REMEDIES = {
    # Apple
    "Apple___Apple_scab": {
        "organic": "Apply neem oil, liquid copper fungicide, or sulfur spray. Rake and burn fallen leaves to prevent overwintering spores.",
        "chemical": "Spray fungicides containing captan, myclobutanil, or mancozeb during early bud stages."
    },
    "Apple___Black_rot": {
        "organic": "Prune out dead or cankered wood during winter. Remove all mummified fruit from the tree and ground.",
        "chemical": "Apply captan or thiophanate-methyl fungicides starting at petal fall."
    },
    "Apple___Cedar_apple_rust": {
        "organic": "Prune galls from nearby juniper/cedar hosts. Apply sulfur or copper fungicides early in spring.",
        "chemical": "Spray myclobutanil or propiconazole at pink-bud stage through petal fall."
    },
    "Apple___healthy": {
        "organic": "No treatment required. Continue regular watering and pruning.",
        "chemical": "No chemical intervention needed."
    },

    # Blueberry
    "Blueberry___healthy": {
        "organic": "Maintain acidic soil pH (4.5–5.5) and keep soil consistently moist with organic mulch.",
        "chemical": "No chemical intervention needed."
    },

    # Cherry
    "Cherry_(including_sour)___Powdery_mildew": {
        "organic": "Apply potassium bicarbonate, neem oil, or sulfur. Ensure good canopy airflow.",
        "chemical": "Apply myclobutanil, quinoxyfen, or tebuconazole fungicides."
    },
    "Cherry_(including_sour)___healthy": {
        "organic": "Maintain balanced soil fertility and proper pruning for light penetration.",
        "chemical": "No chemical intervention needed."
    },

    # Corn (Maize)
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "organic": "Use disease-resistant hybrids and practice crop rotation with non-host crops like soybeans.",
        "chemical": "Apply azoxystrobin, pyraclostrobin, or propiconazole fungicides."
    },
    "Corn_(maize)___Common_rust": {
        "organic": "Plant resistant corn varieties. Destroy infected crop residue after harvest.",
        "chemical": "Apply fungicides containing strobilurins or triazoles if rust appears before tasseling."
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "organic": "Rotate crops annually and plow under crop residue to speed decomposition of fungal spores.",
        "chemical": "Apply foliar fungicides such as mancozeb, azoxystrobin, or propiconazole."
    },
    "Corn_(maize)___healthy": {
        "organic": "Maintain proper plant spacing and soil nitrogen levels.",
        "chemical": "No chemical intervention needed."
    },

    # Grape
    "Grape___Black_rot": {
        "organic": "Remove mummified berries and prune canopy to maximize sunlight and air circulation. Apply copper sprays.",
        "chemical": "Apply myclobutanil, azoxystrobin, or mancozeb from bud break until 4 weeks post-bloom."
    },
    "Grape___Esca_(Black_Measles)": {
        "organic": "Prune out infected wood during dormant season. Disinfect pruning shears between cuts using 70% alcohol.",
        "chemical": "Apply wound protectants (e.g., thiophanate-methyl) immediately after pruning."
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "organic": "Apply copper-based fungicides. Clear fallen leaves around the base of vines.",
        "chemical": "Spray fungicides containing copper hydroxide, mancozeb, or captan."
    },
    "Grape___healthy": {
        "organic": "Prune vines annually to balance leaf canopy and fruit load.",
        "chemical": "No chemical intervention needed."
    },

    # Peach
    "Peach___Bacterial_spot": {
        "organic": "Spray copper fungicides during dormant season. Avoid excessive nitrogen fertilization.",
        "chemical": "Apply oxytetracycline or copper hydroxide mixed with mancozeb during early bloom."
    },
    "Peach___healthy": {
        "organic": "Mulch root zone and monitor for peach tree borer activity.",
        "chemical": "No chemical intervention needed."
    },

    # Pepper (Bell)
    "Pepper,_bell___Bacterial_spot": {
        "organic": "Apply fixed copper sprays combined with liquid soap. Avoid overhead sprinkler irrigation.",
        "chemical": "Spray copper hydroxide combined with mancozeb for enhanced bacterial control."
    },
    "Pepper,_bell___healthy": {
        "organic": "Provide consistent moisture and balanced phosphorus/potassium soil nutrients.",
        "chemical": "No chemical intervention needed."
    },

    # Potato
    "Potato___Early_blight": {
        "organic": "Mulch around base to prevent soil splashback. Spray bio-fungicides containing Bacillus subtilis or copper.",
        "chemical": "Apply chlorothalonil, mancozeb, or azoxystrobin at early disease onset."
    },
    "Potato___Late_blight": {
        "organic": "Destroy infected foliage immediately. Apply fixed copper sprays regularly in humid conditions.",
        "chemical": "Apply systemic fungicides containing cymoxanil, dimethomorph, or chlorothalonil."
    },
    "Potato___healthy": {
        "organic": "Hill potato plants regularly and ensure well-drained soil.",
        "chemical": "No chemical intervention needed."
    },

    # Raspberry
    "Raspberry___healthy": {
        "organic": "Prune old fruited canes after harvest to encourage strong new growth.",
        "chemical": "No chemical intervention needed."
    },

    # Soybean
    "Soybean___healthy": {
        "organic": "Practice 2-year crop rotation with corn or wheat to break pest cycles.",
        "chemical": "No chemical intervention needed."
    },

    # Squash
    "Squash___Powdery_mildew": {
        "organic": "Spray neem oil, potassium bicarbonate, or a diluted milk solution (40% milk, 60% water) on leaves.",
        "chemical": "Apply myclobutanil, trifloxystrobin, or sulfur fungicides."
    },

    # Strawberry
    "Strawberry___Leaf_scorch": {
        "organic": "Remove old infected leaves post-harvest. Apply copper or sulfur sprays.",
        "chemical": "Apply fungicides containing captan, thiram, or myclobutanil."
    },
    "Strawberry___healthy": {
        "organic": "Keep beds weed-free and apply straw mulch to keep fruit clean.",
        "chemical": "No chemical intervention needed."
    },

    # Tomato
    "Tomato___Bacterial_spot": {
        "organic": "Spray copper fungicides. Avoid working with plants while foliage is wet.",
        "chemical": "Apply copper hydroxide mixed with mancozeb for improved bacterial suppression."
    },
    "Tomato___Early_blight": {
        "organic": "Prune lower leaves touching the soil. Apply copper fungicide or potassium bicarbonate.",
        "chemical": "Apply chlorothalonil, mancozeb, or pyraclostrobin fungicides."
    },
    "Tomato___Late_blight": {
        "organic": "Remove and bag infected plants immediately. Apply copper sprays defensively.",
        "chemical": "Spray fungicides containing chlorothalonil, famoxadone, or cymoxanil."
    },
    "Tomato___Leaf_Mold": {
        "organic": "Improve greenhouse airflow and lower relative humidity below 85%. Apply copper fungicide.",
        "chemical": "Apply chlorothalonil, difenoconazole, or mancozeb."
    },
    "Tomato___Septoria_leaf_spot": {
        "organic": "Remove lower infected leaves as spots appear. Apply copper-based organic fungicides.",
        "chemical": "Spray chlorothalonil or mancozeb every 7–10 days during rainy periods."
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "organic": "Release predatory mites (Phytoseiulus persimilis). Spray insecticidal soap, neem oil, or rosemary oil.",
        "chemical": "Apply miticides containing abamectin, bifenazate, or spiromesifen."
    },
    "Tomato___Target_Spot": {
        "organic": "Provide wide spacing between plants for ventilation. Spray copper-based fungicides.",
        "chemical": "Apply fungicides containing azoxystrobin, chlorothalonil, or mancozeb."
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "organic": "Control whiteflies using yellow sticky traps and neem oil. Cover plants with 50-mesh insect netting.",
        "chemical": "Apply systemic insecticides like imidacloprid or acetamiprid to suppress whitefly vectors."
    },
    "Tomato___Tomato_mosaic_virus": {
        "organic": "Disinfect tools in 10% bleach solution. Remove and burn infected plants (no direct viral cure).",
        "chemical": "No chemical cure available for viral infections. Focus on controlling vector insects."
    },
    "Tomato___healthy": {
        "organic": "Provide deep watering at base level, full sun, and sturdy staking/caging.",
        "chemical": "No chemical intervention needed."
    }
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
    st.error("❌ Model file not found. Ensure your trained model exists inside 'models/'.")

# 7. Upload and Interface Section
st.subheader("🔍 Upload Leaf Sample")
uploaded_file = st.file_uploader("Drop a clear leaf image below (PNG, JPG, JPEG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and model_loaded:
    image = Image.open(uploaded_file)
    
    # Display preview image in a neat layout
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(image, caption="Uploaded Leaf Sample", use_container_width=True)
    
    with col2:
        st.markdown("### Sample Ready")
        st.write("Click below to start neural network analysis.")
        run_analysis = st.button("⚡ Run AI Diagnosis")

    if run_analysis:
        with st.spinner("🔍 Processing tensor embeddings..."):
            class_name, confidence = predictor.predict(image)
            formatted_label = class_name.replace("___", " - ").replace("_", " ")

            st.markdown("---")
            st.markdown("## 📊 Analysis Findings")
            
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.metric(label="Diagnosed Condition", value=formatted_label)
            with res_col2:
                st.metric(label="Confidence Rating", value=f"{confidence * 100:.2f}%")

            st.markdown("---")
            st.subheader("🛠️ Prescription & Action Plan")

            if "healthy" in class_name.lower():
                st.balloons()
                organic_text = "No treatment required. Maintain standard watering, proper soil nutrients, and full sunlight."
                chemical_text = "No chemical intervention needed."
                st.success("🟢 **Optimal Plant Health Detected!**")
            else:
                treatment = REMEDIES.get(class_name, {
                    "organic": "Apply neem oil or copper-based organic fungicides. Prune affected areas to improve airflow.",
                    "chemical": "Consult a local agricultural expert for targeted fungicides suitable for your crop."
                })
                organic_text = treatment["organic"]
                chemical_text = treatment["chemical"]

                tab1, tab2 = st.tabs(["🌱 Organic / Bio Remedies", "🧪 Chemical Control"])
                with tab1:
                    st.info(organic_text)
                with tab2:
                    st.warning(chemical_text)

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