# src/scrapers/scrapy_crawler/ebay_crawler/settings.py
# Corrected for running via subprocess from the project's root.

BOT_NAME = "ebay_crawler"

SPIDER_MODULES = ["ebay_crawler.spiders"]
NEWSPIDER_MODULE = "ebay_crawler.spiders"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 3

# --- CRITICAL CHANGE FOR PIPELINES ---
# When Scrapy is run from its own directory, it automatically knows
# how to find its own pipelines.
ITEM_PIPELINES = {
   # This is the path relative to the Scrapy project itself.
   "ebay_crawler.pipelines.SQLitePipeline": 300,
}