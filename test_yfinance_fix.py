#!/usr/bin/env python3
"""
Test script to verify yfinance 401 error fix
"""

import yfinance as yf
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

def test_basic_yfinance():
    """Test basic yfinance functionality"""
    print("Testing basic yfinance...")
    try:
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d")
        print(f"✓ Basic test passed - got {len(hist)} days of data")
        return True
    except Exception as e:
        print(f"✗ Basic test failed: {e}")
        return False

def test_with_session():
    """Test yfinance with custom session and headers"""
    print("\nTesting with custom session...")
    try:
        # Create a session with proper headers
        session = requests.Session()
        
        # Add headers to mimic a real browser
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Add retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Test with session
        ticker = yf.Ticker("AAPL", session=session)
        hist = ticker.history(period="5d")
        info = ticker.info
        
        print(f"✓ Session test passed - got {len(hist)} days of data")
        print(f"✓ Info test passed - company: {info.get('longName', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"✗ Session test failed: {e}")
        return False

def test_multiple_tickers():
    """Test multiple tickers with delays"""
    print("\nTesting multiple tickers with delays...")
    try:
        tickers = ["AAPL", "MSFT", "GOOGL"]
        
        for ticker_symbol in tickers:
            print(f"  Testing {ticker_symbol}...")
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="2d")
            
            if len(hist) > 0:
                print(f"    ✓ {ticker_symbol}: ${hist['Close'].iloc[-1]:.2f}")
            else:
                print(f"    ✗ {ticker_symbol}: No data")
            
            # Small delay between requests
            time.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"✗ Multiple ticker test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("YFINANCE 401 ERROR DIAGNOSTIC TEST")
    print("=" * 50)
    
    # Run tests
    basic_ok = test_basic_yfinance()
    session_ok = test_with_session()
    multiple_ok = test_multiple_tickers()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Basic test: {'PASS' if basic_ok else 'FAIL'}")
    print(f"Session test: {'PASS' if session_ok else 'FAIL'}")
    print(f"Multiple ticker test: {'PASS' if multiple_ok else 'FAIL'}")
    
    if all([basic_ok, session_ok, multiple_ok]):
        print("\n✓ All tests passed! yfinance is working correctly.")
    else:
        print("\n✗ Some tests failed. Need to implement fixes.")