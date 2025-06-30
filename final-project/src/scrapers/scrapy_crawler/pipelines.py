# pipelines.py in src/scrapers/scrapy_crawler/

import sqlite3
import os
from itemadapter import ItemAdapter
from pathlib import Path

class SQLitePipeline:
    def open_spider(self, spider):
        # This file is in: .../src/scrapers/scrapy_crawler/
        # We need to go up 3 directories to get to the project root.
        project_root = Path(__file__).resolve().parents[3]
        db_dir = project_root / 'data_output'
        
        os.makedirs(db_dir, exist_ok=True)
        db_path = db_dir / 'product_prices.db'
        
        spider.logger.info(f"Pipeline connecting to database at: {db_path}")
        
        self.conn = sqlite3.connect(str(db_path))
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            url TEXT UNIQUE,
            rating TEXT,
            scraped_at TEXT NOT NULL
        );
        """)

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
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
            spider.logger.info(f"Saved item to DB: {adapter.get('title')[:40]}...")
        except sqlite3.Error as e:
            spider.logger.error(f"Failed to insert item into DB: {e}")
        return item