"""Tests for MCP tool handlers with mocked yfinance API."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import server module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    get_stock_price,
    get_company_info,
    get_market_news,
    get_technical_analysis,
    get_market_overview,
    calculate_portfolio,
    compare_stocks,
    get_crypto_price,
    get_earnings,
    screen_stocks,
    list_tools,
    call_tool,
)


class TestGetStockPrice:
    """Tests for get_stock_price tool."""

    @pytest.mark.asyncio
    async def test_basic_price_fetch(self, mock_yfinance_ticker):
        """Should return basic stock price data."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_stock_price("AAPL")

        assert result["symbol"] == "AAPL"
        assert result["name"] == "Apple Inc."
        assert result["price"] == 185.92
        assert result["previous_close"] == 183.50
        assert "change" in result
        assert "change_percent" in result

    @pytest.mark.asyncio
    async def test_price_with_history(self, mock_yfinance_ticker):
        """Should include history when requested."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_stock_price("AAPL", include_history=True)

        assert "history" in result
        assert len(result["history"]) > 0
        assert "date" in result["history"][0]
        assert "close" in result["history"][0]
        assert "volume" in result["history"][0]

    @pytest.mark.asyncio
    async def test_symbol_uppercased(self, mock_yfinance_ticker):
        """Should uppercase the symbol."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_stock_price("aapl")

        assert result["symbol"] == "AAPL"

    @pytest.mark.asyncio
    async def test_change_calculation(self, mock_yfinance_ticker):
        """Should correctly calculate price change."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_stock_price("AAPL")

        expected_change = 185.92 - 183.50
        expected_pct = (expected_change / 183.50) * 100

        assert result["change"] == round(expected_change, 2)
        assert result["change_percent"] == round(expected_pct, 2)


class TestGetCompanyInfo:
    """Tests for get_company_info tool."""

    @pytest.mark.asyncio
    async def test_company_info_structure(self, mock_yfinance_ticker):
        """Should return structured company information."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_company_info("AAPL")

        assert result["symbol"] == "AAPL"
        assert result["name"] == "Apple Inc."
        assert result["sector"] == "Technology"
        assert "financials" in result
        assert "per_share" in result
        assert "ratios" in result
        assert "dividends" in result
        assert "analyst" in result

    @pytest.mark.asyncio
    async def test_financials_section(self, mock_yfinance_ticker):
        """Should include financial metrics."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_company_info("AAPL")

        financials = result["financials"]
        assert "market_cap" in financials
        assert "revenue" in financials
        assert "profit_margin" in financials


class TestGetMarketNews:
    """Tests for get_market_news tool."""

    @pytest.mark.asyncio
    async def test_news_with_symbol(self, mock_yfinance_ticker):
        """Should fetch news for specific symbol."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_market_news("AAPL", limit=5)

        assert result["symbol"] == "AAPL"
        assert "articles" in result
        assert result["count"] == len(result["articles"])

    @pytest.mark.asyncio
    async def test_news_article_structure(self, mock_yfinance_ticker):
        """Should return properly structured articles."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_market_news("AAPL", limit=5)

        if result["articles"]:
            article = result["articles"][0]
            assert "title" in article
            assert "publisher" in article
            assert "link" in article
            assert "published" in article

    @pytest.mark.asyncio
    async def test_market_news_without_symbol(self, mock_yfinance_ticker):
        """Should fetch general market news when no symbol provided."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_market_news(None, limit=5)

        assert result["symbol"] == "MARKET"


class TestGetTechnicalAnalysis:
    """Tests for get_technical_analysis tool."""

    @pytest.mark.asyncio
    async def test_technical_analysis_structure(self, mock_yfinance_ticker):
        """Should return all technical indicators."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_technical_analysis("AAPL", period="3mo")

        assert result["symbol"] == "AAPL"
        assert "trend" in result
        assert "moving_averages" in result
        assert "momentum" in result
        assert "levels" in result
        assert "volatility" in result

    @pytest.mark.asyncio
    async def test_moving_averages(self, mock_yfinance_ticker):
        """Should calculate moving averages."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_technical_analysis("AAPL", period="3mo")

        ma = result["moving_averages"]
        assert "ma_20" in ma
        assert "ma_50" in ma

    @pytest.mark.asyncio
    async def test_momentum_indicators(self, mock_yfinance_ticker):
        """Should calculate RSI and MACD."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_technical_analysis("AAPL", period="3mo")

        momentum = result["momentum"]
        assert "rsi_14" in momentum
        assert "rsi_signal" in momentum
        assert "macd" in momentum

    @pytest.mark.asyncio
    async def test_empty_history_returns_error(self):
        """Should return error for empty history."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()

        with patch('server.yf.Ticker', return_value=mock_ticker):
            result = await get_technical_analysis("INVALID")

        assert "error" in result


class TestGetMarketOverview:
    """Tests for get_market_overview tool."""

    @pytest.mark.asyncio
    async def test_market_overview_structure(self, mock_ticker_info):
        """Should return overview of major indices."""
        mock_ticker = MagicMock()
        mock_ticker.info = mock_ticker_info

        with patch('server.yf.Ticker', return_value=mock_ticker):
            result = await get_market_overview()

        assert "timestamp" in result
        assert "market_status" in result
        assert "indices" in result
        assert len(result["indices"]) > 0

    @pytest.mark.asyncio
    async def test_market_status_determination(self, mock_ticker_info):
        """Should determine market status correctly."""
        mock_ticker = MagicMock()
        mock_ticker.info = mock_ticker_info

        with patch('server.yf.Ticker', return_value=mock_ticker):
            result = await get_market_overview()

        assert result["market_status"] in ["Open", "Closed", "Closed (Weekend)"]


class TestCalculatePortfolio:
    """Tests for calculate_portfolio tool."""

    @pytest.mark.asyncio
    async def test_portfolio_calculation(self, mock_yfinance_ticker, sample_positions):
        """Should calculate portfolio value and P&L."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await calculate_portfolio(sample_positions)

        assert "total_value" in result
        assert "total_cost" in result
        assert "total_pnl" in result
        assert "total_pnl_percent" in result
        assert "holdings" in result
        assert len(result["holdings"]) == len(sample_positions)

    @pytest.mark.asyncio
    async def test_individual_holding_pnl(self, mock_yfinance_ticker, sample_positions):
        """Should calculate P&L for each holding."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await calculate_portfolio(sample_positions)

        for holding in result["holdings"]:
            if "error" not in holding:
                assert "pnl" in holding
                assert "pnl_percent" in holding
                assert "market_value" in holding


class TestCompareStocks:
    """Tests for compare_stocks tool."""

    @pytest.mark.asyncio
    async def test_compare_multiple_stocks(self, mock_yfinance_ticker):
        """Should compare multiple stocks."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await compare_stocks(["AAPL", "MSFT", "GOOGL"])

        assert "comparison" in result
        assert len(result["comparison"]) == 3
        assert "metrics" in result

    @pytest.mark.asyncio
    async def test_compare_requires_two_stocks(self):
        """Should error with less than 2 stocks."""
        result = await compare_stocks(["AAPL"])

        assert "error" in result

    @pytest.mark.asyncio
    async def test_compare_limits_to_five(self, mock_yfinance_ticker):
        """Should limit comparison to 5 stocks."""
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]

        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await compare_stocks(symbols)

        assert len(result["comparison"]) == 5


class TestGetCryptoPrice:
    """Tests for get_crypto_price tool."""

    @pytest.mark.asyncio
    async def test_crypto_price_fetch(self, mock_crypto_info):
        """Should fetch cryptocurrency price."""
        mock_ticker = MagicMock()
        mock_ticker.info = mock_crypto_info

        with patch('server.yf.Ticker', return_value=mock_ticker):
            result = await get_crypto_price("BTC")

        assert result["symbol"] == "BTC"
        assert "price" in result
        assert "change_24h" in result
        assert "market_cap" in result


class TestGetEarnings:
    """Tests for get_earnings tool."""

    @pytest.mark.asyncio
    async def test_earnings_data(self, mock_yfinance_ticker):
        """Should return earnings data."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await get_earnings("AAPL")

        assert result["symbol"] == "AAPL"
        assert "next_earnings_date" in result
        assert "earnings_history" in result


class TestScreenStocks:
    """Tests for screen_stocks tool."""

    @pytest.mark.asyncio
    async def test_screen_with_criteria(self, mock_yfinance_ticker):
        """Should filter stocks based on criteria."""
        criteria = {
            "min_market_cap": 100,
            "max_pe": 50,
            "sector": "Technology"
        }

        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await screen_stocks(criteria)

        assert "criteria" in result
        assert "matches" in result
        assert "stocks" in result

    @pytest.mark.asyncio
    async def test_screen_empty_criteria(self, mock_yfinance_ticker):
        """Should work with empty criteria."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await screen_stocks({})

        assert "stocks" in result


class TestListTools:
    """Tests for MCP list_tools handler."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """Should return all available tools."""
        tools = await list_tools()

        assert len(tools) == 10
        tool_names = [t.name for t in tools]
        assert "get_stock_price" in tool_names
        assert "get_company_info" in tool_names
        assert "get_market_news" in tool_names
        assert "get_technical_analysis" in tool_names
        assert "get_market_overview" in tool_names
        assert "calculate_portfolio" in tool_names
        assert "compare_stocks" in tool_names
        assert "get_crypto_price" in tool_names
        assert "get_earnings" in tool_names
        assert "screen_stocks" in tool_names

    @pytest.mark.asyncio
    async def test_tools_have_descriptions(self):
        """Each tool should have a description."""
        tools = await list_tools()

        for tool in tools:
            assert tool.description
            assert len(tool.description) > 10

    @pytest.mark.asyncio
    async def test_tools_have_input_schemas(self):
        """Each tool should have an input schema."""
        tools = await list_tools()

        for tool in tools:
            assert tool.inputSchema
            assert tool.inputSchema["type"] == "object"


class TestCallTool:
    """Tests for MCP call_tool handler."""

    @pytest.mark.asyncio
    async def test_call_unknown_tool(self):
        """Should return error for unknown tool."""
        result = await call_tool("unknown_tool", {})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "error" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_exception_handling(self):
        """Should handle exceptions gracefully."""
        with patch('server.get_stock_price', side_effect=Exception("API Error")):
            result = await call_tool("get_stock_price", {"symbol": "AAPL"})

        assert len(result) == 1
        assert "error" in result[0].text

    @pytest.mark.asyncio
    async def test_call_get_stock_price(self, mock_yfinance_ticker):
        """Should call get_stock_price correctly."""
        with patch('server.yf.Ticker', return_value=mock_yfinance_ticker):
            result = await call_tool("get_stock_price", {"symbol": "AAPL"})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "AAPL" in result[0].text
