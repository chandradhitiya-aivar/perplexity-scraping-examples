import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from fake_useragent import UserAgent

class PerplexityScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.ua = UserAgent()
        
    def random_delay(self, min_t=1, max_t=3):
        time.sleep(random.uniform(min_t, max_t))
    
    def human_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
    
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        options.add_argument(f"user-agent={self.ua.random}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1280,720")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        return driver
    
    def scrape_shared_link(self, url):
        driver = self.setup_driver()
        
        try:
            # Initial navigation with random delays
            driver.get("https://www.google.com")
            self.random_delay(1, 2)
            
            # Access the shared link
            driver.get(url)
            self.random_delay(3, 5)
            
            # Bypass potential paywalls/interstitials
            try:
                driver.find_element(By.CSS_SELECTOR, "button:contains('Continue')").click()
                self.random_delay()
            except Exception as e:
                print(f"Continue button not found: {e}")
            
            # Extract all content sections
            content = {}
            
            try:
                # 1. Main answer content
                main_answer = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".prose, .answer-content")))
                content['main_answer'] = main_answer.text
            except Exception as e:
                print(f"Main answer not found: {e}")
                content['main_answer'] = "Not found"
            
            try:
                # 2. Sources/references
                sources = driver.find_elements(By.CSS_SELECTOR, ".sources a")
                content['sources'] = [s.get_attribute('href') for s in sources]
            except Exception as e:
                print(f"Sources not found: {e}")
                content['sources'] = []
            
            try:
                # 3. Related questions
                related = driver.find_elements(By.CSS_SELECTOR, ".related-question")
                content['related_questions'] = [q.text for q in related]
            except Exception as e:
                print(f"Related questions not found: {e}")
                content['related_questions'] = []
            
            try:
                # 4. Metadata
                content['title'] = driver.find_element(By.CSS_SELECTOR, "h1").text
                content['date'] = driver.find_element(By.CSS_SELECTOR, "time").get_attribute('datetime')
            except Exception as e:
                print(f"Metadata not found: {e}")
                content['title'] = driver.title
                content['date'] = None
            
            return content
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            driver.save_screenshot("error.png")
            return None
            
        finally:
            driver.quit()

if __name__ == "__main__":
    scraper = PerplexityScraper(headless=False)
    shared_url = "shared_link_1"
    result = scraper.scrape_shared_link(shared_url)
    
    if result:
        print("Scraped Content:")
        print(f"Title: {result.get('title')}")
        print(f"Date: {result.get('date')}")
        print("\nMain Answer:")
        print(result.get('main_answer', '')[:500] + "...")
        print(f"\nSources: {len(result.get('sources', []))}")
        print(f"Related Questions: {len(result.get('related_questions', []))}")
    else:
        print("Scraping failed")