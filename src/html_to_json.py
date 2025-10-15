"""
HTML to JSON Converter
Bu modül HTML dosyalarını yapılandırılmış JSON formatına dönüştürür.
"""

import json
import os
import asyncio
import aiofiles
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from tqdm import tqdm

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HTMLToJSONConverter:
    """HTML dosyalarını JSON formatına dönüştürücü"""
    
    def __init__(self, input_dir: str = "db", output_dir: str = "json_output"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """HTML'den temiz metin içeriği çıkar"""
        # Script ve style etiketlerini kaldır
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Metni al ve temizle
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_metadata(self, soup: BeautifulSoup, file_path: str) -> Dict[str, Any]:
        """HTML'den metadata çıkar"""
        metadata = {
            "file_path": str(file_path),
            "title": "",
            "description": "",
            "keywords": [],
            "author": "",
            "created_date": "",
            "last_modified": "",
            "language": "tr",
            "encoding": "utf-8"
        }
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata["title"] = title_tag.get_text().strip()
        
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            metadata["description"] = desc_tag.get('content', '').strip()
        
        # Meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            keywords = keywords_tag.get('content', '').strip()
            if keywords:
                metadata["keywords"] = [k.strip() for k in keywords.split(',')]
        
        # Meta author
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if author_tag:
            metadata["author"] = author_tag.get('content', '').strip()
        
        # Language
        lang_tag = soup.find('html')
        if lang_tag:
            metadata["language"] = lang_tag.get('lang', 'tr')
        
        return metadata
    
    def extract_links(self, soup: BeautifulSoup, base_path: str) -> List[Dict[str, str]]:
        """HTML'den linkleri çıkar"""
        links = []
        
        for link in soup.find_all('a', href=True):
            link_info = {
                "text": link.get_text().strip(),
                "href": link.get('href'),
                "title": link.get('title', ''),
                "target": link.get('target', '')
            }
            
            # İç link mi dış link mi kontrol et
            href = link.get('href', '')
            if href.startswith('http'):
                link_info["type"] = "external"
            elif href.startswith('#'):
                link_info["type"] = "anchor"
            else:
                link_info["type"] = "internal"
            
            links.append(link_info)
        
        return links
    
    def extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """HTML'den resimleri çıkar"""
        images = []
        
        for img in soup.find_all('img'):
            img_info = {
                "src": img.get('src', ''),
                "alt": img.get('alt', ''),
                "title": img.get('title', ''),
                "width": img.get('width', ''),
                "height": img.get('height', '')
            }
            images.append(img_info)
        
        return images
    
    def extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """HTML'den başlıkları çıkar"""
        headings = []
        
        for level in range(1, 7):  # h1-h6
            for heading in soup.find_all(f'h{level}'):
                heading_info = {
                    "level": level,
                    "text": heading.get_text().strip(),
                    "id": heading.get('id', ''),
                    "class": heading.get('class', [])
                }
                headings.append(heading_info)
        
        return headings
    
    def extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """HTML'den tabloları çıkar"""
        tables = []
        
        for table in soup.find_all('table'):
            table_data = {
                "headers": [],
                "rows": [],
                "caption": ""
            }
            
            # Caption
            caption = table.find('caption')
            if caption:
                table_data["caption"] = caption.get_text().strip()
            
            # Headers (th)
            headers = table.find_all('th')
            if headers:
                table_data["headers"] = [th.get_text().strip() for th in headers]
            
            # Rows (tr)
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = [cell.get_text().strip() for cell in cells]
                    table_data["rows"].append(row_data)
            
            if table_data["headers"] or table_data["rows"]:
                tables.append(table_data)
        
        return tables
    
    def extract_lists(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """HTML'den listeleri çıkar"""
        lists = []
        
        for list_tag in soup.find_all(['ul', 'ol']):
            list_type = list_tag.name
            list_items = []
            
            for li in list_tag.find_all('li', recursive=False):
                item_text = li.get_text().strip()
                # Alt listeleri kontrol et
                sublists = li.find_all(['ul', 'ol'], recursive=False)
                if sublists:
                    # Basit metin çıkarma için alt listeleri geç
                    item_text = item_text.split('\n')[0].strip()
                
                list_items.append(item_text)
            
            if list_items:
                lists.append({
                    "type": list_type,
                    "items": list_items
                })
        
        return lists
    
    def extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """HTML'den formları çıkar"""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                "action": form.get('action', ''),
                "method": form.get('method', 'get'),
                "fields": []
            }
            
            # Form alanlarını çıkar
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                field_data = {
                    "type": input_tag.get('type', input_tag.name),
                    "name": input_tag.get('name', ''),
                    "id": input_tag.get('id', ''),
                    "placeholder": input_tag.get('placeholder', ''),
                    "value": input_tag.get('value', ''),
                    "required": input_tag.get('required') is not None
                }
                
                # Textarea için özel işlem
                if input_tag.name == 'textarea':
                    field_data["value"] = input_tag.get_text().strip()
                
                # Select için seçenekleri ekle
                if input_tag.name == 'select':
                    options = []
                    for option in input_tag.find_all('option'):
                        options.append({
                            "value": option.get('value', ''),
                            "text": option.get_text().strip(),
                            "selected": option.get('selected') is not None
                        })
                    field_data["options"] = options
                
                form_data["fields"].append(field_data)
            
            forms.append(form_data)
        
        return forms
    
    async def convert_html_to_json(self, html_file_path: Path) -> Dict[str, Any]:
        """Tek bir HTML dosyasını JSON'a dönüştür"""
        try:
            # HTML dosyasını oku
            async with aiofiles.open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = await f.read()
            
            # BeautifulSoup ile parse et
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # JSON yapısını oluştur
            json_data = {
                "metadata": self.extract_metadata(soup, html_file_path),
                "content": {
                    "text": self.extract_text_content(soup),
                    "headings": self.extract_headings(soup),
                    "links": self.extract_links(soup, str(html_file_path)),
                    "images": self.extract_images(soup),
                    "tables": self.extract_tables(soup),
                    "lists": self.extract_lists(soup),
                    "forms": self.extract_forms(soup)
                },
                "raw_html": html_content,
                "conversion_date": datetime.now().isoformat()
            }
            
            return json_data
            
        except Exception as e:
            logger.error(f"HTML to JSON dönüştürme hatası ({html_file_path}): {str(e)}")
            return {}
    
    async def convert_all_html_files(self):
        """Tüm HTML dosyalarını JSON'a dönüştür"""
        html_files = list(self.input_dir.rglob("*.html"))
        
        if not html_files:
            logger.warning(f"Hiç HTML dosyası bulunamadı: {self.input_dir}")
            return
        
        logger.info(f"{len(html_files)} HTML dosyası bulundu, dönüştürme başlıyor...")
        
        # Progress bar
        pbar = tqdm(html_files, desc="Dönüştürülüyor", unit="dosya")
        
        for html_file in pbar:
            try:
                # JSON'a dönüştür
                json_data = await self.convert_html_to_json(html_file)
                
                if json_data:
                    # Çıktı dosya yolunu belirle
                    relative_path = html_file.relative_to(self.input_dir)
                    json_file_path = self.output_dir / relative_path.with_suffix('.json')
                    
                    # Dizin yapısını oluştur
                    json_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # JSON dosyasını kaydet
                    async with aiofiles.open(json_file_path, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(json_data, ensure_ascii=False, indent=2))
                    
                    pbar.set_postfix({"Dönüştürülen": html_file.name})
                
            except Exception as e:
                logger.error(f"Dosya işleme hatası ({html_file}): {str(e)}")
        
        pbar.close()
        logger.info(f"Tüm HTML dosyaları JSON'a dönüştürüldü: {self.output_dir}")
    
    async def create_master_index(self):
        """Ana indeks dosyası oluştur"""
        json_files = list(self.output_dir.rglob("*.json"))
        
        master_index = {
            "created_at": datetime.now().isoformat(),
            "total_files": len(json_files),
            "files": []
        }
        
        for json_file in json_files:
            try:
                # JSON dosyasını oku
                async with aiofiles.open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.loads(await f.read())
                
                file_info = {
                    "file_path": str(json_file.relative_to(self.output_dir)),
                    "title": json_data.get("metadata", {}).get("title", ""),
                    "description": json_data.get("metadata", {}).get("description", ""),
                    "keywords": json_data.get("metadata", {}).get("keywords", []),
                    "word_count": len(json_data.get("content", {}).get("text", "").split()),
                    "link_count": len(json_data.get("content", {}).get("links", [])),
                    "image_count": len(json_data.get("content", {}).get("images", [])),
                    "heading_count": len(json_data.get("content", {}).get("headings", [])),
                    "table_count": len(json_data.get("content", {}).get("tables", [])),
                    "conversion_date": json_data.get("conversion_date", "")
                }
                
                master_index["files"].append(file_info)
                
            except Exception as e:
                logger.error(f"İndeks oluşturma hatası ({json_file}): {str(e)}")
        
        # Ana indeksi kaydet
        master_index_path = self.output_dir / "master_index.json"
        async with aiofiles.open(master_index_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(master_index, ensure_ascii=False, indent=2))
        
        logger.info(f"Ana indeks oluşturuldu: {master_index_path}")


async def main():
    """Ana fonksiyon"""
    converter = HTMLToJSONConverter("db", "json_output")
    
    # HTML dosyalarını JSON'a dönüştür
    await converter.convert_all_html_files()
    
    # Ana indeksi oluştur
    await converter.create_master_index()


if __name__ == "__main__":
    asyncio.run(main())
