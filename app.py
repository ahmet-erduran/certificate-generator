#!/usr/bin/env python3
"""
Web Tabanlı Sertifika Oluşturucu ve Düzenleyici
"""

import os
import io
import base64
import zipfile
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import fitz

from generate_certificates import (
    load_participants,
    render_certificate_image,
    safe_filename,
    find_font,
    fix_turkish_name
)

app = Flask(__name__, template_folder="templates", static_folder="static")

# Dosya yüklemeleri için maksimum boyut (32 MB)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "sertifikalar")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Bellekte varsayılan şablon/katılımcı önbelleği
DEFAULT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.pdf")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/parse-excel", methods=["POST"])
def parse_excel():
    """Yüklenen Excel dosyasını okuyup sütun ve katılımcı listesini döndürür."""
    if 'file' not in request.files:
        return jsonify({"error": "Excel dosyası bulunamadı."}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "Dosya seçilmedi."}), 400

    try:
        content = file.read()
        file_bytes = io.BytesIO(content)

        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_bytes)
        else:
            df = pd.read_excel(file_bytes)

        columns = [str(c) for c in df.columns]

        # Tekrar başa sarıp katılımcıları oku
        file_bytes.seek(0)
        participants = load_participants(file_bytes)

        return jsonify({
            "columns": columns,
            "participants": participants,
            "count": len(participants)
        })
    except Exception as e:
        return jsonify({"error": f"Excel dosyası okunamadı: {str(e)}"}), 500


@app.route("/api/render-preview", methods=["POST"])
def render_preview():
    """Sertifika üzerindeki metni ayarlara göre oluşturup PNG olarak döndürür."""
    try:
        data = request.form
        name_text = data.get("name", "Örnek Katılımcı Adı")
        y_ratio = float(data.get("y_ratio", 0.62))
        x_ratio = float(data.get("x_ratio", 0.50))
        font_size = int(data.get("font_size", 84))
        font_color = data.get("font_color", "#000000")
        align = data.get("align", "center")
        dpi = int(data.get("dpi", 150)) # Önizleme için 150 DPI hızlıdır

        name_text = fix_turkish_name(name_text)

        # Şablon dosyası (yüklenmiş dosya varsa onu, yoksa varsayılanı kullan)
        if 'template' in request.files and request.files['template'].filename:
            template_bytes = request.files['template'].read()
        elif os.path.exists(DEFAULT_TEMPLATE_PATH):
            with open(DEFAULT_TEMPLATE_PATH, "rb") as f:
                template_bytes = f.read()
        else:
            return jsonify({"error": "Lütfen önce bir PDF şablonu yükleyin."}), 400

        font_path = find_font()

        img = render_certificate_image(
            name=name_text,
            template_path_or_bytes=template_bytes,
            font_path=font_path,
            font_size=font_size,
            y_ratio=y_ratio,
            x_ratio=x_ratio,
            font_color=font_color,
            align=align,
            dpi=dpi
        )

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return jsonify({
            "image": f"data:image/png;base64,{base64_str}",
            "width": img.width,
            "height": img.height
        })
    except Exception as e:
        return jsonify({"error": f"Önizleme oluşturulurken hata: {str(e)}"}), 500


@app.route("/api/render-base-template", methods=["POST"])
def render_base_template():
    """Şablonun sadece kendisini (yazısız) görsel olarak döndürür (Tuval üzerine çizim için)."""
    try:
        if 'template' in request.files and request.files['template'].filename:
            template_bytes = request.files['template'].read()
        elif os.path.exists(DEFAULT_TEMPLATE_PATH):
            with open(DEFAULT_TEMPLATE_PATH, "rb") as f:
                template_bytes = f.read()
        else:
            return jsonify({"error": "Şablon bulunamadı."}), 400

        doc = fitz.open(stream=template_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72), alpha=False)
        buffer = io.BytesIO(pix.tobytes("png"))
        doc.close()

        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return jsonify({
            "image": f"data:image/png;base64,{base64_str}",
            "width": pix.width,
            "height": pix.height
        })
    except Exception as e:
        return jsonify({"error": f"Şablon okunamadı: {str(e)}"}), 500


@app.route("/api/generate-batch", methods=["POST"])
def generate_batch():
    """Tüm katılımcılar için sertifikaları üretip ZIP dosyası olarak veya klasöre kaydeder."""
    try:
        # Form verileri
        y_ratio = float(request.form.get("y_ratio", 0.62))
        x_ratio = float(request.form.get("x_ratio", 0.50))
        font_size = int(request.form.get("font_size", 84))
        font_color = request.form.get("font_color", "#000000")
        align = request.form.get("align", "center")
        save_to_disk = request.form.get("save_to_disk", "false").lower() == "true"

        # Şablon PDF
        if 'template' in request.files and request.files['template'].filename:
            template_bytes = request.files['template'].read()
        elif os.path.exists(DEFAULT_TEMPLATE_PATH):
            with open(DEFAULT_TEMPLATE_PATH, "rb") as f:
                template_bytes = f.read()
        else:
            return jsonify({"error": "Lütfen önce bir PDF şablonu yükleyin."}), 400

        # Katılımcılar
        participants = []
        if 'excel' in request.files and request.files['excel'].filename:
            excel_bytes = io.BytesIO(request.files['excel'].read())
            participants = load_participants(excel_bytes)
        elif request.form.get("participants_json"):
            import json
            participants = json.loads(request.form.get("participants_json"))

        if not participants:
            return jsonify({"error": "Üretilecek katılımcı bulunamadı. Lütfen Excel dosyası yükleyin."}), 400

        font_path = find_font()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for name in participants:
                pdf_bytes_io = io.BytesIO()
                img = render_certificate_image(
                    name=name,
                    template_path_or_bytes=template_bytes,
                    font_path=font_path,
                    font_size=font_size,
                    y_ratio=y_ratio,
                    x_ratio=x_ratio,
                    font_color=font_color,
                    align=align,
                    dpi=300 # Baskı kalitesinde 300 DPI
                )
                img.save(pdf_bytes_io, format="PDF", resolution=300)

                filename = f"{safe_filename(name)}.pdf"
                pdf_bytes = pdf_bytes_io.getvalue()
                
                # ZIP içine ekle
                zip_file.writestr(filename, pdf_bytes)

                # Diske kaydetme istendiyse
                if save_to_disk:
                    out_path = os.path.join(OUTPUT_FOLDER, filename)
                    with open(out_path, "wb") as f:
                        f.write(pdf_bytes)

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="sertifikalar.zip"
        )
    except Exception as e:
        return jsonify({"error": f"Sertifikalar üretilirken hata oluştu: {str(e)}"}), 500


if __name__ == "__main__":
    print("Sertifika Web Arayüzü başlatılıyor...")
    print("Erişim adresi: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
