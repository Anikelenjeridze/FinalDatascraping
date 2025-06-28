import sqlite3
from pathlib import Path  # <-- Import Path
from src.utils.config import SETTINGS
from src.utils.logger import logger
from src.data.models import Product
from typing import List

class Database:
    """Handles all database operations."""
    def __init__(self):
        self.db_path = Path(SETTINGS['database']['path']) # <-- Use Path object
        self.conn = None

    def __enter__(self):
        try:
            # Ensure the parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True) # <-- Add this line
            
            self.conn = sqlite3.connect(self.db_path)
            self.create_table()
            return self
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def create_table(self):
        """Creates the products table if it doesn't exist."""
        create_table_sql = """
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
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_sql)
            logger.info("Database table 'products' is ready.")
        except sqlite3.Error as e:
            logger.error(f"Error creating table: {e}")

    def save_products(self, products: List[Product]):
        """Saves a list of Product objects to the database, ignoring duplicates."""
        insert_sql = """
        INSERT OR IGNORE INTO products (query, source, title, price, url, rating, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        product_data = [
            (p.query, p.source, p.title, p.price, p.url, p.rating, p.scraped_at)
            for p in products
        ]
        try:
            cursor = self.conn.cursor()
            cursor.executemany(insert_sql, product_data)
            self.conn.commit()
            logger.info(f"Saved {cursor.rowcount} new products to the database.")
        except sqlite3.Error as e:
            logger.error(f"Error saving products: {e}")