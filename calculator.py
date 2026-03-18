import streamlit as st


def render_calculator():
    st.subheader("Support Calculator")
    st.caption("The same tools a BitMEX support agent uses when a user asks 'why was I liquidated?'")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Liquidation Price")
        entry_price = st.number_input("Entry Price ($)", value=85000, step=100)
        leverage = st.slider("Leverage", min_value=1, max_value=100, value=10)
        side = st.selectbox("Position Side", ["Long", "Short"])

        maintenance_margin = 0.005
        initial_margin = 1 / leverage

        if side == "Long":
            liq_price = entry_price * (1 - initial_margin + maintenance_margin)
        else:
            liq_price = entry_price * (1 + initial_margin - maintenance_margin)

        distance_pct = abs(entry_price - liq_price) / entry_price * 100
        color = "#ef5350" if side == "Long" else "#26a69a"

        st.markdown(f"""
        <div style='background:#1e1e2e;padding:16px;border-radius:8px;border-left:4px solid {color}'>
        <h3 style='color:{color};margin:0'>Liq. Price: ${liq_price:,.2f}</h3>
        <p style='color:#aaa;margin:4px 0 0 0'>
            {distance_pct:.1f}% away from entry<br>
            Initial Margin: {initial_margin*100:.1f}% | Maint. Margin: 0.5%
        </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Funding Cost")
        position_size = st.number_input("Position Size (contracts)", value=10000, step=1000)
        holding_days = st.slider("Holding Period (days)", 1, 365, 30)
        funding_rate = st.number_input("Funding Rate (% per 8h)", value=0.01, format="%.4f") / 100

        payments_per_day = 3
        daily_cost_usd = (position_size / entry_price) * funding_rate * payments_per_day
        total_cost = daily_cost_usd * holding_days
        cost_pct = total_cost / (position_size / entry_price) * 100

        st.metric("Daily Funding Cost", f"${daily_cost_usd:.4f}")
        st.metric(f"Total over {holding_days} days", f"${total_cost:.4f}")
        st.metric("As % of position", f"{cost_pct:.4f}%")

    st.info("""
    **Support Tip:** If a user says their position was liquidated "too early",
    use this calculator to verify. Ask for their entry price, leverage, and side —
    you can reconstruct their exact liquidation price and show them the math.
    """)