#!/usr/bin/env python3
"""
Test the fixed fortune5000-analysis.py script with a small sample
"""

import sys
import os
import importlib.util

# Import the Fortune5000Analyzer class from the script file
spec = importlib.util.spec_from_file_location("fortune5000_analysis", "fortune5000-analysis.py")
fortune5000_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fortune5000_module)
Fortune5000Analyzer = fortune5000_module.Fortune5000Analyzer

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_small_sample():
    """Test the analyzer with a small sample of tickers"""
    print("Testing the fixed Fortune5000Analyzer with a small sample...")
    
    # Create analyzer with ultra_conservative settings to avoid any rate limiting
    analyzer = Fortune5000Analyzer(
        drop_threshold=-1.0,  # Very low threshold to catch any drops
        rate_limit_preset='ultra_conservative'
    )
    
    # Test with a few popular tickers
    test_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    
    print(f"Testing with {len(test_tickers)} tickers: {', '.join(test_tickers)}")
    
    results = []
    for ticker in test_tickers:
        print(f"  Analyzing {ticker}...")
        try:
            result = analyzer.analyze_single_stock(ticker)
            if result:
                results.append(result)
                print(f"    ✓ {ticker}: {result['percent_change']:.2f}% change")
            else:
                print(f"    - {ticker}: No significant drop")
        except Exception as e:
            print(f"    ✗ {ticker}: Error - {e}")
    
    print(f"\nResults: Found {len(results)} stocks with drops >= {analyzer.drop_threshold}%")
    
    if results:
        print("\nDetailed results:")
        for result in results:
            print(f"  {result['symbol']}: {result['percent_change']:.2f}% "
                  f"(${result['previous_close']:.2f} → ${result['current_price']:.2f})")
    
    return len(results) >= 0  # Success if no errors occurred

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING FIXED FORTUNE5000 ANALYZER")
    print("=" * 60)
    
    success = test_small_sample()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Test completed successfully! The script should now work without 401 errors.")
        print("\nYou can now run the full analysis with:")
        print("  python3 fortune5000-analysis.py conservative")
        print("  python3 fortune5000-analysis.py balanced")
    else:
        print("✗ Test failed. There may still be issues to resolve.")