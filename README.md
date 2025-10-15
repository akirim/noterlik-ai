# Noterlik Rehberi - Modern Web Arayüzü

## 📋 Proje Hakkında

Bu proje, Noterlik Rehberi'nin modern web arayüzü versiyonudur. Orijinal desktop uygulamasının tüm içeriğini modern, responsive bir web arayüzüne dönüştürür.

## ✨ Özellikler

### 🎨 **Modern Tasarım**
- Responsive tasarım (mobil, tablet, masaüstü)
- Modern CSS Grid ve Flexbox layout
- Dark mode desteği
- Font Awesome ikonları
- Inter font ailesi

### 🔍 **Gelişmiş Arama ve Filtreleme**
- 19 kategori filtreleme sistemi
- Gerçek zamanlı arama
- Kategori bazlı içerik görüntüleme
- Gelişmiş filtreleme seçenekleri

### 📊 **Veri İstatistikleri**
- **Toplam Döküman**: 908
- **Toplam Kategori**: 19
- **HTML Dosyası**: 1,830+

### 📁 **Kategori Dağılımı**
1. **MAHKEME KARARLARI**: 345 döküman
2. **GENEL**: 240 döküman
3. **GENELGELER**: 75 döküman
4. **İŞLEME**: 64 döküman
5. **YAZI SERVİSİ**: 60 döküman
6. **ARTES - Araç Tescil**: 35 döküman
7. **MAKALELER**: 27 döküman
8. **MEVZUAT**: 19 döküman
9. **TNB MEVZUATI**: 14 döküman
10. **NOTERLİK KANUNU**: 8 döküman

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.7+
- Modern web tarayıcısı

### Kurulum
```bash
# Repository'yi klonlayın
git clone https://github.com/akirim/noterlik-ai.git
cd noterlik-ai

# Python bağımlılıklarını yükleyin
pip install -r requirements.txt
```

### Çalıştırma
```bash
# Web sunucusunu başlatın
python -m http.server 8001

# Tarayıcıda açın
# http://localhost:8001/modern_index.html
```

## 📁 Proje Yapısı

```
noterlik-ai/
├── modern_index.html          # Modern web arayüzü
├── modern_data_complete.json  # Tam veri seti
├── html/                      # Orijinal HTML dosyaları
│   ├── index.html
│   └── ... (1,830+ dosya)
├── complete_analysis.json     # Kapsamlı analiz sonuçları
├── requirements.txt           # Python bağımlılıkları
└── README.md                 # Bu dosya
```

## 🛠️ Geliştirme Araçları

### Veri Analizi Scriptleri
- `complete_crawler.py` - Kapsamlı web tarama
- `download_website.py` - Website indirme
- `html_to_json.py` - HTML'den JSON'a dönüştürme

### Test Scriptleri
- `test_urls.py` - URL testleri
- `download_missing_files.py` - Eksik dosya indirme

## 📱 Responsive Breakpoints

- **Masaüstü**: 1200px+ (Grid layout)
- **Tablet**: 768px-1199px (Adaptive layout)
- **Mobil**: 767px altı (Single column)

## 🎯 Teknik Özellikler

- **Vanilla JavaScript** (framework bağımlılığı yok)
- **CSS Custom Properties** (tema desteği)
- **Fetch API** (modern veri yükleme)
- **ES6+ syntax** (modern JavaScript)
- **Progressive Enhancement** (temel işlevsellik garantisi)

## 📊 Veri Yapısı

```json
{
  "categories": {
    "MAHKEME KARARLARI": [
      {
        "id": "unique-id",
        "title": "Sayfa Başlığı",
        "main_title": "Ana Başlık",
        "category": "Kategori",
        "content": "İçerik metni...",
        "file": "dosya.html",
        "url": "http://..."
      }
    ]
  },
  "total_documents": 908,
  "total_categories": 19
}
```

## 🔄 Güncelleme Süreci

1. **Veri Toplama**: Orijinal uygulamadan tüm içerik analiz edilir
2. **Kategorizasyon**: Otomatik kategori belirleme
3. **Modern Arayüz**: Responsive web tasarımı
4. **Test**: Tüm cihazlarda test edilir

## 📈 Gelecek Planları

- [ ] Sol menü + tab sistemi (orijinal tasarım yapısı)
- [ ] Hierarchical navigasyon
- [ ] Favori sayfalar
- [ ] Yazdırma optimizasyonu
- [ ] Offline çalışma desteği
- [ ] Gelişmiş arama algoritmaları

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

- **GitHub**: [akirim](https://github.com/akirim)
- **Repository**: [noterlik-ai](https://github.com/akirim/noterlik-ai)

---

**Not**: Bu proje, Noterlik Rehberi'nin modern web versiyonudur. Tüm içerik orijinal kaynaklardan alınmıştır.