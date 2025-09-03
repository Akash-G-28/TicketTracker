"""
scraper.py
Web scraper for monitoring BookMyShow movie ticket availability.
"""

import requests
import logging
import time
from bs4 import BeautifulSoup
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class BookMyShowScraper:
    def __init__(self):
        """Initialize scraper with headers + session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                      'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
        })
        self.last_request_time = 0
        self.min_request_interval = 2  # seconds

    def _rate_limit(self) -> None:
        """Enforce delay between requests"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            logger.info(f"Sleeping {sleep_time:.2f}s for rate limiting")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def check_ticket_availability(self, url: str) -> Dict[str, any]:
        """Check if tickets are available on given BookMyShow URL."""
        result = {
            'available': False,
            'status': 'Unknown',
            'error': None,
            'title': 'Unknown Movie',
            'url': url
        }

        try:
            self._rate_limit()
            logger.info(f"Checking tickets at: {url}")

            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')

            # Extract title
            for sel in ['h1[data-testid="movie-title"]', 'h1.movie-title', '.movie-name h1', 'h1']:
                el = soup.select_one(sel)
                if el:
                    result['title'] = el.get_text(strip=True)
                    break

            # Look for booking indicators
            booking_indicators = ['Book tickets', 'Book now', 'Buy tickets', 'Select seats']
            text = soup.get_text().lower()

            if any(ind.lower() in text for ind in booking_indicators):
                result['available'] = True
                result['status'] = "Tickets available"
                return result

            for btn in soup.find_all(['button', 'a']):
                btn_text = btn.get_text(strip=True)
                if any(ind.lower() in btn_text.lower() for ind in booking_indicators):
                    result['available'] = True
                    result['status'] = f"Booking button found: {btn_text}"
                    return result

            # Check unavailable indicators
            unavailable = ['sold out', 'not available', 'coming soon', 'no shows available']
            if any(ind in text for ind in unavailable):
                result['status'] = "Not available"
                return result

            result['status'] = "No clear booking indicators found"
        except requests.RequestException as e:
            result['status'] = "Request failed"
            result['error'] = str(e)
        except Exception as e:
            result['status'] = "Scraping failed"
            result['error'] = str(e)

        return result

    def get_movie_info(self, url: str) -> Optional[Dict[str, str]]:
        """Extract title, genre, rating if available."""
        try:
            self._rate_limit()
            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, 'html.parser')

            info = {}
            title = soup.select_one('h1[data-testid="movie-title"], h1.movie-title, h1')
            if title: info['title'] = title.get_text(strip=True)
            genre = soup.select_one('.genre, .movie-genre')
            if genre: info['genre'] = genre.get_text(strip=True)
            rating = soup.select_one('.rating, .movie-rating')
            if rating: info['rating'] = rating.get_text(strip=True)

            return info or None
        except Exception as e:
            logger.error(f"Error extracting info from {url}: {e}")
            return None
