# Python Data Scraping Final Project: E-Commerce Price Monitor

This project is a multi-source data collection system built as the final project for a Python Data Scraping course. It implements **Option A: The E-Commerce Price Monitoring System**, designed to scrape product information from various e-commerce websites, store the data, and generate analytical reports.

The system targets Best Buy, eBay, and Amazon, employing different scraping techniques appropriate for each site's complexity.

## Features

- **Multi-Source Scraping**: Concurrently collects data from Best Buy, eBay, and Amazon.
- **Hybrid Scraping Techniques**:
  - **Static Scraping**: Uses `requests` and `BeautifulSoup4` for the server-rendered Best Buy website.
  - **Framework-Based Crawling**: Implements a full `Scrapy` project for efficient, asynchronous crawling of eBay.
  - **Advanced Dynamic Scraping**: Leverages `Selenium` with `undetected-chromedriver` to handle JavaScript-heavy sites and advanced anti-bot measures.
- **Robust Anti-Bot Handling**: The system is designed to be resilient. It successfully bypasses basic protections and, in the case of Amazon's advanced blocking, it correctly identifies the block, logs the event, and exits gracefully without crashing the application.
- **Concurrent Execution**: Employs `concurrent.futures.ThreadPoolExecutor` to run all scrapers simultaneously, significantly reducing total runtime.
- **Persistent Data Storage**: Persists collected data in a `SQLite` database, automatically creating the schema and preventing duplicate entries using a `UNIQUE` constraint.
- **Data Processing & Analysis**: Features a data cleaning pipeline to standardize fields like price. It uses `pandas` for statistical analysis and `matplotlib` for data visualization.
- **Automated Reporting**: Generates comprehensive `HTML` reports with summary statistics, charts, and a full data table using a `Jinja2` template.
- **Professional Command-Line Interface (CLI)**: A user-friendly CLI built with `Click` provides easy control over scraping and reporting tasks.
- **Configuration-Driven Design**: Key settings like URLs, CSS selectors, and file paths are externalized to `YAML` files for easy maintenance and updates.

## Project Structure

Use code with caution.
Markdown
final-project/
|-- config/
| |-- settings.yaml
| -- scrapers.yaml |-- data_output/ | |-- reports/ |-- product_prices.db
|-- docs/
| |-- architecture.md
| |-- user_guide.md
| -- CONTRIBUTIONS.md |-- src/ | |-- analysis/ | |-- cli/ | |-- data/ | |-- scrapers/ |-- utils/
|-- tests/
| |-- unit/
|-- main.py
|-- requirements.txt
|-- README.md
`-- setup.py
Generated code

## Setup and Installation

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/Anikelenjeridze/FinalDatascraping.git
    cd final-project
    ```

2.  **Create and Activate a Virtual Environment:**

    - On Windows (PowerShell):
      ```powershell
      python -m venv venv
      .\venv\Scripts\Activate.ps1
      ```
    - On macOS/Linux:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **Install Dependencies:**
    This project's dependencies are listed in `requirements.txt` and are compatible with Python 3.10+.
    ```bash
    pip install -r requirements.txt
    ```

## Usage Instructions

The application is controlled via the command line.

### 1. Scrape Data

You can scrape a single site or all configured sites. Data is saved to `data_output/product_prices.db`.

**Scrape all sites concurrently:**

```bash
python main.py scrape --all-sites "RTX 4070"
python main.py scrape --site amazon "iPhone 15"
python main.py scrape --site ebay "Playstation 5"
```
