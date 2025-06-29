## 1. Introduction

This document outlines the technical architecture of the E-Commerce Price Monitoring System. The system is engineered as a modular, resilient, and maintainable solution for collecting, storing, and analyzing product data from diverse web sources. The architecture prioritizes a clear separation of concerns, robust error handling, and efficient, concurrent data collection.

## 2. System Components & Design Patterns

The application is divided into several logical packages, each with a distinct responsibility. This design makes the system easy to understand, test, and extend.

### 2.1. Configuration (`config/`)

To decouple the system from hard-coded values, all settings are externalized into YAML files.

- **`settings.yaml`**: Manages global settings like database paths, logging levels, and default scraper configurations.
- **`scrapers.yaml`**: Defines the configuration for each target website. This includes the base URL, the type of scraper to use (`static`, `selenium`, `scrapy`), and the specific CSS selectors for data extraction. This declarative approach allows for easy updates when a website's layout changes.

### 2.2. Core Logic (`src/`)

This package contains the application's business logic, organized by function.

- **`scrapers/`**: This module employs a **Strategy Design Pattern**. A `BaseScraper` abstract class defines a common interface, and concrete implementations provide different scraping strategies:

  - `StaticScraper`: Uses `requests` and `BeautifulSoup4` for fast and simple HTML parsing.
  - `SeleniumScraper`: Uses `undetected-chromedriver` to control a stealthy browser, designed to handle JavaScript-heavy sites and evade bot detection.
  - `scrapy_crawler/`: A self-contained `Scrapy` project that leverages its asynchronous engine for efficient, large-scale crawling.

- **`data/`**: This module is responsible for the system's data persistence and structure.

  - `models.py`: Defines the `Product` dataclass, which acts as a standardized Data Transfer Object (DTO) throughout the application.
  - `database.py`: Encapsulates all database interactions with SQLite. It uses a context manager for safe connection handling and includes the logic for table creation and `INSERT OR IGNORE` operations to prevent data duplication.
  - `processors.py`: Provides utility functions for data cleaning and validation (e.g., converting price strings to floats).

- **`analysis/`**: This module transforms raw data into actionable insights.

  - `reports.py`: Uses `pandas` to query the database and perform statistical analysis. It then uses `matplotlib` to generate plots and `Jinja2` to render these insights into a final HTML report from a template.

- **`cli/`**: This module provides the user-facing entry point.
  - `interface.py`: Uses the `Click` library to build a professional command-line interface. It includes a **Factory Design Pattern** (`scraper_factory`) to dynamically instantiate the correct scraper object based on the configuration file. It also orchestrates the concurrent execution of scrapers using a `ThreadPoolExecutor`.

## 3. Data Flow

1.  **Initiation**: The user executes a command (e.g., `scrape --all-sites "query"`) via the CLI.
2.  **Dispatch**: The `scraper_factory` in the CLI reads the `scrapers.yaml` config and creates the appropriate scraper object for each site.
3.  **Concurrency**: A `ThreadPoolExecutor` is used to run each scraper task in a separate thread. This is ideal for I/O-bound web scraping, as it allows network requests to happen in parallel.
4.  **Execution**: Each scraper fetches and parses its target site. In case of a block (like with Amazon), the scraper's error handling identifies the issue, logs it, and exits gracefully.
5.  **Storage**: Data from successful scrapes is passed to the `Database` module for cleaning and insertion into the SQLite database. The Scrapy pipeline saves its data directly.
6.  **Reporting**: The `report` command queries the database, processes the data with `pandas`, generates plots with `matplotlib`, and renders the final `HTML` file.

## 4. Error Handling and Resilience

The system is designed to be resilient to common scraping failures.

- **HTTP Errors**: `requests` is configured to raise exceptions for non-2xx status codes.
- **Parsing Errors**: Individual item parsing is wrapped in `try...except` blocks, so a single malformed product does not halt the entire scrape.
- **Anti-Bot Detection**: The `SeleniumScraper` includes a patient waiting strategy. If the expected content does not load, it correctly assumes a block/CAPTCHA page, saves the HTML for debugging, and terminates the task gracefully without crashing the application.
- **Logging**: A comprehensive logging system records informational messages, warnings, and errors to `app.log`, providing crucial traceability for debugging.
