import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import json
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from datetime import datetime

with open("final_prices.json", "r") as file:
    data = json.load(file)

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

predictions = [
    ("SHEL", "Formula 1", 0.03),
    ("AAPL", "Soccer", 0.02),
    ("RACE", "Formula 1", -0.01),
    ("NFLX", "Football", -0.03)
]

def create_prediction_box(ticker, sport, percent_change):
    color = "green" if percent_change > 0 else "red"
    return f"""
    <div style="background-color:{color}; padding: 20px; border-radius: 10px; text-align: center;">
        <h4>{ticker}</h4>
        <p>{sport}</p>
        <p><strong>{percent_change * 100:.2f}%</strong></p>
    </div>
    """

if 'page' not in st.session_state:
    st.session_state.page = "Main Page"

if st.session_state.page == "Main Page":
    st.sidebar.empty()

    st.title("BrandBull")
    st.subheader("Today's Stock Picks")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(create_prediction_box(*predictions[0]), unsafe_allow_html=True)
    with col2:
        st.markdown(create_prediction_box(*predictions[1]), unsafe_allow_html=True)
    with col3:
        st.markdown(create_prediction_box(*predictions[2]), unsafe_allow_html=True)
    with col4:
        st.markdown(create_prediction_box(*predictions[3]), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("View More"):
        st.session_state.page = "Stock Analysis"
        st.experimental_rerun()

elif st.session_state.page == "Stock Analysis":
    st.sidebar.header("Select Stock Ticker")
    tickers = sorted(df['ticker'].unique())
    selected_ticker = st.sidebar.radio("Choose a stock ticker:", tickers)

    filtered_df = df[df['ticker'] == selected_ticker]

    earliest_date = filtered_df['date'].min()
    latest_date = filtered_df['date'].max()

    start_date_slider = earliest_date - pd.DateOffset(years=1)
    start_date_slider = start_date_slider.date()

    latest_date_slider = latest_date.date()

    start_date_slider, end_date_slider = st.slider(
        f"Select Date Range for {selected_ticker}",
        min_value=start_date_slider,
        max_value=latest_date_slider,
        value=(start_date_slider, latest_date_slider),
        format="YYYY-MM-DD"
    )

    start_date_slider = pd.Timestamp(start_date_slider)
    end_date_slider = pd.Timestamp(end_date_slider)

    stock_data = yf.download(selected_ticker, start=start_date_slider, end=end_date_slider)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(stock_data.index, stock_data['Close'], label="Stock Price", color="blue")

    for i, row in filtered_df.iterrows():
        sport = row["sport"].strip().lower()
        threshold = 0.75 if sport == "formula 1" else 0.5
        color = "green" if float(row["outcome"]) > threshold else "red"

        if start_date_slider <= row['date'] <= end_date_slider:
            closest_date_idx = np.abs(stock_data.index.date - row["date"].date()).argmin()
            closest_date = stock_data.index[closest_date_idx]

            ax.scatter(closest_date, stock_data['Close'].iloc[closest_date_idx], color=color, s=50, edgecolor="black")

    green_patch = mpatches.Patch(color='green', label='Won Game (Outcome > threshold)')
    red_patch = mpatches.Patch(color='red', label='Lost Game (Outcome <= threshold)')
    ax.legend(handles=[green_patch, red_patch, plt.Line2D([0], [0], color="blue", lw=2, label="Stock Price")])

    ax.set_xlabel("Date")
    ax.set_ylabel("Stock Price ($)")
    ax.set_title(f"Stock Price and Game Outcomes for {selected_ticker}")

    st.pyplot(fig)

    if st.button("Back to Main Page"):
        st.session_state.page = "Main Page"
        st.experimental_rerun()
