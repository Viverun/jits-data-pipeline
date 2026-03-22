"""
Indian Kanoon downloader with resumable query batches and cross-query dedupe.
"""

import hashlib
import json
import logging
import random
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class IndianKanoonDownloader:
    def __init__(
        self,
        output_dir="raw/judgments/unclassified",
        checkpoint_file="download_checkpoint.json",
        manifest_file="download_manifest.jsonl",
        min_chars=500,
        search_pause=(3, 6),
        download_pause=(8, 14),
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = Path(checkpoint_file)
        self.manifest_file = Path(manifest_file)
        self.min_chars = min_chars
        self.search_pause = search_pause
        self.download_pause = download_pause
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        }
        self.progress = {}
        self.completed_queries = set()
        self.downloaded_doc_ids = set()
        self.content_hashes = set()
        self.load_checkpoint()
        self._index_existing_corpus()

    def load_checkpoint(self):
        default_progress = {
            "completed_queries": [],
            "downloaded_doc_ids": [],
            "total_downloaded": 0,
            "duplicate_doc_ids": 0,
            "duplicate_texts": 0,
            "short_content": 0,
            "failed_downloads": 0,
        }

        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                default_progress.update(loaded)

        self.progress = default_progress
        self.completed_queries = set(self.progress.get("completed_queries", []))
        self.downloaded_doc_ids = set(self.progress.get("downloaded_doc_ids", []))

    def save_checkpoint(self):
        self.progress["completed_queries"] = sorted(self.completed_queries)
        self.progress["downloaded_doc_ids"] = sorted(self.downloaded_doc_ids)
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _normalize_text_for_hash(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _index_existing_corpus(self):
        txt_files = sorted(self.output_dir.rglob("*.txt"))
        indexed_hashes = 0

        for file_path in txt_files:
            stem = file_path.stem
            if stem.startswith("ik_"):
                self.downloaded_doc_ids.add(stem.split("_", 1)[1])

            try:
                text = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            normalized = self._normalize_text_for_hash(text)
            if not normalized:
                continue

            content_hash = hashlib.sha1(normalized.encode("utf-8")).hexdigest()
            if content_hash not in self.content_hashes:
                self.content_hashes.add(content_hash)
                indexed_hashes += 1

        logger.info(
            "Indexed existing corpus: %s files, %s unique content hashes, %s known doc IDs",
            len(txt_files),
            indexed_hashes,
            len(self.downloaded_doc_ids),
        )

    def count_saved_files(self) -> int:
        return len(list(self.output_dir.rglob("*.txt")))

    def _sleep(self, bounds):
        low, high = bounds
        time.sleep(random.uniform(low, high))

    @staticmethod
    def extract_clean_text(element) -> str:
        if not element:
            return ""

        for cite_tag in element.find_all("a", class_="cite_tag"):
            cite_tag.decompose()

        text = element.get_text(separator=" ", strip=True)
        text = re.sub(
            r"\[\s*Cites\s*\d+\s*,\s*Cited\s*by\s*\d+\s*\]",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\s+\d+\s+(?=,|\]|Cited)", " ", text)
        text = re.sub(r"\s+", " ", text)

        paragraphs = []
        for child in element.find_all(["p", "div"], recursive=False):
            para_text = child.get_text(separator=" ", strip=True)
            para_text = re.sub(r"\s+", " ", para_text).strip()
            if para_text and len(para_text) > 10:
                paragraphs.append(para_text)
        if paragraphs:
            text = "\n\n".join(paragraphs)

        text = re.sub(
            r"\[\s*Cites\s*\d+\s*,\s*Cited\s*by\s*\d+\s*\]",
            "",
            text,
            flags=re.IGNORECASE,
        )
        return text.strip()

    @staticmethod
    def _extract_doc_links(soup):
        doc_links = []
        seen = set()
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if href.startswith("/doc/") and any(ch.isdigit() for ch in href):
                if href not in seen:
                    seen.add(href)
                    doc_links.append(href)
        return doc_links

    def _record_manifest(self, record):
        with open(self.manifest_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def search(self, query, max_results=25):
        base_url = "https://indiankanoon.org/search/"
        doc_links = []
        pages = max(1, (max_results // 10) + 1)

        for page in range(pages):
            if len(doc_links) >= max_results:
                break

            params = {"formInput": query, "pagenum": page}
            try:
                resp = requests.get(base_url, params=params, headers=self.headers, timeout=20)
                if resp.status_code == 429:
                    logger.warning("Rate limit hit during search. Sleeping 5 minutes...")
                    time.sleep(300)
                    continue

                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for href in self._extract_doc_links(soup):
                    if href not in doc_links:
                        doc_links.append(href)

                self._sleep(self.search_pause)
            except Exception as e:
                logger.error("Search failed for query=%s page=%s: %s", query, page, e)
                break

        return doc_links[:max_results]

    def _download_single_case(self, query, category, link):
        doc_id = link.strip("/").split("/")[-1]
        case_url = f"https://indiankanoon.org{link}"
        file_path = self.output_dir / f"ik_{doc_id}.txt"

        if doc_id in self.downloaded_doc_ids or file_path.exists():
            self.progress["duplicate_doc_ids"] += 1
            return False

        logger.info("Downloading: %s", case_url)
        try:
            resp = requests.get(case_url, headers=self.headers, timeout=20)
            if resp.status_code == 429:
                logger.warning("Rate limit hit during download. Sleeping 5 minutes...")
                time.sleep(300)
                return False

            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            content = soup.find("div", class_="judgments") or soup.find("div", class_="doc_content")

            if not content:
                self.progress["failed_downloads"] += 1
                return False

            clean_text = self.extract_clean_text(content)
            if len(clean_text) < self.min_chars:
                self.progress["short_content"] += 1
                return False

            normalized = self._normalize_text_for_hash(clean_text)
            content_hash = hashlib.sha1(normalized.encode("utf-8")).hexdigest()
            if content_hash in self.content_hashes:
                self.progress["duplicate_texts"] += 1
                self.downloaded_doc_ids.add(doc_id)
                self.save_checkpoint()
                return False

            file_path.write_text(clean_text, encoding="utf-8")
            self.downloaded_doc_ids.add(doc_id)
            self.content_hashes.add(content_hash)
            self.progress["total_downloaded"] += 1
            self.save_checkpoint()
            self._record_manifest(
                {
                    "doc_id": doc_id,
                    "query": query,
                    "category": category,
                    "source_url": case_url,
                    "filename": file_path.name,
                    "char_count": len(clean_text),
                    "content_hash": content_hash,
                    "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )

            logger.info("Saved %s (%s chars)", file_path.name, len(clean_text))
            self._sleep(self.download_pause)
            return True
        except Exception as e:
            self.progress["failed_downloads"] += 1
            logger.warning("Failed %s: %s", case_url, e)
            return False

    def search_and_download(self, query, category, max_results=25):
        if query in self.completed_queries:
            logger.info("Skipping completed query: %s", query)
            return 0

        logger.info("Query [%s]: %s (target=%s)", category, query, max_results)
        doc_links = self.search(query, max_results=max_results)

        downloaded = 0
        for link in doc_links:
            if self._download_single_case(query, category, link):
                downloaded += 1

        self.completed_queries.add(query)
        self.save_checkpoint()
        return downloaded


IndianKanoonScraper = IndianKanoonDownloader
