import io
import datetime
from fpdf import FPDF
from PIL import Image

class PlantReportPDF(FPDF):
    def header(self):
        # Header banner
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(34, 139, 34)  # Forest Green
        self.cell(0, 10, "Plant Health Diagnosis Report", border=False, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_draw_color(200, 200, 200)
        self.line(10, 22, 200, 22)
        self.ln(5)

    def footer(self):
        # Page numbers
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf_report(disease_name, confidence, organic_remedy, chemical_remedy, leaf_image: Image.Image = None):
    pdf = PlantReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Date and Time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Generated on: {current_time}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # 1. Embed Leaf Image (if provided)
    if leaf_image:
        # Convert PIL image to bytes buffer for FPDF
        img_buffer = io.BytesIO()
        leaf_image.convert("RGB").save(img_buffer, format="JPEG")
        img_buffer.seek(0)
        
        # Insert image into PDF (width=60mm, centered)
        pdf.image(img_buffer, x=75, w=60)
        pdf.ln(5)

    # 2. Diagnosis Section
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "1. Diagnosis Results", new_x="LMARGIN", new_y="NEXT")

    formatted_disease = disease_name.replace("___", " - ").replace("_", " ")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Condition Detected: {formatted_disease}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Model Confidence: {confidence * 100:.2f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # 3. Treatments Section
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Recommended Treatments", new_x="LMARGIN", new_y="NEXT")

    # Organic Treatment
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(0, 7, "Organic Remedies:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 6, organic_remedy)
    pdf.ln(3)

    # Chemical Treatment
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(178, 34, 34)  # Firebrick Red
    pdf.cell(0, 7, "Chemical Remedies:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 6, chemical_remedy)

    # Return PDF binary stream
    return bytes(pdf.output())