# Project Contributions

This project was developed by a single student, [Your Name], as a final project for a Python Data Scraping course. As the sole contributor, I was responsible for all aspects of the project's lifecycle, from initial design and architecture to implementation, testing, and documentation.

### Summary of Contributions

My contributions can be broken down into the following key areas:

1.  **Core Architecture and Design**

    - Designed the modular project structure with a clear separation of concerns (`config`, `src`, `tests`).
    - Planned the data flow from collection to reporting.
    - Designed the SQLite database schema, including the `UNIQUE` constraint for data deduplication.
    - Selected and integrated all key technologies, including `Click`, `Scrapy`, `Selenium`, and `pandas`.

2.  **Scraper Implementation**

    - Implemented the **static scraper** using `requests` and `BeautifulSoup` to handle the Best Buy website.
    - Built and configured the **Scrapy project** for asynchronous crawling of eBay, including the item pipeline for direct database insertion.
    - Developed the **dynamic scraper** using `Selenium` and `undetected-chromedriver` to tackle Amazon. This involved an iterative debugging process to handle version mismatches and implement advanced anti-bot evasion techniques.
    - Engineered the graceful failure mechanism for the Amazon scraper to correctly identify and report when it is blocked.

3.  **Backend and Data Processing**

    - Wrote the data processing functions to clean and standardize scraped data.
    - Developed the concurrent execution engine using `concurrent.futures.ThreadPoolExecutor` to run scrapers in parallel.
    - Implemented the entire reporting pipeline, using `pandas` for data analysis, `matplotlib` for generating charts, and `Jinja2` for rendering the final HTML report.

4.  **User Interface**

    - Built the professional command-line interface (CLI) using the `Click` library, providing users with clear and easy-to-use commands.

5.  **Testing and Documentation**
    - Wrote unit tests using `pytest` to ensure the reliability of the data processing and database modules.
    - Authored all project documentation, including the `README.md`, `ARCHITECTURE.md`, and this `CONTRIBUTIONS.md` file.

Through this project, I have demonstrated a comprehensive understanding of various data scraping techniques, software architecture, and the real-world challenges involved in building a resilient data collection system.
