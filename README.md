# FastAPI Scraping Tool

## Overview
This project is a web scraping tool built with FastAPI that extracts product details (title, price, and image) from the Dental Stall website. The scraped data is saved locally in a JSON database, with a caching mechanism to avoid unnecessary updates.

## Features
- Authentication using a static token.
- Configurable page limits and optional proxy support.
- Retry mechanism for failed requests.
- Local image storage for scraped products.
- In-memory caching using Redis.

## Requirements
- Python 3.9+
- Redis

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start a Redis server:
   ```bash
   redis-server
   ```
4. Run the FastAPI app:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Example Usage
To scrape the first 5 pages with a static token:
```bash
curl -X POST "http://127.0.0.1:8000/scrape?limit=5" -H "x-token: my_secure_token"
```
