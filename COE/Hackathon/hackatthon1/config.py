# Configuration file
import os

# API Keys (use free tiers)
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'demo_key')  # Get free from newsapi.org
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'demo')

# Companies to analyze
COMPANIES = {
    'Apple Inc.': 'AAPL',
    'Microsoft Corporation': 'MSFT',
    'Alphabet Inc.': 'GOOGL', 
    'Tesla Inc.': 'TSLA',
    'JPMorgan Chase': 'JPM',
    'Johnson & Johnson': 'JNJ',
    'Procter & Gamble': 'PG',
    'Coca-Cola': 'KO',
    'Walmart': 'WMT',
    'Amazon': 'AMZN'
}

# Model parameters
MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 6,
    'learning_rate': 0.1,
    'random_state': 42
}

# Risk thresholds
RISK_LEVELS = {
    'LOW': 70,
    'MEDIUM': 40,
    'HIGH': 0
}