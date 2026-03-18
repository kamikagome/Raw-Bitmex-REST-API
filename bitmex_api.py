import requests
import pandas as pd

BASE_URL = "https://www.bitmex.com/api/v1"


def get_ohlcv(symbol: str = "XBTUSD", bin_size: str = "1h", count: int = 500) -> pd.DataFrame:
    """Fetch OHLCV candlestick data from BitMEX."""
    print(f"Fetching {count} x {bin_size} candles for {symbol}...")

    response = requests.get(f"{BASE_URL}/trade/bucketed", params={
        "symbol": symbol,
        "binSize": bin_size,
        "count": count,
        "reverse": True,
    })
    response.raise_for_status()

    df = pd.DataFrame(response.json())
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    print(f"Loaded {len(df)} candles")
    print(f"Period: {df['timestamp'].min()} → {df['timestamp'].max()}")
    print(f"Close price: min ${df['close'].min():,.0f}, max ${df['close'].max():,.0f}")
    return df[["timestamp", "open", "high", "low", "close", "volume"]]


def get_liquidations(symbol: str = "XBTUSD", count: int = 500) -> pd.DataFrame:
    """Fetch recent liquidations from BitMEX."""
    print(f"Fetching {count} liquidations for {symbol}...")

    response = requests.get(f"{BASE_URL}/liquidation", params={
        "symbol": symbol,
        "count": count,
        "reverse": True,
    })
    response.raise_for_status()

    df = pd.DataFrame(response.json())
    if df.empty:
        print("No liquidations found.")
        return pd.DataFrame(columns=["symbol", "side", "quantity", "price"])

    # API returns leavesQty, rename to quantity for consistency
    if "leavesQty" in df.columns:
        df = df.rename(columns={"leavesQty": "quantity"})

    total_value = df["quantity"].sum()
    print(f"Loaded {len(df)} liquidations | Total value: {total_value:,} contracts")

    cols = ["symbol", "side", "quantity", "price"]
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        cols.insert(0, "timestamp")
    return df[cols]


def get_funding_history(symbol: str = "XBTUSD", count: int = 500) -> pd.DataFrame:
    """Fetch historical funding rates from BitMEX."""
    print(f"Fetching {count} funding rate entries for {symbol}...")

    response = requests.get(f"{BASE_URL}/funding", params={
        "symbol": symbol,
        "count": count,
        "reverse": True,
    })
    response.raise_for_status()

    df = pd.DataFrame(response.json())
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["fundingRateDaily"] = df["fundingRate"] * 3  # 3 payments per day
    df["fundingRateAnnual"] = df["fundingRate"] * 3 * 365

    print(f"Loaded {len(df)} funding rate entries")
    print(f"Latest funding rate: {df['fundingRate'].iloc[-1] * 100:.4f}%")
    return df[["timestamp", "fundingRate", "fundingRateDaily", "fundingRateAnnual"]]


if __name__ == "__main__":
    df_ohlcv = get_ohlcv()
    print()
    df_liq = get_liquidations()
    print()
    df_fund = get_funding_history()
