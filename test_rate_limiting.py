#!/usr/bin/env python3
"""
Test script to verify rate limiting is working properly.
Tests with a small subset of stocks to validate the implementation.
"""

import sys
import time
from fortune5000_analysis import Fortune5000Analyzer
from rate_limit_config import get_config, print_config_info
import logging

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rate_limiting(preset='balanced', num_stocks=10):
    """
    Test rate limiting with a small subset of stocks.
    
    Args:
        preset: Rate limiting preset to test
        num_stocks: Number of stocks to test with
    """
    print(f"Testing rate limiting with '{preset}' preset")
    print(f"Testing with {num_stocks} stocks")
    print("=" * 50)
    
    # Create analyzer with test configuration
    analyzer = Fortune5000Analyzer(drop_threshold=-0.1, rate_limit_preset=preset)  # Very low threshold to catch more stocks
    
    # Get a small subset of tickers for testing
    all_tickers = analyzer.get_fortune5000_tickers()
    if not all_tickers:
        print("❌ Failed to load tickers")
        return False
    
    test_tickers = all_tickers[:num_stocks]
    print(f"Testing with tickers: {test_tickers}")
    
    # Test single stock analysis
    print("\n1. Testing single stock analysis...")
    start_time = time.time()
    
    test_ticker = test_tickers[0]
    result = analyzer.analyze_single_stock(test_ticker)
    
    elapsed = time.time() - start_time
    print(f"   Single stock analysis took {elapsed:.2f} seconds")
    
    if result:
        print(f"   ✅ Successfully analyzed {test_ticker}")
        print(f"   Company: {result.get('company_name', 'Unknown')}")
        print(f"   Price change: {result.get('percent_change', 0):.2f}%")
    else:
        print(f"   ℹ️  {test_ticker} didn't meet drop threshold or had no data")
    
    # Test batch processing
    print(f"\n2. Testing batch processing with {len(test_tickers)} stocks...")
    start_time = time.time()
    
    batch_results = analyzer.process_batch(test_tickers)
    
    elapsed = time.time() - start_time
    print(f"   Batch processing took {elapsed:.2f} seconds")
    print(f"   Found {len(batch_results)} stocks meeting criteria")
    print(f"   Average time per stock: {elapsed/len(test_tickers):.2f} seconds")
    
    # Test news fetching (additional API call)
    if batch_results:
        print(f"\n3. Testing news fetching...")
        start_time = time.time()
        
        news = analyzer.get_stock_news(batch_results[0]['symbol'])
        
        elapsed = time.time() - start_time
        print(f"   News fetching took {elapsed:.2f} seconds")
        print(f"   Found {len(news)} news items")
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"   Request count: {analyzer.request_count}")
    print(f"   Failed requests: {len(analyzer.failed_requests)}")
    print(f"   Configuration: {analyzer.max_workers} workers, {analyzer.batch_size} batch size")
    print(f"   Delay range: {analyzer.delay_range[0]}-{analyzer.delay_range[1]}s")
    
    if analyzer.failed_requests:
        print(f"   ⚠️  Some requests failed: {analyzer.failed_requests}")
        return False
    else:
        print(f"   ✅ All requests successful!")
        return True

def main():
    """Main test function."""
    print("Rate Limiting Test Suite")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['help', '-h', '--help']:
            print("Usage: python test_rate_limiting.py [preset] [num_stocks]")
            print("Presets: aggressive, balanced, conservative, ultra_conservative")
            print("Example: python test_rate_limiting.py conservative 5")
            return
        
        preset = sys.argv[1]
        num_stocks = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    else:
        preset = 'balanced'
        num_stocks = 10
    
    print(f"Testing preset: {preset}")
    print(f"Number of test stocks: {num_stocks}")
    
    # Show configuration info
    config = get_config(preset)
    print(f"\nConfiguration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("\nStarting test...")
    success = test_rate_limiting(preset, num_stocks)
    
    if success:
        print(f"\n🎉 Rate limiting test PASSED for '{preset}' preset!")
        print("You can now run the full analysis with confidence.")
    else:
        print(f"\n❌ Rate limiting test FAILED for '{preset}' preset.")
        print("Consider using a more conservative preset.")
        print("\nTry running: python test_rate_limiting.py conservative 5")

if __name__ == "__main__":
    main()