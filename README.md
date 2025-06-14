# S&P 500 Stock Analysis Tool

A comprehensive Python tool for analyzing S&P 500 stocks to identify significant price drops and provide detailed market analysis.

## Features

- **Real-time Analysis**: Fetches current S&P 500 ticker list from Wikipedia
- **Drop Detection**: Identifies stocks with significant single-day drops (configurable threshold)
- **Comprehensive Data**: Provides market cap, 52-week ranges, volume analysis
- **News Integration**: Fetches recent news for stocks with significant drops
- **Concurrent Processing**: Uses multithreading for faster analysis
- **Data Export**: Saves results to CSV files with timestamps
- **Robust Error Handling**: Includes logging and retry mechanisms
- **Trading Day Awareness**: Handles weekends and holidays properly

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python sp500-analysis.py
```

### Customization

You can modify the analysis parameters by editing the `main()` function:

```python
# Change drop threshold (default: -10%)
analyzer = SP500Analyzer(drop_threshold=-5.0, max_workers=10)

# Adjust concurrent workers (default: 10)
analyzer = SP500Analyzer(drop_threshold=-10.0, max_workers=20)
```

## Output

The tool provides:

1. **Console Output**: 
   - Summary table of all stocks with significant drops
   - Detailed analysis of top 3 drops including recent news
   - Progress indicators during analysis

2. **CSV Export**: 
   - Timestamped CSV file with complete analysis data
   - Saved as `sp500_drops_YYYYMMDD_HHMMSS.csv`

3. **Log File**: 
   - Detailed logging saved to `sp500_analysis.log`
   - Includes errors, warnings, and progress information

## Sample Output

```
================================================================================
S&P 500 SIGNIFICANT DROP ANALYSIS
Threshold: -10.0% or lower
Analysis Date: 2025-06-13 20:34:50
================================================================================

📉 Found 3 stocks with significant drops:
------------------------------------------------------------------------------------------------------------------------
Symbol   Company                        Sector               Change   Price      Mkt Cap    From 52W High
------------------------------------------------------------------------------------------------------------------------
EXAMPLE  Example Corp                   Technology           -12.45%  $  45.67   $12.3B        -25.1%
TEST     Test Industries                Healthcare           -11.20%  $ 123.45   $5.67B        -18.7%
DEMO     Demo Solutions                 Finance              -10.80%  $  78.90   $2.34B        -15.2%
```

## Improvements Over Original Script

### Performance Enhancements
- **Concurrent Processing**: Uses ThreadPoolExecutor for parallel stock analysis
- **Rate Limiting**: Implements delays to avoid API rate limits
- **Efficient Data Fetching**: Optimized yfinance calls

### Robustness
- **Trading Day Logic**: Properly handles weekends and holidays
- **Error Handling**: Specific exception handling with detailed logging
- **Retry Mechanisms**: Automatic retries for network failures
- **Data Validation**: Validates data quality before analysis

### Features
- **Rich Output**: Formatted tables with comprehensive stock information
- **News Integration**: Fetches and displays recent news for dropped stocks
- **Data Export**: CSV export functionality with timestamps
- **Logging**: Comprehensive logging to file and console
- **Configurability**: Easily adjustable parameters

### Code Quality
- **Type Hints**: Full type annotations for better code clarity
- **Documentation**: Comprehensive docstrings and comments
- **Class Structure**: Object-oriented design for better maintainability
- **Dependencies**: Proper requirements management

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `drop_threshold` | -10.0 | Minimum percentage drop to flag stocks |
| `max_workers` | 10 | Number of concurrent threads for analysis |
| `max_news` | 3 | Maximum news items to fetch per stock |

## Dependencies

- `pandas`: Data manipulation and analysis
- `yfinance`: Yahoo Finance API for stock data
- `requests`: HTTP library for web requests
- `lxml`: XML/HTML parser for pandas.read_html()
- `html5lib`: HTML parser for pandas.read_html()

## Error Handling

The tool includes comprehensive error handling for:
- Network connectivity issues
- Invalid ticker symbols
- Missing or insufficient data
- API rate limiting
- File I/O operations

## Logging

All operations are logged to both console and file:
- **INFO**: General progress and status updates
- **WARNING**: Non-critical issues (e.g., missing data for specific stocks)
- **ERROR**: Critical errors that prevent analysis

## License

This project is open source and available under the MIT License.