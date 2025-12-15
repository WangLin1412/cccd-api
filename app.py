from flask import Flask, request, send_file, jsonify
import pytesseract
from PIL import Image
import io
import re
from openpyxl import Workbook

app = Flask(__name__)

# =============================
# 1) HÀM OCR ẢNH
# =============================
def ocr_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img, lang="vie")
    return text

# =============================
# 2) HÀM TRÍCH XUẤT THÔNG TIN CCCD
# =============================
def extract_cccd_info(text):
    info = {}

    patterns = {
        "ho_ten": r"Họ tên[:\s]*([A-ZÀ-Ỹ\s]+)",
        "so_cccd": r"\b0\d{11}\b",
        "ngay_sinh": r"Ngày sinh[:\s]*([0-9/]+)",
        "gioi_tinh": r"Giới tính[:\s]*(Nam|Nữ)",
        "quoc_tich": r"Quốc tịch[:\s]*([A-Za-zÀ-ỹ\s]+)",
        "dia_chi": r"(Thường trú|Địa chỉ)[:\s]*(.+)",
        "ngay_cap": r"Ngày cấp[:\s]*([0-9/]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info[key] = match.group(1).strip()

    return info

# =============================
# 3) TẠO FILE EXCEL
# =============================
def create_excel(data):
    wb = Workbook()
    ws = wb.active
    ws.title = "CCCD"

    ws.append(["Trường", "Giá trị"])

    for k, v in data.items():
        ws.append([k, v])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# =============================
# 4) API /ocr-cccd
# =============================
@app.route("/ocr-cccd", methods=["POST"])
def ocr_cccd():
    if "file" not in request.files:
        return jsonify({"error": "Không có file upload"}), 400

    file = request.files["file"]
    img_bytes = file.read()

    text = ocr_image(img_bytes)
    data = extract_cccd_info(text)

    if len(data) == 0:
        return jsonify({"error": "Không trích xuất được thông tin"}), 400

    excel_file = create_excel(data)

    return send_file(
        excel_file,
        download_name="cccd.xlsx",
        as_attachment=True
    )

@app.route("/", methods=["GET"])
def home():
    return "API CCCD OCR is running"

if __name__ == "__main__":
    app.run(debug=True)
