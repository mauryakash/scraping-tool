import httpx
from bs4 import BeautifulSoup
import os
import time

class Scraper:
    def __init__(self, limit=None, proxy=None):
        self.base_url = "https://dentalstall.com/shop/page/"
        self.limit = limit
        self.proxy = proxy
        self.retries = 3

    def fetch_page(self, url):
        for attempt in range(self.retries):
            try:
                proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
                response = httpx.get(url, proxies=proxies, timeout=10)
                response.raise_for_status()
                return response.text
            except httpx.RequestError as e:
                print(f"Request error {e}, retrying in 3 seconds...")
                time.sleep(3)
        return None

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        products = []
        for item in soup.select(".product"):  # Adjust the selector as per the site
            title = item.select_one(".product-title").get_text(strip=True)
            price = float(item.select_one(".price").get_text(strip=True).replace("$", ""))
            image_url = item.select_one("img")['src']

            # Download the image
            image_path = f"images/{title.replace(' ', '_')}.jpg"
            os.makedirs("images", exist_ok=True)
            with open(image_path, "wb") as img_file:
                img_file.write(httpx.get(image_url).content)

            products.append({
                "product_title": title,
                "product_price": price,
                "path_to_image": image_path
            })
        return products

    def run(self):
        scraped_data = []
        page = 1
        while self.limit is None or page <= self.limit:
            html = self.fetch_page(f"{self.base_url}{page}")
            if not html:
                break
            products = self.parse_page(html)
            scraped_data.extend(products)
            page += 1
        return scraped_data