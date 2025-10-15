#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML dosyalarını JSON veritabanına dönüştüren Python scripti
Bu script html klasöründeki tüm HTML dosyalarını okur ve hiyerarşik bir JSON yapısında saklar.
"""

import os
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict

def clean_text(text):
    """Metni temizler ve gereksiz boşlukları kaldırır"""
    if not text:
        return ""
    # Gereksiz boşlukları ve karakterleri temizle
    text = re.sub(r'\s+', ' ', text.strip())
    # HTML entity'lerini düzelt
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    return text

def extract_content_from_html(file_path):
    """HTML dosyasından içerik bilgilerini çıkarır"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Temel bilgileri çıkar
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = clean_text(title_tag.get_text())
        
        # Meta bilgileri
        description = ""
        desc_meta = soup.find('meta', {'name': 'description'})
        if desc_meta:
            description = clean_text(desc_meta.get('content', ''))
        
        keywords = ""
        keywords_meta = soup.find('meta', {'name': 'keywords'})
        if keywords_meta:
            keywords = clean_text(keywords_meta.get('content', ''))
        
        # Ana başlık
        main_title = ""
        h1_tag = soup.find('h1', class_='p_Heading1')
        if h1_tag:
            main_title = clean_text(h1_tag.get_text())
        
        # İçerik alanını bul (idcontent div'i)
        content_div = soup.find('div', {'id': 'idcontent'})
        content_text = ""
        if content_div:
            # Script ve style tag'lerini kaldır
            for script in content_div.find_all(['script', 'style']):
                script.decompose()
            content_text = clean_text(content_div.get_text())
        
        # Tablo içeriğini özel olarak işle (genelge listeleri için)
        table_content = []
        tables = soup.find_all('table', class_='Genelge')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                for cell in cells:
                    cell_text = clean_text(cell.get_text())
                    if cell_text:
                        # Linkleri de çıkar
                        links = cell.find_all('a')
                        for link in links:
                            href = link.get('href', '')
                            if href:
                                table_content.append({
                                    'text': cell_text,
                                    'link': href
                                })
                                break
                        else:
                            table_content.append({
                                'text': cell_text,
                                'link': None
                            })
        
        # Dosya adından yıl bilgisini çıkar
        filename = os.path.basename(file_path)
        year_match = re.search(r'(\d{4})', filename)
        year = year_match.group(1) if year_match else ""
        
        # Dosya türünü belirle
        file_type = "genelge"
        if "yili-genelgeleri" in filename:
            file_type = "yillik_liste"
        elif "sayili-genelge" in filename:
            file_type = "tekil_genelge"
        
        return {
            'filename': filename,
            'title': title,
            'main_title': main_title,
            'description': description,
            'keywords': keywords,
            'year': year,
            'file_type': file_type,
            'content': content_text,
            'table_content': table_content,
            'file_path': file_path,
            'created_at': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"Hata: {file_path} dosyası işlenirken hata oluştu: {str(e)}")
        return None

def organize_by_year_and_type(documents):
    """Dökümanları yıl ve türe göre organize eder"""
    organized = defaultdict(lambda: defaultdict(list))
    
    for doc in documents:
        if doc:
            year = doc['year']
            file_type = doc['file_type']
            organized[year][file_type].append(doc)
    
    # Her kategorideki dosyaları sırala
    for year in organized:
        for file_type in organized[year]:
            organized[year][file_type].sort(key=lambda x: x['filename'])
    
    return dict(organized)

def main():
    """Ana fonksiyon"""
    html_dir = "html"
    output_file = "noter_genelgeleri.json"
    
    print("HTML dosyaları işleniyor...")
    
    # HTML dosyalarını bul
    html_files = []
    if os.path.exists(html_dir):
        for filename in os.listdir(html_dir):
            if filename.endswith('.html'):
                html_files.append(os.path.join(html_dir, filename))
    
    if not html_files:
        print("HTML dosyası bulunamadı!")
        return
    
    print(f"{len(html_files)} HTML dosyası bulundu.")
    
    # Her HTML dosyasını işle
    documents = []
    for i, file_path in enumerate(html_files, 1):
        print(f"İşleniyor ({i}/{len(html_files)}): {os.path.basename(file_path)}")
        doc = extract_content_from_html(file_path)
        if doc:
            documents.append(doc)
    
    print(f"{len(documents)} dosya başarıyla işlendi.")
    
    # Verileri organize et
    organized_data = organize_by_year_and_type(documents)
    
    # İstatistikler
    stats = {
        'total_documents': len(documents),
        'years': list(organized_data.keys()),
        'year_counts': {year: len([doc for doc in documents if doc['year'] == year]) 
                       for year in organized_data.keys()},
        'type_counts': {
            'yillik_liste': len([doc for doc in documents if doc['file_type'] == 'yillik_liste']),
            'tekil_genelge': len([doc for doc in documents if doc['file_type'] == 'tekil_genelge']),
            'genelge': len([doc for doc in documents if doc['file_type'] == 'genelge'])
        }
    }
    
    # JSON yapısını oluştur
    json_data = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'source_directory': html_dir,
            'total_files': len(html_files),
            'processed_files': len(documents),
            'statistics': stats
        },
        'documents': organized_data
    }
    
    # JSON dosyasına yaz
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nJSON veritabanı başarıyla oluşturuldu: {output_file}")
        print(f"Toplam {len(documents)} döküman işlendi.")
        print(f"Yıllar: {', '.join(sorted(organized_data.keys()))}")
        
        # Dosya boyutunu göster
        file_size = os.path.getsize(output_file)
        print(f"Dosya boyutu: {file_size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"JSON dosyası yazılırken hata oluştu: {str(e)}")

if __name__ == "__main__":
    main()
