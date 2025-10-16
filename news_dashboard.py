# news_dashboard.py
import os
import json
from datetime import datetime, timedelta

import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.express as px

# Google Gemini (optional; if not configured we'll skip AI summaries)
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False

# Auto-refresh helper
from streamlit_autorefresh import st_autorefresh

# -------------------------
# CONFIG (use env vars)
# -------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NEWS_API_KEY   = os.environ.get("NEWS_API_KEY")
SUMMARY_FILE   = "latest_news.json"

STOCK_TICKERS = ["AAPL", "MSFT", "GOOGL"]
INDICES = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "NIKKEI 225": "^N225", "NIFTY 50": "^NSEI"}
CRYPTO_IDS = ["bitcoin", "ethereum", "solana"]
JOB_API = "........................................................."

FUEL_API_URL = os.environ.get("FUEL_API_URL")
FUEL_API_KEY = os.environ.get("FUEL_API_KEY")
FOOD_API_URL = os.environ.get("FOOD_API_URL")
FOOD_API_KEY = os.environ.get("FOOD_API_KEY")

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
AUTO_REFRESH_MS = 5 * 60 * 1000  # 5 minutes

# -------------------------
# Helper functions
# -------------------------
def fetch_stock(ticker, period="1mo", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        return df
    except Exception:
        return None

def fetch_latest_price(ticker):
    df = fetch_stock(ticker, period="5d")
    if df is None or df.empty or len(df) < 2:
        return None, None
    latest = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    pct = (latest - prev) / prev * 100
    return float(latest), float(pct)

def fetch_crypto_prices(ids):
    try:
        ids_str = ",".join(ids)
        url = f"..............................................................."
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def fetch_news_articles(api_key, page_size=5):
    if not api_key:
        return []
    url = "......................................................"
    params = {"category":"business","language":"en","pageSize":page_size,"apiKey":api_key}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("articles", [])
    except Exception:
        return []

def fetch_jobs(limit=5):
    try:
        r = requests.get(JOB_API, timeout=10)
        r.raise_for_status()
        jobs = r.json().get("jobs", [])[:limit]
        return jobs
    except Exception:
        return []

def fetch_fuel_prices():
    if FUEL_API_URL:
        try:
            headers = {"Authorization": f"Bearer {FUEL_API_KEY}"} if FUEL_API_KEY else {}
            r = requests.get(FUEL_API_URL, headers=headers, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception:
            pass
    return {"Petrol": 110.5, "Diesel": 97.8, "Crude Oil (USD/barrel)": 85.3}

def fetch_food_prices():
    if FOOD_API_URL:
        try:
            headers = {"Authorization": f"Bearer {FOOD_API_KEY}"} if FOOD_API_KEY else {}
            r = requests.get(FOOD_API_URL, headers=headers, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception:
            pass
    return {"Wheat (kg)": 45.5, "Rice (kg)": 60.2, "Milk (liter)": 55.0, "Egg (pc)": 6.5}

# AI helpers
def configure_gemini():
    if not HAS_GEMINI or not GEMINI_API_KEY:
        return False
    genai.configure(api_key=GEMINI_API_KEY)
    return True

def ai_summarize_text(prompt, model_name=GEMINI_MODEL):
    if not HAS_GEMINI or not GEMINI_API_KEY:
        return "AI not configured."
    try:
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"[AI error] {e}"

def ai_sentiment(headlines, model_name=GEMINI_MODEL):
    if not headlines:
        return "No headlines."
    prompt = "Read these news headlines and answer in JSON with fields: overall_sentiment (Positive/Neutral/Negative) and one_sentence_explanation.\n\nHeadlines:\n"
    for h in headlines:
        prompt += "- " + h + "\n"
    prompt += "\nAnswer concisely."
    return ai_summarize_text(prompt, model_name=model_name)

def save_summaries(summaries):
    try:
        with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
            json.dump(summaries, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# -------------------------
# Streamlit UI
# -------------------------
st_autorefresh(interval=AUTO_REFRESH_MS, key="autorefresh")
st.set_page_config(page_title="SmartStock & News AI", layout="wide")
st.title("📊 SmartStock & News AI — Daily Insights")
st.markdown(f"*Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

left_col, mid_col, right_col = st.columns([2, 4, 2])

# LEFT: Stocks, Fuel, Food, Crypto, Indices
with left_col:
    st.header("💹 Markets & Prices")

    st.subheader("Stocks (latest close)")
    for t in STOCK_TICKERS:
        price, pct = fetch_latest_price(t)
        if price is None:
            st.write(f"**{t}**: data not available")
        else:
            if pct >= 0:
                st.success(f"**{t}**: ${price:.2f}  ▲ {pct:.2f}%")
            else:
                st.error(f"**{t}**: ${price:.2f}  ▼ {pct:.2f}%")

    st.markdown("---")
    st.subheader("Global Indices")
    for name, symbol in INDICES.items():
        try:
            df_idx = fetch_stock(symbol, period="5d")
            if df_idx is not None and not df_idx.empty:
                last_close = df_idx['Close'].iloc[-1]
                st.write(f"{name}: {last_close} Ticker {symbol}")
            else:
                st.write(f"{name}: N/A")
        except Exception:
            st.write(f"{name}: N/A")

    st.markdown("---")
    st.subheader("⛽ Fuel & Crude")
    for k, v in fetch_fuel_prices().items():
        st.write(f"**{k}**: {v}")

    st.markdown("---")
    st.subheader("🍎 Food Prices (local)")
    for k, v in fetch_food_prices().items():
        st.write(f"**{k}**: {v}")

    st.markdown("---")
    st.subheader("🪙 Crypto (USD)")
    cryptos = fetch_crypto_prices(CRYPTO_IDS)
    if cryptos:
        for cid in CRYPTO_IDS:
            val = cryptos.get(cid, {}).get("usd")
            st.write(f"**{cid.capitalize()}**: ${val}" if val else f"**{cid.capitalize()}**: N/A")
    else:
        st.write("Crypto data unavailable")

# MIDDLE: News summaries, sentiment, charts
with mid_col:
    st.header("📰 AI News — Summaries & Market View")
    articles = fetch_news_articles(NEWS_API_KEY, page_size=6)

    summaries = []
    headlines = []

    genai_available = configure_gemini()

    for i, art in enumerate(articles, start=1):
        title = art.get("title", "No title")
        desc = art.get("description") or ""
        url = art.get("url", "")
        headlines.append(title)
        prompt = f"Summarize the following news article in 2 short lines for a technical finance audience:\n\nTitle: {title}\nDescription: {desc}"
        summary = ai_summarize_text(prompt) if genai_available else desc or "Summary not available"
        summaries.append({"title": title, "url": url, "summary": summary})

        st.markdown(f"### 📰 {i}. {title}")
        st.markdown(f"🔗 [Read full article]({url})")
        st.info(summary)
        st.markdown("---")

    save_summaries(summaries)

    st.subheader("📊 Market Sentiment (from headlines)")
    if genai_available and headlines:
        sentiment = ai_sentiment(headlines)
        st.success(sentiment)
    elif headlines:
        st.info("AI not configured — sentiment skipped.")
    else:
        st.info("No headlines found.")

    st.subheader("🧠 AI Market Summary")
    if genai_available:
        overview_prompt = "Using the following headlines, give a concise 3-line market summary mentioning stocks, commodities or risks:\n" + "\n".join(["- " + h for h in headlines])
        overview = ai_summarize_text(overview_prompt)
        st.success(overview)
    else:
        st.info("AI not configured — overview skipped.")

    st.markdown("---")
    st.subheader("📈 Stock Trends (1 month)")

    try:
        for sample in STOCK_TICKERS:
            df_sample = fetch_stock(sample, period="1mo")
            if df_sample is not None and not df_sample.empty:
                df_sample = df_sample.reset_index()
                df_sample.columns = [col[0] if isinstance(col, tuple) else col for col in df_sample.columns]

                # Create color column: green if close increased, red if decreased
                df_sample['color'] = ['green' if df_sample['Close'].iloc[i] >= df_sample['Close'].iloc[i-1] else 'red'
                                      for i in range(len(df_sample))]
                df_sample['color'][0] = 'green'  # first day default

                fig = px.scatter(df_sample, x="Date", y="Close", color='color', color_discrete_map={'green':'green','red':'red'},
                                 title=f"{sample} - 1 month Close", hover_data=['Close'])

                # Add line connecting the points
                fig.add_traces(px.line(df_sample, x="Date", y="Close").data)

                # Set background to light blue
                fig.update_layout(plot_bgcolor='lightblue', paper_bgcolor='lightblue')

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write(f"No chart data for {sample}.")
    except Exception as e:
        st.write("Chart error:", e)

# RIGHT: Jobs, events, alerts
with right_col:
    st.header("💼 Jobs & Events")

    st.subheader("🔎 Latest Remote Dev Jobs")
    jobs = fetch_jobs(limit=5)
    if jobs:
        for j in jobs:
            st.markdown(f"**{j.get('title')}**")
            st.write(f"Company: {j.get('company_name')}")
            st.markdown(f"[Apply]({j.get('url')})")
            st.markdown("---")
    else:
        st.write("No jobs found or API failed.")

    st.subheader("📅 Upcoming Economic Events")
    events = [
        {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "event": "CPI Release (Country X)"},
        {"date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), "event": "Central Bank Meeting"},
        {"date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"), "event": "Unemployment Rate (Country Y)"},
    ]
    for ev in events:
        st.write(f"📅 {ev['date']} — {ev['event']}")

    st.markdown("---")
    st.subheader("🔔 Alerts")
    alert_triggered = False
    for t in STOCK_TICKERS:
        price, pct = fetch_latest_price(t)
        if pct is None:
            continue
        if abs(pct) >= 3:
            alert_triggered = True
            st.warning(f"🚀 {t} moved up {pct:.2f}% today" if pct > 0 else f"⚠️ {t} dropped {pct:.2f}% today")
    if not alert_triggered:
        st.write("No alerts. Markets stable.")

st.markdown("---")
st.caption("Built with yfinance, NewsAPI, CoinGecko, Google Gemini (optional). Configure API keys via environment variables.")

