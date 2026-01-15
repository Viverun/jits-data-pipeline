import requests
from bs4 import BeautifulSoup
import json
import time
import os
from pathlib import Path

def search_and_download(query, max_results=10):
    base_url = "https://indiankanoon.org/search/"
    params = {'formInput': query}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"  [ERROR] Search failed for query '{query}': {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = soup.find_all('a', href=True)
    
    doc_links = []
    for a in all_links:
        href = a['href']
        # Capture anything that looks like a document link (/doc/NUMBER)
        if href.startswith('/doc/') and any(char.isdigit() for char in href):
            if href not in doc_links:
                doc_links.append(href)

    print(f"    [DEBUG] Found {len(doc_links)} potential document links.")

    cases = []
    seen_urls = set()
    
    for link in doc_links:
        if len(cases) >= max_results:
            break
            
        case_url = f"https://indiankanoon.org{link}"
        if case_url in seen_urls:
            continue
        seen_urls.add(case_url)
        
        print(f"    -> Downloading: {case_url}")
        case_data = download_full_judgment(case_url, headers)
        if case_data:
            cases.append(case_data)
            time.sleep(2) 
    
    return cases

def download_full_judgment(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        judgment_div = soup.find('div', class_='judgments') or soup.find('div', class_='doc_content')
        text = judgment_div.get_text(separator='\n') if judgment_div else ''
        
        if len(text.strip()) < 500: # Ensure we get substantial text
            return None
            
        title = soup.find('h1').text if soup.find('h1') else 'Unknown'
        
        return {
            'url': url,
            'title': title.strip(),
            'text': text.strip()
        }
    except Exception as e:
        print(f"    [WARNING] Failed to download {url}: {e}")
        return None

def download_cases_stratified(output_dir='raw/judgments/unclassified'):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Simplified queries for better reliability
    queries = [
        ('Supreme Court IPC 302', 5, 'SC'),
        ('Supreme Court IPC 420', 5, 'SC'),
        ('High Court bail application', 10, 'HC'),
        ('High Court IPC 498A', 10, 'HC'),
        ('District Court IPC 379', 15, 'DC'),
        ('District Court IPC 323', 15, 'DC')
    ]
    
    print("🚀 Starting stratified download...")
    
    case_count = 0
    for query, count, court_level in queries:
        print(f"\n🔍 Query: {query} (Target: {count})")
        cases = search_and_download(query, max_results=count)
        
        for case in cases:
            filename = f"{court_level}_{case_count:04d}.txt"
            file_path = os.path.join(output_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(case['text'])
            case_count += 1
            
        time.sleep(3)
    
    print(f"\n✅ Downloaded {case_count} cases to {output_dir}")

if __name__ == '__main__':
    download_cases_stratified()
