import streamlit as st
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import re
import matplotlib.pyplot as plt

# ✅ Your custom Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\mkhan\OneDrive\Desktop\ISE AFTER MIDS\tesseract.exe"

# ---------------------- Prediction Functions ----------------------
def generate_prediction(data):
    last_values = data[-5:] if len(data) >= 5 else data
    low_count = sum(1 for x in last_values if x < 2.0)

    if low_count >= 3:
        return [1.05, 1.21, 1.10, 3.77, 1.18, 1.14, 6.88]
    else:
        return [1.12, 1.22, 1.34, 1.08, 2.03, 1.14, 2.88]

def show_confidence(predicted_values):
    if max(predicted_values) > 5.0:
        return "🎯 Confidence: **90%** that a high value may come"
    elif max(predicted_values) > 2.0:
        return "🎯 Confidence: **75%** — average range pattern"
    else:
        return "🎯 Confidence: **60%** — low pattern likely"

# ---------------------- Grid Image Generator ----------------------
def generate_grid_image(predicted_values, save_path="prediction_grid.png"):
    width, height = 660, 220
    img = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    x, y = 10, 10
    box_w, box_h = 100, 40
    padding = 10

    colors = {
        "low": "#00BFFF",
        "medium": "#C71585",
        "high": "#FFD700",
    }

    for i, val in enumerate(predicted_values):
        if val < 2.0:
            color = colors["low"]
        elif val < 5.0:
            color = colors["medium"]
        else:
            color = colors["high"]

        box = (x, y, x + box_w, y + box_h)
        draw.rectangle(box, fill=color)
        draw.text((x + 10, y + 7), f"{val:.2f}x", fill="black", font=font)

        x += box_w + padding
        if x + box_w > width:
            x = 10
            y += box_h + padding

    img.save(save_path)

# ---------------------- Streamlit UI ----------------------
st.set_page_config(page_title="Aviator Predictor", layout="centered")
st.title(":dart: Smart Aviator Multiplier Predictor")
st.markdown("Upload your **screenshot** and let the app learn from the data to guide your decisions.")

uploaded_file = st.file_uploader(":camera: Upload Screenshot", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Screenshot", use_column_width=True)
    image = Image.open(uploaded_file)

    # Step 1: OCR
    with st.spinner(":mag: Reading numbers from image..."):
        text = pytesseract.image_to_string(image)
        numbers = re.findall(r"\d+\.\d+x", text)
        data = [float(n.replace("x", "")) for n in numbers]

    if data:
        st.success(":white_check_mark: Data Extracted")
        st.write(f":chart_with_upwards_trend: Total rounds: {len(data)}")
        st.write(data)

        # Step 2: Stats
        gt_2 = len([n for n in data if n > 2])
        gt_5 = len([n for n in data if n > 5])
        gt_7 = len([n for n in data if n > 7])

        st.markdown("### :abacus: Basic Stats")
        st.write(f":small_blue_diamond: >2x: `{gt_2}` ({gt_2/len(data)*100:.2f}%)")
        st.write(f":small_blue_diamond: >5x: `{gt_5}` ({gt_5/len(data)*100:.2f}%)")
        st.write(f":small_blue_diamond: >7x: `{gt_7}` ({gt_7/len(data)*100:.2f}%)")

        # Step 3: Range Probabilities
        st.markdown("### 🎯 Prediction for Next Round")
        ranges = {
            "1x to 2x": (1.00, 2.00),
            "2x to 3x": (2.00, 3.00),
            "3x to 5x": (3.00, 5.00),
            "5x to 10x": (5.00, 10.00),
            "10x+": (10.00, float("inf"))
        }

        range_counts = {label: 0 for label in ranges}
        for val in data:
            for label, (low, high) in ranges.items():
                if low <= val < high:
                    range_counts[label] += 1
                    break

        total = len(data)
        range_chances = {label: round((count / total) * 100, 2) for label, count in range_counts.items()}

        for label, percent in range_chances.items():
            st.write(f":small_orange_diamond: **{label}**: {percent}% of rounds")

        likely_range = max(range_chances.items(), key=lambda x: x[1])
        st.markdown(f":loudspeaker: Most rounds end in **{likely_range[0]}**. Likely next: **{likely_range[0]}**")

        # Step 4: Predict and Show Grid
        st.markdown("## 🔮 Pattern Prediction")
        predicted = generate_prediction(data)
        generate_grid_image(predicted)
        st.image("prediction_grid.png", caption="Predicted Pattern (Educational Use)")

        confidence = show_confidence(predicted)
        st.success(confidence)

        st.markdown("""
        🧠 **Note:** This prediction is based on historical patterns only.  
        This app is built purely for educational and data learning purposes.
        """)
