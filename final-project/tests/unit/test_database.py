import pytest
import sqlite3
from src.data.database import Database
from src.data.models import Product

@pytest.fixture
def memory_db(monkeypatch):
    """Fixture to use an in-memory SQLite database for tests."""
    def mock_db_init(self):
        self.db_path = ":memory:"
        self.conn = None
    monkeypatch.setattr(Database, "__init__", mock_db_init)

def test_create_table(memory_db):
    with Database() as db:
        cursor = db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
        assert cursor.fetchone() is not None

def test_save_products(memory_db):
    products = [
        Product(query="test", source="test", title="Product A", price=99.99, url="http://a.com"),
        Product(query="test", source="test", title="Product B", price=199.99, url="http://b.com"),
    ]
    with Database() as db:
        db.save_products(products)
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products;")
        assert cursor.fetchone()[0] == 2

    # Test uniqueness constraint (OR IGNORE)
    with Database() as db:
        db.save_products(products) # Try to save again
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products;")
        assert cursor.fetchone()[0] == 2