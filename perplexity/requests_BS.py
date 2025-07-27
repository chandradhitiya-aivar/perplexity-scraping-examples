import random
import time
from playwright.sync_api import sync_playwright
from datetime import datetime

class PerplexityScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"
        ]
        
    def random_delay(self, min_sec=0.5, max_sec=2.0):
        """Random delay between actions"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def human_type(self, element, text):
        """Simulate human typing with random delays"""
        for char in text:
            element.type(char, delay=random.randint(30, 150))
            if random.random() > 0.9:  # Occasionally pause longer
                self.random_delay(0.1, 0.3)
    
    def mouse_movement(self, page):
        """Generate human-like mouse movements"""
        width = random.randint(800, 1200)
        height = random.randint(600, 900)
        page.mouse.move(
            random.randint(0, width),
            random.randint(0, height)
        )
    
    def get_search_results(self, page, query):
        """Extract search results from page"""
        try:
            # Multiple possible selectors for results
            selectors = [
                ".prose",
                ".answer-content",
                "[role='article']",
                "main >> div >> nth=2"
            ]
            
            for selector in selectors:
                try:
                    page.wait_for_selector(selector, state="visible", timeout=15000)
                    content = page.inner_text(selector)
                    if content and len(content) > 50:  # Minimum content length
                        return content
                except:
                    continue
            return None
        except Exception as e:
            print(f"Error extracting results: {str(e)}")
            return None
    
    def scrape(self, query, max_retries=3):
        """Main scraping function"""
        for attempt in range(max_retries):
            try:
                with sync_playwright() as p:
                    # Configure browser with stealth options
                    browser = p.chromium.launch(
                        headless=self.headless,
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--start-maximized",
                            f"--user-agent={random.choice(self.user_agents)}"
                        ]
                    )
                    
                    context = browser.new_context(
                        viewport={"width": random.randint(1000, 1400), "height": random.randint(800, 1000)},
                        locale="en-US",
                        timezone_id="America/New_York",
                        color_scheme="light"
                    )
                    
                    # Add stealth scripts
                    context.add_init_script("""
                        delete navigator.webdriver;
                        window.chrome = {runtime: {}};
                        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
                    """)
                    
                    page = context.new_page()
                    
                    try:
                        # Random browsing pattern
                        if random.random() > 0.7:
                            page.goto("https://www.google.com/search?q=perplexity+ai", timeout=60000)
                            self.random_delay(1, 3)
                        
                        # Main page navigation
                        page.goto("https://www.perplexity.ai/search/hi-i-want-to-sracp-from-the-in-PeGJB0VsQ3qi1JRTkjjgJA", timeout=60000)
                        self.random_delay(2, 4)
                        
                        # Human-like mouse movement
                        self.mouse_movement(page)
                        
                        # Find search box with multiple fallbacks
                        # Updated selectors (check manually via DevTools)
                        search_selectors = [
                            "textarea[placeholder*='ask']",  # Case-insensitive match
                            "div[contenteditable='true']",   # New rich-text input
                            "input.search-box-input",         # Class-based selector
                            "xpath=//textarea | //input[@type='text']"  # Broad fallback
                        ]
                        
                        search_box = None
                        for selector in search_selectors:
                            try:
                                search_box = page.wait_for_selector(selector, state="visible", timeout=10000)
                                if search_box:
                                    search_box.highlight()  # Visual confirmation
                                    break
                            except:
                                continue
                        
                        if not search_box:
                            raise Exception("Search box not found")
                        
                        # Human-like interaction
                        search_box.click()
                        self.random_delay(0.5, 1)
                        self.human_type(search_box, query)
                        self.random_delay(0.3, 0.7)
                        
                        # Submit search with multiple methods
                        button_selectors = [
                            "button[aria-label='Search']",
                            "button:has-text('Search')",
                            "xpath=//button[contains(., 'Search')]"
                        ]
                        
                        submitted = False
                        for selector in button_selectors:
                            try:
                                button = page.wait_for_selector(selector, timeout=5000)
                                button.click()
                                submitted = True
                                break
                            except:
                                continue
                        
                        if not submitted:
                            search_box.press("Enter")  # Fallback
                        
                        # Get results
                        self.random_delay(3, 6)  # Wait for results to load
                        result = self.get_search_results(page, query)
                        
                        if result:
                            # Save screenshot for debugging
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            page.screenshot(path=f"perplexity_result_{timestamp}.png")
                            return result
                        else:
                            raise Exception("No results found")
                    
                    except Exception as e:
                        print(f"Attempt {attempt + 1} failed: {str(e)}")
                        page.screenshot(path=f"error_{attempt}.png")
                        continue
                    
                    finally:
                        self.random_delay(1, 3)  # Random delay before closing
                        browser.close()
            
            except Exception as e:
                print(f"Browser error: {str(e)}")
                continue
        
        return None

if __name__ == "__main__":
    scraper = PerplexityScraper(headless=False)  # Set to True in production
    query = "Explain quantum computing in simple terms"
    
    print("Starting scrape...")
    result = scraper.scrape(query)
    
    if result:
        print("\n=== SCRAPED RESULTS ===")
        print(result[:2000] + "...")  # Print first 2000 characters
    else:
        print("Scraping failed after multiple attempts")