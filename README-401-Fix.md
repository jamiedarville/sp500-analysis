# Yahoo Finance 401 Error Fix

## Problem
The `fortune5000-analysis.py` script was experiencing HTTP 401 errors when making requests to Yahoo Finance. This is a common issue that started occurring more frequently due to Yahoo Finance implementing stricter anti-bot measures.

## Root Cause
- Yahoo Finance has implemented more aggressive rate limiting and bot detection
- The 401 errors occur intermittently, especially under heavy load or rapid requests
- The errors are temporary and can be resolved with proper retry logic and rate limiting

## Solution Implemented

### 1. Enhanced Error Handling
Updated the `rate_limited_request` decorator to handle multiple types of HTTP errors:
- **401 Unauthorized**: Now retries with exponential backoff
- **429 Too Many Requests**: Existing rate limit handling
- **500/502/503/504**: Server errors that warrant retry
- **Timeout errors**: Network-related issues

### 2. Improved Rate Limiting
Updated the default "balanced" preset to be more conservative:
- Reduced max workers from 3 to 2
- Reduced batch size from 50 to 30
- Increased delay range from (0.5-2.0s) to (1.0-3.0s)
- Increased inter-batch delay from (2.0-5.0s) to (3.0-6.0s)

### 3. Better Retry Logic
- Exponential backoff for all retryable errors
- Specific logging for different error types
- Maximum of 3 retry attempts per request
- Graceful handling of non-retryable errors

## How to Use

### Quick Test
Run a small test to verify the fixes work:
```bash
python3 test_fixed_script.py
```

### Conservative Analysis (Recommended)
For the most reliable results with minimal 401 errors:
```bash
python3 fortune5000-analysis.py conservative
```

### Balanced Analysis
For faster processing with moderate reliability:
```bash
python3 fortune5000-analysis.py balanced
```

### Ultra Conservative (If Still Getting Errors)
If you continue to experience issues:
```bash
python3 fortune5000-analysis.py ultra_conservative
```

## Rate Limiting Presets

| Preset | Workers | Batch Size | Delay Range | Inter-batch Delay | Est. Time/1000 stocks |
|--------|---------|------------|-------------|-------------------|----------------------|
| aggressive | 5 | 100 | 0.2-1.0s | 1.0-3.0s | ~8 minutes |
| balanced | 2 | 30 | 1.0-3.0s | 3.0-6.0s | ~25 minutes |
| conservative | 1 | 20 | 1.0-3.0s | 5.0-10.0s | ~45 minutes |
| ultra_conservative | 1 | 10 | 2.0-5.0s | 10.0-20.0s | ~90 minutes |

## What Changed

### In `fortune5000-analysis.py`:
- Enhanced `rate_limited_request()` decorator with better error handling
- Added specific handling for 401 errors
- Improved logging for different error types

### In `rate_limit_config.py`:
- Made the "balanced" preset more conservative
- Reduced concurrent workers and batch sizes
- Increased delays between requests

## Expected Behavior

### Normal Operation
- The script should run without errors
- Occasional 401 errors may still occur but will be automatically retried
- Progress will be logged every 50 requests

### If 401 Errors Persist
1. Use a more conservative preset (`conservative` or `ultra_conservative`)
2. Check your internet connection
3. Try running the script at a different time (Yahoo Finance may have varying load)

## Monitoring
Watch the log output for:
- `HTTP 401 error on attempt X, waiting Y.Ys before retry` - Normal, will retry
- `Rate limited on attempt X, waiting Y.Ys` - Normal rate limiting
- `Failed after 3 attempts` - Persistent issue, may need more conservative settings

## Troubleshooting

### Still Getting 401 Errors?
1. Try the ultra_conservative preset
2. Ensure you have the latest yfinance version: `pip install --upgrade yfinance`
3. Check if your IP is being rate limited by trying from a different network

### Script Running Too Slowly?
1. Start with `conservative` preset
2. If stable, try `balanced` preset
3. Only use `aggressive` if you're confident about rate limits

## Files Modified
- `fortune5000-analysis.py` - Enhanced error handling
- `rate_limit_config.py` - More conservative defaults
- `test_fixed_script.py` - Test script to verify fixes
- `test_401_error.py` - Diagnostic script for 401 errors

The script should now be much more resilient to Yahoo Finance's rate limiting and 401 errors while maintaining good performance.