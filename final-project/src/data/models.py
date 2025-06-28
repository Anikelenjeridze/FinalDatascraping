from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Product:
    """Data model for a scraped product."""
    query: str
    source: str
    title: str
    price: float
    url: str
    rating: str = "N/A"
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())