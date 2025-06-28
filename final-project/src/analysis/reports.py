import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from src.utils.config import SETTINGS
from src.utils.logger import logger
from datetime import datetime

def generate_report(query: str):
    """Generates an HTML report with data analysis and visualizations."""
    logger.info(f"Generating report for query: {query}")
    
    # 1. Fetch data from database
    db_path = SETTINGS['database']['path']
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM products WHERE query = '{query}'", conn)
    conn.close()

    if df.empty:
        logger.warning(f"No data found for query '{query}'. Report not generated.")
        return None

    # 2. Perform analysis
    analysis = {
        "total_records": len(df),
        "avg_price": f"${df['price'].mean():.2f}",
        "min_price_item": df.loc[df['price'].idxmin()].to_dict(),
        "max_price_item": df.loc[df['price'].idxmax()].to_dict(),
        "price_by_source": df.groupby('source')['price'].mean().round(2).to_dict()
    }

    # 3. Create visualization
    plt.figure(figsize=(10, 6))
    df.groupby('source')['price'].mean().plot(kind='bar', color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    plt.title(f'Average Price for "{query}" by Retailer')
    plt.ylabel('Average Price ($)')
    plt.xlabel('Retailer')
    plt.xticks(rotation=0)
    plt.tight_layout()
    
    reports_dir = Path(SETTINGS['output_paths']['reports'])
    reports_dir.mkdir(exist_ok=True)
    plot_path = reports_dir / f"{query.replace(' ', '_')}_price_comparison.png"
    plt.savefig(plot_path)
    logger.info(f"Generated plot: {plot_path}")
    
    # 4. Render HTML report using Jinja2
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'templates'))
    template = env.get_template('report_template.html')

    html_content = template.render(
        query=query,
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        analysis=analysis,
        plot_path=plot_path.name, # Use relative path for HTML
        products_table=df.to_html(classes='table table-striped', index=False)
    )

    report_filename = reports_dir / f"report_{query.replace(' ', '_')}.html"
    with open(report_filename, 'w') as f:
        f.write(html_content)
        
    logger.info(f"Successfully generated HTML report: {report_filename}")
    return str(report_filename)