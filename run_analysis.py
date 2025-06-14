#!/usr/bin/env python3
"""
Wrapper script to run Fortune 5000 analysis with different rate limiting presets.
This makes it easy to choose the right configuration for your needs.
"""

import sys
import subprocess
from rate_limit_config import print_config_info, PRESETS

def main():
    print("Fortune 5000 Stock Analysis - Rate Limiting Configuration")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        preset = sys.argv[1].lower()
        if preset in PRESETS:
            print(f"Running analysis with '{preset}' preset...")
            subprocess.run([sys.executable, "fortune5000-analysis.py", preset])
            return
        elif preset in ['help', '-h', '--help']:
            print_help()
            return
        else:
            print(f"Unknown preset: {preset}")
            print_help()
            return
    
    # Interactive mode
    print("\nChoose a rate limiting preset:")
    print("1. Aggressive (fastest, higher risk of rate limiting)")
    print("2. Balanced (recommended)")
    print("3. Conservative (slower, safer)")
    print("4. Ultra Conservative (slowest, safest)")
    print("5. Show detailed configuration info")
    print("6. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                run_analysis('aggressive')
                break
            elif choice == '2':
                run_analysis('balanced')
                break
            elif choice == '3':
                run_analysis('conservative')
                break
            elif choice == '4':
                run_analysis('ultra_conservative')
                break
            elif choice == '5':
                print_config_info()
                continue
            elif choice == '6':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def run_analysis(preset):
    """Run the analysis with the specified preset."""
    print(f"\nStarting analysis with '{preset}' preset...")
    print("Press Ctrl+C to interrupt the analysis at any time.")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "fortune5000-analysis.py", preset])
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")

def print_help():
    """Print help information."""
    print("\nUsage:")
    print("  python run_analysis.py [preset]")
    print("\nAvailable presets:")
    for preset in PRESETS.keys():
        print(f"  {preset}")
    print("\nExamples:")
    print("  python run_analysis.py balanced")
    print("  python run_analysis.py conservative")
    print("\nFor interactive mode, run without arguments:")
    print("  python run_analysis.py")

if __name__ == "__main__":
    main()