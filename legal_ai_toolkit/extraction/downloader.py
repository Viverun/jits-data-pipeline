"""
Indian Kanoon downloader with improved text extraction.

CHANGES FROM ORIGINAL:
1. Replaced div.get_text(separator='\n') with custom text cleaning
2. Added whitespace normalization at source
3. Strips HTML artifacts during extraction
4. Preserves paragraph structure without excessive newlines
"""

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import json
import time
import random
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)



class IndianKanoonDownloader:
    def __init__(self, output_dir='raw/judgments/unclassified', checkpoint_file='download_checkpoint.json'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = Path(checkpoint_file)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
        self.load_checkpoint()

    def load_checkpoint(self):
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {'completed_queries': [], 'total_downloaded': 0}

    def save_checkpoint(self):
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    @staticmethod
    def extract_clean_text(element) -> str:
        """
        Extract text from BeautifulSoup element with proper cleaning.

        IMPROVEMENTS:
        - Removes citation count elements BEFORE text extraction
        - Uses separator=' ' instead of '\n' to prevent newline artifacts
        - Normalizes whitespace (multiple spaces -> single space)
        - Removes citation count artifacts [Cites X, Cited by Y]
        - Preserves paragraph boundaries with double newlines
        - Strips leading/trailing whitespace

        Args:
            element: BeautifulSoup element (div, p, etc.)

        Returns:
            Clean text string with normalized whitespace
        """
        if not element:
            return ""

        # CRITICAL FIX: Remove citation elements BEFORE extracting text
        # Indian Kanoon puts [Cites X, Cited by Y] in <a> tags with class 'cite_tag'
        for cite_tag in element.find_all('a', class_='cite_tag'):
            cite_tag.decompose()  # Remove the element entirely

        # Also remove any elements that contain the citation pattern
        # SAFE FIX: Removing destructive parent.decompose() which was causing data loss
        # The regex cleaning below handles this text removal safely
        pass


        # Extract text with space separator (prevents \n artifacts)
        text = element.get_text(separator=' ', strip=True)

        # Remove any remaining citation count artifacts in text
        text = re.sub(r'\[\s*Cites\s*\d+\s*,\s*Cited\s*by\s*\d+\s*\]', '', text, flags=re.IGNORECASE)

        # Remove standalone numbers that look like citation counts
        text = re.sub(r'\s+\d+\s+(?=,|\]|Cited)', ' ', text)

        # Normalize multiple spaces to single space
        text = re.sub(r'\s+', ' ', text)

        # Normalize paragraph breaks (optional: preserves structure)
        paragraphs = []
        for p in element.find_all(['p', 'div'], recursive=False):
            para_text = p.get_text(separator=' ', strip=True)
            if para_text and len(para_text) > 10:  # Skip very short fragments
                paragraphs.append(para_text)
        if paragraphs:
            text = '\n\n'.join(paragraphs)

        # FINAL PASS: Remove any lingering citation artifacts
        text = re.sub(r'\[\s*Cites\s*\d+\s*,\s*Cited\s*by\s*\d+\s*\]', '', text, flags=re.IGNORECASE)

        return text.strip()

    def search_and_download(self, query, category, max_results=25):
        if query in self.progress['completed_queries']:
            logger.info(f"Skipping completed query: {query}")
            return 0

        logger.info(f"Query [{category}]: {query} (Target: {max_results})")
        base_url = "https://indiankanoon.org/search/"
        doc_links = []
        pages = (max_results // 10) + 1

        # === SEARCH PHASE (unchanged) ===
        for page in range(pages):
            if len(doc_links) >= max_results:
                break

            params = {'formInput': query, 'pagenum': page}
            try:
                resp = requests.get(base_url, params=params, headers=self.headers, timeout=15)
                if resp.status_code == 429:
                    logger.warning("Rate limit hit. Sleeping 5 mins...")
                    time.sleep(300)
                    continue

                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')

                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('/doc/') and any(c.isdigit() for c in href):
                        if href not in doc_links:
                            doc_links.append(href)

                time.sleep(random.uniform(3, 6))

            except Exception as e:
                logger.error(f"Page {page} failed: {e}")
                break

        # === DOWNLOAD PHASE (IMPROVED) ===
        downloaded = 0
        for link in doc_links[:max_results]:
            case_url = f"https://indiankanoon.org{link}"
            doc_id = link.strip('/').split('/')[-1]
            filename = f"{category}_{doc_id}.txt"
            file_path = self.output_dir / filename

            if file_path.exists():
                downloaded += 1
                continue

            logger.info(f"Downloading: {case_url}")
            try:
                resp = requests.get(case_url, headers=self.headers, timeout=15)
                if resp.status_code == 429:
                    logger.warning("Rate limit hit. Sleeping 5 mins...")
                    time.sleep(300)
                    continue

                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Find judgment content div
                div = soup.find('div', class_='judgments') or soup.find('div', class_='doc_content')

                if div:
                    # === KEY CHANGE: Use new extraction method ===
                    clean_text = self.extract_clean_text(div)

                    # Validate minimum content length
                    if len(clean_text) > 500:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(clean_text)
                        downloaded += 1
                        self.progress['total_downloaded'] += 1
                        logger.info(f"Saved {len(clean_text)} characters")
                    else:
                        logger.warning(f"Content too short ({len(clean_text)} chars)")

                time.sleep(random.uniform(10, 20))

            except Exception as e:
                logger.warning(f"Failed {case_url}: {e}")

        self.progress['completed_queries'].append(query)
        self.save_checkpoint()
        return downloaded


# === BACKWARD COMPATIBILITY ===
# If you have scripts that import the old class name
IndianKanoonScraper = IndianKanoonDownloader