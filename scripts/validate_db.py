import json
import os
from urllib.parse import urlsplit

DB_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")


def main():
    index_path = os.path.join(DB_ROOT, "index.json")
    if not os.path.exists(index_path):
        print("index.json bulunamadı")
        return
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", {})
    missing = []
    for url, meta in nodes.items():
        rel = meta.get("local_path")
        if not rel:
            missing.append(url)
            continue
        full = os.path.join(DB_ROOT, rel)
        if not os.path.exists(full):
            missing.append(url)

    print(f"Toplam kayıtlı sayfa: {len(nodes)}")
    print(f"Eksik dosya sayısı: {len(missing)}")

    if missing:
        seeds_path = os.path.join(DB_ROOT, "missing_seeds.txt")
        with open(seeds_path, "w", encoding="utf-8") as sf:
            for u in missing:
                sf.write(u + "\n")
        print(f"Eksik URL'ler {seeds_path} dosyasına yazıldı")


if __name__ == "__main__":
    main()


