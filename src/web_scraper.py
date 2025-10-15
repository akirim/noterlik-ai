"""
Asenkron Web Scraper - Recursive HTML İndirici
Bu modül localhost'taki HTML dosyalarını recursive olarak indirir ve hiyerarşik olarak organize eder.
"""

import asyncio
import aiohttp
import aiofiles
import os
import json
import time
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup
from typing import Set, Dict, List, Optional
from pathlib import Path
from tqdm.asyncio import tqdm
import logging
from datetime import datetime
import hashlib

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HierarchicalIndexer:
    """Hiyerarşik dosya indeksleme sistemi"""
    
    def __init__(self):
        self.index = {}
        self.file_counter = {}
        self.path_mapping = {}
        
    def generate_unique_filename(self, original_path: str, content: str = None) -> str:
        """Benzersiz dosya adı oluştur"""
        # URL'den dosya adını çıkar
        parsed = urlparse(original_path)
        path_parts = parsed.path.strip('/').split('/')
        
        if not path_parts or path_parts == ['']:
            filename = "index.html"
        else:
            filename = path_parts[-1]
            if not filename.endswith('.html'):
                filename += '.html'
        
        # Hiyerarşik yol oluştur
        hierarchical_path = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ""
        
        # Aynı isimde dosya varsa sayı ekle
        base_name = filename.replace('.html', '')
        if base_name in self.file_counter:
            self.file_counter[base_name] += 1
            filename = f"{base_name}_{self.file_counter[base_name]}.html"
        else:
            self.file_counter[base_name] = 1
            
        # Hiyerarşik yol ile birleştir
        if hierarchical_path:
            final_path = f"{hierarchical_path}/{filename}"
        else:
            final_path = filename
            
        # Path mapping'i güncelle
        self.path_mapping[original_path] = final_path
        
        return final_path
    
    def save_index(self, filepath: str):
        """İndeksi JSON dosyasına kaydet"""
        index_data = {
            'created_at': datetime.now().isoformat(),
            'file_count': len(self.path_mapping),
            'path_mapping': self.path_mapping,
            'file_counter': self.file_counter
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)


class AsyncWebScraper:
    """Asenkron web scraper - recursive HTML indirici"""
    
    def __init__(self, base_url: str, output_dir: str = "db", max_concurrent: int = 50):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.max_concurrent = max_concurrent
        self.visited_urls: Set[str] = set()
        self.pending_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.indexer = HierarchicalIndexer()
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.stats = {
            'downloaded': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Çıktı dizinini oluştur
        self.output_dir.mkdir(exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager girişi"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager çıkışı"""
        if self.session:
            await self.session.close()
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """Tek bir HTML sayfasını indir"""
        async with self.semaphore:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"İndirildi: {url}")
                        return content
                    else:
                        logger.warning(f"HTTP {response.status}: {url}")
                        self.failed_urls.add(url)
                        return None
            except Exception as e:
                logger.error(f"Hata ({url}): {str(e)}")
                self.failed_urls.add(url)
                return None
    
    def extract_links(self, html_content: str, current_url: str) -> List[str]:
        """HTML içeriğinden linkleri çıkar"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            # Tüm href linklerini bul
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href:
                    # Mutlak URL'ye dönüştür
                    absolute_url = urljoin(current_url, href)
                    
                    # Aynı domain'de mi kontrol et
                    if urlparse(absolute_url).netloc == urlparse(self.base_url).netloc:
                        # Fragment'ları kaldır
                        absolute_url = absolute_url.split('#')[0]
                        links.append(absolute_url)
            
            return list(set(links))  # Duplikatları kaldır
            
        except Exception as e:
            logger.error(f"Link çıkarma hatası ({current_url}): {str(e)}")
            return []
    
    async def save_html_file(self, url: str, content: str) -> str:
        """HTML içeriğini dosyaya kaydet"""
        try:
            # Hiyerarşik dosya adı oluştur
            relative_path = self.indexer.generate_unique_filename(url, content)
            file_path = self.output_dir / relative_path
            
            # Dizin yapısını oluştur
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Dosyayı kaydet
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            self.stats['downloaded'] += 1
            logger.info(f"Kaydedildi: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Dosya kaydetme hatası ({url}): {str(e)}")
            self.failed_urls.add(url)
            self.stats['failed'] += 1
            return ""
    
    async def process_url(self, url: str) -> List[str]:
        """Tek bir URL'yi işle ve yeni linkleri döndür"""
        if url in self.visited_urls:
            self.stats['skipped'] += 1
            return []
        
        self.visited_urls.add(url)
        
        # HTML içeriğini indir
        content = await self.fetch_html(url)
        if not content:
            return []
        
        # Dosyayı kaydet
        await self.save_html_file(url, content)
        
        # Linkleri çıkar
        new_links = self.extract_links(content, url)
        
        # Yeni linkleri filtrele
        filtered_links = []
        for link in new_links:
            if (link not in self.visited_urls and 
                link not in self.pending_urls and 
                link not in self.failed_urls):
                filtered_links.append(link)
                self.pending_urls.add(link)
        
        return filtered_links
    
    async def scrape_recursive(self, start_url: str, max_depth: int = None):
        """Recursive olarak tüm HTML dosyalarını indir"""
        self.stats['start_time'] = datetime.now()
        logger.info(f"Scraping başlatılıyor: {start_url}")
        
        # Başlangıç URL'ini kuyruğa ekle
        self.pending_urls.add(start_url)
        
        # Progress bar
        pbar = tqdm(desc="İndiriliyor", unit="dosya")
        
        while self.pending_urls:
            # Batch işleme için URL'leri al
            current_batch = list(self.pending_urls)[:self.max_concurrent * 2]
            self.pending_urls -= set(current_batch)
            
            if not current_batch:
                break
            
            # Paralel işleme
            tasks = []
            for url in current_batch:
                task = self.process_url(url)
                tasks.append(task)
            
            # Tüm görevleri çalıştır
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Sonuçları işle
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Görev hatası: {str(result)}")
                elif isinstance(result, list):
                    # Yeni linkler bulundu, onları da ekle
                    for new_url in result:
                        if new_url not in self.visited_urls and new_url not in self.pending_urls:
                            self.pending_urls.add(new_url)
            
            # Progress bar güncelle
            pbar.update(len(current_batch))
            pbar.set_postfix({
                'İndirilen': self.stats['downloaded'],
                'Başarısız': self.stats['failed'],
                'Kuyruk': len(self.pending_urls)
            })
        
        pbar.close()
        self.stats['end_time'] = datetime.now()
        
        # İstatistikleri yazdır
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        logger.info(f"Scraping tamamlandı!")
        logger.info(f"Toplam süre: {duration:.2f} saniye")
        logger.info(f"İndirilen dosya: {self.stats['downloaded']}")
        logger.info(f"Başarısız: {self.stats['failed']}")
        logger.info(f"Atlandı: {self.stats['skipped']}")
        logger.info(f"Toplam ziyaret edilen URL: {len(self.visited_urls)}")
        
        # İndeksi kaydet
        index_path = self.output_dir / "file_index.json"
        self.indexer.save_index(str(index_path))
        logger.info(f"İndeks kaydedildi: {index_path}")


async def main():
    """Ana fonksiyon"""
    base_url = "http://127.0.0.1:8000/9B2F1556-3672-40F0-987D-D82A926AEFA4/index.html"
    output_dir = "db"
    
    async with AsyncWebScraper(base_url, output_dir, max_concurrent=30) as scraper:
        await scraper.scrape_recursive(base_url)


if __name__ == "__main__":
    asyncio.run(main())
