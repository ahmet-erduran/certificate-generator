# AGENTS.md

Web tabanlı sertifika oluşturucu. Flask (`app.py`) ile sunulur; PDF şablonu üzerine katılımcı isimlerini çizen `generate_certificates.py` motorunu kullanır, `templates/index.html` arayüzü canlı sürükle-bırak düzenleme ve ZIP indirme sağlar. Paket manifesti yok, lint/config yok. Kod ve dokümanlar Türkçe — yeni mesaj/commit'ler Türkçe olmalı.

## Çalıştırma

```bash
pip install flask pymupdf pandas openpyxl pillow
python app.py          # http://127.0.0.1:5000
python test_app.py     # API endpoint'lerini test eder
```

CLI katmanı kaldırıldı; motor sadece `app.py` tarafından import edilir. `generate_certificates.py`'de `main()`/`if __name__` yok — CLI eklemeyin.

## Mimari

- `app.py` — Sunucu; endpoint'ler: `GET /`, `POST /api/parse-excel`, `POST /api/render-preview`, `POST /api/render-base-template`, `POST /api/generate-batch`.
- `generate_certificates.py` — Motor: `find_font()`, `fix_turkish_name()`, `safe_filename()`, `load_participants()`, `render_certificate_image()`. PDF şablonunu PIL ile görsele çevirir, ismi basar, PDF/ZIP üretir.
- `templates/index.html` — Tek sayfa arayüz (Tailwind CDN + Vanilla JS); drag handle önizlemede ismi hareket ettirir, `x_ratio`/`y_ratio` slider'ları ile eşleşir.
- `test_app.py` — Flask test client ile endpoint'leri doğrular.

## Dikkat Edilecekler

- Excel dosyası **`AD` ve `SOYAD`** sütunlarını içermeli; yoksa `load_participants()` isim/soyisim sütunlarını otomatik uyarlar.
- `find_font()` sabit font yollarını arar: Windows Arial + Linux Noto/DejaVu/Liberation. Font yoksa `FileNotFoundError`.
- Önizlemede isim konumu `y_ratio`/`x_ratio` oranlarıyla (0.0–1.0) hesaplanır; "center" hizasında isim genişliğine göre X ayarlanır.
- `fix_turkish_name()` Türkçe'ye özel I→ı, i→İ dönüşümü yapar; naif `.title()` bu karakterleri bozar.
- Şablon `template.pdf` dizinde durmalı ya da arayüzden yüklenmeli; `.gitignore` `*.pdf` içerdiği için şablon repo'da değil.
- Toplu üretim 300 DPI'da ZIP döndürür; `sertifikalar/`'a diske kaydetme opsiyoneldir (`save_to_disk`).
- `sertifikalar/` içinde geçmiş etkinlikler `sertifikalar_genelkurul/` vb. şeklinde `<etkinlik>` suffix kuralıyla adlandırılmış — yeni çıktı klasörü oluşturulursa bu kuralı izle.
- Yüklenen dosyalar RAM'da tutulur, kalıcı `uploads/` klasörü kullanılmaz.

## Repo / Git

- `.gitignore`: `*.xlsx`, `*.pdf`, `sertifikalar/` gibi çalışma gerektiren dosyalar repo dışında; şablon olmadan test edilemez.
- Tek commit'li repo; commit mesajları Türkçe.
