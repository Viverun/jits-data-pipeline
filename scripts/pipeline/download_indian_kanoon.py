import requests
from bs4 import BeautifulSoup
import json
import time
import os
import random
from pathlib import Path

class ScaledDownloader:
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

    def search_and_download(self, query, category, max_results=25):
        if query in self.progress['completed_queries']:
            print(f"✓ Skipping completed query: {query}")
            return 0

        print(f"\n🔍 Query [{category}]: {query} (Target: {max_results})")
        base_url = "https://indiankanoon.org/search/"
        doc_links = []
        pages = (max_results // 10) + 1
        
        for page in range(pages):
            if len(doc_links) >= max_results: break
            params = {'formInput': query, 'pagenum': page}
            try:
                resp = requests.get(base_url, params=params, headers=self.headers, timeout=15)
                if resp.status_code == 429:
                    print("⚠️ Rate limit hit. Sleeping 5 mins...")
                    time.sleep(300)
                    continue
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('/doc/') and any(c.isdigit() for char in href for c in char):
                        if href not in doc_links: doc_links.append(href)
                time.sleep(random.uniform(3, 6))
            except Exception as e:
                print(f"  [ERROR] Page {page} failed: {e}")
                break

        downloaded = 0
        for link in doc_links[:max_results]:
            case_url = f"https://indiankanoon.org{link}"
            doc_id = link.strip('/').split('/')[-1]
            filename = f"{category}_{doc_id}.txt"
            file_path = self.output_dir / filename

            if file_path.exists():
                downloaded += 1
                continue

            print(f"    -> Downloading: {case_url}")
            try:
                resp = requests.get(case_url, headers=self.headers, timeout=15)
                if resp.status_code == 429:
                    print("⚠️ Rate limit hit. Sleeping 5 mins...")
                    time.sleep(300)
                    continue
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')
                div = soup.find('div', class_='judgments') or soup.find('div', class_='doc_content')
                if div and len(div.get_text()) > 500:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(div.get_text(separator='\n'))
                    downloaded += 1
                    self.progress['total_downloaded'] += 1
                    time.sleep(random.uniform(10, 20))
            except Exception as e:
                print(f"    [WARNING] Failed {case_url}: {e}")

        self.progress['completed_queries'].append(query)
        self.save_checkpoint()
        return downloaded

def main():
    downloader = ScaledDownloader()
    
    query_plan = {
        'CRIMINAL': [
            "IPC 304B dowry death bail application 2023",
            "IPC 498A cruelty bail 2023",
            "IPC 376 rape bail hearing 2024",
            "NDPS Act bail rejection 2023",
            "IPC 302 murder sentence appeal 2023",
            "IPC 306 abetment suicide dying declaration"
        ],
        'SERVICE': [
            "promotion seniority service rules DPC 2023",
            "promotion denial Article 16 service matter",
            "seniority list challenged service law",
            "pension gratuity calculation service",
            "pay scale revision arrears service"
        ],
        'CIVIL': [
            "specific performance sale agreement 2023",
            "partition suit property division",
            "arbitration award challenge Section 34",
            "arbitration jurisdiction Section 11"
        ],
        'LANDMARK': [
            "Kesavananda Bharati", "Maneka Gandhi", "Vishaka", "Bachan Singh",
            "Sharad Birdhichand Sarda", "Anvar P.V. v. P.K. Basheer"
        ]
    }

    print("🚀 Starting JITS Scaled Download...")
    for cat, queries in query_plan.items():
        for q in queries:
            downloader.search_and_download(q, cat, max_results=25 if cat != 'LANDMARK' else 1)

    print(f"\n🏁 Download Session Complete. Total in repo: {downloader.progress['total_downloaded']}")

if __name__ == '__main__':
    main()
