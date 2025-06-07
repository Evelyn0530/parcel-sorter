import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import cv2
import pytesseract
import re

# --- Helper functions ---
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

# --- Video processor ---
class OCRProcessor(VideoProcessorBase):
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        raw_text = pytesseract.image_to_string(thresh)
        cleaned = clean_ocr_text(raw_text)
        postcode = extract_postcode(cleaned)
        zone = classify_zone(postcode) if postcode else "N/A"

        display_text = f"Postcode: {postcode if postcode else 'Not Found'} | Zone: {zone}"
        cv2.putText(img, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- Streamlit interface ---
st.title("📦 Parcel Zone Sorter System")
st.markdown("Hold a parcel label up to your webcam. The system will extract the postcode and show the delivery zone.")

webrtc_streamer(
    key="ocr-zone",
    video_processor_factory=OCRProcessor,
    rtc_configuration=RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
)
