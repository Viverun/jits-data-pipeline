import requests
from bs4 import BeautifulSoup
import json
import time
import os
import random
from pathlib import Path

def search_and_download(query, max_results=10):
    base_url = "https://indiankanoon.org/search/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    
    doc_links = []
    pages = (max_results // 10) + 1
    
    for page in range(pages):
        if len(doc_links) >= max_results:
            break
            
        current_params = {'formInput': query, 'pagenum': page}
        try:
            response = requests.get(base_url, params=current_params, headers=headers, timeout=15)
            
            if response.status_code == 429:
                print("⚠️ Hit Rate Limit (429). Cooling down for 5 minutes...")
                time.sleep(300)
                continue
                
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            all_links = soup.find_all('a', href=True)
            
            page_links = []
            for a in all_links:
                href = a['href']
                if href.startswith('/doc/') and any(char.isdigit() for char in href):
                    if href not in doc_links and href not in page_links:
                        page_links.append(href)
            
            doc_links.extend(page_links)
            print(f"    [DEBUG] Page {page}: Found {len(page_links)} links. Total: {len(doc_links)}")
            time.sleep(random.uniform(3, 7)) # Random delay between search pages
            
        except Exception as e:
            print(f"  [ERROR] Search failed: {e}")
            break

    cases = []
    seen_urls = set()
    doc_links = doc_links[:max_results]

    for link in doc_links:
        case_url = f"https://indiankanoon.org{link}"
        if case_url in seen_urls:
            continue
        seen_urls.add(case_url)
        
        print(f"    -> Downloading: {case_url}")
        case_data = download_full_judgment(case_url, headers)
        if case_data:
            cases.append(case_data)
            # v0.3: Much longer, randomized delay to avoid 429s
            time.sleep(random.uniform(8, 15)) 
    
    return cases

def download_full_judgment(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 429:
            print("⚠️ Hit Rate Limit (429) during download. Cooling down for 5 minutes...")
            time.sleep(300)
            return None
            
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        judgment_div = soup.find('div', class_='judgments') or soup.find('div', class_='doc_content')
        text = judgment_div.get_text(separator='\n') if judgment_div else ''
        
        if len(text.strip()) < 500:
            return None
            
        title = soup.find('h1').text if soup.find('h1') else 'Unknown'
        return {'url': url, 'title': title.strip(), 'text': text.strip()}
    except Exception as e:
        print(f"    [WARNING] Failed to download {url}: {e}")
        return None

def download_cases_stratified(output_dir='raw/judgments/unclassified'):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    queries = [
        ('Supreme Court IPC 302', 50, 'SC'),
        ('Supreme Court IPC 420', 50, 'SC'),
        ('High Court IPC 498A', 100, 'HC'),
        ('High Court IPC 376', 100, 'HC'),
        ('District Court IPC 379', 100, 'DC'),
        ('District Court IPC 323', 100, 'DC'),
    ]
    
    print("🚀 Starting Conservative Large-Scale Download (Target: ~500 cases)...")
    print("⚠️ This will be slow to avoid being blocked. Estimated time: 4-6 hours.")
    
    case_count = 0
    for query, count, court_level in queries:
        print(f"\n🔍 Query: {query} (Target: {count})")
        cases = search_and_download(query, max_results=count)
        
        for case in cases:
            filename = f"{court_level}_{case_count:04d}.txt"
            file_path = os.path.join(output_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(case['text'])
                case_count += 1
            
        print(f"✅ Finished query. Total cases: {case_count}")
        time.sleep(random.uniform(10, 20)) # Delay between queries
    
    print(f"\n🏁 DOWNLOAD COMPLETE. Total new cases: {case_count}")

if __name__ == '__main__':
    download_cases_stratified()
