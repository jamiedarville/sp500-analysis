#!/usr/bin/env python3
"""
Quick start guide for the rate-limited Fortune 5000 analysis.
This script helps you get started with the right configuration.
"""

import os
import sys
from rate_limit_config import print_config_info

def main():
    print("🚀 Fortune 5000 Analysis - Quick Start Guide")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        'us_public_tickers.csv',
        'fortune5000-analysis.py',
        'rate_limit_config.py',
        'run_analysis.py'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all files are in the current directory.")
        return
    
    print("✅ All required files found!")
    
    print("\n📋 Available Options:")
    print("1. 🧪 Test rate limiting (recommended first step)")
    print("2. 🏃 Run full analysis with interactive preset selection")
    print("3. 📊 View detailed configuration information")
    print("4. 📖 Read the rate limiting documentation")
    print("5. ⚡ Quick run with balanced preset")
    print("6. 🐌 Quick run with conservative preset (if experiencing issues)")
    
    while True:
        try:
            choice = input("\nWhat would you like to do? (1-6): ").strip()
            
            if choice == '1':
                print("\n🧪 Testing rate limiting...")
                print("This will test with 10 stocks to verify everything works.")
                os.system(f"{sys.executable} test_rate_limiting.py balanced 10")
                break
                
            elif choice == '2':
                print("\n🏃 Starting interactive analysis...")
                os.system(f"{sys.executable} run_analysis.py")
                break
                
            elif choice == '3':
                print("\n📊 Configuration Details:")
                print_config_info()
                continue
                
            elif choice == '4':
                print("\n📖 Rate Limiting Documentation:")
                print("Please read README-RateLimiting.md for detailed information.")
                if os.path.exists('README-RateLimiting.md'):
                    print("File found in current directory.")
                else:
                    print("Documentation file not found.")
                continue
                
            elif choice == '5':
                print("\n⚡ Running with balanced preset...")
                print("This is the recommended setting for most users.")
                os.system(f"{sys.executable} fortune5000-analysis.py balanced")
                break
                
            elif choice == '6':
                print("\n🐌 Running with conservative preset...")
                print("This is slower but safer if you're experiencing rate limits.")
                os.system(f"{sys.executable} fortune5000-analysis.py conservative")
                break
                
            else:
                print("Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
    
    print("\n" + "=" * 50)
    print("💡 Tips for Success:")
    print("• Start with the test script to verify everything works")
    print("• Use 'balanced' preset for most situations")
    print("• Switch to 'conservative' if you get rate limited")
    print("• Monitor the logs for any error messages")
    print("• The analysis can take 2-4 hours for all ~8000 stocks")
    print("• You can interrupt with Ctrl+C and resume later")

if __name__ == "__main__":
    main()