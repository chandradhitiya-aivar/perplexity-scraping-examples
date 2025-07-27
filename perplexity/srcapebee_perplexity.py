from scrapingbee import ScrapingBeeClient
import json
from datetime import datetime
import time
import random
from urllib.parse import urlparse
import re

class PerplexitySharedLinkScraper:
    def __init__(self, api_key):
        self.client = ScrapingBeeClient(api_key=api_key)
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        ]
        
    def random_delay(self):
        """Avoid rate limiting"""
        time.sleep(random.uniform(1, 3))
    
    def scrape_shared_link(self, shared_url, retries=3):
        """Extract content from Perplexity shared links"""
        params = {
            'render_js': 'true',
            'stealth_proxy': 'true',
            'premium_proxy': 'true',
            'wait': 8000,  # Longer wait for shared links
            'wait_for': '.prose, .shared-content-container',
            'block_ads': 'true',
            'country_code': random.choice(['us', 'gb', 'ca']),
            'user_agent': random.choice(self.user_agents),
            'custom_google': 'true'  # Bypass Googlebot checks
        }
        
        for attempt in range(retries):
            try:
                response = self.client.get(shared_url, params=params)
                
                if response.status_code == 200:
                    return self.parse_shared_link_content(response.content, shared_url)
                elif response.status_code == 403:
                    print(f"Blocked - rotating parameters (attempt {attempt + 1})")
                    params['country_code'] = random.choice(['de', 'fr', 'jp'])  # Different country
                    params['user_agent'] = random.choice(self.user_agents)
                else:
                    print(f"HTTP Error {response.status_code}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
            
            self.random_delay()
        
        return None
    
    def parse_shared_link_content(self, html, url):
        """Parse shared link specific structure"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        result = {
            'metadata': {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'title': soup.title.string if soup.title else "Perplexity Shared Link"
            },
            'content': {}
        }
        
        # Extract main content (shared links have different structure)
        content_div = soup.find('div', class_=re.compile(r'prose|shared-content|answer-container'))
        if content_div:
            result['content']['main_answer'] = self.clean_html(str(content_div))
        
        # Extract sources (shared links often put these in footers)
        result['content']['sources'] = [
            {'text': a.get_text(strip=True), 'url': a['href']}
            for a in soup.select('footer a[href^="http"]')
        ]
        
        # Extract related content
        result['content']['related'] = [
            li.get_text(strip=True) 
            for li in soup.select('.related-content li, .suggested-questions li')
        ]
        
        return result
    
    def clean_html(self, html):
        """Convert HTML to clean markdown"""
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        return h.handle(html).strip()
    
    def save_to_markdown(self, data, filename=None):
        """Save to markdown with shared link formatting"""
        if not filename:
            domain = urlparse(data['metadata']['url']).netloc.replace('.', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"perplexity_shared_{domain}_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# {data['metadata']['title']}\n\n")
            f.write(f"**Shared Link:** [{data['metadata']['url']}]({data['metadata']['url']})  \n")
            f.write(f"**Captured:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Main Content
            if data['content'].get('main_answer'):
                f.write("## Key Content\n")
                f.write(data['content']['main_answer'] + "\n\n")
            
            # Sources
            if data['content'].get('sources'):
                f.write("## Sources\n")
                for source in data['content']['sources']:
                    f.write(f"- [{source['text']}]({source['url']})\n")
                f.write("\n")
            
            # Related Content
            if data['content'].get('related'):
                f.write("## Related\n")
                for item in data['content']['related']:
                    f.write(f"- {item}\n")
        
        print(f"Saved shared link content to {filename}")
        return filename

# Usage Example
if __name__ == "__main__":
    API_KEY = "D0MT0DIIZGECAZIU5Q3356UCT40W8R9GXM01HD8VQE5X76JINAXUL985CH09HJGMXZKIZV80C8OYKFL6"  # Replace with your key
    
    scraper = PerplexitySharedLinkScraper(API_KEY)
    
    # Example shared links (replace with yours)
    SHARED_LINKS = [
        "https://www.perplexity.ai/search/top-10-cars-in-india-LNcLFbJ4Q4WaCFPZbJvdog"
    ]
    
    for link in SHARED_LINKS:
        print(f"\nProcessing shared link: {link}")
        result = scraper.scrape_shared_link(link)
        
        if result:
            md_file = scraper.save_to_markdown(result)
            print(f"✅ Success! First 50 chars: {result['content'].get('main_answer','')[:50]}...")
        else:
            print("❌ Failed to scrape shared link")
        
        scraper.random_delay()  # Be polite between requests