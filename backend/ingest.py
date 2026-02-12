"""
Web scraping module for endurance racing live timing data.
Supports WEC (Al Kamel Systems) and IMSA timing pages.
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from typing import List, Dict, Optional
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WECScraper:
    """Scraper for WEC timing data from Al Kamel Systems"""
    
    def __init__(self, url: str = None):
        self.url = url or os.getenv("WEC_TIMING_URL", "https://timing.71wytham.org.uk/")
        self.session = None
        self.user_agent = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    async def init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            headers = {"User-Agent": self.user_agent}
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def fetch_live_data(self) -> Dict:
        """
        Fetch live timing data from WEC timing page.
        Returns structured data with positions, lap times, etc.
        """
        await self.init_session()
        
        try:
            async with self.session.get(self.url, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch WEC data: {response.status}")
                    return {}
                
                html = await response.text()
                return self._parse_wec_html(html)
        
        except asyncio.TimeoutError:
            logger.error("Timeout fetching WEC data")
            return {}
        except Exception as e:
            logger.error(f"Error fetching WEC data: {e}")
            return {}
    
    def _parse_wec_html(self, html: str) -> Dict:
        """Parse WEC timing HTML"""
        soup = BeautifulSoup(html, 'lxml')
        
        data = {
            "series": "WEC",
            "timestamp": datetime.utcnow().isoformat(),
            "cars": []
        }
        
        # This is a placeholder - actual parsing depends on Al Kamel's HTML structure
        # You'll need to inspect the live timing page to get the correct selectors
        
        try:
            # Example parsing (adjust selectors based on actual page structure)
            timing_rows = soup.select('.timing-row')  # Adjust selector
            
            for row in timing_rows:
                car_data = {
                    "car_number": self._safe_extract(row, '.car-number'),
                    "team_name": self._safe_extract(row, '.team-name'),
                    "car_class": self._safe_extract(row, '.class'),
                    "position": self._safe_extract_int(row, '.position'),
                    "laps_completed": self._safe_extract_int(row, '.laps'),
                    "last_lap_time": self._safe_extract_float(row, '.last-lap'),
                    "best_lap_time": self._safe_extract_float(row, '.best-lap'),
                    "gap_to_leader": self._safe_extract_gap(row, '.gap'),
                    "in_pit": 'pit' in row.get('class', [])
                }
                
                data["cars"].append(car_data)
        
        except Exception as e:
            logger.error(f"Error parsing WEC HTML: {e}")
        
        return data
    
    def _safe_extract(self, element, selector: str) -> Optional[str]:
        """Safely extract text from element"""
        try:
            found = element.select_one(selector)
            return found.text.strip() if found else None
        except:
            return None
    
    def _safe_extract_int(self, element, selector: str) -> Optional[int]:
        """Safely extract integer from element"""
        text = self._safe_extract(element, selector)
        try:
            return int(text) if text else None
        except:
            return None
    
    def _safe_extract_float(self, element, selector: str) -> Optional[float]:
        """Safely extract float from element (lap time)"""
        text = self._safe_extract(element, selector)
        try:
            # Handle formats like "1:23.456" or "83.456"
            if ':' in text:
                parts = text.split(':')
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            return float(text)
        except:
            return None
    
    def _safe_extract_gap(self, element, selector: str) -> Optional[float]:
        """Safely extract gap time"""
        text = self._safe_extract(element, selector)
        if not text or text == 'Leader':
            return 0.0
        try:
            # Handle "+1 LAP" or "+2.345"
            if 'LAP' in text.upper():
                laps = int(text.split()[0].replace('+', ''))
                return laps * 100  # Approximate (100s per lap)
            return float(text.replace('+', ''))
        except:
            return None


class IMSAScraper:
    """Scraper for IMSA timing data using Selenium (for dynamic content)"""
    
    def __init__(self, url: str = None):
        self.url = url or os.getenv("IMSA_TIMING_URL", "https://www.imsa.com/scoring/")
        self.driver = None
    
    def init_driver(self):
        """Initialize Selenium WebDriver"""
        if not self.driver:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'user-agent={os.getenv("USER_AGENT")}')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def close(self):
        """Close Selenium driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def fetch_live_data(self) -> Dict:
        """
        Fetch live timing data from IMSA page.
        Returns structured data with positions, lap times, etc.
        """
        self.init_driver()
        
        try:
            self.driver.get(self.url)
            
            # Wait for timing table to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "timing-table"))
            )
            
            html = self.driver.page_source
            return self._parse_imsa_html(html)
        
        except Exception as e:
            logger.error(f"Error fetching IMSA data: {e}")
            return {}
    
    def _parse_imsa_html(self, html: str) -> Dict:
        """Parse IMSA timing HTML"""
        soup = BeautifulSoup(html, 'lxml')
        
        data = {
            "series": "IMSA",
            "timestamp": datetime.utcnow().isoformat(),
            "cars": []
        }
        
        # Placeholder parsing - adjust based on actual IMSA page structure
        try:
            timing_rows = soup.select('.timing-row')  # Adjust selector
            
            for row in timing_rows:
                car_data = {
                    "car_number": self._safe_extract(row, '.car-number'),
                    "team_name": self._safe_extract(row, '.team'),
                    "car_class": self._safe_extract(row, '.class'),
                    "position": self._safe_extract_int(row, '.pos'),
                    "laps_completed": self._safe_extract_int(row, '.laps'),
                    "last_lap_time": self._safe_extract_float(row, '.last'),
                    "best_lap_time": self._safe_extract_float(row, '.best'),
                }
                
                data["cars"].append(car_data)
        
        except Exception as e:
            logger.error(f"Error parsing IMSA HTML: {e}")
        
        return data
    
    def _safe_extract(self, element, selector: str) -> Optional[str]:
        """Safely extract text from element"""
        try:
            found = element.select_one(selector)
            return found.text.strip() if found else None
        except:
            return None
    
    def _safe_extract_int(self, element, selector: str) -> Optional[int]:
        """Safely extract integer"""
        text = self._safe_extract(element, selector)
        try:
            return int(text) if text else None
        except:
            return None
    
    def _safe_extract_float(self, element, selector: str) -> Optional[float]:
        """Safely extract float (lap time)"""
        text = self._safe_extract(element, selector)
        try:
            if ':' in text:
                parts = text.split(':')
                return int(parts[0]) * 60 + float(parts[1])
            return float(text)
        except:
            return None


class DataIngestionManager:
    """Manages data ingestion from multiple sources"""
    
    def __init__(self, series: str = "WEC"):
        self.series = series
        self.scraper = None
        self.is_running = False
        
        if series == "WEC":
            self.scraper = WECScraper()
        elif series == "IMSA":
            self.scraper = IMSAScraper()
    
    async def start_ingestion(self, callback):
        """Start continuous data ingestion"""
        self.is_running = True
        interval = int(os.getenv("SCRAPE_INTERVAL", 10))
        
        logger.info(f"Starting {self.series} data ingestion (interval: {interval}s)")
        
        while self.is_running:
            try:
                if self.series == "WEC":
                    data = await self.scraper.fetch_live_data()
                else:
                    data = self.scraper.fetch_live_data()
                
                if data and data.get("cars"):
                    await callback(data)
                    logger.info(f"Ingested data for {len(data['cars'])} cars")
                
                await asyncio.sleep(interval)
            
            except Exception as e:
                logger.error(f"Error in ingestion loop: {e}")
                await asyncio.sleep(interval)
    
    async def stop_ingestion(self):
        """Stop data ingestion"""
        self.is_running = False
        
        if self.series == "WEC":
            await self.scraper.close()
        else:
            self.scraper.close()
        
        logger.info(f"Stopped {self.series} data ingestion")
