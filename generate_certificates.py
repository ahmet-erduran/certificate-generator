#!/usr/bin/env python3
"""
Sertifika Üretici - Katılımcı listesinden tek tek sertifika görselleri/PDF'leri üretir.
Web arayüzünün (app.py) kullandığı motor fonksiyonlarını içerir.
"""

import fitz
import pandas as pd
import os
import re
from PIL import Image, ImageDraw, ImageFont

# ─── VARSYAYILAN AYARLAR ─────────────────────────────────────────────────────
DPI = 300
NAME_FONT_SIZE = 84
NAME_Y_RATIO = 0.620
NAME_X_RATIO = 0.5
NAME_COLOR = (0, 0, 0)


# ─── FONT YOLU ──────────────────────────────────────────────────────────────


def find_font():
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\ArialBD.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Font bulunamadı! Arial veya benzeri bir font yüklü olmalı.")


# ─── İSİM DÜZELTİCİ (TÜRKÇE UYUMLU) ──────────────────────────────────────────


def fix_turkish_name(name):
    """İsimlerin sadece baş harflerini büyük, kalanını küçük yapar."""
    if not name or not isinstance(name, str):
        return ""
    lower_map = {ord("I"): "ı", ord("İ"): "i"}
    upper_map = {ord("i"): "İ", ord("ı"): "I"}

    words = name.split()
    fixed_words = []

    for word in words:
        if not word:
            continue
        first_char = word[0].translate(upper_map).upper()
        rest_chars = word[1:].translate(lower_map).lower()
        fixed_words.append(first_char + rest_chars)

    return " ".join(fixed_words)


# ────────────────────────────────────────────────────────────────────────────


def safe_filename(name):
    name = str(name).strip()
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.replace(" ", "_")


def load_participants(excel_path_or_stream, name_col=None, surname_col=None):
    """Excel veya CSV dosyasından katılımcı listesini yükler."""
    if isinstance(excel_path_or_stream, str) and excel_path_or_stream.endswith('.csv'):
        df = pd.read_csv(excel_path_or_stream)
    else:
        df = pd.read_excel(excel_path_or_stream)

    participants = []
    seen = set()

    for _, row in df.iterrows():
        ad = ""
        soyad = ""

        if name_col and name_col in row and pd.notna(row[name_col]):
            ad = str(row[name_col]).strip()
        elif "AD" in row and pd.notna(row["AD"]):
            ad = str(row["AD"]).strip()
        elif "Ad" in row and pd.notna(row["Ad"]):
            ad = str(row["Ad"]).strip()

        if surname_col and surname_col in row and pd.notna(row[surname_col]):
            soyad = str(row[surname_col]).strip()
        elif "SOYAD" in row and pd.notna(row["SOYAD"]):
            soyad = str(row["SOYAD"]).strip()
        elif "Soyad" in row and pd.notna(row["Soyad"]):
            soyad = str(row["Soyad"]).strip()

        # Eğer tek sütunda tam ad varsa (Ad Soyad)
        if not ad and not soyad and len(df.columns) == 1:
            full_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        else:
            full_name = f"{ad} {soyad}".strip()

        if not full_name:
            continue

        clean_name = fix_turkish_name(full_name)
        key = clean_name.lower()
        if key in seen:
            continue
        seen.add(key)
        participants.append(clean_name)

    return participants


def render_certificate_image(
    name,
    template_path_or_bytes,
    font_path=None,
    font_size=NAME_FONT_SIZE,
    y_ratio=NAME_Y_RATIO,
    x_ratio=NAME_X_RATIO,
    font_color=NAME_COLOR,
    align="center",
    dpi=DPI
):
    """Sertifikayı PIL Image nesnesi olarak render eder."""
    font_path = font_path or find_font()

    if isinstance(template_path_or_bytes, bytes):
        doc = fitz.open(stream=template_path_or_bytes, filetype="pdf")
    else:
        doc = fitz.open(template_path_or_bytes)

    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), name, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    if align == "left":
        x = img.width * x_ratio
    elif align == "right":
        x = (img.width * x_ratio) - tw
    else:  # center
        x = (img.width * x_ratio) - (tw / 2)

    y = (img.height * y_ratio) - (th / 2)

    # Renk formatı kontrolü (hex string veya tuple)
    if isinstance(font_color, str) and font_color.startswith("#"):
        font_color = font_color.lstrip("#")
        font_color = tuple(int(font_color[i:i+2], 16) for i in (0, 2, 4))

    draw.text((x, y), name, fill=font_color, font=font)
    return img