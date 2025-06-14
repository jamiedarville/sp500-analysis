import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
import logging
from typing import List, Optional, Dict, Any
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
import numpy as np
import ta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sp500_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)

class SP500Analyzer:
    """
    A comprehensive S&P 500 stock analyzer that identifies significant price drops
    and provides detailed analysis including historical data and recent news.
    """
    
    def __init__(self, drop_threshold: float = -10.0, max_workers: int = 10):
        """
        Initialize the analyzer with configurable parameters.
        
        Args:
            drop_threshold: Minimum percentage drop to flag (default: -10%)
            max_workers: Maximum number of concurrent threads for data fetching
        """
        self.drop_threshold = drop_threshold
        self.max_workers = max_workers
        self.session = requests.Session()
        
    def get_sp500_tickers(self) -> Optional[List[str]]:
        """
        Retrieves the list of S&P 500 tickers from Wikipedia.
        
        Returns:
            List of ticker symbols or None if failed
        """
        try:
            logger.info("Fetching S&P 500 ticker list from Wikipedia...")
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            
            # Add retry logic for network requests
            for attempt in range(3):
                try:
                    tables = pd.read_html(url)
                    sp500_df = tables[0]
                    tickers = sp500_df['Symbol'].tolist()
                    
                    # Clean tickers (remove any invalid characters)
                    tickers = [ticker.replace('.', '-') for ticker in tickers if ticker]
                    
                    logger.info(f"Successfully retrieved {len(tickers)} S&P 500 tickers")
                    return tickers
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        time.sleep(2)
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Error fetching S&P 500 tickers: {e}")
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

    def analyze_single_stock(self, ticker_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single stock for significant price drops.
        
        Args:
            ticker_symbol: Stock ticker symbol
            
        Returns:
            Dictionary with analysis results or None if no significant drop
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # Get more historical data for technical indicators (30 days)
            hist = ticker.history(period="30d")
            
            if hist.empty or len(hist) < 2:
                logger.warning(f"Insufficient data for {ticker_symbol}")
                return None
                
            # Get the two most recent trading days
            previous_close = hist['Close'].iloc[-2]
            current_close = hist['Close'].iloc[-1]
            
            # Calculate percentage change
            percent_change = ((current_close - previous_close) / previous_close) * 100
            
            if percent_change <= self.drop_threshold:
                # Get additional stock info
                info = ticker.info
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
            return None

    def get_stock_news(self, ticker_symbol: str, max_news: int = 3) -> List[Dict[str, str]]:
        """
        Get recent news for a stock ticker.
        
        Args:
            ticker_symbol: Stock ticker symbol
            max_news: Maximum number of news items to return
            
        Returns:
            List of news items with title and link
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            news = ticker.news
            
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

    def analyze_sp500_stocks(self) -> None:
        """
        Main analysis function that processes all S&P 500 stocks.
        """
        logger.info("Starting S&P 500 analysis...")
        
        tickers = self.get_sp500_tickers()
        if not tickers:
            logger.error("Failed to retrieve ticker list. Exiting.")
            return

        print("\n" + "="*80)
        print("S&P 500 SIGNIFICANT DROP ANALYSIS")
        print(f"Threshold: {self.drop_threshold}% or lower")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        dropped_stocks = []
        processed_count = 0
        
        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(self.analyze_single_stock, ticker): ticker
                for ticker in tickers
            }
            
            # Process completed tasks
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                processed_count += 1
                
                try:
                    result = future.result()
                    if result:
                        dropped_stocks.append(result)
                        
                    # Progress indicator
                    if processed_count % 50 == 0:
                        logger.info(f"Processed {processed_count}/{len(tickers)} stocks...")
                        
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {e}")
                
                # Rate limiting
                time.sleep(0.1)

        # Display results
        self.display_results(dropped_stocks)
        
        # Save results to CSV
        if dropped_stocks:
            self.save_results_to_csv(dropped_stocks)

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
        
        # Show detailed analysis for top 3 drops
        print(f"\n📊 DETAILED ANALYSIS - Top 3 Drops:")
        print("="*80)
        
        for i, stock in enumerate(dropped_stocks[:3], 1):
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
            filename = f"sp500_drops_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"Results saved to {filename}")
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            logger.error(f"Error saving results to CSV: {e}")


def main():
    """Main function to run the analysis."""
    try:
        # Create analyzer instance
        analyzer = SP500Analyzer(drop_threshold=-1.0, max_workers=10)
        
        # Run analysis
        analyzer.analyze_sp500_stocks()
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ An error occurred: {e}")


if __name__ == "__main__":
    main()