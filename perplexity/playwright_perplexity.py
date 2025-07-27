from playwright.sync_api import sync_playwright
import random
import time
from datetime import datetime
import json

def scrape_perplexity_shared_link(url):
    """Scrape content from a Perplexity.ai shared link"""
    with sync_playwright() as p:
        # Configure browser with stealth settings
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 120)}.0.0.0 Safari/537.36"
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="en-US",
            timezone_id="America/New_York"
        )

        # Stealth modifications
        context.add_init_script("""
            delete navigator.webdriver;
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        """)

        page = context.new_page()
        
        try:
            # Navigate to the shared link
            page.goto(url, timeout=60000)
            
            # Wait for content to load
            page.wait_for_selector(".prose, .answer-content, [role='article']", timeout=15000)
            
            # Extract content structure
            result = {
                "title": get_element_text(page, "h1") or page.title(),
                "timestamp": datetime.now().isoformat(),
                "source_url": url,
                "content": {}
            }

            # Main content
            result["content"]["main_answer"] = get_element_text(
                page, 
                ".prose, .answer-content, [role='article']"
            )

            # Sources/references
            result["content"]["sources"] = page.eval_on_selector_all(
                ".sources a, a[href*='http']", 
                "elements => elements.map(el => ({text: el.innerText, url: el.href}))"
            )

            # Related questions
            result["content"]["related_questions"] = page.eval_on_selector_all(
                ".related-question, .related-questions li", 
                "elements => elements.map(el => el.innerText)"
            )

            # Save screenshot for debugging
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"perplexity_{timestamp}.png")

            return result

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            page.screenshot(path="error.png")
            return None

        finally:
            browser.close()

def get_element_text(page, selector):
    """Helper to safely get text content"""
    try:
        return page.locator(selector).first.text_content()
    except:
        return None

if __name__ == "__main__":
    # Example shared link (replace with your target URL)
    SHARED_LINK = "shared_link_1"
    
    print(f"Scraping {SHARED_LINK}...")
    results = scrape_perplexity_shared_link(SHARED_LINK)
    
    md_filename = f"perplexity_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(md_filename, 'w') as f:
        f.write(f"# Scraping Results for {SHARED_LINK}\n\n")
        if results:
            f.write(f"## Title: {results.get('title', '')}\n")
            f.write(f"**Timestamp:** {results.get('timestamp', '')}\n")
            f.write(f"**Source URL:** {results.get('source_url', '')}\n\n")
            f.write("### Main Answer\n")
            f.write(results['content'].get('main_answer', 'No answer found.') + "\n\n")
            f.write("### Sources\n")
            sources = results['content'].get('sources', [])
            if sources:
                for src in sources:
                    f.write(f"- [{src.get('text','')}]({src.get('url','')})\n")
            else:
                f.write("No sources found.\n")
            f.write("\n### Related Questions\n")
            related = results['content'].get('related_questions', [])
            if related:
                for q in related:
                    f.write(f"- {q}\n")
            else:
                f.write("No related questions found.\n")
        else:
            f.write("Scraping failed.\n")
    print(f"Results saved to {md_filename}")