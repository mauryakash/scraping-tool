import httpx
from bs4 import BeautifulSoup
import os
import re
import time

class Scraper:
    def __init__(self, limit=None, proxy=None):
        self.base_url = "https://dentalstall.com/shop/page/"
        self.home_url = "https://dentalstall.com/shop"
        self.limit = limit
        self.proxy = proxy
        self.retries = 3

    def fetch_page(self, url):
        for attempt in range(self.retries):
            try:
            # Updated proxy configuration
                client_args = {
                    "timeout": httpx.Timeout(10.0),
                    "follow_redirects": True
                }
                
                # If proxy is set, add it to the client configuration
                if self.proxy:
                    client_args['proxies'] = {
                        'http://': self.proxy,
                        'https://': self.proxy
                    }

                with httpx.Client(**client_args) as client:
                    response = client.get(url)
                    response.raise_for_status()
                    return response.text
            except httpx.RequestError as e:
                print(f"Request error {e}, retrying in 3 seconds...")
            time.sleep(3)
        return None


    def parse_page(self, html):
        products = []
        soup = BeautifulSoup(html, 'html.parser')

        # Dynamically detect product elements based on heuristics
        product_elements = soup.find_all(lambda tag: tag.name == 'div' and tag.find('img'))

        for product in product_elements:
            # Attempt to locate title, price, and image
            title_element = product.find(lambda tag: tag.name in ['h2', 'h3', 'h4'] and tag.get_text(strip=True))
            price_element = product.find(lambda tag: tag.name == 'span' and re.search(r'\d+', tag.get_text(strip=True)))
            image_element = product.find('img')

            if title_element and price_element and image_element:
                title = title_element.get_text(strip=True)
                price_text = price_element.get_text(strip=True)
                image_url = image_element['src']

                # Extract numeric price
                price_match = re.search(r'[\d.,]+', price_text)
                price = float(price_match.group().replace(',', '')) if price_match else 0.0

                products.append({
                    "product_title": title,
                    "product_price": price,
                    "path_to_image": image_url
                })

        return products

    def run(self):
        scraped_data = []

        # Scrape the home page first
        home_html = self.fetch_page(self.home_url)
        if home_html:
            scraped_data.extend(self.parse_page(home_html))

        # Scrape paginated results
        page = 1
        while self.limit is None or page <= self.limit:
            html = self.fetch_page(f"{self.base_url}{page}")
            if not html:
                break
            products = self.parse_page(html)
            scraped_data.extend(products)
            page += 1

        return scraped_data