import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import pickle
from datetime import datetime
import warnings
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COMPANIES


warnings.filterwarnings('ignore')

class CreditScoringModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'debt_to_equity', 'current_ratio', 'quick_ratio', 'return_on_equity',
            'return_on_assets', 'profit_margin', 'operating_margin', 'revenue_growth',
            'earnings_growth', 'price_to_book', 'price_to_earnings', 'beta',
            'stock_volatility', 'price_momentum_30d', 'volume_trend', 'sentiment_score'
        ]
        
    def create_synthetic_training_data(self, companies_data):
        """Create training data with heuristic-based credit scores"""
        training_data = []
        
        for ticker, data in companies_data.items():
            if data is None:
                continue
                
            # Extract features
            features = []
            for col in self.feature_columns:
                value = data.get(col, 0)
                # Handle None values and inf values
                if value is None or np.isinf(value) or np.isnan(value):
                    value = 0
                features.append(float(value))
            
            # Create synthetic credit score using financial health heuristics
            credit_score = self.calculate_heuristic_score(data)
            
            training_data.append(features + [credit_score])
        
        # Convert to DataFrame
        columns = self.feature_columns + ['credit_score']
        df = pd.DataFrame(training_data, columns=columns)
        
        return df
    
    def calculate_heuristic_score(self, data):
        """Calculate credit score using financial health heuristics (0-100)"""
        score = 50  # Start with neutral score
        
        # Liquidity (25% weight)
        current_ratio = data.get('current_ratio', 1)
        if current_ratio > 2:
            score += 15
        elif current_ratio > 1.5:
            score += 10
        elif current_ratio > 1:
            score += 5
        else:
            score -= 10
        
        # Profitability (30% weight)
        roe = data.get('return_on_equity', 0)
        profit_margin = data.get('profit_margin', 0)
        
        if roe > 15:
            score += 12
        elif roe > 10:
            score += 8
        elif roe > 5:
            score += 4
        else:
            score -= 5
            
        if profit_margin > 20:
            score += 8
        elif profit_margin > 10:
            score += 5
        elif profit_margin > 5:
            score += 2
        
        # Leverage (25% weight)
        debt_to_equity = data.get('debt_to_equity', 0)
        if debt_to_equity < 30:
            score += 12
        elif debt_to_equity < 50:
            score += 8
        elif debt_to_equity < 100:
            score += 2
        else:
            score -= 10
        
        # Market sentiment & stability (20% weight)
        sentiment_score = data.get('sentiment_score', 50)
        volatility = data.get('stock_volatility', 20)
        
        # Sentiment impact
        if sentiment_score > 60:
            score += 8
        elif sentiment_score > 40:
            score += 2
        else:
            score -= 5
        
        # Volatility impact
        if volatility < 15:
            score += 5
        elif volatility < 25:
            score += 2
        elif volatility > 40:
            score -= 8
        
        # Growth factors
        revenue_growth = data.get('revenue_growth', 0)
        if revenue_growth > 10:
            score += 5
        elif revenue_growth < -10:
            score -= 8
        
        # Ensure score is between 0-100
        return max(0, min(100, score))
    
    def train_model(self, companies_data):
        """Train the credit scoring model"""
        print("Creating training data...")
        training_df = self.create_synthetic_training_data(companies_data)
        
        if len(training_df) < 3:
            raise ValueError("Need at least 3 companies to train model")
        
        # Prepare features and target
        X = training_df[self.feature_columns].fillna(0)
        y = training_df['credit_score']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train XGBoost model
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        self.model.fit(X_scaled, y)
        
        print(f"Model trained on {len(training_df)} companies")
        return self.model
    
    def predict(self, company_data):
        """Predict credit score for a company"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Extract features
        features = []
        for col in self.feature_columns:
            value = company_data.get(col, 0)
            if value is None or np.isinf(value) or np.isnan(value):
                value = 0
            features.append(float(value))
        
        # Scale features
        features_scaled = self.scaler.transform([features])
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        
        # Ensure score is between 0-100
        return max(0, min(100, prediction))
    
    def get_feature_importance(self):
        """Get feature importance from the trained model"""
        if self.model is None:
            return {}
        
        importance_scores = self.model.feature_importances_
        importance_dict = dict(zip(self.feature_columns, importance_scores))
        
        # Sort by importance
        sorted_importance = dict(sorted(importance_dict.items(), 
                                     key=lambda x: x[1], reverse=True))
        
        return sorted_importance
    
    def save_model(self, filepath):
        """Save the trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath):
        """Load a saved model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']

# Test the model
if __name__ == "__main__":
    from data_collector import DataCollector
    from config import COMPANIES
    
    # Collect data for training
    collector = DataCollector()
    companies_data = {}
    
    for name, ticker in list(COMPANIES.items())[:5]:  # Use first 5 companies
        data = collector.get_complete_data(ticker)
        if data:
            companies_data[ticker] = data
    
    # Train model
    model = CreditScoringModel()
    model.train_model(companies_data)
    
    # Test prediction
    test_data = companies_data[list(companies_data.keys())[0]]
    score = model.predict(test_data)
    print(f"Credit score: {score:.1f}")
    print("Feature importance:", model.get_feature_importance())