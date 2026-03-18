# BitMEX XBTUSD Liquidation Dashboard

A Streamlit dashboard for analysing Bitcoin perpetual swap liquidations on BitMEX.

Core REST API concepts we use:

GET requests — We fetch read-only data from three public endpoints using HTTP GET (no authentication needed). Each endpoint represents a different resource: /trade/bucketed for candles, /liquidation for liquidations, /funding for funding rates.

Query parameters — We filter results by passing options in the params dict: symbol="XBTUSD", count=500 (how many records), reverse=True (newest first), binSize="1h" (candle interval). The API URL-encodes these into the query string automatically.

JSON responses — The API returns structured JSON data,


bitmex_api.py calls the BitMEX REST API directly using the requests library with no wrapper or SDK. 

Using three public endpoint:

GET /trade/bucketed — OHLCV candles
GET /liquidation — liquidations
GET /funding — funding rates

No authentication is needed. 

## Features
- Live XBTUSD candlestick chart with liquidation bubble overlay
- Liquidation heatmap by price level ($500 buckets)
- Historical funding rate with annualized cost analysis
- Liquidation price & funding cost calculator

## Run Locally
```
pip install -r requirements.txt
streamlit run app.py
```

## API
Uses BitMEX public REST API — no API key required.
Rate limit: 120 requests/minute (unauthenticated).
