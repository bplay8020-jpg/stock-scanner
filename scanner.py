import streamlit as st
import yfinance as yf
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Stock Gap Scanner", layout="wide")

st.title("📉 Gap & Crap Scanner")
st.markdown("Find stocks under **$50** with **Market Cap < $5B** gapping up **>3%**.")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("Scanner Settings")
    min_gap = st.slider("Min Gap %", 1.0, 20.0, 3.0)
    min_price = st.number_input("Min Price ($)", value=2.0)
    max_price = st.number_input("Max Price ($)", value=50.0)
    max_cap_b = st.number_input("Max Cap (Billions)", value=5.0)

# --- STOCK LIST (DEC 2025) ---
tickers_to_scan = [
    "MARA", "RIOT", "CLSK", "HUT", "BITF", "IREN", "WULF", "CIFR", "BTBT", 
    "MSTR", "COIN", "PLTR", "SOFI", "AI", "BBAI", "SOUN", "IONQ", "LCID", 
    "RIVN", "NKLA", "GOEV", "PSNY", "NIO", "XPEV", "LI", "QS", "RKLB", 
    "ASTS", "LUNR", "SPCE", "HOOD", "UPST", "AFRM", "OPEN", "DKNG", "AMC", 
    "GME", "BB", "TLRY", "CGC", "SNDL", "DNA", "CRSP", "NTLA"
]

def get_data(tickers):
    opportunities = []
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(tickers)
    
    for i, ticker in enumerate(tickers):
        # Update progress
        progress_bar.progress((i + 1) / total)
        status_text.text(f"Scanning {ticker}...")
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            
            if len(hist) < 2:
                continue

            prev_close = hist['Close'].iloc[-2]
            current_price = hist['Close'].iloc[-1]
            gap_percent = ((current_price - prev_close) / prev_close) * 100
            
            # Filters
            if not (min_price <= current_price <= max_price):
                continue
            if gap_percent < min_gap:
                continue
            
            # Cap Check (Simplified for speed)
            try:
                cap = stock.info.get('marketCap', 0)
            except:
                cap = 0
            
            if cap > (max_cap_b * 1_000_000_000):
                continue
            
            opportunities.append({
                'Ticker': ticker,
                'Price': f"${current_price:.2f}",
                'Gap': f"+{gap_percent:.1f}%",
                'RawGap': gap_percent, # Hidden column for sorting
                'Volume': hist['Volume'].iloc[-1],
                'Cap (B)': f"${cap / 1_000_000_000:.2f}B"
            })
            
        except Exception:
            continue
            
    status_text.empty()
    progress_bar.empty()
    return pd.DataFrame(opportunities)

# --- MAIN APP ---
if st.button("🚀 Run Scanner"):
    with st.spinner('Fetching market data...'):
        df = get_data(tickers_to_scan)
    
    if not df.empty:
        # Sort by biggest gap
        df_sorted = df.sort_values(by='RawGap', ascending=False)
        
        # Display as an interactive table
        st.success(f"Found {len(df)} opportunities!")
        st.dataframe(
            df_sorted[['Ticker', 'Price', 'Gap', 'Cap (B)', 'Volume']],
            use_container_width=True
        )
    else:
        st.warning("No stocks matched your criteria right now.")