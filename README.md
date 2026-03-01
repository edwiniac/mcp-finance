# 📈 MCP Finance Server

[![CI](https://github.com/edwiniac/mcp-finance/actions/workflows/ci.yml/badge.svg)](https://github.com/edwiniac/mcp-finance/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that provides financial data tools for AI assistants. Get real-time stock prices, company info, market news, and technical analysis through a standardized interface.

## 🚀 Features

- **Stock Prices** — Real-time and historical price data
- **Company Info** — Fundamentals, financials, and company profiles  
- **Market News** — Latest news and sentiment for any ticker
- **Technical Analysis** — Moving averages, RSI, MACD, and key indicators
- **Portfolio Tracking** — Track multiple positions with P&L calculations
- **Market Overview** — Major indices (S&P 500, NASDAQ, Dow) and market status
- **Stock Screener** — Filter stocks by market cap, P/E, sector, dividends
- **Crypto Prices** — Bitcoin, Ethereum, and other cryptocurrency data

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/edwiniac/mcp-finance.git
cd mcp-finance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "finance": {
      "command": "python",
      "args": ["/path/to/mcp-finance/server.py"]
    }
  }
}
```

### With uvx (Recommended)

```json
{
  "mcpServers": {
    "finance": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/edwiniac/mcp-finance", "mcp-finance"]
    }
  }
}
```

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `get_stock_price` | Current price, daily change, volume, 52-week range |
| `get_company_info` | Full company profile, financials, analyst ratings |
| `get_market_news` | Latest news articles for any ticker |
| `get_technical_analysis` | MA, RSI, MACD, support/resistance levels |
| `get_market_overview` | Major indices and market status |
| `calculate_portfolio` | Portfolio value and P&L tracking |
| `compare_stocks` | Side-by-side stock comparison |
| `get_crypto_price` | Cryptocurrency prices (BTC, ETH, etc.) |
| `get_earnings` | Earnings dates and history |
| `screen_stocks` | Filter stocks by criteria |

## 💬 Example Conversations

Once connected to Claude (or any MCP-compatible assistant):

**Stock Price Check:**
```
User: What's Apple trading at?
Assistant: Apple (AAPL) is currently at $185.92, up +1.24% today.
          Day range: $184.50 - $186.75
          52-week range: $164.08 - $199.62
```

**Technical Analysis:**
```
User: Give me a technical analysis of NVDA
Assistant: NVDA Technical Analysis (3-month):
          - Trend: Bullish
          - RSI(14): 62.5 (Neutral)
          - Price vs MA20: +4.2%
          - Support: $875 | Resistance: $950
```

**Portfolio Tracking:**
```
User: Calculate my portfolio: 10 AAPL at $150, 5 GOOGL at $140, 20 MSFT at $380
Assistant: Portfolio Summary:
          Total Value: $12,450.30
          Total P&L: +$1,892.50 (+17.9%)
          
          Holdings:
          - AAPL: +$359 (+23.9%)
          - GOOGL: +$285 (+40.7%)
          - MSFT: +$1,248 (+16.4%)
```

**Stock Comparison:**
```
User: Compare AAPL, MSFT, and GOOGL
Assistant: Comparison:
          | Metric      | AAPL    | MSFT    | GOOGL   |
          |-------------|---------|---------|---------|
          | Price       | $185.92 | $442.50 | $175.20 |
          | P/E Ratio   | 31.2    | 37.8    | 25.4    |
          | Market Cap  | $2.87T  | $3.29T  | $2.15T  |
          | 1Y Return   | +28.5%  | +19.2%  | +45.3%  |
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           MCP Finance Server            │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Stock   │  │Technical│  │Portfolio│ │
│  │ Data    │  │Analysis │  │ Calc    │ │
│  └────┬────┘  └────┬────┘  └────┬────┘ │
│       │            │            │       │
│  ┌────▼────────────▼────────────▼────┐ │
│  │         Yahoo Finance API         │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
         │
         │ MCP Protocol (stdio)
         ▼
┌─────────────────────────────────────────┐
│     Claude / AI Assistant               │
└─────────────────────────────────────────┘
```

## 🔌 Data Sources

- **Yahoo Finance** — Stock prices, company info, historical data (via `yfinance`)
- Free tier, no API key required
- Rate limits apply for heavy usage

## 📊 Technical Indicators

The `get_technical_analysis` tool provides:

- **Moving Averages**: MA20, MA50, MA200
- **Momentum**: RSI(14), MACD, Signal Line
- **Levels**: Support, Resistance, 52-week range
- **Volatility**: Annualized volatility, average daily range
- **Trend**: Bullish/Bearish/Neutral classification

## 🚀 Development

```bash
# Run server directly (for testing)
python server.py

# Run with MCP inspector
npx @modelcontextprotocol/inspector python server.py
```

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

**Built with** [Model Context Protocol](https://modelcontextprotocol.io/) • [yfinance](https://github.com/ranaroussi/yfinance) • Python
