import asyncio
import concurrent.futures
import sys
 
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
 
from markdown_cleaner import clean_markdown
 
 
async def async_scrape(urls: list[str], base_url: str) -> list[dict]:
    """
    Async function that scrapes multiple URLs and returns a list of dicts
    with url and its markdown content.
    """
 
    prune_filter = PruningContentFilter(
        threshold=0.6,
        threshold_type="dynamic",
        min_word_threshold=150
    )
 
    md_generator = DefaultMarkdownGenerator(
        content_filter=prune_filter,
        options={
            "ignore_links": True,
            "escape_html": False,
            "only_text": True,
        }
    )
 
    browser_config = BrowserConfig(headless=True, verbose=False)
 
    run_config = CrawlerRunConfig(
        markdown_generator=md_generator,
        cache_mode=CacheMode.BYPASS,
        excluded_tags=["nav", "footer"],
        css_selector="main, article, .content, .main, #content",
        stream=False
    )
 
    async with AsyncWebCrawler(config=browser_config) as crawler:
 
        results = await crawler.arun_many(urls=urls, config=run_config)
 
        structured_results = []
 
        for result in results:
            if result.success and result.markdown:
                raw = result.markdown.raw_markdown.strip()
 
                cleaned = clean_markdown(raw)
 
                if len(raw) < 200:
                    continue
 
                structured_results.append({
                    "url": result.url,
                    "base_url": base_url,
                    "content": f"Source: {result.url}\n\n{cleaned}"
                })
 
        print(f"Scraping completed for {len(urls)} URLs.")
        return structured_results
 
 
def scrape(urls: list[str], base_url: str) -> list[dict]:
    """
    Synchronous entry point for scraping.
 
    On Windows, Streamlit uses SelectorEventLoop which does not support
    subprocess creation (required by Playwright). The fix is to spin up
    a brand new thread, set a ProactorEventLoop on it, and run all async
    scraping there — completely isolated from Streamlit's event loop.
 
    All crawl4ai and markdown_cleaner imports are repeated inside the
    thread function because the new thread does not inherit the parent
    thread's module-level namespace on Windows.
 
    On macOS/Linux, asyncio.run() works fine directly.
    """
 
    if sys.platform == "win32":
 
        def run_in_thread():
            import asyncio

            from crawl4ai import (
                AsyncWebCrawler,
                BrowserConfig,
                CacheMode,
                CrawlerRunConfig,
            )
            from crawl4ai.content_filter_strategy import PruningContentFilter
            from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

            from markdown_cleaner import clean_markdown
 
            async def _scrape():
                prune_filter = PruningContentFilter(
                    threshold=0.6,
                    threshold_type="dynamic",
                    min_word_threshold=150
                )
                md_generator = DefaultMarkdownGenerator(
                    content_filter=prune_filter,
                    options={
                        "ignore_links": True,
                        "escape_html": False,
                        "only_text": True,
                    }
                )
                browser_config = BrowserConfig(headless=True, verbose=False)
                run_config = CrawlerRunConfig(
                    markdown_generator=md_generator,
                    cache_mode=CacheMode.BYPASS,
                    excluded_tags=["nav", "footer"],
                    css_selector="main, article, .content, .main, #content",
                    stream=False
                )
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    results = await crawler.arun_many(urls=urls, config=run_config)
                    structured_results = []
                    for result in results:
                        if result.success and result.markdown:
                            raw = result.markdown.raw_markdown.strip()
                            cleaned = clean_markdown(raw)
                            if len(raw) < 200:
                                continue
                            structured_results.append({
                                "url": result.url,
                                "base_url": base_url,
                                "content": f"Source: {result.url}\n\n{cleaned}"
                            })
                    print(f"Scraping completed for {len(urls)} URLs.")
                    return structured_results
 
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(_scrape())
            finally:
                loop.close()
 
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(run_in_thread).result()
 
    else:
        # macOS / Linux — no event loop conflict with Streamlit
        return asyncio.run(async_scrape(urls, base_url))
 
 
if __name__ == "__main__":
    print(scrape(["https://docs.langchain.com/oss/python/integrations/tools"], "https://docs.langchain.com/")[0]['url'])