# src/scrapers/selenium_scraper.py (Final Stealth Version)

import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # Import this
from bs4 import BeautifulSoup
from typing import List
from src.scrapers.base_scraper import BaseScraper
from src.data.models import Product
from src.data.processors import clean_price, clean_title
from src.utils.logger import logger
from src.utils.config import SETTINGS

class SeleniumScraper(BaseScraper):
    """Scraper for dynamic websites using a stealthy version of Selenium."""
    def scrape(self, query: str) -> List[Product]:
        products = []
        search_url = self.config['base_url'].format(query=query.replace(' ', '+'))
        logger.info(f"[{self.site_name}] Scraping {search_url} with undetected-chromedriver.")

        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        
        # --- Make the browser look more human ---
        options.add_argument(f"user-agent={SETTINGS['scraper_settings']['default_user_agent']}")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--incognito") # Running in incognito can sometimes help
        # --- End of human-like options ---

        driver = None
        try:
            # Pin the driver version to match your installed Chrome browser
            driver = uc.Chrome(options=options, version_main=137, use_subprocess=True) # use_subprocess can help with stability
            
            driver.get(search_url)

            # --- A more patient waiting strategy ---
            try:
                # First, wait for the page body to be present. This should always be fast.
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                logger.debug("Page body loaded. Now waiting for search results...")
                
                # Now, wait specifically for the search results container.
                # If this fails, it's a clear sign of a block/CAPTCHA page.
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-results"]'))
                )
                logger.debug("Search results container is present.")

            except TimeoutException:
                logger.error("Timed out waiting for search results. The page is likely a CAPTCHA or block page.")
                with open("block_page.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                logger.info("Saved the block page source to block_page.html for manual inspection.")
                return [] # Exit gracefully
            # --- End of waiting strategy ---

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup.select(self.config['product_container'])
            logger.info(f"[{self.site_name}] Found {len(items)} potential item containers for query '{query}'.")

            # --- The rest of the parsing logic is the same ---
            for i, item in enumerate(items, 1):
                try:
                    title_elem = item.select_one(self.config['data_selectors']['title'])
                    price_elem = item.select_one(self.config['data_selectors']['price'])
                    url_elem = item.select_one(self.config['data_selectors']['url'])

                    raw_title = title_elem.get_text(strip=True) if title_elem else "TITLE NOT FOUND"
                    raw_price = price_elem.get_text(strip=True) if price_elem else "PRICE NOT FOUND"
                    logger.debug(f"Item #{i}: Raw Title='{raw_title}', Raw Price='{raw_price}'")

                    if item.select_one('a.s-sponsored-label-text'):
                        logger.debug(f"Skipping item #{i} because it is a sponsored product.")
                        continue
                    
                    title = clean_title(title_elem.get_text(strip=True)) if title_elem else "N/A"
                    price = clean_price(price_elem.get_text(strip=True)) if price_elem else 0.0

                    if url_elem and url_elem.get('href') and url_elem['href'].startswith('/'):
                        url = "https://www.amazon.com" + url_elem['href']
                    else:
                        logger.warning(f"Skipping item #{i} due to invalid or missing URL.")
                        continue

                    if title != "N/A" and price > 0.0 and "/gp/slredirect/" not in url:
                        products.append(Product(query=query, source=self.site_name, title=title, price=price, url=url))
                    else:
                        logger.debug(f"Skipping item #{i}. Final check failed.")
                except Exception as e:
                    logger.error(f"An unexpected error occurred parsing item #{i}: {e}", exc_info=False)

            logger.info(f"Completed scrape task for '{self.site_name}', successfully processed and saved {len(products)} products.")
            return products

        except Exception as e:
            logger.error(f"[{self.site_name}] A critical error occurred during scraping: {e}", exc_info=False)
            if driver:
                with open("critical_error_page.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                logger.info("Saved page source on critical error to critical_error_page.html")
            return []
        finally:
            if driver:
                driver.quit()
                logger.debug("WebDriver has been closed.")