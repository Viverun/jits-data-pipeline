import requests
from bs4 import BeautifulSoup

def debug_search(query):
    base_url = "https://indiankanoon.org/search/"
    params = {'formInput': query}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    
    print(f"DEBUG: Searching for '{query}'...")
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        print(f"DEBUG: Status Code: {response.status_code}")
        print(f"DEBUG: Response URL: {response.url}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Print some info about the page
        print(f"DEBUG: Title: {soup.title.string if soup.title else 'No Title'}")
        
        # Check for common bot protection strings
        if "captcha" in response.text.lower():
            print("DEBUG: Detected 'captcha' in response!")
        if "robot" in response.text.lower():
            print("DEBUG: Detected 'robot' in response!")
            
        # Look for any links
        links = soup.find_all('a', href=True)
        print(f"DEBUG: Found {len(links)} total links.")
        
        doc_links = [a['href'] for a in links if '/doc/' in a['href']]
        print(f"DEBUG: Found {len(doc_links)} links containing '/doc/'.")
        
        if doc_links:
            print(f"DEBUG: First 3 doc links: {doc_links[:3]}")
        else:
            print("DEBUG: No doc links found. Printing first 1000 chars of body:")
            print(response.text[:1000])

    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")

if __name__ == "__main__":
    debug_search("IPC 302")
