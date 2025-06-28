import re

def clean_price(price_str: str) -> float:
    """Extracts a float value from a price string (e.g., '$1,299.99')."""
    if not price_str:
        return 0.0
    # Remove currency symbols, commas, and other non-numeric characters
    price_str = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(price_str)
    except (ValueError, TypeError):
        return 0.0

def clean_title(title_str: str) -> str:
    """Cleans and standardizes a product title."""
    if not title_str:
        return "N/A"
    return title_str.strip()