import yfinance as yf

stock = yf.Ticker("AAPL")
data = stock.history(period="5d")

if len(data) >= 2:
    latest_price = data['Close'].iloc[-1]
    previous_price = data['Close'].iloc[-2]
    percent_change = ((latest_price - previous_price) / previous_price) * 100

    print("📊 Stock: Apple (AAPL)")
    print(f"💰 Latest Price: ${latest_price:.2f}")
    print(f"🔁 Change: {percent_change:.2f}%")
else:
    print("⚠️ Not enough data available for Apple stock.")
