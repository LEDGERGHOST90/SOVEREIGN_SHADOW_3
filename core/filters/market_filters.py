import logging
from typing import Dict, Optional
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OracleMarketFilters:
    """
    ORACLE: Market Filters Module
    Fetches and interprets Fear & Greed Index and DXY (US Dollar Index) data
    to provide market sentiment and dollar strength signals.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.fear_greed_api_url = self.config.get("fear_greed_api_url", "https://api.alternative.me/fng/?limit=1")
        self.dxy_api_url = self.config.get("dxy_api_url", "https://api.stlouisfed.org/fred/series/observations") # Placeholder, real FRED API needs key
        self.fred_api_key = self.config.get("fred_api_key", "YOUR_FRED_API_KEY") # FRED API requires a key
        
        self.fear_greed_data: Optional[Dict] = None
        self.dxy_data: Optional[float] = None
        self.last_fng_fetch: Optional[datetime] = None
        self.last_dxy_fetch: Optional[datetime] = None

        logger.info("ORACLE Market Filters Module initialized.")

    def fetch_fear_greed_index(self, force_fetch: bool = False) -> Optional[Dict]:
        """
        Fetches the latest Fear & Greed Index.
        Caches data for a short period to avoid excessive API calls.
        """
        if not force_fetch and self.last_fng_fetch and (datetime.now() - self.last_fng_fetch) < timedelta(minutes=10):
            logger.debug("Using cached Fear & Greed Index data.")
            return self.fear_greed_data

        try:
            response = requests.get(self.fear_greed_api_url, timeout=5)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            if data and data.get("data"):
                self.fear_greed_data = data["data"][0]
                self.last_fng_fetch = datetime.now()
                logger.info(f"Fetched Fear & Greed Index: {self.fear_greed_data.get('value')} ({self.fear_greed_data.get('value_classification')})")
                return self.fear_greed_data
            else:
                logger.warning("Fear & Greed API returned no data.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
            return None

    def get_fear_greed_signal(self) -> str:
        """
        Interprets the Fear & Greed Index into a simple trading signal.
        """
        fng_data = self.fetch_fear_greed_index()
        if fng_data:
            value_classification = fng_data.get("value_classification")
            value = int(fng_data.get("value"))
            
            if value_classification == "Extreme Fear" and value < 10:
                return "BUY_OPPORTUNITY_EXTREME_FEAR"
            elif value_classification == "Fear" and value < 30:
                return "BUY_OPPORTUNITY_FEAR"
            elif value_classification == "Extreme Greed" and value > 90:
                return "SELL_SIGNAL_EXTREME_GREED"
            elif value_classification == "Greed" and value > 70:
                return "SELL_SIGNAL_GREED"
            else:
                return "NEUTRAL"
        return "UNKNOWN"

    def fetch_dxy_index(self, force_fetch: bool = False) -> Optional[float]:
        """
        Fetches the latest DXY (US Dollar Index) value from FRED.
        Note: A real FRED API call requires proper series_id and an API key.
        This is a placeholder for demonstration purposes.
        """
        if not self.fred_api_key or self.fred_api_key == "YOUR_FRED_API_KEY":
            logger.warning("FRED API key not set. Cannot fetch DXY.")
            return None

        if not force_fetch and self.last_dxy_fetch and (datetime.now() - self.last_dxy_fetch) < timedelta(hours=1):
            logger.debug("Using cached DXY data.")
            return self.dxy_data

        try:
            # Placeholder for actual FRED API call for DXY (e.g., DXY data series)
            # This would typically involve parameters like series_id, observation_start, api_key, file_type=json
            # For a real implementation, you'd need to consult FRED API documentation.
            # Example structure: https://api.stlouisfed.org/fred/series/observations?series_id=DTB3&api_key=abcdefg&file_type=json
            logger.info("Simulating DXY fetch. In a real scenario, this requires a FRED API key and specific series_id.")
            
            # Simulate a DXY value
            simulated_dxy = 103.5 + (datetime.now().minute % 10 - 5) * 0.1 # Some arbitrary fluctuation
            self.dxy_data = simulated_dxy
            self.last_dxy_fetch = datetime.now()
            logger.info(f"Simulated DXY Index: {self.dxy_data:.2f}")
            return self.dxy_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching DXY Index: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during DXY fetch: {e}")
            return None

    def get_dxy_strength_signal(self) -> str:
        """
        Interprets the DXY index into a dollar strength signal.
        """
        dxy_value = self.fetch_dxy_index()
        if dxy_value is not None:
            if dxy_value > 104.0:
                return "STRONG_DOLLAR_RISK_OFF"
            elif dxy_value < 102.0:
                return "WEAK_DOLLAR_RISK_ON"
            else:
                return "NEUTRAL_DOLLAR"
        return "UNKNOWN"


# Example usage (for testing)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    oracle = OracleMarketFilters()

    print("\n--- Fear & Greed Index Test ---")
    fng_data = oracle.fetch_fear_greed_index(force_fetch=True)
    if fng_data:
        print(f"Raw F&G: {fng_data}")
        print(f"F&G Signal: {oracle.get_fear_greed_signal()}")

    print("\n--- DXY Index Test ---")
    # Set a dummy FRED API key for demonstration (replace with real key for live use)
    oracle.fred_api_key = "DEMO_KEY"
    dxy_value = oracle.fetch_dxy_index(force_fetch=True)
    if dxy_value is not None:
        print(f"Raw DXY: {dxy_value:.2f}")
        print(f"DXY Signal: {oracle.get_dxy_strength_signal()}")
    else:
        print("DXY fetch failed. Check API key and configuration.")
