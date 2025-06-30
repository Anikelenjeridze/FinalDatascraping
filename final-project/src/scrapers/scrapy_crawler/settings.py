# settings.py in src/scrapers/scrapy_crawler/

BOT_NAME = "ebay_crawler"

SPIDER_MODULES = ["spiders"]
NEWSPIDER_MODULE = "spiders"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 3

# This path is now simpler because the pipeline is in the same directory.
ITEM_PIPELINES = {
   "pipelines.SQLitePipeline": 300,
}