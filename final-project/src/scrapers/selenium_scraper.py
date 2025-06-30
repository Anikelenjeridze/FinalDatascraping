# src/scrapers/selenium_scraper.py (THE FINAL VERSION)

import time
import random
from selenium_stealth import stealth # Import the new stealth library
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from typing import List
from src.scrapers.base_scraper import BaseScraper
from src.data.models import Product
from src.data.processors import clean_price, clean_title
from src.utils.logger import logger
from src.utils.config import SETTINGS

class SeleniumScraper(BaseScraper):
    """Scraper for dynamic websites using the selenium-stealth library."""
    def scrape(self, query: str) -> List[Product]:
        products = []
        search_url = self.config['base_url'].format(query=query.replace(' ', '+'))
        logger.info(f"[{self.site_name}] Scraping {search_url} with FINAL stealth configuration.")

        # selenium-stealth works with a standard options object
        options = uc.ChromeOptions()
        # For debugging, we will run with a visible browser.
        # To run headless again later, add this line:
        # options.add_argument("--headless=new")

        # Give it a persistent profile directory to look more like a real user
        options.add_argument("user-data-dir=./chrome_profile")
        
        driver = None
        try:
            # Pin the driver version to match your installed Chrome browser
            driver = uc.Chrome(options=options, version_main=137, use_subprocess=True)

            # --- APPLYING THE STEALTH SETTINGS ---
            # This function from selenium-stealth applies a wide range of
            # patches to make the browser appear human.
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )
            # --- END OF STEALTH ---

            driver.get(search_url)

            # A longer, more patient random pause
            time.sleep(random.uniform(5, 10))

            try:
                # First, check for the CAPTCHA by looking for its specific input field
                captcha_input = driver.find_elements(By.ID, "captchacharacters")
                if captcha_input:
                    logger.error("CAPTCHA page detected! Cannot proceed.")
                    with open("captcha_page_final.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    return []
                
                # If no CAPTCHA, wait for the search results
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-results"]'))
                )
                logger.debug("Search results container is present.")

            except TimeoutException:
                logger.error("Timed out waiting for search results. The page is likely a different type of block page.")
                with open("block_page_final.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                return []

            # --- Parsing loop remains the same ---
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup.select(self.config['product_container'])
            logger.info(f"[{self.site_name}] Found {len(items)} potential item containers.")

            for i, item in enumerate(items, 1):
                try:
                    title_elem = item.select_one(self.config['data_selectors']['title'])
                    price_elem = item.select_one(self.config['data_selectors']['price'])
                    url_elem = item.select_one(self.config['data_selectors']['url'])

                    if not (title_elem and price_elem and url_elem):
                        continue

                    title = clean_title(title_elem.get_text(strip=True))
                    price = clean_price(price_elem.get_text(strip=True))
                    
                    if url_elem['href'].startswith('/'):
                        url = "https://www.amazon.com" + url_elem['href']
                    else:
                        continue

                    if price > 0.0 and "Sponsored" not in title and "/gp/slredirect/" not in url:
                        products.append(Product(query=query, source=self.site_name, title=title, price=price, url=url))
                        logger.debug(f"Successfully parsed item #{i}: {title[:30]}...")

                except Exception as e:
                    logger.warning(f"An error occurred parsing item #{i}: {e}")
            
            logger.info(f"Completed scrape task for '{self.site_name}', successfully processed and saved {len(products)} products.")
            return products

        except Exception as e:
            logger.error(f"[{self.site_name}] A critical error occurred: {e}", exc_info=False)
            if driver:
                try:
                    with open("critical_error_page_final.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    logger.info("Saved page source on critical error.")
                except Exception as save_e:
                    logger.error(f"Could not save page source after crash: {save_e}")
            return []
        finally:
            if driver:
                driver.quit()
                logger.debug("WebDriver has been closed.")