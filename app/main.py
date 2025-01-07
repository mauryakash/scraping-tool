from fastapi import FastAPI, Depends, HTTPException, Header
from app.scraper.scraper import Scraper
from app.db.storage import Storage
from app.db.cache import Cache
from typing import Optional

app = FastAPI()

# Static token for authentication
STATIC_TOKEN = "my_secure_token"

def verify_token(x_token: str = Header(...)):
    if x_token != STATIC_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/scrape")
async def scrape(limit: Optional[int] = None, proxy: Optional[str] = None, token: str = Depends(verify_token)):
    scraper = Scraper(limit=limit, proxy=proxy)
    scraped_data = scraper.run()

    storage = Storage()
    cache = Cache()

    count = 0
    for product in scraped_data:
        cached_price = cache.get(product['product_title'])
        if cached_price is None or cached_price != product['product_price']:
            storage.save(product)
            cache.set(product['product_title'], product['product_price'])
            count += 1

    return {"message": f"Scraped and updated {count} products."}