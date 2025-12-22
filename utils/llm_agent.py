import os
import requests
import google.generativeai as genai
from google.generativeai.types import content_types

# Global variable to store the Alpha Vantage key dynamically
ALPHA_VANTAGE_API_KEY = None

API_BASE_URL = "https://www.alphavantage.co/query"

def call_api_tool(function_name, **params):
    """
    Llama a un endpoint específico de Alpha Vantage usando la API estándar (GET).
    """
    if not ALPHA_VANTAGE_API_KEY:
        return {"error": "Alpha Vantage API Key not set."}
        
    payload = {"function": function_name, **params}
    try:
        response = requests.get(API_BASE_URL, params={**payload, "apikey": ALPHA_VANTAGE_API_KEY})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- Tool Definitions ---

def get_fx_daily(from_symbol: str, to_symbol: str):
    """
    Obtiene los precios diarios de Forex para un par de divisas.
    Args:
        from_symbol: Símbolo de la divisa de origen (ej. "EUR")
        to_symbol: Símbolo de la divisa de destino (ej. "USD")
    Returns:
        Datos JSON con series temporales diarias.
    """
    return call_api_tool("FX_DAILY", from_symbol=from_symbol, to_symbol=to_symbol)

def get_fx_intraday(from_symbol: str, to_symbol: str, interval: str = "5min"):
    """
    Obtiene los precios intradía de Forex para un par de divisas.
    Args:
        from_symbol: Símbolo de la divisa de origen (ej. "EUR")
        to_symbol: Símbolo de la divisa de destino (ej. "USD")
        interval: Intervalo de tiempo (ej. "1min", "5min", "15min", "30min", "60min")
    Returns:
        Datos JSON con series temporales intradía.
    """
    return call_api_tool("FX_INTRADAY", from_symbol=from_symbol, to_symbol=to_symbol, interval=interval)

def get_fx_weekly(from_symbol: str, to_symbol: str):
    """
    Obtiene los precios semanales de Forex para un par de divisas.
    Returns:
        Datos JSON con series temporales semanales.
    """
    return call_api_tool("FX_WEEKLY", from_symbol=from_symbol, to_symbol=to_symbol)

def get_fx_monthly(from_symbol: str, to_symbol: str):
    """
    Obtiene los precios mensuales de Forex para un par de divisas.
    Returns:
        Datos JSON con series temporales mensuales.
    """
    return call_api_tool("FX_MONTHLY", from_symbol=from_symbol, to_symbol=to_symbol)

def get_news_sentiment(tickers: str = None, topics: str = None, time_from: str = None, time_to: str = None, limit: int = 50):
    """
    Obtiene noticias financieras con análisis de sentimiento.
    """
    params = {}
    if tickers: params["tickers"] = tickers
    if topics: params["topics"] = topics
    if time_from: params["time_from"] = time_from
    if time_to: params["time_to"] = time_to
    params["limit"] = limit
    return call_api_tool("NEWS_SENTIMENT", **params)

def _build_symbol(from_symbol=None, to_symbol=None, symbol=None):
    if symbol:
        return symbol.upper()
    if from_symbol and to_symbol:
        return f"{from_symbol.upper()}{to_symbol.upper()}"
    return None

def get_sma(from_symbol: str = None, to_symbol: str = None, symbol: str = None, interval: str = "daily", time_period: int = 10, series_type: str = "close"):
    """Obtiene el Simple Moving Average (SMA)."""
    sym = _build_symbol(from_symbol, to_symbol, symbol)
    if not sym: return {"error": "Missing symbol info"}
    return call_api_tool("SMA", symbol=sym, interval=interval, time_period=time_period, series_type=series_type)

def get_ema(from_symbol: str = None, to_symbol: str = None, symbol: str = None, interval: str = "daily", time_period: int = 10, series_type: str = "close"):
    """Obtiene el Exponential Moving Average (EMA)."""
    sym = _build_symbol(from_symbol, to_symbol, symbol)
    if not sym: return {"error": "Missing symbol info"}
    return call_api_tool("EMA", symbol=sym, interval=interval, time_period=time_period, series_type=series_type)

def get_macd(from_symbol: str = None, to_symbol: str = None, symbol: str = None, interval: str = "daily", series_type: str = "close", fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
    """Obtiene el MACD."""
    sym = _build_symbol(from_symbol, to_symbol, symbol)
    if not sym: return {"error": "Missing symbol info"}
    return call_api_tool("MACD", symbol=sym, interval=interval, series_type=series_type, fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)

def get_rsi(from_symbol: str = None, to_symbol: str = None, symbol: str = None, interval: str = "daily", time_period: int = 14, series_type: str = "close"):
    """Obtiene el RSI."""
    sym = _build_symbol(from_symbol, to_symbol, symbol)
    if not sym: return {"error": "Missing symbol info"}
    return call_api_tool("RSI", symbol=sym, interval=interval, time_period=time_period, series_type=series_type)

def get_adx(from_symbol: str = None, to_symbol: str = None, symbol: str = None, interval: str = "daily", time_period: int = 14):
    """Obtiene el ADX."""
    sym = _build_symbol(from_symbol, to_symbol, symbol)
    if not sym: return {"error": "Missing symbol info"}
    return call_api_tool("ADX", symbol=sym, interval=interval, time_period=time_period)

def get_bbands(from_symbol: str = None, to_symbol: str = None, symbol: str = None, interval: str = "daily", time_period: int = 20, series_type: str = "close", nbdevup: int = 2, nbdevdn: int = 2, matype: int = 0):
    """Obtiene las Bollinger Bands."""
    sym = _build_symbol(from_symbol, to_symbol, symbol)
    if not sym: return {"error": "Missing symbol info"}
    return call_api_tool("BBANDS", symbol=sym, interval=interval, time_period=time_period, series_type=series_type, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype)

# --- Main Agent Logic ---

def get_llm_response(prompt, config):
    """
    Main entry point called by the Streamlit app.
    Adapts the specific Gemini tool logic.
    """
    global ALPHA_VANTAGE_API_KEY
    
    provider = config.get("provider")
    gemini_key = config.get("gemini_key")
    av_key = config.get("av_key")
    
    if provider != "Gemini":
        return "Advanced Forex Tools are currently only available with Gemini. Please select Gemini as the provider."

    if not gemini_key or not av_key:
        return "Please provide both Gemini and Alpha Vantage API keys."

    # Set keys
    ALPHA_VANTAGE_API_KEY = av_key
    genai.configure(api_key=gemini_key)
    
    tools_list = [
        get_fx_daily, get_fx_intraday, get_fx_weekly, get_fx_monthly, 
        get_news_sentiment, get_sma, get_ema, get_macd, get_rsi, 
        get_adx, get_bbands
    ]
    
    # Initialize Model with Tools
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        tools=tools_list
    )
    
    chat = model.start_chat()
    
    # Send initial prompt with instructions + user query
    # We combine the system instruction-like prefix with the user query for the single turn or multi-turn
    full_prompt = (
        f"Eres un analista experto en Forex. Usa los tools disponibles para obtener precios, indicadores técnicos, noticias y sentimientos. "
        f"Analiza la consulta del usuario: '{prompt}'. Proporciona un análisis detallado, incluyendo tendencias basadas en promedios móviles, "
        f"MACD, RSI, ADX, Bollinger Bands, precios recientes, sentimientos de noticias y recomendaciones basadas en datos.\n"
        f"IMPORTANTE: Si falta un parámetro obligatorio (como 'symbol'), intenta inferirlo o preguntar. Para 'symbol', usa el formato estándar (ej. EURUSD, USDJPY)."
    )
    
    try:
        response = chat.send_message(full_prompt)
        
        # Helper to handle tool calls
        # Loop while the model asks for function calls
        max_turns = 10
        turn = 0
        
        while response.parts and any(part.function_call for part in response.parts) and turn < max_turns:
            turn += 1
            parts = []
            for part in response.parts:
                if part.function_call:
                    func_name = part.function_call.name
                    func_args = dict(part.function_call.args)
                    
                    # Call the appropriate function
                    # Using a mapping would be cleaner but if-elif is safe enough here
                    func_response = {"error": "Unknown function"}
                    
                    if func_name == "get_fx_daily": func_response = get_fx_daily(**func_args)
                    elif func_name == "get_fx_intraday": func_response = get_fx_intraday(**func_args)
                    elif func_name == "get_fx_weekly": func_response = get_fx_weekly(**func_args)
                    elif func_name == "get_fx_monthly": func_response = get_fx_monthly(**func_args)
                    elif func_name == "get_news_sentiment": func_response = get_news_sentiment(**func_args)
                    elif func_name == "get_sma": func_response = get_sma(**func_args)
                    elif func_name == "get_ema": func_response = get_ema(**func_args)
                    elif func_name == "get_macd": func_response = get_macd(**func_args)
                    elif func_name == "get_rsi": func_response = get_rsi(**func_args)
                    elif func_name == "get_adx": func_response = get_adx(**func_args)
                    elif func_name == "get_bbands": func_response = get_bbands(**func_args)
                    
                    # Append response part
                    parts.append(
                        content_types.to_part({
                            "function_response": {
                                "name": func_name,
                                "response": func_response
                            }
                        })
                    )
            
            # Send function responses back to the model
            response = chat.send_message(parts)
            
        return response.text
    except Exception as e:
        return f"Error interacting with Gemini: {str(e)}"
