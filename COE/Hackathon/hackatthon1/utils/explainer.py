import shap
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CreditExplainer:
    def __init__(self, model):
        self.model = model
        self.explainer = None
        self.feature_explanations = {
            'debt_to_equity': 'Debt-to-Equity Ratio: Lower values indicate less financial leverage and lower risk',
            'current_ratio': 'Current Ratio: Higher values show better ability to pay short-term obligations',
            'quick_ratio': 'Quick Ratio: Measures immediate liquidity without inventory',
            'return_on_equity': 'Return on Equity: Higher values indicate more efficient use of shareholder equity',
            'return_on_assets': 'Return on Assets: Shows how efficiently company uses its assets',
            'profit_margin': 'Profit Margin: Higher margins indicate better operational efficiency',
            'operating_margin': 'Operating Margin: Core business profitability measure',
            'revenue_growth': 'Revenue Growth: Positive growth indicates business expansion',
            'earnings_growth': 'Earnings Growth: Shows profitability trend',
            'price_to_book': 'Price-to-Book Ratio: Market valuation relative to book value',
            'price_to_earnings': 'P/E Ratio: Market valuation relative to earnings',
            'beta': 'Beta: Market risk measure (>1 = more volatile than market)',
            'stock_volatility': 'Stock Volatility: Price stability measure (lower is better)',
            'price_momentum_30d': '30-Day Price Momentum: Recent stock performance',
            'volume_trend': 'Volume Trend: Trading activity pattern',
            'sentiment_score': 'News Sentiment: Market perception from recent news'
        }
    
    def initialize_explainer(self, training_data):
        """Initialize SHAP explainer with training data"""
        try:
            # Get feature data for background
            X_background = training_data[self.model.feature_columns].fillna(0)
            X_background_scaled = self.model.scaler.transform(X_background)
            
            # Create SHAP explainer
            self.explainer = shap.Explainer(self.model.model, X_background_scaled)
            print("SHAP explainer initialized")
        except Exception as e:
            print(f"Could not initialize SHAP explainer: {e}")
            self.explainer = None
    
    def explain_prediction(self, company_data, prediction_score):
        """Generate comprehensive explanation for credit score"""
        
        explanation = {
            'overall_score': prediction_score,
            'risk_category': self.get_risk_category(prediction_score),
            'key_strengths': [],
            'key_weaknesses': [],
            'feature_impacts': {},
            'recent_events': company_data.get('recent_news', []),
            'recommendations': [],
            'summary': ''
        }
        
        # Analyze each feature
        for feature in self.model.feature_columns:
            value = company_data.get(feature, 0)
            if value is None or np.isinf(value) or np.isnan(value):
                value = 0
            
            impact = self.analyze_feature_impact(feature, value)
            explanation['feature_impacts'][feature] = impact
            
            if impact['impact_type'] == 'positive' and impact['strength'] == 'high':
                explanation['key_strengths'].append(impact)
            elif impact['impact_type'] == 'negative' and impact['strength'] == 'high':
                explanation['key_weaknesses'].append(impact)
        
        # Generate SHAP explanations if available
        if self.explainer:
            try:
                shap_explanation = self.get_shap_explanation(company_data)
                explanation['shap_values'] = shap_explanation
            except Exception as e:
                print(f"SHAP explanation failed: {e}")
        
        # Generate recommendations
        explanation['recommendations'] = self.generate_recommendations(explanation)
        
        # Generate summary
        explanation['summary'] = self.generate_summary(explanation, company_data)
        
        return explanation
    
    def get_risk_category(self, score):
        """Categorize risk level based on score"""
        if score >= 70:
            return {'level': 'LOW', 'color': 'green', 'description': 'Strong credit profile'}
        elif score >= 50:
            return {'level': 'MEDIUM', 'color': 'yellow', 'description': 'Moderate credit risk'}
        elif score >= 30:
            return {'level': 'HIGH', 'color': 'orange', 'description': 'Elevated credit risk'}
        else:
            return {'level': 'VERY HIGH', 'color': 'red', 'description': 'Significant credit concerns'}
    
    def analyze_feature_impact(self, feature, value):
        """Analyze individual feature impact"""
        impact = {
            'feature': feature,
            'value': value,
            'description': self.feature_explanations.get(feature, f'{feature}: {value}'),
            'impact_type': 'neutral',
            'strength': 'low',
            'explanation': ''
        }
        
        # Feature-specific analysis
        if feature == 'debt_to_equity':
            if value < 30:
                impact.update({'impact_type': 'positive', 'strength': 'high', 
                              'explanation': 'Low debt levels indicate strong financial stability'})
            elif value > 100:
                impact.update({'impact_type': 'negative', 'strength': 'high',
                              'explanation': 'High debt levels may indicate financial stress'})
                
        elif feature == 'current_ratio':
            if value > 2:
                impact.update({'impact_type': 'positive', 'strength': 'medium',
                              'explanation': 'Strong liquidity position'})
            elif value < 1:
                impact.update({'impact_type': 'negative', 'strength': 'high',
                              'explanation': 'Potential liquidity concerns'})
                
        elif feature == 'return_on_equity':
            if value > 15:
                impact.update({'impact_type': 'positive', 'strength': 'high',
                              'explanation': 'Excellent return on shareholder investment'})
            elif value < 5:
                impact.update({'impact_type': 'negative', 'strength': 'medium',
                              'explanation': 'Below-average profitability'})
                
        elif feature == 'profit_margin':
            if value > 20:
                impact.update({'impact_type': 'positive', 'strength': 'high',
                              'explanation': 'Strong operational efficiency'})
            elif value < 5:
                impact.update({'impact_type': 'negative', 'strength': 'medium',
                              'explanation': 'Margin pressure concerns'})
                
        elif feature == 'sentiment_score':
            if value > 60:
                impact.update({'impact_type': 'positive', 'strength': 'low',
                              'explanation': 'Positive market sentiment'})
            elif value < 40:
                impact.update({'impact_type': 'negative', 'strength': 'medium',
                              'explanation': 'Negative market sentiment'})
        
        return impact
    
    def get_shap_explanation(self, company_data):
        """Get SHAP-based explanations"""
        if not self.explainer:
            return None
        
        # Prepare features
        features = []
        for col in self.model.feature_columns:
            value = company_data.get(col, 0)
            if value is None or np.isinf(value) or np.isnan(value):
                value = 0
            features.append(float(value))
        
        # Scale features
        features_scaled = self.model.scaler.transform([features])
        
        # Get SHAP values
        shap_values = self.explainer(features_scaled)
        
        # Format for return
        shap_explanation = {
            'base_value': float(shap_values.base_values[0]),
            'shap_values': dict(zip(self.model.feature_columns, 
                                  [float(val) for val in shap_values.values[0]])),
            'feature_values': dict(zip(self.model.feature_columns, features))
        }
        
        return shap_explanation
    
    def generate_recommendations(self, explanation):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on key weaknesses
        for weakness in explanation['key_weaknesses'][:3]:  # Top 3 weaknesses
            feature = weakness['feature']
            
            if feature == 'debt_to_equity':
                recommendations.append({
                    'category': 'Financial Structure',
                    'recommendation': 'Consider debt reduction strategies to improve leverage ratios',
                    'priority': 'High'
                })
            elif feature == 'current_ratio':
                recommendations.append({
                    'category': 'Liquidity Management',
                    'recommendation': 'Improve working capital management to enhance liquidity',
                    'priority': 'High'
                })
            elif feature == 'profit_margin':
                recommendations.append({
                    'category': 'Operational Efficiency',
                    'recommendation': 'Focus on cost optimization and operational improvements',
                    'priority': 'Medium'
                })
            elif feature == 'sentiment_score':
                recommendations.append({
                    'category': 'Market Communication',
                    'recommendation': 'Enhance investor relations and market communication',
                    'priority': 'Low'
                })
        
        # General recommendations based on risk level
        risk_level = explanation['risk_category']['level']
        if risk_level in ['HIGH', 'VERY HIGH']:
            recommendations.append({
                'category': 'Risk Management',
                'recommendation': 'Implement comprehensive risk management framework',
                'priority': 'Critical'
            })
        
        return recommendations
    
    def generate_summary(self, explanation, company_data):
        """Generate natural language summary"""
        company_name = company_data.get('company_name', 'Company')
        score = explanation['overall_score']
        risk_level = explanation['risk_category']['level']
        
        # Start with overall assessment
        summary = f"{company_name} has a credit score of {score:.1f}/100, indicating {risk_level.lower()} credit risk. "
        
        # Add key strengths
        if explanation['key_strengths']:
            strength_features = [s['feature'].replace('_', ' ').title() for s in explanation['key_strengths'][:2]]
            summary += f"Key strengths include strong {' and '.join(strength_features)}. "
        
        # Add key concerns
        if explanation['key_weaknesses']:
            weakness_features = [w['feature'].replace('_', ' ').title() for w in explanation['key_weaknesses'][:2]]
            summary += f"Main concerns are {' and '.join(weakness_features)}. "
        
        # Add news sentiment
        sentiment_label = company_data.get('sentiment_label', 'Neutral')
        if sentiment_label != 'Neutral':
            summary += f"Recent news sentiment is {sentiment_label.lower()}. "
        
        # Add recommendation
        if risk_level == 'LOW':
            summary += "The company demonstrates solid financial health with minimal credit risk."
        elif risk_level == 'MEDIUM':
            summary += "Monitor key financial metrics and market conditions closely."
        else:
            summary += "Immediate attention required to address financial vulnerabilities."
        
        return summary

# Test the explainer
if __name__ == "__main__":
    print("Explainer module ready!")