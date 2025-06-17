#!/usr/bin/env python3
"""
Test script to reproduce and fix the 401 error
"""

import yfinance as yf
import time
import logging

# Set up logging to see detailed errors
logging.basicConfig(level=logging.DEBUG)

def test_rapid_requests():
    """Test rapid requests that might trigger 401 errors"""
    print("Testing rapid requests that might trigger 401 errors...")
    
    # Test tickers from your CSV
    test_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META", "AMZN", "NFLX", "AMD", "INTC"]
    
    errors = []
    successes = 0
    
    for i, ticker_symbol in enumerate(test_tickers):
        try:
            print(f"Testing {ticker_symbol} ({i+1}/{len(test_tickers)})...")
            
            ticker = yf.Ticker(ticker_symbol)
            
            # Get historical data (this is what your script does)
            hist = ticker.history(period="30d")
            
            if hist.empty:
                print(f"  ✗ {ticker_symbol}: No historical data")
                continue
                
            # Get info (this is another API call that might fail)
            info = ticker.info
            
            if not info:
                print(f"  ✗ {ticker_symbol}: No info data")
                continue
                
            # Get news (this is a third API call)
            news = ticker.news
            
            print(f"  ✓ {ticker_symbol}: Success - Price: ${hist['Close'].iloc[-1]:.2f}, Company: {info.get('longName', 'Unknown')}")
            successes += 1
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.1)
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ {ticker_symbol}: Error - {error_msg}")
            errors.append((ticker_symbol, error_msg))
            
            # Check if it's a 401 error
            if "401" in error_msg:
                print(f"    🚨 401 ERROR DETECTED for {ticker_symbol}")
    
    print(f"\nResults: {successes} successes, {len(errors)} errors")
    
    if errors:
        print("\nErrors encountered:")
        for ticker, error in errors:
            print(f"  {ticker}: {error}")
            
    return len(errors) == 0

def test_with_delays():
    """Test with longer delays between requests"""
    print("\n" + "="*50)
    print("Testing with longer delays...")
    
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    errors = []
    
    for ticker_symbol in test_tickers:
        try:
            print(f"Testing {ticker_symbol} with 2s delay...")
            
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="30d")
            info = ticker.info
            
            print(f"  ✓ {ticker_symbol}: Success")
            
            # Longer delay
            time.sleep(2.0)
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ {ticker_symbol}: {error_msg}")
            errors.append((ticker_symbol, error_msg))
    
    return len(errors) == 0

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING FOR 401 ERRORS")
    print("=" * 60)
    
    # Test rapid requests
    rapid_ok = test_rapid_requests()
    
    # Test with delays
    delay_ok = test_with_delays()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"Rapid requests: {'PASS' if rapid_ok else 'FAIL'}")
    print(f"Delayed requests: {'PASS' if delay_ok else 'FAIL'}")
    
    if not rapid_ok and delay_ok:
        print("\n💡 SOLUTION: Increase delays between requests")
    elif rapid_ok:
        print("\n✓ No 401 errors detected. The issue might be intermittent.")
    else:
        print("\n❌ 401 errors persist. Need to implement additional fixes.")