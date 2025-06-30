import pytest
import sqlite3
from src.data.database import Database
from src.data.models import Product
# Fixture to mock Database initialization and use an in-memory SQLite DB
@pytest.fixture
def memory_db(monkeypatch):
    """Fixture to use an in-memory SQLite database for tests."""
    def mock_db_init(self):
        self.db_path = ":memory:"
        self.conn = None
    monkeypatch.setattr(Database, "__init__", mock_db_init)

# This function replaces Database.__init__ to force use of an in-memory DB
def test_create_table(memory_db):
    with Database() as db:
        cursor = db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
        assert cursor.fetchone() is not None


# Test if products are saved correctly and uniqueness is enforced
def test_save_products(memory_db):
    products = [
        Product(query="test", source="test", title="Product A", price=99.99, url="http://a.com"),
        Product(query="test", source="test", title="Product B", price=199.99, url="http://b.com"),
    ]
     # First, save products to DB and check the count
    with Database() as db:
        db.save_products(products)
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products;")
        assert cursor.fetchone()[0] == 2

    # Test uniqueness constraint: saving the same products again
    with Database() as db:
        db.save_products(products) # Try to save again
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products;")
        assert cursor.fetchone()[0] == 2