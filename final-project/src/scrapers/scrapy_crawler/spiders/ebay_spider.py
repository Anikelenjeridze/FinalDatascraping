import scrapy
from ..items import ProductItem
from src.data.processors import clean_price, clean_title
from datetime import datetime

class EbaySpider(scrapy.Spider):
    name = "ebay"
    allowed_domains = ["ebay.com"]

    def __init__(self, query="", *args, **kwargs):
        super(EbaySpider, self).__init__(*args, **kwargs)
        self.start_urls = [f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"]
        self.query = query

    def parse(self, response):
        self.logger.info(f"Parsing page for query: {self.query}")
        products = response.css('.s-item')

        for product in products:
            title = product.css('.s-item__title::text').get()
            price_str = product.css('.s-item__price::text').get()
            url = product.css('.s-item__link::attr(href)').get()

            if title and price_str and url and "Shop on eBay" not in title:
                item = ProductItem()
                item['query'] = self.query
                item['source'] = 'ebay'
                item['title'] = clean_title(title)
                item['price'] = clean_price(price_str)
                item['url'] = url
                item['scraped_at'] = datetime.utcnow().isoformat()
                yield item