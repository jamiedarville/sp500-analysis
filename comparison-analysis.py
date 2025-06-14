#!/usr/bin/env python3
"""
Comparison Analysis: S&P 500 vs Fortune 5000
Shows the differences in coverage and results between the two approaches.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import glob

def load_latest_results():
    """Load the most recent analysis results from both approaches."""
    
    # Find the latest S&P 500 results
    sp500_files = glob.glob("sp500_drops_*.csv")
    fortune5000_files = glob.glob("fortune5000_drops_*.csv")
    
    sp500_data = None
    fortune5000_data = None
    
    if sp500_files:
        latest_sp500 = max(sp500_files, key=os.path.getctime)
        sp500_data = pd.read_csv(latest_sp500)
        print(f"Loaded S&P 500 data from: {latest_sp500}")
    
    if fortune5000_files:
        latest_fortune5000 = max(fortune5000_files, key=os.path.getctime)
        fortune5000_data = pd.read_csv(latest_fortune5000)
        print(f"Loaded Fortune 5000 data from: {latest_fortune5000}")
    
    return sp500_data, fortune5000_data

def analyze_coverage_differences(sp500_data, fortune5000_data):
    """Analyze the differences in coverage between S&P 500 and Fortune 5000."""
    
    print("\n" + "="*80)
    print("COVERAGE ANALYSIS: S&P 500 vs Fortune 5000")
    print("="*80)
    
    if sp500_data is not None:
        print(f"S&P 500 Analysis:")
        print(f"  • Companies with significant drops: {len(sp500_data)}")
        print(f"  • Sectors covered: {sp500_data['sector'].nunique()}")
        print(f"  • Average drop: {sp500_data['percent_change'].mean():.2f}%")
        print(f"  • Largest drop: {sp500_data['percent_change'].min():.2f}%")
        
        # Top sectors by number of drops
        sp500_sectors = sp500_data['sector'].value_counts().head(5)
        print(f"  • Top sectors with drops:")
        for sector, count in sp500_sectors.items():
            print(f"    - {sector}: {count} companies")
    
    if fortune5000_data is not None:
        print(f"\nFortune 5000 Analysis:")
        print(f"  • Companies with significant drops: {len(fortune5000_data)}")
        print(f"  • Sectors covered: {fortune5000_data['sector'].nunique()}")
        print(f"  • Average drop: {fortune5000_data['percent_change'].mean():.2f}%")
        print(f"  • Largest drop: {fortune5000_data['percent_change'].min():.2f}%")
        
        # Top sectors by number of drops
        fortune5000_sectors = fortune5000_data['sector'].value_counts().head(5)
        print(f"  • Top sectors with drops:")
        for sector, count in fortune5000_sectors.items():
            print(f"    - {sector}: {count} companies")
    
    if sp500_data is not None and fortune5000_data is not None:
        # Find unique opportunities in Fortune 5000
        sp500_symbols = set(sp500_data['symbol'].tolist()) if sp500_data is not None else set()
        fortune5000_symbols = set(fortune5000_data['symbol'].tolist())
        
        unique_to_fortune5000 = fortune5000_symbols - sp500_symbols
        overlap = sp500_symbols & fortune5000_symbols
        
        print(f"\nOverlap Analysis:")
        print(f"  • Companies in both analyses: {len(overlap)}")
        print(f"  • Additional opportunities in Fortune 5000: {len(unique_to_fortune5000)}")
        print(f"  • Coverage expansion: {(len(unique_to_fortune5000) / len(sp500_symbols) * 100):.1f}% more opportunities")

def analyze_sector_distribution(sp500_data, fortune5000_data):
    """Analyze sector distribution differences."""
    
    print("\n" + "="*80)
    print("SECTOR DISTRIBUTION ANALYSIS")
    print("="*80)
    
    if sp500_data is not None and fortune5000_data is not None:
        # Compare sector distributions
        sp500_sectors = sp500_data['sector'].value_counts()
        fortune5000_sectors = fortune5000_data['sector'].value_counts()
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame({
            'S&P 500': sp500_sectors,
            'Fortune 5000': fortune5000_sectors
        }).fillna(0)
        
        comparison_df['Difference'] = comparison_df['Fortune 5000'] - comparison_df['S&P 500']
        comparison_df['% Increase'] = (comparison_df['Difference'] / comparison_df['S&P 500'] * 100).replace([float('inf'), -float('inf')], 0)
        
        print("Sector-wise comparison (companies with drops):")
        print("-" * 60)
        print(f"{'Sector':<25} {'S&P 500':<10} {'F5000':<10} {'Diff':<8} {'% Inc':<8}")
        print("-" * 60)
        
        for sector in comparison_df.index:
            sp500_count = int(comparison_df.loc[sector, 'S&P 500'])
            f5000_count = int(comparison_df.loc[sector, 'Fortune 5000'])
            diff = int(comparison_df.loc[sector, 'Difference'])
            pct_inc = comparison_df.loc[sector, '% Increase']
            
            print(f"{sector[:24]:<25} {sp500_count:<10} {f5000_count:<10} {diff:<8} {pct_inc:>6.1f}%")

def analyze_market_cap_distribution(sp500_data, fortune5000_data):
    """Analyze market cap distribution differences."""
    
    print("\n" + "="*80)
    print("MARKET CAP DISTRIBUTION ANALYSIS")
    print("="*80)
    
    def categorize_market_cap(market_cap):
        """Categorize companies by market cap."""
        if market_cap >= 200e9:  # $200B+
            return "Mega Cap (>$200B)"
        elif market_cap >= 10e9:  # $10B-$200B
            return "Large Cap ($10B-$200B)"
        elif market_cap >= 2e9:   # $2B-$10B
            return "Mid Cap ($2B-$10B)"
        else:                     # <$2B
            return "Small Cap (<$2B)"
    
    if sp500_data is not None:
        sp500_data['market_cap_category'] = sp500_data['market_cap'].apply(categorize_market_cap)
        sp500_cap_dist = sp500_data['market_cap_category'].value_counts()
        
        print("S&P 500 Market Cap Distribution:")
        for category, count in sp500_cap_dist.items():
            print(f"  • {category}: {count} companies")
    
    if fortune5000_data is not None:
        fortune5000_data['market_cap_category'] = fortune5000_data['market_cap'].apply(categorize_market_cap)
        fortune5000_cap_dist = fortune5000_data['market_cap_category'].value_counts()
        
        print("\nFortune 5000 Market Cap Distribution:")
        for category, count in fortune5000_cap_dist.items():
            print(f"  • {category}: {count} companies")

def show_top_opportunities(sp500_data, fortune5000_data):
    """Show top opportunities unique to Fortune 5000."""
    
    print("\n" + "="*80)
    print("TOP UNIQUE OPPORTUNITIES IN FORTUNE 5000")
    print("="*80)
    
    if sp500_data is not None and fortune5000_data is not None:
        sp500_symbols = set(sp500_data['symbol'].tolist())
        
        # Find companies unique to Fortune 5000
        unique_fortune5000 = fortune5000_data[~fortune5000_data['symbol'].isin(sp500_symbols)]
        
        if len(unique_fortune5000) > 0:
            # Sort by percentage change (most negative first)
            top_unique = unique_fortune5000.nsmallest(10, 'percent_change')
            
            print("Top 10 unique opportunities not in S&P 500:")
            print("-" * 100)
            print(f"{'Symbol':<8} {'Company':<35} {'Sector':<20} {'Change':<8} {'Mkt Cap':<12}")
            print("-" * 100)
            
            for _, row in top_unique.iterrows():
                market_cap_str = f"${row['market_cap']/1e9:.1f}B" if row['market_cap'] >= 1e9 else f"${row['market_cap']/1e6:.0f}M"
                print(f"{row['symbol']:<8} {str(row['company_name'])[:34]:<35} {str(row['sector'])[:19]:<20} {row['percent_change']:>6.2f}% {market_cap_str:<12}")
        else:
            print("No unique opportunities found (all Fortune 5000 drops are also in S&P 500)")

def generate_summary_report():
    """Generate a comprehensive summary report."""
    
    print("\n" + "="*80)
    print("FORTUNE 5000 EXPANSION SUMMARY REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    sp500_data, fortune5000_data = load_latest_results()
    
    if sp500_data is None and fortune5000_data is None:
        print("❌ No analysis results found. Please run the analysis scripts first.")
        return
    
    # Perform all analyses
    analyze_coverage_differences(sp500_data, fortune5000_data)
    analyze_sector_distribution(sp500_data, fortune5000_data)
    analyze_market_cap_distribution(sp500_data, fortune5000_data)
    show_top_opportunities(sp500_data, fortune5000_data)
    
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    
    if fortune5000_data is not None:
        total_drops = len(fortune5000_data)
        avg_drop = fortune5000_data['percent_change'].mean()
        sectors_covered = fortune5000_data['sector'].nunique()
        
        print(f"✅ Fortune 5000 analysis identified {total_drops} companies with significant drops")
        print(f"✅ Average drop magnitude: {avg_drop:.2f}%")
        print(f"✅ Sector diversity: {sectors_covered} different sectors represented")
        
        # Market cap insights
        large_cap_count = len(fortune5000_data[fortune5000_data['market_cap'] >= 10e9])
        mid_cap_count = len(fortune5000_data[(fortune5000_data['market_cap'] >= 2e9) & (fortune5000_data['market_cap'] < 10e9)])
        
        print(f"✅ Market cap diversity: {large_cap_count} large-cap, {mid_cap_count} mid-cap opportunities")
        
        if sp500_data is not None:
            expansion_rate = (len(fortune5000_data) - len(sp500_data)) / len(sp500_data) * 100
            print(f"✅ {expansion_rate:.1f}% more opportunities compared to S&P 500 analysis")
    
    print("\n💡 The Fortune 5000 expansion provides significantly broader market coverage,")
    print("   identifying more opportunities across diverse sectors and market caps.")

if __name__ == "__main__":
    generate_summary_report()