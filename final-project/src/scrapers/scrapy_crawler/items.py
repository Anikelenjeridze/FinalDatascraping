import scrapy

class ProductItem(scrapy.Item):
    query = scrapy.Field()
    source = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    scraped_at = scrapy.Field()