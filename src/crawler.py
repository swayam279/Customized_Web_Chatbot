import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from markdown_cleaner import clean_markdown


async def async_scrape(urls: list[str], base_url: str) -> list[dict]:
    """ 
    This is an Async function that scrapes multiple URLs and returns a dictionary with url and its markdown content.
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
                # raw = result.markdown.raw_markdown

                cleaned = clean_markdown(raw)

                if len(raw) < 200:
                    continue

                structured_results.append({
                    "url": result.url,
                    "base_url": base_url,
                    "content": f"Source: {result.url}\n\n{cleaned}"
                })

        return structured_results


def scrape(urls: list[str], base_url: str):
    return asyncio.run(async_scrape(urls, base_url))


if __name__ == "__main__":
    print(scrape(["https://docs.langchain.com/oss/python/integrations/tools"], "https://docs.langchain.com/")[0]['url'])