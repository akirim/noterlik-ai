#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from collections import defaultdict

class SafeDataMerger:
    def __init__(self):
        self.backup_dir = "backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        self.all_documents = {}
        self.all_categories = defaultdict(list)
        self.metadata = {
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "total_documents": 0,
            "total_categories": 0,
            "data_sources": []
        }
    
    def create_backup(self):
        """Tüm mevcut dosyaları yedekle"""
        print("🛡️ Güvenlik yedeği oluşturuluyor...")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # JSON dosyalarını yedekle
        json_files = [
            'modern_data_complete.json',
            'complete_analysis.json', 
            'modern_data.json',
            'noter_genelgeleri.json',
            'fihrist_analysis.json',
            'working_links.json',
            'full_analysis.json'
        ]
        
        for file in json_files:
            if os.path.exists(file):
                import shutil
                shutil.copy2(file, f"{self.backup_dir}/{file}")
                print(f"   ✅ {file} yedeklendi")
        
        # HTML klasörünü yedekle
        if os.path.exists('html'):
            import shutil
            shutil.copytree('html', f"{self.backup_dir}/html")
            print(f"   ✅ html/ klasörü yedeklendi")
        
        print(f"✅ Yedek oluşturuldu: {self.backup_dir}")
    
    def analyze_html_files(self):
        """HTML dosyalarını analiz et"""
        print("📁 HTML dosyaları analiz ediliyor...")
        
        html_dir = 'html'
        if not os.path.exists(html_dir):
            print("❌ HTML klasörü bulunamadı!")
            return []
        
        html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
        print(f"   📄 {len(html_files)} HTML dosyası bulundu")
        
        html_documents = []
        for html_file in html_files:
            file_path = os.path.join(html_dir, html_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # HTML'den başlık ve içerik çıkar
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Başlık
                title = soup.find('title')
                title_text = title.get_text().strip() if title else html_file.replace('.html', '')
                
                # Ana başlık
                h1 = soup.find('h1')
                main_title = h1.get_text().strip() if h1 else title_text
                
                # İçerik
                content_div = soup.find('div', {'id': 'idcontent'})
                if content_div:
                    content_text = content_div.get_text().strip()
                else:
                    content_text = soup.get_text().strip()
                
                # İçerik temizleme
                content_text = ' '.join(content_text.split())
                content_text = content_text[:2000] + '...' if len(content_text) > 2000 else content_text
                
                # Kategori belirleme
                category = self.determine_category(html_file)
                
                doc = {
                    'id': html_file.replace('.html', ''),
                    'title': title_text,
                    'main_title': main_title,
                    'category': category,
                    'content': content_text,
                    'file': html_file,
                    'url': f'html/{html_file}',
                    'source': 'html_file'
                }
                
                html_documents.append(doc)
                
            except Exception as e:
                print(f"   ❌ {html_file} okunamadı: {e}")
        
        print(f"✅ {len(html_documents)} HTML dosyası işlendi")
        return html_documents
    
    def determine_category(self, filename):
        """Dosya adından kategori belirle"""
        filename_lower = filename.lower()
        
        if 'artes' in filename_lower:
            return 'ARTES - Araç Tescil'
        elif 'yazi' in filename_lower:
            return 'YAZI SERVİSİ'
        elif 'vezne' in filename_lower:
            return 'VEZNE SERVİSİ'
        elif 'genelge' in filename_lower:
            return 'GENELGELER'
        elif 'makale' in filename_lower:
            return 'MAKALELER'
        elif 'mevzuat' in filename_lower:
            return 'MEVZUAT'
        elif 'takvim' in filename_lower:
            return 'TAKVİM'
        elif 'hesap' in filename_lower:
            return 'HESAP MAKİNESİ'
        elif 'yas' in filename_lower:
            return 'YAŞ HESAPLA'
        elif 'yardim' in filename_lower:
            return 'YARDIM'
        elif 'kaynak' in filename_lower:
            return 'KAYNAK - DESTEK'
        elif 'onoz' in filename_lower:
            return 'ÖNSÖZ'
        elif 'mahkeme' in filename_lower:
            return 'MAHKEME KARARLARI'
        elif 'internet' in filename_lower:
            return 'İNTERNET SİTELERİ'
        elif 'tavsiye' in filename_lower:
            return 'TAVSİYELER'
        elif 'tnb' in filename_lower:
            return 'TNB MEVZUATI'
        elif 'noterlik' in filename_lower:
            return 'NOTERLİK KANUNU'
        elif 'isleme' in filename_lower:
            return 'İŞLEME'
        elif 'islemler' in filename_lower:
            return 'İŞLEMLER'
        else:
            return 'GENEL'
    
    def merge_json_data(self):
        """JSON dosyalarındaki verileri birleştir"""
        print("📊 JSON dosyaları birleştiriliyor...")
        
        json_files = [
            ('modern_data_complete.json', 'modern_data'),
            ('complete_analysis.json', 'complete_analysis'),
            ('modern_data.json', 'modern_data_old'),
            ('noter_genelgeleri.json', 'noter_genelgeleri')
        ]
        
        merged_documents = []
        
        for json_file, source_name in json_files:
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.metadata['data_sources'].append({
                        'file': json_file,
                        'source': source_name,
                        'processed': datetime.now().isoformat()
                    })
                    
                    # Dökümanları çıkar
                    if 'documents' in data:
                        for doc in data['documents']:
                            if isinstance(doc, dict):
                                doc['source'] = source_name
                                merged_documents.append(doc)
                    
                    # Kategorileri çıkar
                    elif 'categories' in data:
                        for category, items in data['categories'].items():
                            if isinstance(items, list):
                                for item in items:
                                    if isinstance(item, dict):
                                        item['source'] = source_name
                                        merged_documents.append(item)
                    
                    print(f"   ✅ {json_file}: {len(data.get('documents', data.get('categories', {})))} öğe işlendi")
                    
                except Exception as e:
                    print(f"   ❌ {json_file} okunamadı: {e}")
        
        print(f"✅ {len(merged_documents)} JSON dökümanı birleştirildi")
        return merged_documents
    
    def create_unified_dataset(self):
        """Birleşik veri seti oluştur"""
        print("🔄 Birleşik veri seti oluşturuluyor...")
        
        # 1. Yedek oluştur
        self.create_backup()
        
        # 2. HTML dosyalarını analiz et
        html_documents = self.analyze_html_files()
        
        # 3. JSON verilerini birleştir
        json_documents = self.merge_json_data()
        
        # 4. Tüm dökümanları birleştir
        all_docs = html_documents + json_documents
        
        # 5. Duplikasyonları kaldır (ID'ye göre)
        unique_docs = {}
        for doc in all_docs:
            doc_id = doc.get('id', doc.get('file', '').replace('.html', ''))
            if doc_id and doc_id not in unique_docs:
                unique_docs[doc_id] = doc
            elif doc_id and doc_id in unique_docs:
                # Aynı ID'li döküman varsa, daha güncel olanı al
                if doc.get('source') == 'html_file':
                    unique_docs[doc_id] = doc
        
        # 6. Kategorilere göre grupla
        for doc_id, doc in unique_docs.items():
            category = doc.get('category', 'GENEL')
            self.all_categories[category].append(doc)
        
        # 7. Metadata güncelle
        self.metadata['total_documents'] = len(unique_docs)
        self.metadata['total_categories'] = len(self.all_categories)
        
        # 8. Final veri setini oluştur
        final_data = {
            "metadata": self.metadata,
            "categories": dict(self.all_categories),
            "documents": list(unique_docs.values())
        }
        
        # 9. Dosyaya kaydet
        output_file = "noterlik_complete.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Birleşik veri seti oluşturuldu: {output_file}")
        print(f"   📊 Toplam döküman: {len(unique_docs)}")
        print(f"   📁 Toplam kategori: {len(self.all_categories)}")
        
        return output_file
    
    def validate_data(self, output_file):
        """Veri bütünlüğünü doğrula"""
        print("🔍 Veri bütünlüğü doğrulanıyor...")
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_docs = data['metadata']['total_documents']
            total_cats = data['metadata']['total_categories']
            
            # Kategori sayısını kontrol et
            actual_cats = len(data['categories'])
            actual_docs = len(data['documents'])
            
            print(f"   📊 Metadata: {total_docs} döküman, {total_cats} kategori")
            print(f"   📊 Gerçek: {actual_docs} döküman, {actual_cats} kategori")
            
            if total_docs == actual_docs and total_cats == actual_cats:
                print("✅ Veri bütünlüğü doğrulandı!")
                return True
            else:
                print("❌ Veri bütünlüğü hatası!")
                return False
                
        except Exception as e:
            print(f"❌ Doğrulama hatası: {e}")
            return False

def main():
    merger = SafeDataMerger()
    
    # Birleşik veri seti oluştur
    output_file = merger.create_unified_dataset()
    
    # Veri bütünlüğünü doğrula
    if merger.validate_data(output_file):
        print("\n🎉 VERİ BİRLEŞTİRME BAŞARILI!")
        print(f"📁 Yedek klasörü: {merger.backup_dir}")
        print(f"📄 Çıktı dosyası: {output_file}")
    else:
        print("\n❌ VERİ BİRLEŞTİRME BAŞARISIZ!")
        print(f"🛡️ Yedek klasöründen geri yükleyebilirsiniz: {merger.backup_dir}")

if __name__ == "__main__":
    main()
