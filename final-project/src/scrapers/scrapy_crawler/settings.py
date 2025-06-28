# ... (existing settings) ...
BOT_NAME = "ebay_crawler"
SPIDER_MODULES = ["src.scrapers.scrapy_crawler.spiders"]
NEWSPIDER_MODULE = "src.scrapers.scrapy_crawler.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Add our pipeline
ITEM_PIPELINES = {
   "src.scrapers.scrapy_crawler.pipelines.SQLitePipeline": 300,
}

# Set a user agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 3