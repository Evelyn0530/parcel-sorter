import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# Set page title and layout
st.set_page_config(page_title="Parcel Zone Sorter System", layout="centered")

# App heading
st.markdown("## 📦 Parcel Zone Sorter System")
st.write("Hold a parcel label up to your webcam. The system will extract the postcode and show the delivery zone.")

# Helper functions
def clean_ocr_text(text):
    text = text.replace("ane", "Name")
    text = re.sub(r'[Pp]osteode', 'Postcode', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_postcode(text):
    match = re.search(r'Postcode[:\s]*([0-9]{5})', text)
    return match.group(1) if match else None

def classify_zone(postcode):
    if postcode:
        pc = int(postcode)
        if 10000 <= pc < 20000: return "Zone A"
        elif 20000 <= pc < 30000: return "Zone B"
        elif 30000 <= pc < 40000: return "Zone C"
        elif 40000 <= pc < 50000: return "Zone D"
        elif 50000 <= pc < 60000: return "Zone E"
        elif 60000 <= pc < 70000: return "Zone F"
        elif 70000 <= pc < 80000: return "Zone G"
    return "Unknown Zone"

# Video processing class
class VideoProcessor(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Convert to grayscale and threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # OCR
        raw_text = pytesseract.image_to_string(thresh)
        cleaned = clean_ocr_text(raw_text)
        postcode = extract_postcode(cleaned)
        zone = classify_zone(postcode)

        # Display info on the frame
        label = f"{postcode if postcode else 'Not Found'} | {zone}"
        cv2.putText(img, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        return img

# Start the webcam with Streamlit WebRTC
webrtc_streamer(
    key="parcel-zone-sorter",
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)
