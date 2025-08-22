# 🏦 Cred_Scorer - AI-Powered Credit Intelligence Platform

**Real-Time Explainable Credit Intelligence Platform for CredTech Hackathon (IIT Kanpur)**

A sophisticated financial technology solution that ingests multi-source financial and unstructured data, generates dynamic creditworthiness scores, and provides interpretable, analyst-friendly dashboards with modern interactive visualizations.

## ✨ Features

### 🎯 Core Capabilities

- **Real-time Credit Scoring**: AI-powered credit assessment with XGBoost models
- **Multi-source Data Integration**: Financial metrics, news sentiment, market data
- **Explainable AI**: SHAP-based feature importance and impact analysis
- **Interactive Dashboards**: Modern Plotly visualizations with real-time updates
- **Company Comparison**: Multi-dimensional analysis across multiple companies
- **Risk Assessment**: Comprehensive risk categorization and recommendations

### 📊 Enhanced Visualizations

- **Credit Score Gauge**: Modern gauge charts with dynamic color coding
- **Feature Impact Analysis**: Enhanced horizontal bar charts with hover details
- **Financial Radar Chart**: Multi-dimensional company health overview
- **Trend Analysis**: 30-day credit score progression with risk zones
- **Real-time Monitoring**: Live updating charts with modern styling
- **Comparison Analytics**: Multi-company radar chart comparisons

### 🎨 Modern UI/UX

- **Glassmorphism Design**: Modern card layouts with backdrop blur effects
- **Gradient Color Schemes**: Contemporary color palettes and styling
- **Responsive Layout**: Optimized for different screen sizes
- **Interactive Elements**: Enhanced hover effects and animations
- **Typography**: Google Fonts integration for professional appearance

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone and Navigate**

   ```bash
   cd Cred_Scorer
   ```

2. **Set up Virtual Environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**

   ```bash
   streamlit run app.py
   ```

   Or use the startup scripts:

   - **Windows**: Double-click `start_app.bat`
   - **macOS/Linux**: Run `./start_app.sh`

## 📱 Application Structure

### Main Dashboard (`app.py`)

- **Score Analysis**: Credit score gauge and feature importance
- **Trends & Radar**: Financial health radar and historical trends
- **Detailed Explanation**: AI-driven insights and recommendations
- **Financial Metrics**: Comprehensive financial ratio analysis
- **News & Sentiment**: Market sentiment analysis from news sources

### Additional Pages

- **Company Comparison** (`pages/02_🔄_Compare_Companies.py`): Multi-company analysis
- **Real-Time Demo** (`pages/03_⚡_Real_Time_Demo.py`): Live monitoring simulation

## 🔧 Technical Architecture

### Data Sources

- **Yahoo Finance**: Stock prices, financial ratios, company information
- **News APIs**: RSS feeds for sentiment analysis
- **Market Data**: Real-time financial metrics and indicators

### Machine Learning

- **XGBoost**: Primary credit scoring model
- **SHAP**: Explainable AI for feature importance
- **TextBlob**: Natural language sentiment analysis
- **Scikit-learn**: Data preprocessing and model evaluation

### Visualization Stack

- **Plotly**: Interactive charts and graphs
- **Streamlit**: Web application framework
- **Custom CSS**: Modern styling and animations

## 📊 Key Metrics Analyzed

### Financial Health Indicators

- **Liquidity**: Current ratio, quick ratio
- **Profitability**: ROE, ROA, profit margins
- **Leverage**: Debt-to-equity ratio
- **Growth**: Revenue and earnings growth
- **Market**: P/E ratio, beta, volatility
- **Sentiment**: News sentiment score

### Risk Assessment Categories

- **Low Risk** (70-100): Strong credit profile
- **Medium Risk** (50-69): Moderate credit risk
- **High Risk** (30-49): Elevated credit risk
- **Very High Risk** (0-29): Significant credit concerns

## 🎨 UI Improvements Made

### Enhanced Visualizations

- Modern gauge charts with gradient colors
- Interactive feature importance bars with detailed tooltips
- Financial health radar charts
- Credit score trend analysis with risk zones
- Enhanced comparison charts with multi-dimensional views

### Modern Styling

- Glassmorphism card effects
- Gradient backgrounds and modern color schemes
- Custom scrollbars and hover animations
- Responsive design for mobile compatibility
- Professional typography with Google Fonts

## 🛠️ Development

### Testing

```bash
# Basic setup test
python test_setup.py

# Integration test
python test_integration.py
```

### File Structure

```
Cred_Scorer/
├── app.py                          # Main application
├── config.py                       # Configuration settings
├── requirements.txt                # Package dependencies
├── utils/                          # Core utilities
│   ├── data_collector.py          # Data acquisition
│   ├── model.py                   # ML models
│   └── explainer.py              # AI explanations
├── pages/                         # Additional pages
│   ├── 02_🔄_Compare_Companies.py
│   └── 03_⚡_Real_Time_Demo.py
├── static/                        # Static assets
├── templates/                     # HTML templates
└── data/                         # Data storage
```

## 🔄 Recent Updates

### Version 2.0 Improvements

- ✅ Fixed package installation compatibility issues
- ✅ Updated deprecated Streamlit functions
- ✅ Enhanced Plotly visualizations with modern styling
- ✅ Added new radar charts and trend analysis
- ✅ Implemented glassmorphism UI design
- ✅ Improved responsive layout and mobile compatibility
- ✅ Added comprehensive error handling and testing

## 🚀 Production Deployment

### Environment Variables

```bash
NEWS_API_KEY=your_news_api_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
```

### Docker Deployment (Optional)

```dockerfile
# Example Dockerfile structure
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Hackathon Context

Developed for the **CredTech Hackathon at IIT Kanpur**, this platform demonstrates:

- Advanced financial technology capabilities
- Real-time data processing and analysis
- Modern web application development
- AI/ML integration for financial services
- User-centric design and experience

## 📞 Support

For questions, issues, or contributions, please refer to the project documentation or create an issue in the repository.

---

**Built with ❤️ for the CredTech Hackathon - IIT Kanpur**
