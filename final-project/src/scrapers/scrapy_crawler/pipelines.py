import sqlite3
from itemadapter import ItemAdapter
from src.utils.logger import logger
from src.utils.config import SETTINGS

class SQLitePipeline:
    def open_spider(self, spider):
        self.conn = sqlite3.connect(SETTINGS['database']['path'])
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO products (query, source, title, price, url, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                adapter.get('query'),
                adapter.get('source'),
                adapter.get('title'),
                adapter.get('price'),
                adapter.get('url'),
                adapter.get('scraped_at'),
            ),
        )
        self.conn.commit()
        logger.info(f"Saved Scrapy item to DB: {adapter.get('title')[:30]}...")
        return item