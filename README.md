# Otomatik Sertifika Üretici 🎓

Bu proje, bir Excel listesindeki katılımcı bilgilerini kullanarak, belirlenmiş bir PDF tasarımı üzerine isimleri otomatik olarak işleyen ve her katılımcı için ayrı bir sertifika üreten bir Python aracıdır.

## ✨ Özellikler
*   **Akıllı İsim Düzeltici:** Türkçe karakter desteği ile isimlerin sadece baş harflerini büyük, geri kalanını küçük yapar (Örn: "AHMET CAN" -> "Ahmet Can").
*   **Yüksek Çözünürlük:** 300 DPI kalitesinde PDF çıktıları üretir.
*   **Mükemmel Hizalama:** İsimleri sertifika üzerinde yatay olarak otomatik olarak ortalar.
*   **Hata Yönetimi:** Dosya çakışmalarını önlemek için güvenli dosya adlandırma (safe filename) kullanır.
*   **Test Modu:** `--test` parametresi ile tüm liste yerine tek bir örnek çıktı alarak ayarları kontrol etme imkanı sunar.

## 📁 Proje Yapısı
Projenin sağlıklı çalışması için klasör düzeni şu şekilde olmalıdır:
*   `generate_certificates.py`: Ana uygulama kodu.
*   `excel.xlsx`: Katılımcı listesi (AD ve SOYAD sütunlarını içermelidir).
*   `template.pdf`: Sertifika şablonu (Tasarım dosyası).
*   `sertifikalar/`: Üretilen sertifikaların kaydedileceği klasör (Otomatik oluşturulur).

## 🛠️ Kurulum ve Kullanım

1.  **Gereksinimleri Yükleyin:**
    ```bash
    pip install pymupdf pandas openpyxl pillow
    ```

2.  **Uygulamayı Çalıştırın:**
    ```bash
    python generate_certificates.py
    ```

3.  **Hızlı Test (Sadece ilk kişi için):**
    ```bash
    python generate_certificates.py --test

## ⚙️ Teknik Detaylar
**Kütüphaneler:** PyMuPDF (PDF okuma), Pillow (Görüntü işleme), Pandas (Veri analizi).

**Font:** Sistemde yüklü olan "Arial" fontunu temel alır.

**Konumlandırma:** İsimler, dikey eksende %62 (NAME_Y_RATIO) seviyesine yerleştirilir.

✍️ Hazırlayan
Ahmet Can Erduran

### Küçük Bir Not:
Kodunda `fitz` (PyMuPDF) ve `openpyxl` (Excel okumak için pandas'ın arkada kullandığı motor) kütüphaneleri kullanılıyor. Eğer bu kütüphaneler bilgisayarında yüklü değilse, terminale şu komutu yazarak hepsini tek seferde kurabilirsin:
```bash
pip install pymupdf pandas openpyxl pillow
