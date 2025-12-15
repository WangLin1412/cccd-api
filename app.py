from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
from PIL import Image
import pandas as pd
import os, uuid

app = Flask(__name__)
CORS(app)

reader = easyocr.Reader(['vi'], gpu=False)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "API CCCD OCR is running"

@app.route("/ocr", methods=["POST"])
def ocr_cccd():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    filename = f"{uuid.uuid4()}.jpg"
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image_file.save(image_path)

    # OCR bằng EasyOCR
    results = reader.readtext(image_path, detail=0)
    text = "\n".join(results)

    data = {
        "raw_text": text.strip()
    }

    excel_name = f"{uuid.uuid4()}.xlsx"
    excel_path = os.path.join(OUTPUT_FOLDER, excel_name)
    pd.DataFrame([data]).to_excel(excel_path, index=False)

    return jsonify({
        "data": data,
        "excel_url": request.host_url + "download/" + excel_name
    })

@app.route("/download/<filename>")
def download_file(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(path):
        return "Not found", 404
    return open(path, "rb").read()
