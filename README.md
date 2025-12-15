# CCCD OCR API

API nhận ảnh CCCD → OCR → trích thông tin → xuất Excel.

Cách chạy local:
pip install -r requirements.txt
python app.py

Deploy Render:
- Build: pip install -r requirements.txt
- Run: gunicorn app:app
