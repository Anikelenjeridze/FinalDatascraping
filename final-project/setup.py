from setuptools import setup, find_packages

setup(
    name="python-data-scraping-project",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
        'click',
        'Jinja2',
        'matplotlib',
        'pandas',
        'PyYAML',
        'requests',
        'selenium',
        'webdriver-manager',
        'Scrapy',
        'pytest'
    ],
    entry_points={
        'console_scripts': [
            'scraper-cli = src.cli.interface:cli',
        ],
    },
)