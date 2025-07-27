import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import json
from datetime import datetime
from urllib.parse import urlparse
import random

class PerplexitySharedLinkItem(scrapy.Item):
    """Data structure for shared link content"""
    timestamp = scrapy.Field()
    share_url = scrapy.Field()
    title = scrapy.Field()
    main_content = scrapy.Field()
    sources = scrapy.Field()
    related_questions = scrapy.Field()

class PerplexitySharedLinkSpider(scrapy.Spider):
    name = 'perplexity_shared'
    
    # Default settings (can be overridden when instantiating)
    custom_settings = {
        'DOWNLOAD_DELAY': random.uniform(2, 7),
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'RETRY_TIMES': 5,
        'FEEDS': {
            'results/shared_links_%(time)s.jsonl': {
                'format': 'jsonlines',
                'encoding': 'utf8',
                'store_empty': False,
            }
        },
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    def __init__(self, shared_links=None, proxies=None, user_agents=None, *args, **kwargs):
        super(PerplexitySharedLinkSpider, self).__init__(*args, **kwargs)
        
        # Accept input directly without files
        self.shared_links = shared_links or [
            "https://www.perplexity.ai/search/quantum-computing-xyz123",
            "https://www.perplexity.ai/search/ai-ethics-abc456"
        ]
        
        self.proxies = proxies or [
            "http://user:pass@proxy1.example.com:8080",
            "http://user:pass@proxy2.example.com:8080"
        ]
        
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        ]
        
        # Configure settings dynamically
        self.custom_settings.update({
            'ROTATING_PROXY_LIST': self.proxies,
            'USER_AGENT_LIST': self.user_agents,
            'DOWNLOADER_MIDDLEWARES': {
                'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
                'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
                'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
                'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
            }
        })

    def start_requests(self):
        """Generate requests for each shared link"""
        for link in self.shared_links:
            yield scrapy.Request(
                url=link,
                callback=self.parse_shared_link,
                errback=self.errback_handler,
                meta={
                    'proxy': random.choice(self.proxies),
                    'handle_httpstatus_list': [403, 404, 429],
                    'shared_link': link,
                },
                headers={
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.google.com/',
                }
            )

    def parse_shared_link(self, response):
        """Extract content from shared link pages"""
        if "perplexity.ai" not in response.url:
            self.logger.error(f"Redirect detected from shared link: {response.url}")
            return

        item = PerplexitySharedLinkItem()
        item['timestamp'] = datetime.utcnow().isoformat()
        item['share_url'] = response.meta['shared_link']
        item['title'] = response.css('title::text').get() or "Perplexity Shared Link"

        # Main content extraction
        content_selectors = [
            'div.prose',
            'div.shared-content',
            'article.content',
            'div.answer-container'
        ]
        for selector in content_selectors:
            if content := response.css(selector).get():
                item['main_content'] = self.clean_content(content)
                break

        item['sources'] = response.css('footer a::attr(href)').getall() or \
                         response.css('div.sources a::attr(href)').getall()

        item['related_questions'] = response.css('div.related-questions li::text').getall() or \
                                   response.css('div.suggested-questions a::text').getall()

        yield item

    def clean_content(self, raw_html):
        """Clean HTML content while preserving structure"""
        from w3lib.html import remove_tags, replace_escape_chars
        cleaned = replace_escape_chars(remove_tags(raw_html), which_ones=('\n', '\t', '\r'))
        return ' '.join(cleaned.split())

    def errback_handler(self, failure):
        """Handle failed requests with proxy rotation"""
        request = failure.request
        if request.meta.get('retry_times', 0) < 5:
            retryreq = request.copy()
            retryreq.dont_filter = True
            retryreq.meta['proxy'] = random.choice(self.proxies)
            return retryreq
        self.logger.error(f"Gave up on {request.url}")

def run_spider(shared_links=None, proxies=None, user_agents=None):
    """Run the spider with direct input"""
    os.makedirs('results', exist_ok=True)
    
    process = CrawlerProcess(get_project_settings())
    process.crawl(
        PerplexitySharedLinkSpider,
        shared_links=shared_links,
        proxies=proxies,
        user_agents=user_agents
    )
    process.start()

if __name__ == "__main__":
    # EXAMPLE USAGE - Provide input directly here
    YOUR_SHARED_LINKS = [
        "shared_link_1"
    ]
    
    YOUR_PROXIES = [
    "103.156.19.229:8080",
    "45.95.147.222:8080", 
    "194.31.33.10:8080"
]
    
    YOUR_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    ]
    
    run_spider(
        shared_links=YOUR_SHARED_LINKS,
        proxies=YOUR_PROXIES,
        user_agents=YOUR_USER_AGENTS
    )