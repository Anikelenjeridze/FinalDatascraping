from abc import ABC, abstractmethod
from typing import List
from src.data.models import Product

class BaseScraper(ABC):
    """Abstract Base Class for all scrapers."""
    def __init__(self, site_name: str, config: dict):
        self.site_name = site_name
        self.config = config

    @abstractmethod
    def scrape(self, query: str) -> List[Product]:
        """The main method to orchestrate the scraping process."""
        pass