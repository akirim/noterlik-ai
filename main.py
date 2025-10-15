"""
Noterlik AI - Ana Çalıştırma Scripti
Bu script tüm işlemleri koordine eder ve kullanıcı arayüzünü sunar.
"""

import asyncio
import sys
import os
import json
import webbrowser
import threading
import time
from pathlib import Path
from datetime import datetime

# Proje kök dizinini Python path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from web_scraper import AsyncWebScraper
from html_to_json import HTMLToJSONConverter


class NoterlikApp:
    """Ana uygulama sınıfı"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/9B2F1556-3672-40F0-987D-D82A926AEFA4/index.html"
        self.output_dir = "db"
        self.json_output_dir = "json_output"
        self.max_concurrent = 30
        
    def print_banner(self):
        """Uygulama banner'ını yazdır"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    NOTERLIK AI v1.0                         ║
║              Gelişmiş Web Scraper & JSON Converter          ║
║                                                              ║
║  • Recursive HTML İndirici                                   ║
║  • Asenkron ve Multi-threaded İşlem                         ║
║  • Hiyerarşik Dosya İndeksleme                              ║
║  • HTML to JSON Dönüştürücü                                  ║
║  • Modern Web Arayüzü                                        ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def print_menu(self):
        """Ana menüyü yazdır"""
        menu = """
┌─────────────────────────────────────────────────────────────┐
│                        ANA MENÜ                             │
├─────────────────────────────────────────────────────────────┤
│  1. Web Scraping Başlat (HTML İndir)                       │
│  2. HTML Dosyalarını JSON'a Dönüştür                       │
│  3. Tüm İşlemleri Sırayla Çalıştır                         │
│  4. Web Arayüzünü Aç                                       │
│  5. Ayarları Düzenle                                       │
│  6. İstatistikleri Görüntüle                               │
│  7. Çıkış                                                   │
└─────────────────────────────────────────────────────────────┘
        """
        print(menu)
    
    async def run_scraping(self):
        """Web scraping işlemini çalıştır"""
        print("\n🔄 Web Scraping başlatılıyor...")
        print(f"📍 Hedef URL: {self.base_url}")
        print(f"📁 Çıktı Klasörü: {self.output_dir}")
        print(f"⚡ Eşzamanlı İstek: {self.max_concurrent}")
        print("-" * 60)
        
        try:
            async with AsyncWebScraper(
                base_url=self.base_url,
                output_dir=self.output_dir,
                max_concurrent=self.max_concurrent
            ) as scraper:
                await scraper.scrape_recursive(self.base_url)
                
            print("\n✅ Web Scraping başarıyla tamamlandı!")
            return True
            
        except Exception as e:
            print(f"\n❌ Web Scraping hatası: {str(e)}")
            return False
    
    async def run_json_conversion(self):
        """HTML to JSON dönüştürme işlemini çalıştır"""
        print("\n🔄 HTML to JSON dönüştürme başlatılıyor...")
        print(f"📁 Kaynak Klasörü: {self.output_dir}")
        print(f"📁 Hedef Klasörü: {self.json_output_dir}")
        print("-" * 60)
        
        try:
            converter = HTMLToJSONConverter(
                input_dir=self.output_dir,
                output_dir=self.json_output_dir
            )
            
            await converter.convert_all_html_files()
            await converter.create_master_index()
            
            print("\n✅ JSON dönüştürme başarıyla tamamlandı!")
            return True
            
        except Exception as e:
            print(f"\n❌ JSON dönüştürme hatası: {str(e)}")
            return False
    
    async def run_full_process(self):
        """Tüm işlemleri sırayla çalıştır"""
        print("\n🚀 Tüm işlemler sırayla başlatılıyor...")
        
        # 1. Web Scraping
        scraping_success = await self.run_scraping()
        
        if not scraping_success:
            print("\n❌ Web Scraping başarısız oldu. JSON dönüştürme atlanıyor.")
            return False
        
        # 2. JSON Dönüştürme
        json_success = await self.run_json_conversion()
        
        if json_success:
            print("\n🎉 Tüm işlemler başarıyla tamamlandı!")
            self.print_summary()
            return True
        else:
            print("\n⚠️ JSON dönüştürme başarısız oldu.")
            return False
    
    def open_web_interface(self):
        """Web arayüzünü aç"""
        index_path = project_root / "index.html"
        
        if index_path.exists():
            print(f"\n🌐 Web arayüzü açılıyor: {index_path}")
            webbrowser.open(f"file://{index_path.absolute()}")
            print("✅ Web arayüzü açıldı!")
        else:
            print("❌ index.html dosyası bulunamadı!")
    
    def edit_settings(self):
        """Ayarları düzenle"""
        print("\n⚙️ AYAR DÜZENLEME")
        print("-" * 30)
        
        print(f"Mevcut Base URL: {self.base_url}")
        new_url = input("Yeni Base URL (boş bırakırsanız mevcut kalır): ").strip()
        if new_url:
            self.base_url = new_url
        
        print(f"Mevcut Çıktı Klasörü: {self.output_dir}")
        new_output = input("Yeni Çıktı Klasörü (boş bırakırsanız mevcut kalır): ").strip()
        if new_output:
            self.output_dir = new_output
        
        print(f"Mevcut JSON Çıktı Klasörü: {self.json_output_dir}")
        new_json_output = input("Yeni JSON Çıktı Klasörü (boş bırakırsanız mevcut kalır): ").strip()
        if new_json_output:
            self.json_output_dir = new_json_output
        
        print(f"Mevcut Eşzamanlı İstek: {self.max_concurrent}")
        try:
            new_concurrent = int(input("Yeni Eşzamanlı İstek (boş bırakırsanız mevcut kalır): ").strip())
            if new_concurrent > 0:
                self.max_concurrent = new_concurrent
        except ValueError:
            pass
        
        print("\n✅ Ayarlar güncellendi!")
    
    def show_statistics(self):
        """İstatistikleri göster"""
        print("\n📊 İSTATİSTİKLER")
        print("-" * 30)
        
        # HTML dosyaları
        html_dir = Path(self.output_dir)
        if html_dir.exists():
            html_files = list(html_dir.rglob("*.html"))
            total_html_size = sum(f.stat().st_size for f in html_files if f.is_file())
            print(f"📄 HTML Dosyaları: {len(html_files)} adet")
            print(f"💾 HTML Toplam Boyut: {self.format_size(total_html_size)}")
        else:
            print("📄 HTML Dosyaları: Henüz oluşturulmadı")
        
        # JSON dosyaları
        json_dir = Path(self.json_output_dir)
        if json_dir.exists():
            json_files = list(json_dir.rglob("*.json"))
            total_json_size = sum(f.stat().st_size for f in json_files if f.is_file())
            print(f"📋 JSON Dosyaları: {len(json_files)} adet")
            print(f"💾 JSON Toplam Boyut: {self.format_size(total_json_size)}")
        else:
            print("📋 JSON Dosyaları: Henüz oluşturulmadı")
        
        # İndeks dosyası
        index_file = json_dir / "file_index.json"
        if index_file.exists():
            print(f"📑 İndeks Dosyası: {index_file}")
            print(f"📅 Oluşturulma Tarihi: {datetime.fromtimestamp(index_file.stat().st_mtime)}")
        
        master_index = json_dir / "master_index.json"
        if master_index.exists():
            print(f"📑 Ana İndeks Dosyası: {master_index}")
            print(f"📅 Oluşturulma Tarihi: {datetime.fromtimestamp(master_index.stat().st_mtime)}")
    
    def print_summary(self):
        """İşlem özetini yazdır"""
        print("\n📋 İŞLEM ÖZETİ")
        print("=" * 50)
        
        html_dir = Path(self.output_dir)
        json_dir = Path(self.json_output_dir)
        
        if html_dir.exists():
            html_files = list(html_dir.rglob("*.html"))
            print(f"✅ İndirilen HTML Dosyaları: {len(html_files)}")
        
        if json_dir.exists():
            json_files = list(json_dir.rglob("*.json"))
            print(f"✅ Oluşturulan JSON Dosyaları: {len(json_files)}")
        
        print(f"📁 HTML Çıktı Klasörü: {html_dir.absolute()}")
        print(f"📁 JSON Çıktı Klasörü: {json_dir.absolute()}")
        print(f"🌐 Web Arayüzü: {project_root / 'index.html'}")
    
    def format_size(self, size_bytes):
        """Dosya boyutunu formatla"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    async def run(self):
        """Ana uygulama döngüsü"""
        self.print_banner()
        
        while True:
            self.print_menu()
            
            try:
                choice = input("\nSeçiminizi yapın (1-7): ").strip()
                
                if choice == "1":
                    await self.run_scraping()
                    
                elif choice == "2":
                    await self.run_json_conversion()
                    
                elif choice == "3":
                    await self.run_full_process()
                    
                elif choice == "4":
                    self.open_web_interface()
                    
                elif choice == "5":
                    self.edit_settings()
                    
                elif choice == "6":
                    self.show_statistics()
                    
                elif choice == "7":
                    print("\n👋 Uygulama kapatılıyor...")
                    break
                    
                else:
                    print("\n❌ Geçersiz seçim! Lütfen 1-7 arasında bir sayı girin.")
                
                input("\nDevam etmek için Enter'a basın...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Uygulama kullanıcı tarafından kapatıldı.")
                break
            except Exception as e:
                print(f"\n❌ Beklenmeyen hata: {str(e)}")
                input("\nDevam etmek için Enter'a basın...")


async def main():
    """Ana fonksiyon"""
    app = NoterlikApp()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Uygulama kapatıldı.")
    except Exception as e:
        print(f"\n❌ Kritik hata: {str(e)}")
        sys.exit(1)
