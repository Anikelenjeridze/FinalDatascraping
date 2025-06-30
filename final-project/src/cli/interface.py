# src/cli/interface.py (THE FINAL GUARANTEED VERSION)

import click
import concurrent.futures
import subprocess
from pathlib import Path

# No complex sys.path manipulation is needed.
from src.scrapers.static_scraper import StaticScraper
from src.scrapers.selenium_scraper import SeleniumScraper
from src.data.database import Database
from src.utils.config import SCRAPERS_CONFIG
from src.utils.logger import logger
from src.analysis import reports

# Design Pattern: Factory
def scraper_factory(site_name: str):
    config = SCRAPERS_CONFIG.get(site_name)
    if not config:
        raise ValueError(f"No configuration found for site: {site_name}")
    
    scraper_type = config.get("type")
    if scraper_type == "static":
        return StaticScraper(site_name, config)
    elif scraper_type == "selenium":
        return SeleniumScraper(site_name, config)
    elif scraper_type == "scrapy":
        return "scrapy"
    else:
        raise ValueError(f"Unknown scraper type: {scraper_type}")

# Simplified scrape task function
def run_scrape_task(site: str, query: str):
    logger.info(f"Starting scrape task for '{site}' with query '{query}'")
    try:
        scraper_or_type = scraper_factory(site)

        if scraper_or_type == "scrapy":
            # Define the exact directory where `scrapy.cfg` is located.
            # This path is robust and will always be correct.
            scrapy_project_dir = Path(__file__).resolve().parent.parent / 'scrapers' / 'scrapy_crawler'
            
            command = ["scrapy", "crawl", "ebay", "-a", f"query={query}"]

            # Run the command FROM that directory and capture all output.
            result = subprocess.run(
                command,
                cwd=scrapy_project_dir,
                check=True,      # This will raise an error if Scrapy fails
                capture_output=True, # This captures stdout and stderr
                text=True            # This ensures output is decoded as text
            )
            
            # Log Scrapy's output for verification. If it succeeds, you'll see it here.
            logger.info(f"[Scrapy STDOUT]:\n{result.stdout}")
            if result.stderr:
                logger.warning(f"[Scrapy STDERR]:\n{result.stderr}")

            return [] # Data is saved by the pipeline
        else:
            # This is for Selenium and Static scrapers
            return scraper_or_type.scrape(query)

    except subprocess.CalledProcessError as e:
        logger.error(f"Scrapy crawl failed with exit code {e.returncode}.")
        logger.error(f"This is the REAL error from Scrapy: \n---_BEGIN_SCRAPY_ERROR_---\n{e.stderr}\n---_END_SCRAPY_ERROR_---")
        return []
    except Exception as e:
        logger.error(f"Failed to scrape '{site}': {e}", exc_info=True)
        return []


# The rest of the file (CLI commands) is largely the same, but simplified for clarity.
@click.group()
def cli():
    """A CLI for the Multi-Source Data Collection System."""
    pass

@cli.command()
@click.option('--site', '-s', type=click.Choice(SCRAPERS_CONFIG.keys()), help='The specific site to scrape.')
@click.option('--all-sites', is_flag=True, help='Scrape all configured sites.')
@click.argument('query')
def scrape(site, all_sites, query):
    if not site and not all_sites:
        click.echo("Error: Please specify a site with --site or use --all-sites.")
        return

    sites_to_scrape = list(SCRAPERS_CONFIG.keys()) if all_sites else [site]
    
    with Database() as db: # Ensure database is ready
        pass

    all_products = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sites_to_scrape)) as executor:
        future_to_site = {executor.submit(run_scrape_task, s, query): s for s in sites_to_scrape}
        for future in concurrent.futures.as_completed(future_to_site):
            site_name = future_to_site[future]
            try:
                products = future.result()
                if products:
                    all_products.extend(products)
            except Exception as exc:
                logger.error(f"'{site_name}' task generated an exception: {exc}")

    if all_products:
        with Database() as db:
            db.save_products(all_products)
    
    click.echo("Scraping process finished. Check app.log for details.")

@cli.command()
@click.argument('query')
def report(query):
    click.echo(f"Generating report for query: {query}")
    report_path = reports.generate_report(query)
    if report_path:
        click.echo(f"Report successfully generated at: {report_path}")
    else:
        click.echo(f"Could not generate report. No data found for query '{query}'.")