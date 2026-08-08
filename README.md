# 🎓 Sertifika Üretici & Görsel Düzenleyici

PDF sertifika şablonu üzerine katılımcı adlarını otomatik olarak basan, web tabanlı görsel bir sertifika oluşturma aracı. Excel'deki katılımcı listesini kullanarak her katılımcı için hazır yüksek çözünürlükte (300 DPI) sertifika üretir.

> **Web arayüzü sayesinde** şablonu yükledikten sonra ismin yazılacağı yeri doğrudan görsele sürükleyerek ayarlayabilir, boyutu, rengi ve hizalamayı canlı olarak değiştirip sonucu anında görebilirsiniz.

---

## ✨ Özellikler

| Özellik | Açıklama |
|---|---|
| 🖼️ **Görsel Düzenleyici** | Sertifika önizlemesinde ismi fareyle sürükleyerek yerleştirir |
| ⚡ **Canlı Önizleme** | Ayarlar değiştikçe isim anında güncellenir |
| 🇹🇷 **Türkçe İsim Desteği** | `AHMET CAN` → `Ahmet Can`, `IŞIK` → `Işık` gibi akıllı düzeltme |
| 🖨️ **Baskı Kalitesi** | 300 DPI çözünürlükte PDF çıktıları |
| 🗂️ **Toplu Paketleme** | Tüm sertifikaları tek ZIP dosyası olarak indirme |
| 📊 **Excel/CSV Desteği** | `.xlsx`, `.xls`, `.csv` katılımcı listeleri |
| 🎨 **Tam Kontrol** | Font boyutu, renk, hizalama ve konum ayarları |

---

## 📁 Dosya Yapısı

```text
.
├── app.py                     # Web sunucusu (Flask)
├── generate_certificates.py   # Sertifika üretim motoru
├── templates/
│   └── index.html             # Web arayüzü (sürükle-bırak düzenleyici)
└── sertifikalar/             # Üretilen sertifikalar (otomatik oluşturulur)

```

---

## 🚀 Kurulum

### Gereksinimler

* Python 3.8+
* pip

### Bağımlılıkları Yükle

```bash
pip install -r requirements.txt

```

---

## 🖥️ Kullanım

### Windows — Tek Tıkla Başlat

Proje klasöründeki **`baslat.bat`** dosyasını çift tıklayın. Sunucu başlar ve tarayıcınızda `http://127.0.0.1:5000` adresi otomatik açılır.

### Manuel

Sunucuyu başlatın:

```bash
python app.py

```

Tarayıcınızda `http://127.0.0.1:5000` adresini açın. Ardından:

1. **Sertifika şablonunuzu** (PDF) ilgili alana yükleyin.
2. **Katılımcı listesini** (Excel/CSV) yükleyin.
3. Sağdaki önizlemede **ismi sürükleyerek** konumlandırın.
4. Font boyutu, renk ve hizalama ayarlarını yapın.
5. **"Tüm Sertifikaları Üret ve ZIP İndir"** butonuyla tek tıkla indirin.

---

## 📋 Excel Gereksinimleri

Katılımcı listesinde sertifika üzerinde yazdırılacak **ad** ve **soyad** bilgileri bulunmalıdır.

| AD | SOYAD |
| --- | --- |
| Ali | Yılmaz |
| Veli | Yılmaz |

> İstenirse tek sütun halinde tam ad da desteklenmektedir (ör. `Ad` sütunu).

---

## 🧪 Test

API uç noktalarını hızlıca doğrulamak için:

```bash
python test_app.py

```

---

## 🛠️ Teknik Detaylar

* **Web:** Flask
* **PDF İşleme:** PyMuPDF (`fitz`)
* **Görüntü İşleme:** Pillow (PIL)
* **Veri:** Pandas ve openpyxl
* **Önizleme Hızı:** Önizleme için 150 DPI, çıktı için 300 DPI kullanılır.
* **Varsayılan Şablon:** Sunucu dizinindeki `template.pdf` dosyası otomatik olarak kullanılır; yoksa web arayüzünden yüklemeniz gerekir.

---

## 📄 Lisans

Bu proje [MIT](https://www.google.com/search?q=LICENSE) lisansı altında yayınlanmaktadır.

```

### 🚀 Son Adım (Kaydet ve Gönder)

Yukarıdaki metni `README.md` dosyana yapıştırıp kaydettikten sonra, terminaline dönüp şu üç komutu sırasıyla çalıştır. Çakışma çözülecek ve projen GitHub'a başarıyla gidecek:

```bash
git add README.md
git commit -m "Merge conflict çözüldü: Güncel web arayüzü dokümantasyonu korundu"
git push origin main

```
