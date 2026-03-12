"""
API Handler for CricketData.org
Handles all API calls to fetch live cricket data
"""

import logging
import requests
import pandas as pd
from typing import Dict, List, Optional, Tuple
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class CricketDataAPI:
    """Handler for CricketData.org API"""
    
    BASE_URL = "https://api.cricapi.com/v1"
    
    def __init__(self, api_key: str):
        """Initialize API handler with API key"""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})
        self.last_request_time = 0.0
        self.min_request_interval = 1  # Minimum 1 second between requests
    
    def _rate_limit(self) -> None:
        """Implement rate limiting to avoid overwhelming the API"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with error handling"""
        self._rate_limit()
        
        if params is None:
            params = {}
        
        # Pass API key as query param (required by cricapi.com API contract)
        params['apikey'] = self.api_key
        
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('data', data)
            else:
                logger.warning("API Error: %s - %s", data.get('status'), data.get('info', 'Unknown error'))
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error("Request failed: %s", e)
            return None
    
    def get_current_matches(self) -> Optional[List[Dict]]:
        """Fetch current/recent matches"""
        return self._make_request('currentMatches')
    
    def get_match_info(self, match_id: str) -> Optional[Dict]:
        """Fetch detailed match information"""
        return self._make_request('match_info', {'id': match_id})
    
    def get_player_finder(self, search_term: str) -> Optional[List[Dict]]:
        """Search for players by name"""
        return self._make_request('players', {'search': search_term})
    
    def check_api_status(self) -> Tuple[bool, str]:
        """Check if API is accessible"""
        try:
            data = self._make_request('currentMatches', {'offset': 0})
            if data is not None:
                return True, "🟢 API Connected"
            else:
                return False, "🔴 API Error"
        except:
            return False, "🔴 API Offline"
    
    def check_connectivity(self) -> Tuple[bool, str]:
        """Quick connectivity test — alias kept for backwards compat."""
        return self.check_api_status()
