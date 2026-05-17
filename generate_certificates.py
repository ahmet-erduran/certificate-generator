#!/usr/bin/env python3
"""
SAYZEK Zirvesi - Sertifika Üretici
"""

import fitz
import pandas as pd
import os, re, sys
from PIL import Image, ImageDraw, ImageFont

# ─── AYARLAR ────────────────────────────────────────────────────────────────

# Dosya adını klasöründekiyle birebir aynı yap (Uzantısı .xlsx olduğundan emin ol)
EXCEL_FILE = r"GENEL KURUL FORM (Yanıtlar).xlsx"
TEMPLATE_PDF = r"Siyah.pdf"
OUTPUT_DIR = "sertifikalar"

DPI = 300
NAME_FONT_SIZE = 84
NAME_Y_RATIO = 0.620
NAME_COLOR = (0, 0, 0)

# ─── FONT YOLU ──────────────────────────────────────────────────────────────


def find_font():
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\ArialBD.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Font bulunamadı! Arial yüklü olmalı.")


# ─── İSİM DÜZELTİCİ (TÜRKÇE UYUMLU) ──────────────────────────────────────────


def fix_turkish_name(name):
    """İsimlerin sadece baş harflerini büyük, kalanını küçük yapar."""
    lower_map = {ord("I"): "ı", ord("İ"): "i"}
    upper_map = {ord("i"): "İ", ord("ı"): "I"}

    words = name.split()
    fixed_words = []

    for word in words:
        if not word:
            continue
        # İlk harf Büyük, kalanlar küçük
        first_char = word[0].translate(upper_map).upper()
        rest_chars = word[1:].translate(lower_map).lower()
        fixed_words.append(first_char + rest_chars)

    return " ".join(fixed_words)


# ────────────────────────────────────────────────────────────────────────────


def safe_filename(name):
    name = name.strip()
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.replace(" ", "_")


def load_participants(excel_path):
    # Excel dosyasını oku
    df = pd.read_excel(excel_path)
    participants = []
    seen = set()

    for _, row in df.iterrows():
        # Ekran görüntüsündeki sütun isimlerini (AD ve SOYAD) kullanıyoruz
        ad = str(row["AD"]).strip() if pd.notna(row.get("AD")) else ""
        soyad = str(row["SOYAD"]).strip() if pd.notna(row.get("SOYAD")) else ""

        if not ad and not soyad:
            continue

        # Ad ve soyadı birleştir ve düzelt
        full_name = f"{ad} {soyad}".strip()
        clean_name = fix_turkish_name(full_name)

        key = clean_name.lower()
        if key in seen:
            continue
        seen.add(key)
        participants.append(clean_name)

    return participants


def generate_certificate(name, output_path, font_path):
    doc = fitz.open(TEMPLATE_PDF)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(DPI / 72, DPI / 72), alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, NAME_FONT_SIZE)
    bbox = draw.textbbox((0, 0), name, font=font)
    tw = bbox[2] - bbox[0]
    x = (img.width - tw) / 2
    y = img.height * NAME_Y_RATIO
    draw.text((x, y), name, fill=NAME_COLOR, font=font)
    img.save(output_path, format="PDF", resolution=DPI)


def main():
    test_mode = "--test" in sys.argv
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        font_path = find_font()
        participants = load_participants(EXCEL_FILE)
    except FileNotFoundError as e:
        print(f"HATA: {e}")
        return
    except Exception as e:
        print(f"Excel okunurken hata oluştu: {e}")
        return

    if test_mode:
        participants = participants[:1]
        print(f"TEST modu: {participants[0]}")
    else:
        print(f"{len(participants)} kişi için işlem başlıyor...")

    errors = []
    for i, name in enumerate(participants, 1):
        fname = f"{safe_filename(name)}.pdf"
        out = os.path.join(OUTPUT_DIR, fname)
        try:
            generate_certificate(name, out, font_path)
            print(f"[{i:3}] {name:<40} Tamam")
        except Exception as e:
            errors.append((name, str(e)))
            print(f"[{i:3}] {name:<40} HATA: {e}")

    print(f"\nSonuç: {len(participants) - len(errors)} başarılı, {len(errors)} hatalı.")


if __name__ == "__main__":
    main()
