import asyncio
import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import aiofiles
import aiohttp
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, urlsplit, urlunsplit, parse_qsl, urlencode
import argparse


START_URL = "http://127.0.0.1:8000/00B57CEA-D815-4B8E-BA11-FB9466D2E6C9/index.html?fihrist.html"
ALLOWED_ORIGIN = ("127.0.0.1", 8000)  # (host, port)
OUTPUT_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")

# Concurrency controls
MAX_CONCURRENCY = int(os.environ.get("SCRAPER_MAX_CONCURRENCY", "100"))
REQUEST_TIMEOUT_SECS = float(os.environ.get("SCRAPER_TIMEOUT_SECS", "20"))
RETRY_LIMIT = int(os.environ.get("SCRAPER_RETRY_LIMIT", "3"))


def canonicalize_url(url: str) -> str:
    """Normalize URL for deduplication: remove fragments, normalize path, keep query as-is."""
    parts = urlsplit(url)
    # drop fragment
    fragmentless = (parts.scheme, parts.netloc, re.sub(r"/+", "/", parts.path), parts.query, "")
    return urlunsplit(fragmentless)


def is_allowed_origin(url: str) -> bool:
    parts = urlsplit(url)
    if parts.hostname != ALLOWED_ORIGIN[0]:
        return False
    # If no explicit port, default ports based on scheme
    port = parts.port
    if port is None:
        if parts.scheme == "http":
            port = 80
        elif parts.scheme == "https":
            port = 443
    return port == ALLOWED_ORIGIN[1]


def is_html_content_type(content_type: Optional[str]) -> bool:
    if not content_type:
        return False
    return content_type.split(";")[0].strip().lower() in {"text/html", "application/xhtml+xml"}


def build_local_path_from_url(url: str) -> Tuple[str, str]:
    """
    Create a local path (relative to OUTPUT_ROOT) where the HTML should be saved.
    Returns (relative_path, filename) where relative_path includes directories.

    - Path: mirrors URL path
    - Filename: original filename or 'index.html'
    - Query: if exists, append __<normalized_query>__<short_hash>.html to avoid collisions
    """
    parts = urlsplit(url)
    path = parts.path
    if path.endswith("/") or path == "":
        path = path + "index.html"

    # split dir/name
    dir_path, base_name = os.path.split(path.lstrip("/"))
    name, ext = os.path.splitext(base_name)
    if ext.lower() not in {".html", ".htm", ""}:
        # force .html extension for consistency
        ext = ".html"

    if parts.query:
        # normalize query order for stability
        query_params = parse_qsl(parts.query, keep_blank_values=True)
        query_params.sort()
        norm_query = urlencode(query_params)
        short_hash = hashlib.sha1(norm_query.encode("utf-8")).hexdigest()[:8]
        base_name = f"{name}__{norm_query}__{short_hash}{ext}"
    else:
        base_name = f"{name}{ext or '.html'}"

    rel_path = os.path.join(dir_path, base_name) if dir_path else base_name
    return rel_path, base_name


def extract_links(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    links: List[str] = []
    for tag in soup.find_all(["a", "link"]):
        href = tag.get("href")
        if not href:
            continue
        # ignore fragments-only and mailto/javascript
        if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
            continue
        abs_url = urljoin(base_url, href)
        links.append(abs_url)
    return links


@dataclass
class PageNode:
    url: str
    title: Optional[str]
    local_path: str
    parent: Optional[str]
    children: List[str]


class HtmlScraper:
    def __init__(self, start_urls: List[str]):
        self.start_urls = [canonicalize_url(u) for u in start_urls if u]
        self.visited: Set[str] = set()
        self.to_visit: asyncio.Queue[str] = asyncio.Queue()
        self.sem = asyncio.Semaphore(MAX_CONCURRENCY)
        self.nodes: Dict[str, PageNode] = {}

    async def run(self) -> None:
        os.makedirs(OUTPUT_ROOT, exist_ok=True)
        if not self.start_urls:
            return
        for u in self.start_urls:
            await self.to_visit.put(u)
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=REQUEST_TIMEOUT_SECS)) as session:
            workers = [asyncio.create_task(self.worker(session)) for _ in range(MAX_CONCURRENCY)]
            await self.to_visit.join()
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
        await self.write_index()

    async def worker(self, session: aiohttp.ClientSession) -> None:
        while True:
            url = await self.to_visit.get()
            try:
                await self.process_url(session, url)
            finally:
                self.to_visit.task_done()

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[Tuple[str, str]]:
        # returns (html, final_url)
        for attempt in range(1, RETRY_LIMIT + 1):
            try:
                async with self.sem:
                    async with session.get(url, allow_redirects=True) as resp:
                        final_url = str(resp.url)
                        ctype = resp.headers.get("Content-Type", "")
                        if resp.status != 200:
                            return None
                        if not is_html_content_type(ctype):
                            return None
                        text = await resp.text(errors="ignore")
                        return text, final_url
            except Exception:
                if attempt == RETRY_LIMIT:
                    return None
                await asyncio.sleep(0.5 * attempt)
        return None

    async def process_url(self, session: aiohttp.ClientSession, url: str, parent: Optional[str] = None) -> None:
        url = canonicalize_url(url)
        if url in self.visited:
            return
        if not is_allowed_origin(url):
            return
        self.visited.add(url)

        fetched = await self.fetch(session, url)
        if not fetched:
            return
        html, final_url = fetched
        final_url = canonicalize_url(final_url)

        # save html
        rel_path, _ = build_local_path_from_url(final_url)
        full_path = os.path.join(OUTPUT_ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        async with aiofiles.open(full_path, "w", encoding="utf-8", errors="ignore") as f:
            await f.write(html)

        # build node
        title = self._extract_title(html)
        self.nodes[final_url] = PageNode(
            url=final_url,
            title=title,
            local_path=rel_path.replace("\\", "/"),
            parent=parent,
            children=[],
        )
        if parent and parent in self.nodes:
            self.nodes[parent].children.append(final_url)

        # enqueue children
        for link in extract_links(html, final_url):
            link = canonicalize_url(link)
            if not is_allowed_origin(link):
                continue
            if link in self.visited:
                continue
            await self.to_visit.put(link)

    async def write_index(self) -> None:
        index_path = os.path.join(OUTPUT_ROOT, "index.json")
        data = {
            "start_urls": self.start_urls,
            "nodes": {
                url: {
                    "title": node.title,
                    "local_path": node.local_path,
                    "parent": node.parent,
                    "children": node.children,
                }
                for url, node in self.nodes.items()
            },
        }
        async with aiofiles.open(index_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))

    @staticmethod
    def _extract_title(html: str) -> Optional[str]:
        try:
            soup = BeautifulSoup(html, "lxml")
            if soup.title and soup.title.text:
                return soup.title.text.strip()
        except Exception:
            return None
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Asenkron HTML scraper (yalnızca HTML, sınırsız derinlik)")
    parser.add_argument("--start-url", action="append", dest="start_urls", help="Başlangıç URL'si (tekrarlanabilir)")
    parser.add_argument("--seeds-file", dest="seeds_file", help="Satır başına bir URL içeren seed dosyası")
    parser.add_argument("--max-concurrency", type=int, default=None, help="Eşzamanlı istek limiti")
    parser.add_argument("--timeout", type=float, default=None, help="İstek zaman aşımı (sn)")
    parser.add_argument("--retry", type=int, default=None, help="Yeniden deneme sayısı")
    return parser.parse_args()


def main():
    global MAX_CONCURRENCY, REQUEST_TIMEOUT_SECS, RETRY_LIMIT
    args = parse_args()

    seeds: List[str] = []
    if args.start_urls:
        seeds.extend(args.start_urls)
    env_url = os.environ.get("SCRAPER_START_URL")
    if env_url:
        seeds.append(env_url)
    if not seeds:
        seeds.append(START_URL)
    if args.seeds_file and os.path.exists(args.seeds_file):
        with open(args.seeds_file, "r", encoding="utf-8", errors="ignore") as sf:
            for line in sf:
                u = line.strip()
                if u:
                    seeds.append(u)

    if args.max_concurrency:
        MAX_CONCURRENCY = args.max_concurrency
    if args.timeout:
        REQUEST_TIMEOUT_SECS = args.timeout
    if args.retry:
        RETRY_LIMIT = args.retry

    scraper = HtmlScraper(seeds)
    asyncio.run(scraper.run())


if __name__ == "__main__":
    main()


