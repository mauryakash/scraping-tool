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
        # Add diagnostic print statements
        soup = BeautifulSoup(html, "html.parser")
        
        # Debug: Print the entire HTML to verify content
        print(f"HTML Length: {len(html)}")
        
        # Debug: Print all available classes
        print("Available Classes:")
        for cls in set(
            [class_ for elem in soup.find_all() for class_ in elem.get('class', [])]
        ):
            print(cls)
        
        # Debug: Print the number of product elements found
        product_items = soup.select(".product")
        print(f"Number of product items found: {len(product_items)}")
        
        products = []
        for item in product_items:
            # Add more robust error handling
            try:
                # Try multiple selectors
                title_elem = (
                    item.select_one(".product-title") or 
                    item.select_one(".woocommerce-loop-product__title") or 
                    item.find('h2')
                )
                
                if not title_elem:
                    print("No title element found for this item")
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # Similar robust approach for other elements
                price_elem = (
                    item.select_one(".price") or 
                    item.select_one(".woocommerce-Price-amount")
                )
                
                if not price_elem:
                    print("No price element found for this item")
                    continue
                
                price_text = price_elem.get_text(strip=True).replace("$", "").replace(",", "")
                price = float(price_text)
                
                image_elem = item.select_one("img")
                if not image_elem:
                    print("No image found for this item")
                    continue
                
                image_url = image_elem.get('src') or image_elem.get('data-src')
                
                # Sanitize filename
                safe_title = "".join(
                    [c for c in title if c.isalnum() or c in (' ', '_')]
                ).rstrip()
                
                image_path = f"images/{safe_title[:50]}.jpg"
                os.makedirs("images", exist_ok=True)
                
                try:
                    with open(image_path, "wb") as img_file:
                        img_file.write(httpx.get(image_url).content)
                except Exception as img_error:
                    print(f"Image download failed: {img_error}")
                    image_path = None
                
                products.append({
                    "product_title": title,
                    "product_price": price,
                    "path_to_image": image_path
                })
            
            except Exception as e:
                print(f"Error processing item: {e}")
        
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