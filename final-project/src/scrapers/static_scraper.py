import requests
import time
from bs4 import BeautifulSoup
from typing import List
from src.scrapers.base_scraper import BaseScraper
from src.data.models import Product
from src.data.processors import clean_price, clean_title
from src.utils.logger import logger
from src.utils.config import SETTINGS

class StaticScraper(BaseScraper):
    """Scraper for static websites using Requests and BeautifulSoup."""
    def scrape(self, query: str) -> List[Product]:
        products = []
        search_url = self.config['base_url'].format(query=query.replace(' ', '+'))
        logger.info(f"[{self.site_name}] Scraping {search_url}")

        try:
            headers = {'User-Agent': SETTINGS['scraper_settings']['default_user_agent']}
            response = requests.get(search_url, headers=headers, timeout=SETTINGS['scraper_settings']['timeout'])
            response.raise_for_status()
            
            time.sleep(SETTINGS['scraper_settings']['rate_limit_delay']) # Rate limiting

            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select(self.config['product_container'])
            logger.info(f"[{self.site_name}] Found {len(items)} items for query '{query}'.")

            for item in items:
                try:
                    title_elem = item.select_one(self.config['data_selectors']['title'])
                    price_elem = item.select_one(self.config['data_selectors']['price'])
                    url_elem = item.select_one(self.config['data_selectors']['url'])

                    title = clean_title(title_elem.get_text()) if title_elem else "N/A"
                    price = clean_price(price_elem.get_text()) if price_elem else 0.0
                    
                    if url_elem and 'http' in url_elem.get('href', ''):
                        url = url_elem['href']
                    elif url_elem:
                        base_site_url = '/'.join(self.config['base_url'].split('/')[:3])
                        url = base_site_url + url_elem['href']
                    else:
                        continue

                    if title != "N/A" and price > 0.0:
                        products.append(Product(
                            query=query, source=self.site_name, title=title, price=price, url=url
                        ))
                except Exception as e:
                    logger.warning(f"[{self.site_name}] Could not parse an item: {e}")
            
            return products

        except requests.RequestException as e:
            logger.error(f"[{self.site_name}] HTTP request failed: {e}")
            return []