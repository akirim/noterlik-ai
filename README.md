# Noterlik AI - Gelişmiş Web Scraper & JSON Converter

Bu proje, localhost'taki HTML dosyalarını recursive olarak indiren, hiyerarşik olarak organize eden ve JSON formatına dönüştüren gelişmiş bir web scraper uygulamasıdır.

## 🚀 Özellikler

### ✨ Ana Özellikler
- **Recursive HTML İndirici**: İç içe geçmiş sayfaları sınırsız derinlikte indirir
- **Asenkron İşlem**: Multi-threaded ve asenkron işlemlerle yüksek performans
- **Hiyerarşik İndeksleme**: Dosyaları hiyerarşik olarak organize eder
- **HTML to JSON Dönüştürücü**: HTML dosyalarını yapılandırılmış JSON formatına dönüştürür
- **Modern Web Arayüzü**: Bootstrap 5 tabanlı responsive arayüz
- **Gerçek Zamanlı İzleme**: Progress bar ve log sistemi ile canlı takip

### 🔧 Teknik Özellikler
- **Python 3.8+** tabanlı
- **aiohttp** ile asenkron HTTP istekleri
- **BeautifulSoup4** ile HTML parsing
- **Bootstrap 5** ile modern UI
- **Font Awesome** ikonları
- **Responsive** tasarım

## 📁 Proje Yapısı

```
noterlik-ai/
├── main.py                 # Ana çalıştırma scripti
├── requirements.txt        # Python bağımlılıkları
├── index.html             # Web arayüzü
├── README.md              # Bu dosya
├── LICENSE                # Lisans dosyası
├── src/                   # Kaynak kodlar
│   ├── web_scraper.py     # Asenkron web scraper
│   ├── html_to_json.py    # HTML to JSON dönüştürücü
│   └── app.js             # Web arayüzü JavaScript
├── db/                    # İndirilen HTML dosyaları
└── json_output/           # JSON dönüştürülmüş dosyalar
```

## 🛠️ Kurulum

### 1. Gereksinimler
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### 2. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 3. Uygulamayı Çalıştır
```bash
python main.py
```

## 🎯 Kullanım

### Komut Satırı Arayüzü
Ana uygulamayı çalıştırdıktan sonra menüden seçenekleri kullanabilirsiniz:

1. **Web Scraping Başlat**: HTML dosyalarını indirir
2. **JSON'a Dönüştür**: HTML dosyalarını JSON formatına çevirir
3. **Tüm İşlemleri Çalıştır**: Her iki işlemi sırayla yapar
4. **Web Arayüzünü Aç**: Modern web arayüzünü açar
5. **Ayarları Düzenle**: Konfigürasyonu değiştirir
6. **İstatistikleri Görüntüle**: İşlem sonuçlarını gösterir
7. **Çıkış**: Uygulamayı kapatır

### Web Arayüzü
`index.html` dosyasını web tarayıcınızda açarak modern arayüzü kullanabilirsiniz:

- **Konfigürasyon**: URL, eşzamanlı istek sayısı ve çıktı klasörü ayarları
- **Kontrol Paneli**: Scraping başlatma, JSON dönüştürme ve durdurma
- **İlerleme Takibi**: Gerçek zamanlı progress bar ve istatistikler
- **Dosya Yapısı**: İndirilen dosyaların hiyerarşik görünümü
- **Sistem Logları**: Detaylı işlem logları

## ⚙️ Konfigürasyon

### Varsayılan Ayarlar
- **Base URL**: `http://127.0.0.1:8000/9B2F1556-3672-40F0-987D-D82A926AEFA4/index.html`
- **Eşzamanlı İstek**: 30
- **HTML Çıktı Klasörü**: `db`
- **JSON Çıktı Klasörü**: `json_output`

### Ayarları Değiştirme
1. Uygulama içinde "Ayarları Düzenle" seçeneğini kullanın
2. Veya `main.py` dosyasındaki `NoterlikApp` sınıfının `__init__` metodunu düzenleyin

## 📊 Çıktı Formatları

### HTML Dosyaları
- Hiyerarşik klasör yapısında organize edilir
- Orijinal URL yapısı korunur
- Benzersiz dosya adları oluşturulur

### JSON Dosyaları
Her HTML dosyası şu yapıda JSON'a dönüştürülür:

```json
{
  "metadata": {
    "file_path": "dosya/yolu.html",
    "title": "Sayfa Başlığı",
    "description": "Sayfa açıklaması",
    "keywords": ["anahtar", "kelimeler"],
    "author": "Yazar",
    "language": "tr",
    "encoding": "utf-8"
  },
  "content": {
    "text": "Temiz metin içeriği",
    "headings": [...],
    "links": [...],
    "images": [...],
    "tables": [...],
    "lists": [...],
    "forms": [...]
  },
  "raw_html": "Orijinal HTML içeriği",
  "conversion_date": "2025-01-16T00:00:00"
}
```

### İndeks Dosyaları
- `file_index.json`: Dosya yolu eşleştirmeleri
- `master_index.json`: Tüm dosyaların özet bilgileri

## 🔍 Özellik Detayları

### Web Scraper
- **Recursive İşlem**: Tüm iç linkleri takip eder
- **Asenkron İşlem**: 30 eşzamanlı istek (ayarlanabilir)
- **Hata Yönetimi**: Başarısız istekleri loglar ve devam eder
- **Progress Tracking**: Gerçek zamanlı ilerleme takibi
- **Duplicate Prevention**: Aynı URL'leri tekrar işlemez

### HTML to JSON Converter
- **Metadata Çıkarma**: Title, description, keywords vb.
- **İçerik Analizi**: Headings, links, images, tables
- **Metin Temizleme**: Script ve style etiketlerini kaldırır
- **Yapılandırılmış Veri**: Organize edilmiş JSON formatı
- **Batch İşlem**: Tüm dosyaları toplu olarak dönüştürür

## 🚨 Dikkat Edilmesi Gerekenler

1. **Rate Limiting**: Çok fazla eşzamanlı istek sunucuyu yorabilir
2. **Disk Alanı**: Büyük siteler için yeterli disk alanı sağlayın
3. **Ağ Bağlantısı**: Stabil internet bağlantısı önemlidir
4. **İzinler**: Hedef klasörlerde yazma izni olmalıdır

## 🐛 Sorun Giderme

### Yaygın Hatalar
- **Connection Error**: Sunucu erişilebilir mi kontrol edin
- **Permission Denied**: Klasör yazma izinlerini kontrol edin
- **Memory Error**: Eşzamanlı istek sayısını azaltın
- **Timeout**: Ağ bağlantınızı kontrol edin

### Log Dosyaları
- `scraper.log`: Detaylı işlem logları
- Console output: Gerçek zamanlı durum bilgileri

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 İletişim

Proje hakkında sorularınız için issue açabilir veya iletişime geçebilirsiniz.

---

**Noterlik AI v1.0** - Gelişmiş Web Scraper & JSON Converter
