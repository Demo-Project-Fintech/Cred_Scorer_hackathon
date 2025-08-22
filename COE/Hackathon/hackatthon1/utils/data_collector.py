import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import feedparser
from textblob import TextBlob
import time

class DataCollector:
    def __init__(self):
        self.cache = {}
        
    def get_financial_data(self, ticker):
        """Get comprehensive financial data"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get historical data for volatility calculation
            hist = stock.history(period="3mo")
            
            # Calculate financial metrics
            financial_data = {
                # Basic info
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                
                # Financial ratios
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 1),
                'quick_ratio': info.get('quickRatio', 1),
                'return_on_equity': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
                'return_on_assets': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
                'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
                'operating_margin': info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else 0,
                'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0,
                'earnings_growth': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0,
                
                # Market metrics
                'market_cap': info.get('marketCap', 0),
                'price_to_book': info.get('priceToBook', 0),
                'price_to_earnings': info.get('trailingPE', 0),
                'beta': info.get('beta', 1),
                
                # Calculated metrics
                'stock_volatility': hist['Close'].pct_change().std() * np.sqrt(252) * 100,  # Annualized volatility
                'price_momentum_30d': ((hist['Close'][-1] / hist['Close'][-30]) - 1) * 100 if len(hist) >= 30 else 0,
                'volume_trend': (hist['Volume'][-10:].mean() / hist['Volume'][-30:-10].mean() - 1) * 100 if len(hist) >= 30 else 0,
            }
            
            return financial_data
            
        except Exception as e:
            print(f"Error getting financial data for {ticker}: {e}")
            return None
    
    def get_news_sentiment(self, company_name, ticker):
        """Get news sentiment using RSS feeds (free alternative)"""
        try:
            # Use Yahoo Finance RSS (free)
            rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
            
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                # Fallback to Google News RSS
                search_term = company_name.replace(' ', '+')
                rss_url = f"https://news.google.com/rss/search?q={search_term}+stock&hl=en-US&gl=US&ceid=US:en"
                feed = feedparser.parse(rss_url)
            
            sentiments = []
            recent_news = []
            
            for entry in feed.entries[:10]:  # Latest 10 articles
                title = entry.title
                summary = entry.get('summary', '')
                
                # Sentiment analysis
                text = f"{title} {summary}"
                blob = TextBlob(text)
                sentiment_score = blob.sentiment.polarity
                
                sentiments.append(sentiment_score)
                recent_news.append({
                    'title': title,
                    'sentiment': sentiment_score,
                    'date': entry.get('published', 'Unknown'),
                    'link': entry.get('link', '')
                })
            
            avg_sentiment = np.mean(sentiments) if sentiments else 0
            
            # Convert sentiment to score (0-100)
            sentiment_score = (avg_sentiment + 1) * 50  # Convert -1,1 range to 0-100
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_label': self.get_sentiment_label(sentiment_score),
                'news_count': len(recent_news),
                'recent_news': recent_news[:5]  # Top 5 for display
            }
            
        except Exception as e:
            print(f"Error getting news sentiment for {company_name}: {e}")
            return {
                'sentiment_score': 50,  # Neutral
                'sentiment_label': 'Neutral',
                'news_count': 0,
                'recent_news': []
            }
    
    def get_sentiment_label(self, score):
        """Convert sentiment score to label"""
        if score >= 60:
            return 'Positive'
        elif score >= 40:
            return 'Neutral'
        else:
            return 'Negative'
    
    def get_complete_data(self, ticker):
        """Get complete dataset for a company"""
        print(f"Collecting data for {ticker}...")
        
        # Get financial data
        financial_data = self.get_financial_data(ticker)
        if not financial_data:
            return None
        
        # Get news sentiment
        news_data = self.get_news_sentiment(financial_data['company_name'], ticker)
        
        # Combine data
        complete_data = {**financial_data, **news_data}
        complete_data['ticker'] = ticker
        complete_data['last_updated'] = datetime.now().isoformat()
        
        return complete_data

# Test the data collector
if __name__ == "__main__":
    collector = DataCollector()
    data = collector.get_complete_data("AAPL")
    print("Sample data:", data)