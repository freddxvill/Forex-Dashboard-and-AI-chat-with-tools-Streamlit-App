import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import get_forex_data
from utils.llm_agent import get_llm_response

st.set_page_config(page_title="Forex Dashboard & AI Chat", layout="wide")

st.title("Forex Dashboard & AI Chat")

# Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    
    st.subheader("API Keys")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    gemini_api_key = st.text_input("Gemini API Key", type="password")
    alpha_vantage_key = st.text_input("Alpha Vantage API Key", type="password")
    
    api_provider = st.radio("Select LLM Provider", ["OpenAI", "Gemini"])

# Main Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Market Overview")
    
    # Filter Controls
    filter_col1, filter_col2 = st.columns([1, 1])
    with filter_col1:
        time_period = st.selectbox(
            "Select Time Period",
            options=["1mo", "3mo", "1y", "ytd", "max"],
            format_func=lambda x: {
                "1mo": "1 Month",
                "3mo": "3 Months",
                "1y": "1 Year",
                "ytd": "Year to Date",
                "max": "Max"
            }.get(x, x)
        )
    with filter_col2:
        if st.button("Update Data"):
            st.rerun()

    # Charts
    pairs = ["GC=F", "EURUSD=X", "JPY=X"] # GC=F (Gold), JPY=X (USD/JPY)
    # USDJPY in yfinance is usually JPY=X (USD/JPY) or similar. 
    # Let's verify standard tickers. XAUUSD=X (Gold), EURUSD=X (Euro), JPY=X (USD/JPY).
    
    for pair in pairs:
        try:
            data = get_forex_data(pair, period=time_period)
            if not data.empty:
                fig = go.Figure(data=[go.Candlestick(x=data.index,
                                open=data['Open'],
                                high=data['High'],
                                low=data['Low'],
                                close=data['Close'])])
                
                title = pair
                if pair == "JPY=X": title = "USD/JPY"
                if pair == "GC=F": title = "Gold (Futures) - Proxy for XAU/USD"
                if pair == "EURUSD=X": title = "EUR/USD"

                fig.update_layout(title=title, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No data found for {pair}")
        except Exception as e:
            st.error(f"Error loading {pair}: {e}")

with col2:
    st.header("AI Analyst")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about market trends..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if (api_provider == "OpenAI" and not openai_api_key) or (api_provider == "Gemini" and not gemini_api_key):
                response = "Please provide an API Key in the sidebar."
                st.write(response)
            else:
                with st.spinner("Analyzing..."):
                    try:
                        # Construct config for the agent
                        config = {
                            "provider": api_provider,
                            "openai_key": openai_api_key,
                            "gemini_key": gemini_api_key,
                            "av_key": alpha_vantage_key
                        }
                        response = get_llm_response(prompt, config)
                        st.markdown(response)
                    except Exception as e:
                        response = f"Error: {e}"
                        st.error(response)
                        
        st.session_state.messages.append({"role": "assistant", "content": response})
