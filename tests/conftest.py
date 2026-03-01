"""Pytest fixtures for MCP Finance tests."""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def mock_ticker_info():
    """Sample ticker info response from yfinance."""
    return {
        "shortName": "Apple Inc.",
        "longName": "Apple Inc.",
        "currentPrice": 185.92,
        "regularMarketPrice": 185.92,
        "previousClose": 183.50,
        "open": 184.00,
        "regularMarketOpen": 184.00,
        "dayHigh": 186.75,
        "regularMarketDayHigh": 186.75,
        "dayLow": 184.50,
        "regularMarketDayLow": 184.50,
        "volume": 50000000,
        "regularMarketVolume": 50000000,
        "marketCap": 2870000000000,
        "trailingPE": 31.2,
        "forwardPE": 28.5,
        "fiftyTwoWeekHigh": 199.62,
        "fiftyTwoWeekLow": 164.08,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "website": "https://www.apple.com",
        "fullTimeEmployees": 161000,
        "country": "United States",
        "city": "Cupertino",
        "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
        "enterpriseValue": 2900000000000,
        "totalRevenue": 383000000000,
        "grossProfits": 170000000000,
        "ebitda": 130000000000,
        "netIncomeToCommon": 97000000000,
        "profitMargins": 0.25,
        "operatingMargins": 0.30,
        "trailingEps": 6.05,
        "bookValue": 4.25,
        "revenuePerShare": 24.32,
        "pegRatio": 2.5,
        "priceToBook": 43.7,
        "priceToSalesTrailing12Months": 7.5,
        "debtToEquity": 180.5,
        "currentRatio": 0.98,
        "dividendRate": 0.96,
        "dividendYield": 0.0052,
        "payoutRatio": 0.15,
        "targetMeanPrice": 200.00,
        "targetHighPrice": 250.00,
        "targetLowPrice": 170.00,
        "recommendationKey": "buy",
        "numberOfAnalystOpinions": 40,
        "beta": 1.28,
    }


@pytest.fixture
def mock_history_df():
    """Sample historical data DataFrame."""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    data = {
        'Open': [180 + i * 0.1 for i in range(100)],
        'High': [182 + i * 0.1 for i in range(100)],
        'Low': [178 + i * 0.1 for i in range(100)],
        'Close': [181 + i * 0.1 for i in range(100)],
        'Volume': [50000000 + i * 100000 for i in range(100)],
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def mock_news():
    """Sample news response."""
    return [
        {
            "title": "Apple Reports Record Q4 Earnings",
            "publisher": "Reuters",
            "link": "https://reuters.com/article/apple-earnings",
            "providerPublishTime": int(datetime.now().timestamp()),
            "type": "STORY",
        },
        {
            "title": "iPhone 16 Sales Beat Expectations",
            "publisher": "Bloomberg",
            "link": "https://bloomberg.com/article/iphone-sales",
            "providerPublishTime": int((datetime.now() - timedelta(hours=2)).timestamp()),
            "type": "STORY",
        },
    ]


@pytest.fixture
def mock_yfinance_ticker(mock_ticker_info, mock_history_df, mock_news):
    """Create a fully mocked yfinance Ticker object."""
    mock_ticker = MagicMock()
    mock_ticker.info = mock_ticker_info
    mock_ticker.history.return_value = mock_history_df
    mock_ticker.news = mock_news
    mock_ticker.calendar = {"Earnings Date": [datetime.now() + timedelta(days=30)]}
    # Create quarterly earnings history with proper date index
    earnings_dates = [
        datetime.now() - timedelta(days=365),
        datetime.now() - timedelta(days=270),
        datetime.now() - timedelta(days=180),
        datetime.now() - timedelta(days=90),
    ]
    mock_ticker.earnings_history = pd.DataFrame({
        "epsEstimate": [1.50, 1.45, 1.40, 1.35],
        "epsActual": [1.52, 1.48, 1.42, 1.33],
        "epsDifference": [0.02, 0.03, 0.02, -0.02],
        "surprisePercent": [1.33, 2.07, 1.43, -1.48],
    }, index=pd.DatetimeIndex(earnings_dates))
    return mock_ticker


@pytest.fixture
def mock_crypto_info():
    """Sample crypto ticker info."""
    return {
        "shortName": "Bitcoin USD",
        "regularMarketPrice": 67500.00,
        "previousClose": 66000.00,
        "regularMarketChange": 1500.00,
        "regularMarketChangePercent": 2.27,
        "regularMarketVolume": 25000000000,
        "volume24Hr": 25000000000,
        "marketCap": 1320000000000,
        "circulatingSupply": 19500000,
    }


@pytest.fixture
def sample_positions():
    """Sample portfolio positions."""
    return [
        {"symbol": "AAPL", "shares": 10, "cost_basis": 150.00},
        {"symbol": "GOOGL", "shares": 5, "cost_basis": 140.00},
        {"symbol": "MSFT", "shares": 20, "cost_basis": 380.00},
    ]
