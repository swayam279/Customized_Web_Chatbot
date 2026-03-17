import asyncio
import time

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
)
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from dotenv import load_dotenv

load_dotenv()

async def async_scrape(urls: str) -> str:
    """
    Async function that scrapes multiple URLs and returns combined markdown content.
    """
    prune_filter = PruningContentFilter(
    threshold=0.4,
    threshold_type="dynamic",  
    # threshold_type="fixed",  
    min_word_threshold=100
)

    md_generator = DefaultMarkdownGenerator(
        content_filter= prune_filter,
        options={
            "ignore_links": True,
            "escape_html": False,
        }
    )

    browser_config = BrowserConfig(
        headless=True,
        verbose=False
    )

    run_config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS,
        excluded_tags=["nav", "footer"],
        stream=False
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:

        results = await crawler.arun(
            url=urls,
            config=run_config
        )

        # markdown_results = []

        for result in results:
            if result.success:
                return result.markdown
            else:
                return f"Failed to crawl {result.url}: {result.error_message}"

        


def scrape(urls: str) -> str:
    """
    Synchronous wrapper for async_scrape.
    """
    return asyncio.run(async_scrape(urls))


if __name__ == "__main__":
    URLS = ['https://webscraper.io/',
 'https://webscraper.io/cloud-scraper',
 'https://webscraper.io/pricing',
 'https://webscraper.io/documentation',
 'https://webscraper.io/tutorials',
 'https://webscraper.io/test-sites',
 'https://webscraper.io/about-us',
 'https://webscraper.io/contact',
 'https://webscraper.io/privacy-policy',
 'https://webscraper.io/extension-privacy-policy',
 'https://webscraper.io/screenshots',
 'https://webscraper.io/documentation/installation',
 'https://webscraper.io/documentation/open-web-scraper',
 'https://webscraper.io/documentation/scraping-a-site',
 'https://webscraper.io/downloads/Web_Scraper_Media_Kit.zip',
 'https://webscraper.io/documentation/selectors',
 'https://webscraper.io/documentation/selectors/text-selector',
 'https://webscraper.io/documentation/selectors/link-selector',
 'https://webscraper.io/documentation/selectors/sitemap-xml-selector',
 'https://webscraper.io/documentation/selectors/image-selector',
 'https://webscraper.io/documentation/selectors/table-selector',
 'https://webscraper.io/documentation/selectors/element-attribute-selector',
 'https://webscraper.io/documentation/selectors/html-selector',
 'https://webscraper.io/documentation/selectors/element-selector',
 'https://webscraper.io/documentation/selectors/element-click-selector',
 'https://webscraper.io/documentation/selectors/pagination-selector',
 'https://webscraper.io/documentation/website-state-setup-2f-sign-in',
 'https://webscraper.io/documentation/css-selector',
 'https://webscraper.io/documentation/web-scraper-cloud',
 'https://webscraper.io/documentation/web-scraper-cloud/sitemap-sync',
 'https://webscraper.io/documentation/web-scraper-cloud/notifications',
 'https://webscraper.io/documentation/web-scraper-cloud/data-quality-control',
 'https://webscraper.io/documentation/web-scraper-cloud/api',
 'https://webscraper.io/documentation/web-scraper-cloud/api/webhooks',
 'https://webscraper.io/documentation/web-scraper-cloud/scheduler',
 'https://webscraper.io/documentation/web-scraper-cloud/data-export',
 'https://webscraper.io/documentation/web-scraper-cloud/image-export',
 'https://webscraper.io/documentation/web-scraper-cloud/parser',
 'https://webscraper.io/documentation/web-scraper-cloud/parser/replace-text',
 'https://webscraper.io/documentation/web-scraper-cloud/parser/regex-match',
 'https://webscraper.io/documentation/web-scraper-cloud/parser/append-and-prepend-text',
 'https://webscraper.io/documentation/web-scraper-cloud/parser/strip-html',
 'https://webscraper.io/documentation/web-scraper-cloud/parser/remove-whitespaces',
 'https://webscraper.io/documentation/web-scraper-cloud/parser/remove-column',
 'https://webscraper.io/documentation/web-scraper-cloud/parser/virtual-column',
 'https://webscraper.io/documentation/web-scraper-cloud/parser/convert-unix-timestamp',
 'https://webscraper.io/tutorials/extension-intro',
 'https://webscraper.io/tutorials/ai-wizard',
 'https://webscraper.io/tutorials/cloud-overview',
 'https://webscraper.io/tutorials/open-web-scraper',
 'https://webscraper.io/tutorials/element-scroll-selector',
 'https://webscraper.io/tutorials/multiple-items',
 'https://webscraper.io/tutorials/general-pagination',
 'https://webscraper.io/tutorials/dropdown-variation',
 'https://webscraper.io/tutorials/jquery-contains-selector',
 'https://webscraper.io/tutorials/parser',
 'https://webscraper.io/tutorials/sitemap-sync',
 'https://webscraper.io/tutorials/create-a-sitemap',
 'https://webscraper.io/tutorials/add-multiple-start-urls',
 'https://webscraper.io/tutorials/action-keys',
 'https://webscraper.io/tutorials/pagination-load-more',
 'https://webscraper.io/tutorials/sitemap-xml',
 'https://webscraper.io/tutorials/element-attribute',
 'https://webscraper.io/tutorials/pagination-next',
 'https://webscraper.io/tutorials/pagination-number-buttons',
 'https://webscraper.io/tutorials/button-variation',
 'https://webscraper.io/tutorials/product-with-multiple-variations',
 'https://webscraper.io/tutorials/jquery-has-selector',
 'https://webscraper.io/tutorials/jquery-not-contains-selector',
 'https://webscraper.io/tutorials/jquery-not-has-selector',
 'https://webscraper.io/blog',
 'https://webscraper.io/blog/how-to-scrape-bbb-business-listings',
 'https://webscraper.io/blog/how-to-scrape-copart-vehicle-listings',
 'https://webscraper.io/blog/how-to-scrape-trustpilot-company-listings',
 'https://webscraper.io/blog/how-to-scrape-diy-product-listings',
 'https://webscraper.io/blog/how-to-scrape-amazon-product-listings',
 'https://webscraper.io/blog/how-to-scrape-rightmove-property-listings',
 'https://webscraper.io/blog/how-to-scrape-amazon-bestsellers',
 'https://webscraper.io/blog/how-to-scrape-g2-companies',
 'https://webscraper.io/blog/how-to-scrape-yellow-pages-businesses',
 'https://webscraper.io/blog/how-to-scrape-realtor-property-listings',
 'https://webscraper.io/blog/google-patches-100-precise-cloudflare-turnstile-bot-check',
 'https://webscraper.io/blog/sitemap-wizard-update',
 'https://webscraper.io/blog/web-scraper-website-state-setup-release',
 'https://webscraper.io/blog/web-scraper-1.79.3-release',
 'https://webscraper.io/blog/web-scraper-1.75.7-release',
 'https://webscraper.io/blog/web-scraper-1.72.5-release',
 'https://webscraper.io/blog/web-scraper-1.29.66-release',
 'https://webscraper.io/blog/web-scraper-1.29.60-release',
 'https://webscraper.io/blog/web-scraper-0.6.5-release',
 'https://webscraper.io/blog/css-and-jquery-selectors',
 'https://webscraper.io/blog/data-analysis-using-anazon-athena',
 'https://webscraper.io/blog/headless-scraping-with-cheerio',
 'https://webscraper.io/blog/scraping-public-data',
 'https://webscraper.io/blog/0.6.0-release',
 'https://webscraper.io/blog/frequently-asked-questions',
 'https://webscraper.io/blog/google-data-export-feature',
 'https://webscraper.io/blog/scraping-customer-reviews',
 'https://webscraper.io/blog/brief-history-of-web-scraping',
 'https://webscraper.io/blog/data-quality-control',
 'https://webscraper.io/blog/ultimate-web-scraping-guide',
 'https://webscraper.io/blog/webscraper-shopify-import',
 'https://webscraper.io/blog/scrape-at-scale',
 'https://webscraper.io/blog/css-selectors',
 'https://webscraper.io/blog/sitemap-scraping-selector',
 'https://webscraper.io/blog/scraping-brands',
 'https://webscraper.io/blog/scraping-the-classical-way',
 'https://webscraper.io/blog/OpenRefine-data-transfromation',
 'https://webscraper.io/blog/0.5.0-release',
 'https://webscraper.io/blog/data-transformation-with-Open-Refine',
 'https://webscraper.io/blog/OpenRefine-Introduction',
 'https://webscraper.io/blog/data-transformation-with-Web-Scraper',
 'https://webscraper.io/blog/web-scraper-collaboration',
 'https://webscraper.io/blog/data-extraction-for-business',
 'https://webscraper.io/blog/the-role-of-big-data',
 'https://webscraper.io/blog/Data-Visualization-Google-Data-Studio',
 'https://webscraper.io/blog/coronavirus-pandemic-google-trends-analysis',
 'https://webscraper.io/blog/sports-arbitrage-betting',
 'https://webscraper.io/blog/Query-Function-Of-Google-Sheets',
 'https://webscraper.io/blog/parser-release',
 'https://webscraper.io/blog/scrape-yellowpages.com',
 'https://webscraper.io/blog/web-scraper-0.4.0-release',
 'https://webscraper.io/marketplace',
 'https://webscraper.io/marketplace/asos-products-listings-scraper',
 'https://webscraper.io/marketplace/amazon-bestsellers-scraper',
 'https://webscraper.io/marketplace/target-products-listings-scraper',
 'https://webscraper.io/marketplace/amazon-products-listings-scraper',
 'https://webscraper.io/marketplace/amazon-asin-scraper',
 'https://webscraper.io/marketplace/sustainablesupply-products-listings-scraper',
 'https://webscraper.io/marketplace/homedepot-products-listings-scraper',
 'https://webscraper.io/marketplace/g2-companies-listings-scraper',
 'https://webscraper.io/marketplace/newegg-products-listings-scraper',
 'https://webscraper.io/marketplace/propertyfinder-property-listings-scraper',
 'https://webscraper.io/marketplace/etsy-products-listings-scraper',
 'https://webscraper.io/marketplace/ebay-products-listings-scraper',
 'https://webscraper.io/marketplace/diy-products-listings-scraper',
 'https://webscraper.io/marketplace/costco-products-listings-scraper',
 'https://webscraper.io/marketplace/samsclub-products-listings-scraper',
 'https://webscraper.io/marketplace/rightmove-property-listings-scraper',
 'https://webscraper.io/marketplace/eventbrite-events-listings-scraper',
 'https://webscraper.io/marketplace/coinmarketcap-crypto-listings-scraper',
 'https://webscraper.io/marketplace/ziprecruiter-jobs-listings-scraper',
 'https://webscraper.io/marketplace/clutch-companies-listings-scraper',
 'https://webscraper.io/marketplace/superpages-businesses-listings-scraper',
 'https://webscraper.io/marketplace/europages-companies-listings-scraper',
 'https://webscraper.io/marketplace/yellowpages-businesses-listings-scraper',
 'https://webscraper.io/marketplace/zillow-property-listings-scraper',
 'https://webscraper.io/marketplace/walmart-products-listings-scraper',
 'https://webscraper.io/marketplace/noon-products-listings-scraper',
 'https://webscraper.io/marketplace/allegro-products-listings-scraper',
 'https://webscraper.io/marketplace/trustpilot-businesses-listings-scraper',
 'https://webscraper.io/marketplace/yelp-businesses-listings-scraper',
 'https://webscraper.io/marketplace/tripadvisor-restaurants-listings-scraper',
 'https://webscraper.io/marketplace/tripadvisor-hotels-listings-scraper',
 'https://webscraper.io/marketplace/zillow-agents-listings-scraper',
 'https://webscraper.io/marketplace/pagesjaunes-businesses-listings-scraper',
 'https://webscraper.io/marketplace/tokopedia-products-listings-scraper',
 'https://webscraper.io/marketplace/bbb-businesses-listings-scraper',
 'https://webscraper.io/marketplace/justdial-businesses-listings-scraper',
 'https://webscraper.io/marketplace/lowes-products-listings-scraper',
 'https://webscraper.io/marketplace/realtor-property-listings-scraper',
 'https://webscraper.io/marketplace/amazon-sellers-scraper',
 'https://webscraper.io/marketplace/booking-stays-listings-scraper',
 'https://webscraper.io/marketplace/producthunt-products-listings-scraper',
 'https://webscraper.io/marketplace/wayfair-products-listings-scraper',
 'https://webscraper.io/marketplace/hotelscom-hotels-listings-scraper',
 'https://webscraper.io/marketplace/monster-jobs-listings-scraper',
 'https://webscraper.io/marketplace/autoscout24-vehicles-listings-scraper',
 'https://webscraper.io/marketplace/copart-vehicles-listings-scraper',
 'https://webscraper.io/marketplace/capterra-software-listings-scraper',
 'https://webscraper.io/marketplace/yell-businesses-listings-scraper',
 'https://webscraper.io/marketplace/manta-businesses-listings-scraper',
 'https://webscraper.io/marketplace/zoopla-property-listings-scraper']
    
    start= time.time()
    
    for url in URLS:
        scrape(url)
        
    end= time.time()
    time_taken= end-start
    print(f"\n\nTime taken : {time_taken} seconds.")