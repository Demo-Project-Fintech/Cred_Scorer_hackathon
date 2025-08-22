import yfinance as yf
import pandas as pd
import streamlit as st

print("Testing yfinance...")
stock = yf.Ticker("AAPL")
info = stock.info
print(f"Apple market cap: ${info.get('marketCap', 0):,}")

print("✅ Setup complete!")