import os
import requests
from langchain_core.tools import tool


@tool
def get_stock_price(stock_symbol: str) -> dict:
    """
    Fetch the current stock price for a given stock symbol using Alpha Vantage.

    Args:
        stock_symbol: The ticker symbol (e.g. AAPL, TSLA).

    Returns:
        A dict with the Global Quote data or an error message.
    """
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE"
        f"&symbol={stock_symbol}"
        f"&apikey={os.getenv('ALPHAVANTAGE_STOCK_API_KEY')}"
    )
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data.get("Global Quote", {"error": "Stock symbol not found or API limit reached."})
    except Exception as e:
        return {"error": str(e)}
