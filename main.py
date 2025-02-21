import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

#  CONFIGURATION 
st.set_page_config(page_title="Stock Market Dashboard", layout="wide", page_icon="📈")

st.markdown("""
    <style>
        .stApp {background-color: #0e1117 !important;}
        .stTitle, .stHeader {color: white !important;}
        .stSubheader, .stMarkdown, .stText, .stDataFrame {color: #ffffff !important;}
        .stSidebar {background-color: #161a23 !important;}
    </style>
""", unsafe_allow_html=True)

#  HEADER 
st.markdown("<h1 style='text-align: center; color: white;'>📈 Stock Market Dashboard</h1>", unsafe_allow_html=True)

#  SIDEBAR 
st.sidebar.header("🔍 Stock Selection")
ticker = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, TSLA, GOOGL)", "AAPL").upper()
start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=90))
end_date = st.sidebar.date_input("End Date", datetime.today())

#  FETCH STOCK DATA 
@st.cache_data(ttl=600)
def get_stock_data(ticker, start, end):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start, end=end)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

data = get_stock_data(ticker, start_date, end_date)

#  FETCH COMPANY INFO
def get_company_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception as e:
        st.warning(f"Could not fetch company info: {e}")
        return None

company_info = get_company_info(ticker)

#  DISPLAY STOCK DATA
if data is not None and not data.empty:
    st.subheader(f"📌 Stock Performance: {ticker}")

    # COMPANY INFO 
    if company_info:
        st.sidebar.subheader("🏢 Company Info")
        st.sidebar.write(f"📌 Name:** {company_info.get('longName', 'N/A')}")
        st.sidebar.write(f"🏢 Sector:** {company_info.get('sector', 'N/A')}")
        st.sidebar.write(f"💼 Industry:** {company_info.get('industry', 'N/A')}")
        st.sidebar.write(f"📊 Market Cap:** {company_info.get('marketCap', 'N/A'):,}")
        st.sidebar.write(f"🌎 Country:** {company_info.get('country', 'N/A')}")
        st.sidebar.write(f"📅 Employees:** {company_info.get('fullTimeEmployees', 'N/A')}")
        st.sidebar.write(f"🌐 Website:** [{company_info.get('website', 'N/A')}]({company_info.get('website', '#')})")

    #  STOCK STATISTICS 
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📌 Latest Price", f"${data['Close'].iloc[-1]:.2f}")
    col2.metric("📈 Daily High", f"${data['High'].iloc[-1]:.2f}")
    col3.metric("📉 Daily Low", f"${data['Low'].iloc[-1]:.2f}")
    col4.metric("🔄 Volume", f"{data['Volume'].iloc[-1]:,}")

    #  HISTORICAL DATA 
    with st.expander("📜 View Historical Data"):
        st.write(data)

    #  STOCK PRICE CHART 
    fig = px.line(data, x=data.index, y="Close", title=f"{ticker} Closing Price",
                  template="plotly_dark", line_shape="spline", markers=True)
    fig.update_traces(line=dict(width=2), marker=dict(size=5))
    st.plotly_chart(fig, use_container_width=True)

    #  MOVING AVERAGES 
    st.sidebar.subheader("📊 Moving Averages")
    short_ma = st.sidebar.slider("Short-Term MA (days)", 5, 50, 10)
    long_ma = st.sidebar.slider("Long-Term MA (days)", 50, 200, 50)

    data[f"{short_ma}-Day MA"] = data["Close"].rolling(window=short_ma).mean()
    data[f"{long_ma}-Day MA"] = data["Close"].rolling(window=long_ma).mean()

    ma_fig = px.line(data, x=data.index, y=["Close", f"{short_ma}-Day MA", f"{long_ma}-Day MA"],
                     title=f"{ticker} Moving Averages", template="plotly_dark", line_shape="spline")
    ma_fig.update_traces(line=dict(width=2))
    st.plotly_chart(ma_fig, use_container_width=True)

    #  VOLUME ANALYSIS 
    st.subheader("📉 Volume Analysis")
    vol_fig = px.bar(data, x=data.index, y="Volume", title=f"{ticker} Trading Volume",
                     template="plotly_dark", color_discrete_sequence=["#00CC96"])
    st.plotly_chart(vol_fig, use_container_width=True)

else:
    st.warning("⚠ No data found. Please check the stock symbol or date range.")

#  FOOTER
st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'>🔹 Built with Streamlit, yFinance & Plotly | 🚀 Created by [Muhammad Rayyan]</p>", unsafe_allow_html=True)