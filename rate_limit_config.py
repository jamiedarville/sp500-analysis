"""
Rate limiting configuration for Fortune 5000 stock analysis.
Adjust these parameters based on your API limits and performance needs.
"""

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    # Basic settings
    'max_workers': 3,  # Number of concurrent threads (reduce if getting rate limited)
    'batch_size': 50,  # Number of stocks to process in each batch
    'delay_range': (0.5, 2.0),  # Random delay between requests (min, max) in seconds
    
    # Advanced settings
    'inter_batch_delay': (2.0, 5.0),  # Delay between batches (min, max) in seconds
    'max_retries': 3,  # Maximum number of retries for failed requests
    'exponential_backoff_base': 1.0,  # Base delay for exponential backoff
    
    # Conservative settings (use if still getting rate limited)
    'conservative_mode': False,  # Enable for stricter rate limiting
    'conservative_max_workers': 1,
    'conservative_batch_size': 20,
    'conservative_delay_range': (1.0, 3.0),
    'conservative_inter_batch_delay': (5.0, 10.0),
}

# Preset configurations
PRESETS = {
    'aggressive': {
        'max_workers': 5,
        'batch_size': 100,
        'delay_range': (0.2, 1.0),
        'inter_batch_delay': (1.0, 3.0),
    },
    'balanced': {
        'max_workers': 3,
        'batch_size': 50,
        'delay_range': (0.5, 2.0),
        'inter_batch_delay': (2.0, 5.0),
    },
    'conservative': {
        'max_workers': 1,
        'batch_size': 20,
        'delay_range': (1.0, 3.0),
        'inter_batch_delay': (5.0, 10.0),
    },
    'ultra_conservative': {
        'max_workers': 1,
        'batch_size': 10,
        'delay_range': (2.0, 5.0),
        'inter_batch_delay': (10.0, 20.0),
    }
}

def get_config(preset='balanced'):
    """
    Get rate limiting configuration.
    
    Args:
        preset: Configuration preset ('aggressive', 'balanced', 'conservative', 'ultra_conservative')
        
    Returns:
        Dictionary with rate limiting parameters
    """
    if preset in PRESETS:
        return PRESETS[preset]
    else:
        return PRESETS['balanced']

def print_config_info():
    """Print information about available configurations."""
    print("Available Rate Limiting Presets:")
    print("=" * 50)
    
    for preset_name, config in PRESETS.items():
        print(f"\n{preset_name.upper()}:")
        print(f"  Max Workers: {config['max_workers']}")
        print(f"  Batch Size: {config['batch_size']}")
        print(f"  Delay Range: {config['delay_range'][0]}-{config['delay_range'][1]}s")
        print(f"  Inter-batch Delay: {config['inter_batch_delay'][0]}-{config['inter_batch_delay'][1]}s")
        
        # Estimate time
        estimated_time_per_stock = (config['delay_range'][0] + config['delay_range'][1]) / 2
        estimated_time_per_batch = config['batch_size'] * estimated_time_per_stock / config['max_workers']
        estimated_inter_batch = (config['inter_batch_delay'][0] + config['inter_batch_delay'][1]) / 2
        
        print(f"  Est. time per 1000 stocks: {((estimated_time_per_batch + estimated_inter_batch) * (1000 / config['batch_size']) / 60):.1f} minutes")

if __name__ == "__main__":
    print_config_info()