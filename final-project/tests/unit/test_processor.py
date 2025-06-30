import pytest
from src.data.processors import clean_price, clean_title
# Test suite for the clean_price function
def test_clean_price():
    assert clean_price("$1,299.99") == 1299.99
    assert clean_price("USD 54.50") == 54.50
    assert clean_price("Free") == 0.0
    assert clean_price(None) == 0.0
    assert clean_price("Contact seller") == 0.0
# Test suite for the clean_title function
def test_clean_title():
    assert clean_title("  Awesome Product  \n") == "Awesome Product"
    assert clean_title(None) == "N/A"