import streamlit as st
from bitmex_api import get_ohlcv, get_liquidations, get_funding_history
from charts import plot_price_liquidations, plot_liquidation_heatmap, plot_funding_rate
from calculator import render_calculator

st.set_page_config(
    page_title="BitMEX XBTUSD Dashboard",
    page_icon="🔥",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## BITMEX")
    st.markdown("XBTUSD Liquidation Dashboard")
    st.divider()

    bin_size = st.selectbox("Candle Interval", ["1h", "4h", "1d"])
    count = st.slider("Data Points", 100, 500, 300)
    refresh = st.button("Refresh Data")


# ── Data Layer (cached) ────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data(bin_size, count):
    df_ohlcv = get_ohlcv(bin_size=bin_size, count=count)
    df_liq = get_liquidations(count=500)
    df_fund = get_funding_history(count=300)
    return df_ohlcv, df_liq, df_fund


if refresh:
    st.cache_data.clear()

try:
    df_ohlcv, df_liq, df_fund = load_data(bin_size, count)
except Exception as e:
    st.error(f"BitMEX API error: {e}. Check your connection or try again shortly.")
    st.stop()

# ── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Price + Liquidations",
    "Liquidation Heatmap",
    "Funding Rate",
    "Calculator",
])

with tab1:
    st.plotly_chart(plot_price_liquidations(df_ohlcv, df_liq), use_container_width=True)

with tab2:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Liquidations", f"{len(df_liq):,}")
    c2.metric("Total Contracts", f"{df_liq['quantity'].sum():,}")
    if not df_liq.empty:
        dominant = df_liq.groupby("side")["quantity"].sum().idxmax()
        c3.metric("Dominant Side Liquidated", dominant + "s")
    else:
        c3.metric("Dominant Side Liquidated", "N/A")
    st.plotly_chart(plot_liquidation_heatmap(df_ohlcv, df_liq), use_container_width=True)

with tab3:
    latest_rate = df_fund["fundingRate"].iloc[-1]
    f1, f2, f3 = st.columns(3)
    f1.metric("Current 8h Rate", f"{latest_rate * 100:.4f}%")
    f2.metric("Daily Rate", f"{latest_rate * 3 * 100:.4f}%")
    f3.metric("Annualized Rate", f"{latest_rate * 3 * 365 * 100:.2f}%")
    st.plotly_chart(plot_funding_rate(df_fund), use_container_width=True)

with tab4:
    render_calculator()
