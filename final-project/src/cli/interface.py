import click
import concurrent.futures
import subprocess
import os
from src.scrapers.static_scraper import StaticScraper
from src.scrapers.selenium_scraper import SeleniumScraper
from src.data.database import Database
from src.utils.config import SCRAPERS_CONFIG
from src.utils.logger import logger
from src.analysis import reports

# Design Pattern: Factory
def scraper_factory(site_name: str):
    """Factory function to create scraper instances."""
    config = SCRAPERS_CONFIG.get(site_name)
    if not config:
        raise ValueError(f"No configuration found for site: {site_name}")
    
    scraper_type = config.get("type")
    if scraper_type == "static":
        return StaticScraper(site_name, config)
    elif scraper_type == "selenium":
        return SeleniumScraper(site_name, config)
    elif scraper_type == "scrapy":
        # Scrapy is handled differently, via subprocess
        return "scrapy"
    else:
        raise ValueError(f"Unknown scraper type: {scraper_type}")

def run_scrape_task(site: str, query: str):
    """Wrapper function for running a single scraper task."""
    logger.info(f"Starting scrape task for '{site}' with query '{query}'")
    try:
        scraper = scraper_factory(site)
        if scraper == "scrapy":
            # Run Scrapy spider as a subprocess from the project root
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            command = [
                "scrapy", "crawl", "ebay", "-a", f"query={query}",
                "-s", "LOG_LEVEL=INFO"
            ]
            # Change directory to where scrapy.cfg is located
            scrapy_dir = os.path.join(project_root, 'src', 'scrapers', 'scrapy_crawler')
            subprocess.run(command, cwd=scrapy_dir, check=True)
            logger.info(f"Scrapy crawl for '{site}' completed.")
            return [] # Data is saved by Scrapy pipeline
        else:
            products = scraper.scrape(query)
            logger.info(f"Completed scrape task for '{site}', found {len(products)} products.")
            return products
    except Exception as e:
        logger.error(f"Failed to scrape '{site}': {e}", exc_info=True)
        return []

@click.group()
def cli():
    """A CLI for the Multi-Source Data Collection System."""
    pass

@cli.command()
@click.option('--site', '-s', type=click.Choice(SCRAPERS_CONFIG.keys()), help='The specific site to scrape.')
@click.option('--all-sites', is_flag=True, help='Scrape all configured sites.')
@click.argument('query')
def scrape(site, all_sites, query):
    """Scrape product data from e-commerce sites."""
    if not site and not all_sites:
        click.echo("Error: Please specify a site with --site or use --all-sites.")
        return

    sites_to_scrape = list(SCRAPERS_CONFIG.keys()) if all_sites else [site]
    all_products = []

    with Database() as db: # Ensure table exists before scraping
        pass 

    # Use ThreadPoolExecutor for concurrent scraping
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sites_to_scrape)) as executor:
        future_to_site = {executor.submit(run_scrape_task, s, query): s for s in sites_to_scrape}
        for future in concurrent.futures.as_completed(future_to_site):
            site_name = future_to_site[future]
            try:
                products = future.result()
                if products: # Scrapy returns empty list, its pipeline saves to DB
                    all_products.extend(products)
            except Exception as exc:
                logger.error(f"'{site_name}' generated an exception: {exc}")

    if all_products:
        with Database() as db:
            db.save_products(all_products)
    
    click.echo("Scraping process finished. Check app.log for details.")

@cli.command()
@click.argument('query')
def report(query):
    """Generate an HTML analysis report for a given query."""
    click.echo(f"Generating report for query: {query}")
    report_path = reports.generate_report(query)
    if report_path:
        click.echo(f"Report successfully generated at: {report_path}")
    else:
        click.echo(f"Could not generate report. No data found for query '{query}'.")