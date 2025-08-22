import sys
sys.path.append('utils')

from data_collector import DataCollector
from model import CreditScoringModel
from explainer import CreditExplainer
from config import COMPANIES

# Test full pipeline
collector = DataCollector()
model = CreditScoringModel()
companies_data = {}

# Collect data for first 3 companies
for name, ticker in list(COMPANIES.items())[:3]:
    data = collector.get_complete_data(ticker)
    if data:
        companies_data[ticker] = data

# Train model
model.train_model(companies_data)

# Create explainer
explainer = CreditExplainer(model)

# Test explanation
test_ticker = list(companies_data.keys())[0]
test_data = companies_data[test_ticker]
score = model.predict(test_data)
explanation = explainer.explain_prediction(test_data, score)

print(f"✅ Integration test passed!")
print(f"Company: {test_data['company_name']}")
print(f"Score: {score:.1f}")
print(f"Risk Level: {explanation['risk_category']['level']}")