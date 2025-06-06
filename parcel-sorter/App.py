import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import pytesseract
import re

# Configure Tesseract path (change if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# OCR utility functions
def clean_ocr_text(text):
    text = text.replace("ane", "Name")
    text = re.sub(r'[Pp]osteode', 'Postcode', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_postcode(text):
    match = re.search(r'Postcode[:\s]*([0-9]{5})', text)
    return match.group(1) if match else None

def classify_zone(postcode):
    pc = int(postcode)
    if 10000 <= pc < 20000: return "Zone A"
    elif 20000 <= pc < 30000: return "Zone B"
    elif 30000 <= pc < 40000: return "Zone C"
    elif 40000 <= pc < 50000: return "Zone D"
    elif 50000 <= pc < 60000: return "Zone E"
    elif 60000 <= pc < 70000: return "Zone F"
    elif 70000 <= pc < 80000: return "Zone G"
    return "Unknown Zone"

# Streamlit UI
st.title("📦 Parcel Zone Sorting system")

# Define video transformer for webcam
class OCRTransformer(VideoTransformerBase):
    def __init__(self):
        self.postcode = None
        self.zone = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Convert to grayscale & threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # OCR
        raw_text = pytesseract.image_to_string(thresh)
        cleaned = clean_ocr_text(raw_text)
        postcode = extract_postcode(cleaned)
        zone = classify_zone(postcode) if postcode else "N/A"

        self.postcode = postcode
        self.zone = zone

        # Display info on webcam feed
        overlay = f"Postcode: {postcode if postcode else 'Not Found'} | Zone: {zone}"
        cv2.putText(img, overlay, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return img

# Start webcam stream
ctx = webrtc_streamer(key="example", video_transformer_factory=OCRTransformer)

# Show result
if ctx.video_transformer:
    postcode = ctx.video_transformer.postcode
    zone = ctx.video_transformer.zone
    if postcode:
        st.success(f"Detected Postcode: {postcode}")
        st.info(f"Zone: {zone}")

