import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
import logging
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
import numpy as np
import ta
import json
import random
from functools import wraps
from rate_limit_config import get_config, RATE_LIMIT_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fortune5000_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)

class Fortune5000Analyzer:
    """
    A comprehensive US stock analyzer that identifies significant price drops across
    all US public companies and provides detailed analysis including historical data
    and recent news. Uses comprehensive ticker data from us_public_tickers.csv.
    """
    
    def __init__(self, drop_threshold: float = -10.0, rate_limit_preset: str = 'balanced'):
        """
        Initialize the analyzer with configurable parameters.
        
        Args:
            drop_threshold: Minimum percentage drop to flag (default: -10%)
            rate_limit_preset: Rate limiting preset ('aggressive', 'balanced', 'conservative', 'ultra_conservative')
        """
        self.drop_threshold = drop_threshold
        
        # Load rate limiting configuration
        config = get_config(rate_limit_preset)
        self.max_workers = config['max_workers']
        self.batch_size = config['batch_size']
        self.delay_range = config['delay_range']
        self.inter_batch_delay = config['inter_batch_delay']
        
        # Rate limiting state
        self.request_count = 0
        self.last_request_time = 0
        self.failed_requests = []
        self.rate_limit_preset = rate_limit_preset
        
        logger.info(f"Initialized with '{rate_limit_preset}' rate limiting preset")
        logger.info(f"Config: {self.max_workers} workers, batch size {self.batch_size}, delay {self.delay_range}")
        
    def get_fortune5000_tickers(self) -> Optional[List[str]]:
        """
        Load all US public company tickers from the us_public_tickers.csv file.
        This provides comprehensive coverage of all US listed stocks.
        
        Returns:
            List of ticker symbols or None if failed
        """
        try:
            logger.info("Loading US public company tickers from us_public_tickers.csv...")
            
            # Read the CSV file
            df = pd.read_csv('us_public_tickers.csv')
            
            # Get the ticker symbols from the 'Symbol' column
            all_tickers = df['Symbol'].dropna().tolist()
            
            # Filter out invalid tickers (ETFs, bonds, warrants, etc.)
            valid_tickers = []
            excluded_suffixes = ['.W', '.U', '.R', '$', '#', '.A', '.B', '.C', '.D', '.E', '.F', '.G', '.H', '.I', '.J', '.K', '.L', '.M', '.N', '.O', '.P', '.Q', '.R', '.S', '.T', '.U', '.V', '.W', '.X', '.Y', '.Z']
            
            for ticker in all_tickers:
                ticker = str(ticker).strip()
                
                # Skip empty or invalid tickers
                if not ticker or ticker == 'nan' or len(ticker) > 6:
                    continue
                    
                # Skip tickers with special suffixes (preferred stocks, warrants, etc.)
                if any(ticker.endswith(suffix) for suffix in excluded_suffixes):
                    continue
                    
                # Skip tickers with special characters except for common ones like BRK-A
                if '$' in ticker or '#' in ticker:
                    continue
                    
                # Handle special cases like BRK.A -> BRK-A
                if '.' in ticker and not ticker.endswith('.'):
                    ticker = ticker.replace('.', '-')
                
                # Only include tickers with letters (and possibly numbers and hyphens)
                if ticker.replace('-', '').replace('.', '').isalnum() and ticker[0].isalpha():
                    valid_tickers.append(ticker)
            
            # Remove duplicates and sort
            valid_tickers = sorted(list(set(valid_tickers)))
            
            logger.info(f"Loaded {len(all_tickers)} total tickers from CSV")
            logger.info(f"Filtered to {len(valid_tickers)} valid common stock tickers")
            
            return valid_tickers
            
        except FileNotFoundError:
            logger.error("us_public_tickers.csv file not found!")
            logger.error("Please ensure the file is in the current directory.")
            return None
        except Exception as e:
            logger.error(f"Error loading tickers from CSV: {e}")
            return None


    def get_last_trading_day(self) -> datetime:
        """
        Get the last trading day (excludes weekends).
        
        Returns:
            Last trading day as datetime object
        """
        today = datetime.now()
        
        # If today is Monday, last trading day was Friday
        if today.weekday() == 0:  # Monday
            return today - timedelta(days=3)
        # If today is Sunday, last trading day was Friday
        elif today.weekday() == 6:  # Sunday
            return today - timedelta(days=2)
        # Otherwise, yesterday was likely a trading day
        else:
            return today - timedelta(days=1)

    def calculate_technical_indicators(self, hist_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate technical indicators (RSI, MACD, OBV) from historical data.
        
        Args:
            hist_data: Historical price data from yfinance
            
        Returns:
            Dictionary containing technical indicator values
        """
        try:
            if len(hist_data) < 14:  # Need at least 14 days for RSI
                return {
                    'rsi': None,
                    'macd': None,
                    'macd_signal': None,
                    'macd_histogram': None,
                    'obv': None
                }
            
            # Calculate RSI (14-day period)
            rsi = ta.momentum.RSIIndicator(hist_data['Close'], window=14).rsi().iloc[-1]
            
            # Calculate MACD
            macd_indicator = ta.trend.MACD(hist_data['Close'])
            macd = macd_indicator.macd().iloc[-1]
            macd_signal = macd_indicator.macd_signal().iloc[-1]
            macd_histogram = macd_indicator.macd_diff().iloc[-1]
            
            # Calculate OBV (On-Balance Volume)
            obv_indicator = ta.volume.OnBalanceVolumeIndicator(hist_data['Close'], hist_data['Volume'])
            obv = obv_indicator.on_balance_volume().iloc[-1]
            
            return {
                'rsi': round(rsi, 2) if not pd.isna(rsi) else None,
                'macd': round(macd, 4) if not pd.isna(macd) else None,
                'macd_signal': round(macd_signal, 4) if not pd.isna(macd_signal) else None,
                'macd_histogram': round(macd_histogram, 4) if not pd.isna(macd_histogram) else None,
                'obv': int(obv) if not pd.isna(obv) else None
            }
            
        except Exception as e:
            logger.warning(f"Error calculating technical indicators: {e}")
            return {
                'rsi': None,
                'macd': None,
                'macd_signal': None,
                'macd_histogram': None,
                'obv': None
            }

    def calculate_fundamental_ratios(self, info: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate fundamental financial ratios from stock info.
        
        Args:
            info: Stock info dictionary from yfinance
            
        Returns:
            Dictionary containing fundamental ratios
        """
        try:
            # P/E Ratio
            pe_ratio = info.get('trailingPE', None)
            forward_pe = info.get('forwardPE', None)
            
            # PEG Ratio
            peg_ratio = info.get('pegRatio', None)
            
            # Debt-to-Equity Ratio
            total_debt = info.get('totalDebt', 0)
            total_equity = info.get('totalStockholderEquity', 0)
            debt_to_equity = (total_debt / total_equity) if total_equity and total_equity != 0 else None
            
            # Free Cash Flow
            free_cash_flow = info.get('freeCashflow', None)
            
            # Dividend Yield
            dividend_yield = info.get('dividendYield', None)
            if dividend_yield:
                dividend_yield = dividend_yield * 100  # Convert to percentage
            
            # Additional useful metrics
            book_value = info.get('bookValue', None)
            price_to_book = info.get('priceToBook', None)
            return_on_equity = info.get('returnOnEquity', None)
            if return_on_equity:
                return_on_equity = return_on_equity * 100  # Convert to percentage
            
            return {
                'pe_ratio': round(pe_ratio, 2) if pe_ratio else None,
                'forward_pe': round(forward_pe, 2) if forward_pe else None,
                'peg_ratio': round(peg_ratio, 2) if peg_ratio else None,
                'debt_to_equity': round(debt_to_equity, 2) if debt_to_equity else None,
                'free_cash_flow': free_cash_flow,
                'dividend_yield': round(dividend_yield, 2) if dividend_yield else None,
                'book_value': round(book_value, 2) if book_value else None,
                'price_to_book': round(price_to_book, 2) if price_to_book else None,
                'return_on_equity': round(return_on_equity, 2) if return_on_equity else None
            }
            
        except Exception as e:
            logger.warning(f"Error calculating fundamental ratios: {e}")
            return {
                'pe_ratio': None,
                'forward_pe': None,
                'peg_ratio': None,
                'debt_to_equity': None,
                'free_cash_flow': None,
                'dividend_yield': None,
                'book_value': None,
                'price_to_book': None,
                'return_on_equity': None
            }

    def rate_limited_request(self, func):
        """
        Decorator to add rate limiting to API requests with exponential backoff.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            max_retries = RATE_LIMIT_CONFIG['max_retries']
            base_delay = RATE_LIMIT_CONFIG['exponential_backoff_base']
            
            for attempt in range(max_retries):
                try:
                    # Implement rate limiting
                    current_time = time.time()
                    time_since_last = current_time - self.last_request_time
                    min_delay = random.uniform(*self.delay_range)
                    
                    if time_since_last < min_delay:
                        sleep_time = min_delay - time_since_last
                        time.sleep(sleep_time)
                    
                    self.last_request_time = time.time()
                    self.request_count += 1
                    
                    # Log progress every 50 requests
                    if self.request_count % 50 == 0:
                        logger.info(f"Made {self.request_count} API requests...")
                    
                    result = func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        # Rate limited - exponential backoff
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Rate limited on attempt {attempt + 1}, waiting {delay:.2f}s")
                        time.sleep(delay)
                        continue
                    else:
                        # Other error - don't retry
                        raise e
            
            # All retries failed
            logger.error(f"Failed after {max_retries} attempts")
            return None
            
        return wrapper

    def analyze_single_stock(self, ticker_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single stock for significant price drops with rate limiting.
        
        Args:
            ticker_symbol: Stock ticker symbol
            
        Returns:
            Dictionary with analysis results or None if no significant drop
        """
        @self.rate_limited_request
        def fetch_stock_data(symbol):
            ticker = yf.Ticker(symbol)
            
            # Get more historical data for technical indicators (30 days)
            hist = ticker.history(period="30d")
            
            if hist.empty or len(hist) < 2:
                logger.warning(f"Insufficient data for {symbol}")
                return None
                
            # Get additional stock info (this is a separate API call)
            info = ticker.info
            
            return hist, info
        
        try:
            result = fetch_stock_data(ticker_symbol)
            if result is None:
                return None
                
            hist, info = result
            
            # Get the two most recent trading days
            previous_close = hist['Close'].iloc[-2]
            current_close = hist['Close'].iloc[-1]
            
            # Calculate percentage change
            percent_change = ((current_close - previous_close) / previous_close) * 100
            
            if percent_change <= self.drop_threshold:
                company_name = info.get('longName', ticker_symbol)
                sector = info.get('sector', 'Unknown')
                market_cap = info.get('marketCap', 0)
                
                # Get 52-week high/low for context
                fifty_two_week_high = info.get('fiftyTwoWeekHigh', 0)
                fifty_two_week_low = info.get('fiftyTwoWeekLow', 0)
                
                # Calculate distance from 52-week high
                distance_from_high = ((current_close - fifty_two_week_high) / fifty_two_week_high) * 100 if fifty_two_week_high else 0
                
                # Calculate technical indicators
                technical_indicators = self.calculate_technical_indicators(hist)
                
                # Calculate fundamental ratios
                fundamental_ratios = self.calculate_fundamental_ratios(info)
                
                # Combine all data
                result = {
                    'symbol': ticker_symbol,
                    'company_name': company_name,
                    'sector': sector,
                    'current_price': current_close,
                    'previous_close': previous_close,
                    'percent_change': percent_change,
                    'market_cap': market_cap,
                    'fifty_two_week_high': fifty_two_week_high,
                    'fifty_two_week_low': fifty_two_week_low,
                    'distance_from_high': distance_from_high,
                    'volume': hist['Volume'].iloc[-1],
                    'avg_volume': hist['Volume'].mean()
                }
                
                # Add technical indicators
                result.update(technical_indicators)
                
                # Add fundamental ratios
                result.update(fundamental_ratios)
                
                return result
                
        except Exception as e:
            logger.error(f"Error analyzing {ticker_symbol}: {e}")
            self.failed_requests.append(ticker_symbol)
            return None

    def get_stock_news(self, ticker_symbol: str, max_news: int = 3) -> List[Dict[str, str]]:
        """
        Get recent news for a stock ticker with rate limiting.
        
        Args:
            ticker_symbol: Stock ticker symbol
            max_news: Maximum number of news items to return
            
        Returns:
            List of news items with title and link
        """
        @self.rate_limited_request
        def fetch_news(symbol):
            ticker = yf.Ticker(symbol)
            return ticker.news
        
        try:
            news = fetch_news(ticker_symbol)
            
            if news:
                return [
                    {
                        'title': item.get('title', 'No title'),
                        'link': item.get('link', ''),
                        'publisher': item.get('publisher', 'Unknown'),
                        'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M') if item.get('providerPublishTime') else 'Unknown'
                    }
                    for item in news[:max_news]
                ]
            return []
            
        except Exception as e:
            logger.error(f"Error fetching news for {ticker_symbol}: {e}")
            return []

    def format_market_cap(self, market_cap: int) -> str:
        """Format market cap in readable format."""
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
        else:
            return f"${market_cap:,.0f}"

    def format_large_number(self, number: float) -> str:
        """Format large numbers (like FCF) in readable format."""
        if number is None:
            return "N/A"
        
        if abs(number) >= 1e12:
            return f"${number/1e12:.2f}T"
        elif abs(number) >= 1e9:
            return f"${number/1e9:.2f}B"
        elif abs(number) >= 1e6:
            return f"${number/1e6:.2f}M"
        elif abs(number) >= 1e3:
            return f"${number/1e3:.2f}K"
        else:
            return f"${number:,.0f}"

    def process_batch(self, ticker_batch: List[str]) -> List[Dict[str, Any]]:
        """
        Process a batch of tickers with controlled concurrency.
        
        Args:
            ticker_batch: List of ticker symbols to process
            
        Returns:
            List of analysis results
        """
        batch_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks in the batch
            future_to_ticker = {
                executor.submit(self.analyze_single_stock, ticker): ticker
                for ticker in ticker_batch
            }
            
            # Process completed tasks
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                
                try:
                    result = future.result()
                    if result:
                        batch_results.append(result)
                        
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {e}")
        
        return batch_results

    def analyze_us_stocks(self) -> None:
        """
        Main analysis function that processes all US public stocks with improved rate limiting.
        """
        logger.info("Starting comprehensive US stock analysis with rate limiting...")
        
        tickers = self.get_fortune5000_tickers()
        if not tickers:
            logger.error("Failed to retrieve ticker list. Exiting.")
            return

        print("\n" + "="*80)
        print("COMPREHENSIVE US STOCK ANALYSIS (Rate Limited)")
        print(f"Threshold: {self.drop_threshold}% or lower")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Analyzing {len(tickers)} US public companies")
        print(f"Batch size: {self.batch_size}, Max workers: {self.max_workers}")
        print(f"Delay range: {self.delay_range[0]}-{self.delay_range[1]}s")
        print("="*80)

        dropped_stocks = []
        processed_count = 0
        
        # Process tickers in batches to avoid overwhelming the API
        total_batches = (len(tickers) + self.batch_size - 1) // self.batch_size
        
        for batch_num in range(0, len(tickers), self.batch_size):
            batch_tickers = tickers[batch_num:batch_num + self.batch_size]
            current_batch = (batch_num // self.batch_size) + 1
            
            logger.info(f"Processing batch {current_batch}/{total_batches} ({len(batch_tickers)} tickers)")
            
            # Process the batch
            batch_results = self.process_batch(batch_tickers)
            dropped_stocks.extend(batch_results)
            
            processed_count += len(batch_tickers)
            
            # Progress update
            logger.info(f"Batch {current_batch} complete. Processed {processed_count}/{len(tickers)} stocks. Found {len(batch_results)} drops in this batch.")
            
            # Inter-batch delay to be respectful to the API
            if current_batch < total_batches:  # Don't sleep after the last batch
                inter_batch_delay = random.uniform(2.0, 5.0)
                logger.info(f"Waiting {inter_batch_delay:.1f}s before next batch...")
                time.sleep(inter_batch_delay)

        # Display results
        self.display_results(dropped_stocks)
        
        # Save results to CSV
        if dropped_stocks:
            self.save_results_to_csv(dropped_stocks)
        
        # Report failed requests
        if self.failed_requests:
            logger.warning(f"Failed to process {len(self.failed_requests)} tickers: {self.failed_requests[:10]}...")
            print(f"\n⚠️  Failed to process {len(self.failed_requests)} tickers due to rate limiting or errors")

    def display_results(self, dropped_stocks: List[Dict[str, Any]]) -> None:
        """Display analysis results in a formatted manner."""
        
        if not dropped_stocks:
            print("\n🎉 No stocks found with significant drops today!")
            return
            
        # Sort by percentage change (most negative first)
        dropped_stocks.sort(key=lambda x: x['percent_change'])
        
        print(f"\n📉 Found {len(dropped_stocks)} stocks with significant drops:")
        print("-" * 120)
        
        # Header
        print(f"{'Symbol':<8} {'Company':<30} {'Sector':<20} {'Change':<8} {'Price':<10} {'Mkt Cap':<10} {'From 52W High':<12}")
        print("-" * 120)
        
        for stock in dropped_stocks:
            print(f"{stock['symbol']:<8} "
                  f"{stock['company_name'][:29]:<30} "
                  f"{stock['sector'][:19]:<20} "
                  f"{stock['percent_change']:>7.2f}% "
                  f"${stock['current_price']:>8.2f} "
                  f"{self.format_market_cap(stock['market_cap']):<10} "
                  f"{stock['distance_from_high']:>10.1f}%")
        
        print("-" * 120)
        
        # Show detailed analysis for top 5 drops (increased from 3 for larger dataset)
        print(f"\n📊 DETAILED ANALYSIS - Top 5 Drops:")
        print("="*80)
        
        for i, stock in enumerate(dropped_stocks[:5], 1):
            print(f"\n{i}. {stock['symbol']} - {stock['company_name']}")
            print(f"   Sector: {stock['sector']}")
            print(f"   Price Change: ${stock['previous_close']:.2f} → ${stock['current_price']:.2f} ({stock['percent_change']:.2f}%)")
            print(f"   Market Cap: {self.format_market_cap(stock['market_cap'])}")
            print(f"   52-Week Range: ${stock['fifty_two_week_low']:.2f} - ${stock['fifty_two_week_high']:.2f}")
            print(f"   Volume: {stock['volume']:,.0f} (Avg: {stock['avg_volume']:,.0f})")
            
            # Display fundamental ratios
            print(f"\n   📈 FUNDAMENTAL METRICS:")
            pe_ratio = stock.get('pe_ratio', 'N/A')
            peg_ratio = stock.get('peg_ratio', 'N/A')
            debt_to_equity = stock.get('debt_to_equity', 'N/A')
            dividend_yield = stock.get('dividend_yield', 'N/A')
            free_cash_flow = self.format_large_number(stock.get('free_cash_flow'))
            
            print(f"   • P/E Ratio: {pe_ratio}")
            print(f"   • PEG Ratio: {peg_ratio}")
            print(f"   • Debt-to-Equity: {debt_to_equity}")
            print(f"   • Dividend Yield: {dividend_yield}%" if dividend_yield != 'N/A' else f"   • Dividend Yield: {dividend_yield}")
            print(f"   • Free Cash Flow: {free_cash_flow}")
            
            # Display technical indicators
            print(f"\n   📊 TECHNICAL INDICATORS:")
            rsi = stock.get('rsi', 'N/A')
            macd = stock.get('macd', 'N/A')
            macd_signal = stock.get('macd_signal', 'N/A')
            obv = stock.get('obv', 'N/A')
            
            print(f"   • RSI (14): {rsi}")
            print(f"   • MACD: {macd}")
            print(f"   • MACD Signal: {macd_signal}")
            print(f"   • OBV: {obv:,}" if obv != 'N/A' else f"   • OBV: {obv}")
            
            # RSI interpretation
            if rsi != 'N/A':
                if rsi < 30:
                    print(f"     → RSI indicates oversold conditions")
                elif rsi > 70:
                    print(f"     → RSI indicates overbought conditions")
                else:
                    print(f"     → RSI indicates neutral conditions")
            
            # Get and display news
            news = self.get_stock_news(stock['symbol'])
            if news:
                print(f"\n   📰 RECENT NEWS:")
                for item in news:
                    print(f"     • {item['title'][:80]}...")
                    print(f"       {item['publisher']} - {item['published']}")
            else:
                print(f"\n   📰 No recent news available")
            
            print("-" * 80)

    def save_results_to_csv(self, dropped_stocks: List[Dict[str, Any]]) -> None:
        """Save results to a CSV file."""
        try:
            df = pd.DataFrame(dropped_stocks)
            filename = f"fortune5000_drops_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"Results saved to {filename}")
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            logger.error(f"Error saving results to CSV: {e}")


def main():
    """Main function to run the analysis."""
    import sys
    
    try:
        # Check if a rate limiting preset was provided as command line argument
        if len(sys.argv) > 1:
            preset = sys.argv[1].lower()
            if preset not in ['aggressive', 'balanced', 'conservative', 'ultra_conservative']:
                print(f"Invalid preset: {preset}")
                print("Valid presets: aggressive, balanced, conservative, ultra_conservative")
                return
        else:
            preset = 'balanced'  # Default preset
        
        # Create analyzer instance with rate limiting preset
        analyzer = Fortune5000Analyzer(
            drop_threshold=-1.0,
            rate_limit_preset=preset
        )
        
        # Run analysis
        analyzer.analyze_us_stocks()
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ An error occurred: {e}")


if __name__ == "__main__":
    main()