import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_price_liquidations(df_ohlcv: pd.DataFrame, df_liq: pd.DataFrame) -> go.Figure:
    """Candlestick chart with liquidation bubbles overlaid."""

    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df_ohlcv["timestamp"],
        open=df_ohlcv["open"],
        high=df_ohlcv["high"],
        low=df_ohlcv["low"],
        close=df_ohlcv["close"],
        name="XBTUSD",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
    ))

    # Liquidation bubbles
    has_timestamp = "timestamp" in df_liq.columns
    for side, color, name in [("Buy", "#ef5350", "Long Liquidated"), ("Sell", "#26a69a", "Short Liquidated")]:
        mask = df_liq["side"] == side
        subset = df_liq[mask]
        if subset.empty:
            continue

        # Use timestamp if available, otherwise spread across the OHLCV time range
        if has_timestamp:
            x_vals = subset["timestamp"]
        else:
            x_vals = pd.date_range(
                df_ohlcv["timestamp"].min(),
                df_ohlcv["timestamp"].max(),
                periods=len(subset),
            )

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=subset["price"],
            mode="markers",
            marker=dict(
                size=subset["quantity"].clip(upper=subset["quantity"].quantile(0.95)),
                sizemode="area",
                sizeref=2.0 * subset["quantity"].max() / (30 ** 2),
                color=color,
                opacity=0.6,
                line=dict(width=0),
            ),
            name=name,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Price: $%{y:,.0f}<br>"
                "Contracts: %{customdata:,}<br>"
                "<extra></extra>"
            ),
            text=[side] * len(subset),
            customdata=subset["quantity"],
        ))

    fig.update_layout(
        title="XBTUSD Price + Liquidation Events",
        template="plotly_dark",
        xaxis_rangeslider_visible=True,
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def plot_liquidation_heatmap(df_ohlcv: pd.DataFrame, df_liq: pd.DataFrame) -> go.Figure:
    """Horizontal bar heatmap showing liquidation density by price level."""

    # Bucket liquidations into $500 price bands
    bucket_size = 500
    df_liq = df_liq.copy()
    df_liq["price_bucket"] = (df_liq["price"] / bucket_size).round() * bucket_size
    heatmap = df_liq.groupby("price_bucket")["quantity"].sum().reset_index()
    heatmap.columns = ["price_bucket", "total_qty"]
    heatmap = heatmap.sort_values("price_bucket")

    current_price = df_ohlcv["close"].iloc[-1]

    # Top 3 clusters for annotation
    top3 = heatmap.nlargest(3, "total_qty")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=heatmap["total_qty"],
        y=heatmap["price_bucket"],
        orientation="h",
        marker=dict(
            color=heatmap["total_qty"],
            colorscale="Reds",
            showscale=True,
            colorbar=dict(title="Contracts Liquidated"),
        ),
        name="Liquidations",
        hovertemplate="Price: $%{y:,.0f}<br>Contracts: %{x:,}<extra></extra>",
    ))

    max_qty = heatmap["total_qty"].max() if not heatmap.empty else 1

    # Current price line
    fig.add_shape(
        type="line",
        x0=0, x1=max_qty,
        y0=current_price, y1=current_price,
        line=dict(color="#FFD700", width=2, dash="dash"),
    )
    fig.add_annotation(
        x=max_qty * 0.95,
        y=current_price,
        text=f"  Current: ${current_price:,.0f}",
        showarrow=False,
        font=dict(color="#FFD700", size=11),
    )

    # Annotate top 3 clusters
    for _, row in top3.iterrows():
        fig.add_annotation(
            x=row["total_qty"],
            y=row["price_bucket"],
            text=f"  {row['total_qty']:,}",
            showarrow=False,
            font=dict(color="white", size=10),
            xanchor="left",
        )

    fig.update_layout(
        title="XBTUSD Liquidation Heatmap — Where Did People Get Wrecked?",
        template="plotly_dark",
        xaxis_title="Total Contracts Liquidated",
        yaxis_title="Price Level (USD)",
        height=700,
    )

    return fig


def plot_funding_rate(df_funding: pd.DataFrame) -> go.Figure:
    """Dual-panel chart: funding rate bars + annualized funding rate line."""

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("Funding Rate per 8h Period", "Annualized Funding Rate"),
        row_heights=[0.6, 0.4],
    )

    # Bar colors: green for positive, red for negative
    colors = ["#26a69a" if r >= 0 else "#ef5350" for r in df_funding["fundingRate"]]

    # Top panel: funding rate bars
    fig.add_trace(go.Bar(
        x=df_funding["timestamp"],
        y=df_funding["fundingRate"] * 100,
        marker_color=colors,
        name="Funding Rate (%)",
        hovertemplate="Time: %{x}<br>Rate: %{y:.4f}%<extra></extra>",
    ), row=1, col=1)

    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)

    # Bottom panel: annualized rate line
    fig.add_trace(go.Scatter(
        x=df_funding["timestamp"],
        y=df_funding["fundingRateAnnual"] * 100,
        mode="lines",
        line=dict(color="#FFD700", width=2),
        name="Annualized Rate (%)",
        hovertemplate="Time: %{x}<br>Annualized: %{y:.2f}%<extra></extra>",
    ), row=2, col=1)

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)

    # Annotation explaining funding
    fig.add_annotation(
        text="Positive rate: Long holders pay shorts. Negative: Short holders pay longs.",
        xref="paper", yref="paper",
        x=0.5, y=1.08,
        showarrow=False,
        font=dict(color="#aaaaaa", size=11),
        align="center",
    )

    fig.update_layout(
        title="XBTUSD Funding Rate History",
        template="plotly_dark",
        height=600,
        showlegend=False,
    )

    fig.update_yaxes(title_text="Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Annual (%)", row=2, col=1)

    return fig
