from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import pandas as pd
import os
import uuid

app = Flask(__name__)
CORS(app)

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

    # OCR
    text = pytesseract.image_to_string(Image.open(image_path), lang="vie")

    data = {
        "raw_text": text.strip()
    }

    # Xuất Excel
    excel_name = f"{uuid.uuid4()}.xlsx"
    excel_path = os.path.join(OUTPUT_FOLDER, excel_name)

    df = pd.DataFrame([data])
    df.to_excel(excel_path, index=False)

    excel_url = request.host_url + "download/" + excel_name

    return jsonify({
        "data": data,
        "excel_url": excel_url
    })


@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return open(file_path, "rb").read()
