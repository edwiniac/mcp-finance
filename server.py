#!/usr/bin/env python3
"""
MCP Finance Server - Financial data tools for AI assistants.

Provides real-time stock prices, company info, market news, and technical analysis
through the Model Context Protocol (MCP).
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Optional

import yfinance as yf
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP server
server = Server("mcp-finance")


def format_number(n: float | int | None, decimals: int = 2) -> str:
    """Format numbers with appropriate suffixes."""
    if n is None:
        return "N/A"
    if abs(n) >= 1e12:
        return f"${n/1e12:.{decimals}f}T"
    if abs(n) >= 1e9:
        return f"${n/1e9:.{decimals}f}B"
    if abs(n) >= 1e6:
        return f"${n/1e6:.{decimals}f}M"
    return f"${n:,.{decimals}f}"


def format_percent(n: float | None) -> str:
    """Format percentage values."""
    if n is None:
        return "N/A"
    return f"{n:+.2f}%"


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available finance tools."""
    return [
        Tool(
            name="get_stock_price",
            description="Get current stock price with daily change, volume, and key stats. "
                       "Use for real-time price checks and basic stock info.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, TSLA, GOOGL)"
                    },
                    "include_history": {
                        "type": "boolean",
                        "description": "Include 5-day price history",
                        "default": False
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_company_info",
            description="Get detailed company information including business description, "
                       "sector, employees, financials, and key metrics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_market_news",
            description="Get latest news articles and headlines for a stock or the general market.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (optional, omit for general market news)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of news items to return",
                        "default": 5
                    }
                }
            }
        ),
        Tool(
            name="get_technical_analysis",
            description="Get technical analysis indicators including moving averages, RSI, "
                       "MACD, and support/resistance levels.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "period": {
                        "type": "string",
                        "description": "Analysis period: '1mo', '3mo', '6mo', '1y'",
                        "default": "3mo"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_market_overview",
            description="Get an overview of major market indices (S&P 500, Dow Jones, NASDAQ, etc.) "
                       "and overall market status.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="calculate_portfolio",
            description="Calculate total value and P&L for a portfolio of stocks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "positions": {
                        "type": "array",
                        "description": "List of positions with symbol, shares, and cost_basis",
                        "items": {
                            "type": "object",
                            "properties": {
                                "symbol": {"type": "string"},
                                "shares": {"type": "number"},
                                "cost_basis": {"type": "number", "description": "Average cost per share"}
                            },
                            "required": ["symbol", "shares", "cost_basis"]
                        }
                    }
                },
                "required": ["positions"]
            }
        ),
        Tool(
            name="compare_stocks",
            description="Compare multiple stocks side by side on key metrics like price, "
                       "P/E ratio, market cap, and performance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of ticker symbols to compare (2-5 stocks)"
                    }
                },
                "required": ["symbols"]
            }
        ),
        Tool(
            name="get_crypto_price",
            description="Get current cryptocurrency price and 24h change.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Crypto symbol (e.g., BTC, ETH, SOL)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_earnings",
            description="Get upcoming and past earnings data for a stock.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="screen_stocks",
            description="Screen stocks based on criteria like market cap, P/E ratio, sector.",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_market_cap": {
                        "type": "number",
                        "description": "Minimum market cap in billions"
                    },
                    "max_pe": {
                        "type": "number",
                        "description": "Maximum P/E ratio"
                    },
                    "sector": {
                        "type": "string",
                        "description": "Sector filter (Technology, Healthcare, Finance, etc.)"
                    },
                    "min_dividend_yield": {
                        "type": "number",
                        "description": "Minimum dividend yield percentage"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a finance tool."""
    try:
        if name == "get_stock_price":
            result = await get_stock_price(
                arguments["symbol"],
                arguments.get("include_history", False)
            )
        elif name == "get_company_info":
            result = await get_company_info(arguments["symbol"])
        elif name == "get_market_news":
            result = await get_market_news(
                arguments.get("symbol"),
                arguments.get("limit", 5)
            )
        elif name == "get_technical_analysis":
            result = await get_technical_analysis(
                arguments["symbol"],
                arguments.get("period", "3mo")
            )
        elif name == "get_market_overview":
            result = await get_market_overview()
        elif name == "calculate_portfolio":
            result = await calculate_portfolio(arguments["positions"])
        elif name == "compare_stocks":
            result = await compare_stocks(arguments["symbols"])
        elif name == "get_crypto_price":
            result = await get_crypto_price(arguments["symbol"])
        elif name == "get_earnings":
            result = await get_earnings(arguments["symbol"])
        elif name == "screen_stocks":
            result = await screen_stocks(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except Exception as e:
        error_result = {"error": str(e), "tool": name}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def get_stock_price(symbol: str, include_history: bool = False) -> dict:
    """Get current stock price and basic info."""
    ticker = yf.Ticker(symbol.upper())
    info = ticker.info

    result = {
        "symbol": symbol.upper(),
        "name": info.get("shortName", info.get("longName", symbol)),
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "previous_close": info.get("previousClose"),
        "open": info.get("open") or info.get("regularMarketOpen"),
        "day_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
        "day_low": info.get("dayLow") or info.get("regularMarketDayLow"),
        "volume": info.get("volume") or info.get("regularMarketVolume"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "52_week_high": info.get("fiftyTwoWeekHigh"),
        "52_week_low": info.get("fiftyTwoWeekLow"),
        "timestamp": datetime.now().isoformat()
    }

    # Calculate change
    if result["price"] and result["previous_close"]:
        change = result["price"] - result["previous_close"]
        change_percent = (change / result["previous_close"]) * 100
        result["change"] = round(change, 2)
        result["change_percent"] = round(change_percent, 2)

    # Add history if requested
    if include_history:
        hist = ticker.history(period="5d")
        if not hist.empty:
            result["history"] = [
                {
                    "date": idx.strftime("%Y-%m-%d"),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"])
                }
                for idx, row in hist.iterrows()
            ]

    return result


async def get_company_info(symbol: str) -> dict:
    """Get detailed company information."""
    ticker = yf.Ticker(symbol.upper())
    info = ticker.info

    return {
        "symbol": symbol.upper(),
        "name": info.get("longName"),
        "description": info.get("longBusinessSummary"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "website": info.get("website"),
        "employees": info.get("fullTimeEmployees"),
        "country": info.get("country"),
        "city": info.get("city"),
        "financials": {
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "revenue": info.get("totalRevenue"),
            "gross_profit": info.get("grossProfits"),
            "ebitda": info.get("ebitda"),
            "net_income": info.get("netIncomeToCommon"),
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
        },
        "per_share": {
            "earnings": info.get("trailingEps"),
            "book_value": info.get("bookValue"),
            "revenue": info.get("revenuePerShare"),
        },
        "ratios": {
            "pe_trailing": info.get("trailingPE"),
            "pe_forward": info.get("forwardPE"),
            "peg": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
        },
        "dividends": {
            "rate": info.get("dividendRate"),
            "yield": info.get("dividendYield"),
            "payout_ratio": info.get("payoutRatio"),
        },
        "analyst": {
            "target_mean": info.get("targetMeanPrice"),
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            "recommendation": info.get("recommendationKey"),
            "num_analysts": info.get("numberOfAnalystOpinions"),
        }
    }


async def get_market_news(symbol: Optional[str] = None, limit: int = 5) -> dict:
    """Get market news for a symbol or general market."""
    if symbol:
        ticker = yf.Ticker(symbol.upper())
        news = ticker.news[:limit] if ticker.news else []
    else:
        # Get general market news from major index
        ticker = yf.Ticker("^GSPC")
        news = ticker.news[:limit] if ticker.news else []

    articles = []
    for item in news:
        articles.append({
            "title": item.get("title"),
            "publisher": item.get("publisher"),
            "link": item.get("link"),
            "published": datetime.fromtimestamp(item.get("providerPublishTime", 0)).isoformat()
            if item.get("providerPublishTime") else None,
            "type": item.get("type"),
        })

    return {
        "symbol": symbol.upper() if symbol else "MARKET",
        "count": len(articles),
        "articles": articles
    }


async def get_technical_analysis(symbol: str, period: str = "3mo") -> dict:
    """Get technical analysis indicators."""
    ticker = yf.Ticker(symbol.upper())
    hist = ticker.history(period=period)

    if hist.empty:
        return {"error": f"No data available for {symbol}"}

    close = hist["Close"]
    current_price = close.iloc[-1]

    # Moving averages
    ma_20 = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else None
    ma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None
    ma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None

    # RSI calculation
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1] if not rsi.empty else None

    # MACD
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    # Support/Resistance (simple: recent lows/highs)
    recent_high = hist["High"].tail(20).max()
    recent_low = hist["Low"].tail(20).min()

    # Volatility
    returns = close.pct_change().dropna()
    volatility = returns.std() * (252 ** 0.5) * 100  # Annualized

    # Trend determination
    if ma_20 and ma_50:
        if current_price > ma_20 > ma_50:
            trend = "Bullish"
        elif current_price < ma_20 < ma_50:
            trend = "Bearish"
        else:
            trend = "Neutral"
    else:
        trend = "Insufficient data"

    return {
        "symbol": symbol.upper(),
        "current_price": round(current_price, 2),
        "period": period,
        "trend": trend,
        "moving_averages": {
            "ma_20": round(ma_20, 2) if ma_20 else None,
            "ma_50": round(ma_50, 2) if ma_50 else None,
            "ma_200": round(ma_200, 2) if ma_200 else None,
            "price_vs_ma20": f"{((current_price/ma_20)-1)*100:+.2f}%" if ma_20 else None,
            "price_vs_ma50": f"{((current_price/ma_50)-1)*100:+.2f}%" if ma_50 else None,
        },
        "momentum": {
            "rsi_14": round(current_rsi, 2) if current_rsi else None,
            "rsi_signal": "Overbought" if current_rsi and current_rsi > 70 else "Oversold" if current_rsi and current_rsi < 30 else "Neutral",
            "macd": round(macd_line.iloc[-1], 4) if not macd_line.empty else None,
            "macd_signal": round(signal_line.iloc[-1], 4) if not signal_line.empty else None,
            "macd_histogram": round(macd_histogram.iloc[-1], 4) if not macd_histogram.empty else None,
        },
        "levels": {
            "resistance": round(recent_high, 2),
            "support": round(recent_low, 2),
            "52_week_range": f"{hist['Low'].min():.2f} - {hist['High'].max():.2f}",
        },
        "volatility": {
            "annualized": f"{volatility:.2f}%",
            "daily_avg_range": f"{(hist['High'] - hist['Low']).mean():.2f}",
        }
    }


async def get_market_overview() -> dict:
    """Get overview of major market indices."""
    indices = {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "NASDAQ": "^IXIC",
        "Russell 2000": "^RUT",
        "VIX": "^VIX",
        "10Y Treasury": "^TNX",
    }

    results = []
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get("regularMarketPrice") or info.get("previousClose")
            prev_close = info.get("previousClose")

            change = None
            change_pct = None
            if price and prev_close:
                change = price - prev_close
                change_pct = (change / prev_close) * 100

            results.append({
                "name": name,
                "symbol": symbol,
                "price": round(price, 2) if price else None,
                "change": round(change, 2) if change else None,
                "change_percent": round(change_pct, 2) if change_pct else None,
            })
        except Exception:
            results.append({"name": name, "symbol": symbol, "error": "Failed to fetch"})

    # Market status
    from datetime import datetime
    now = datetime.now()
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)

    if now.weekday() >= 5:
        status = "Closed (Weekend)"
    elif market_open <= now <= market_close:
        status = "Open"
    else:
        status = "Closed"

    return {
        "timestamp": datetime.now().isoformat(),
        "market_status": status,
        "indices": results
    }


async def calculate_portfolio(positions: list[dict]) -> dict:
    """Calculate portfolio value and P&L."""
    total_value = 0
    total_cost = 0
    holdings = []

    for pos in positions:
        symbol = pos["symbol"].upper()
        shares = pos["shares"]
        cost_basis = pos["cost_basis"]

        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")

        if current_price:
            market_value = shares * current_price
            cost_value = shares * cost_basis
            pnl = market_value - cost_value
            pnl_pct = (pnl / cost_value) * 100

            total_value += market_value
            total_cost += cost_value

            holdings.append({
                "symbol": symbol,
                "shares": shares,
                "cost_basis": cost_basis,
                "current_price": round(current_price, 2),
                "market_value": round(market_value, 2),
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_pct, 2),
            })
        else:
            holdings.append({
                "symbol": symbol,
                "error": "Could not fetch price"
            })

    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0

    return {
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_percent": round(total_pnl_pct, 2),
        "holdings": holdings
    }


async def compare_stocks(symbols: list[str]) -> dict:
    """Compare multiple stocks."""
    if len(symbols) < 2:
        return {"error": "Need at least 2 symbols to compare"}
    if len(symbols) > 5:
        symbols = symbols[:5]  # Limit to 5

    comparisons = []
    for symbol in symbols:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        hist = ticker.history(period="1y")

        ytd_return = None
        if not hist.empty and len(hist) > 1:
            ytd_return = ((hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1) * 100

        comparisons.append({
            "symbol": symbol.upper(),
            "name": info.get("shortName"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "dividend_yield": info.get("dividendYield"),
            "52_week_return": round(ytd_return, 2) if ytd_return else None,
            "sector": info.get("sector"),
            "beta": info.get("beta"),
        })

    return {
        "comparison": comparisons,
        "metrics": ["price", "market_cap", "pe_ratio", "forward_pe", "dividend_yield", "52_week_return", "beta"]
    }


async def get_crypto_price(symbol: str) -> dict:
    """Get cryptocurrency price."""
    # Yahoo Finance uses -USD suffix for crypto
    crypto_symbol = f"{symbol.upper()}-USD"
    ticker = yf.Ticker(crypto_symbol)
    info = ticker.info

    return {
        "symbol": symbol.upper(),
        "name": info.get("shortName", symbol),
        "price": info.get("regularMarketPrice"),
        "previous_close": info.get("previousClose"),
        "change_24h": info.get("regularMarketChange"),
        "change_24h_percent": info.get("regularMarketChangePercent"),
        "volume_24h": info.get("volume24Hr") or info.get("regularMarketVolume"),
        "market_cap": info.get("marketCap"),
        "circulating_supply": info.get("circulatingSupply"),
        "timestamp": datetime.now().isoformat()
    }


async def get_earnings(symbol: str) -> dict:
    """Get earnings data."""
    ticker = yf.Ticker(symbol.upper())

    # Get earnings dates
    try:
        calendar = ticker.calendar
        earnings_date = calendar.get("Earnings Date", [None])[0] if calendar else None
    except Exception:
        earnings_date = None

    # Get earnings history
    try:
        earnings_hist = ticker.earnings_history
        history = []
        if earnings_hist is not None and not earnings_hist.empty:
            for idx, row in earnings_hist.tail(4).iterrows():
                history.append({
                    "date": idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx),
                    "eps_estimate": row.get("epsEstimate"),
                    "eps_actual": row.get("epsActual"),
                    "surprise": row.get("epsDifference"),
                    "surprise_percent": row.get("surprisePercent"),
                })
    except Exception:
        history = []

    return {
        "symbol": symbol.upper(),
        "next_earnings_date": str(earnings_date) if earnings_date else None,
        "earnings_history": history
    }


async def screen_stocks(criteria: dict) -> dict:
    """Screen stocks based on criteria (simplified version)."""
    # Pre-defined popular stocks to screen from
    # In production, this would query a proper database
    popular_symbols = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
        "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "NFLX",
        "ADBE", "CRM", "INTC", "AMD", "QCOM", "T", "VZ", "PFE", "MRK", "KO"
    ]

    matches = []
    for symbol in popular_symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            market_cap = info.get("marketCap")
            pe = info.get("trailingPE")
            sector = info.get("sector")
            div_yield = info.get("dividendYield")

            # Apply filters
            if criteria.get("min_market_cap"):
                if not market_cap or market_cap < criteria["min_market_cap"] * 1e9:
                    continue
            if criteria.get("max_pe"):
                if not pe or pe > criteria["max_pe"]:
                    continue
            if criteria.get("sector"):
                if not sector or criteria["sector"].lower() not in sector.lower():
                    continue
            if criteria.get("min_dividend_yield"):
                if not div_yield or div_yield < criteria["min_dividend_yield"] / 100:
                    continue

            matches.append({
                "symbol": symbol,
                "name": info.get("shortName"),
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "market_cap": market_cap,
                "pe_ratio": pe,
                "sector": sector,
                "dividend_yield": f"{div_yield*100:.2f}%" if div_yield else None,
            })

            if len(matches) >= 10:  # Limit results
                break
        except Exception:
            continue

    return {
        "criteria": criteria,
        "matches": len(matches),
        "stocks": matches
    }


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
