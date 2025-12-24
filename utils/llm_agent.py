import os
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

API_BASE_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_API_KEY = None

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

@tool
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

@tool
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

@tool
def get_fx_weekly(from_symbol: str, to_symbol: str):
    """
    Obtiene los precios semanales de Forex para un par de divisas.
    Args:
        from_symbol: Símbolo de la divisa de origen (ej. "EUR")
        to_symbol: Símbolo de la divisa de destino (ej. "USD")
    Returns:
        Datos JSON con series temporales semanales.
    """
    return call_api_tool("FX_WEEKLY", from_symbol=from_symbol, to_symbol=to_symbol)

@tool
def get_fx_monthly(from_symbol: str, to_symbol: str):
    """
    Obtiene los precios mensuales de Forex para un par de divisas.
    Args:
        from_symbol: Símbolo de la divisa de origen (ej. "EUR")
        to_symbol: Símbolo de la divisa de destino (ej. "USD")
    Returns:
        Datos JSON con series temporales mensuales.
    """
    return call_api_tool("FX_MONTHLY", from_symbol=from_symbol, to_symbol=to_symbol)

@tool
def get_news_sentiment(tickers: str = None, topics: str = None, time_from: str = None, time_to: str = None, limit: int = 50):
    """
    Obtiene noticias financieras con análisis de sentimiento de Alpha Vantage.
    Args:
        tickers: Tickers a buscar noticias (ej. "EUR,USD")
        topics: Temas a buscar (ej. "economy_fiscal")
        time_from: Fecha de inicio (YYYYMMDDTHHMM)
        time_to: Fecha de fin (YYYYMMDDTHHMM)
        limit: Límite de resultados
    """
    params = {}
    if tickers: params["tickers"] = tickers
    if topics: params["topics"] = topics
    if time_from: params["time_from"] = time_from
    if time_to: params["time_to"] = time_to
    params["limit"] = limit
    return call_api_tool("NEWS_SENTIMENT", **params)

# --- Main Agent Logic ---

def get_llm_response(prompt, config):
    """
    Main entry point called by the Streamlit app.
    Uses LangChain to support multiple providers.
    """
    global ALPHA_VANTAGE_API_KEY
    
    provider = config.get("provider")
    openai_key = config.get("openai_key")
    gemini_key = config.get("gemini_key")
    claude_key = config.get("claude_key")
    av_key = config.get("av_key")
    
    ALPHA_VANTAGE_API_KEY = av_key
    
    # Initialize appropriate Chat Model
    if provider == "Gemini":
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=gemini_key)
    elif provider == "OpenAI":
        llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)
    elif provider == "Claude":
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", anthropic_api_key=claude_key)
    else:
        return f"Unsupported provider: {provider}"

    tools = [get_fx_daily, get_fx_intraday, get_fx_weekly, get_fx_monthly, get_news_sentiment]
    
    # Load system prompt complement from file
    try:
        # Check both possible locations for the prompt file
        prompt_path = "utils/promp.txt"
        if not os.path.exists(prompt_path):
            prompt_path = "promp.txt"
            
        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt_complementario = file.read()
    except Exception:
        prompt_complementario = ""

    system_instruction = (
        "Eres un analista experto en Forex. Usa los tools disponibles para obtener precios, indicadores técnicos, noticias y sentimientos. "
        "Analiza la consulta del usuario y proporciona un análisis detallado, incluyendo tendencias basadas en promedios móviles, "
        "precios recientes, sentimientos de noticias y recomendaciones basadas en datos.\n"
        "IMPORTANTE: Si falta un parámetro obligatorio (como 'symbol'), intenta inferirlo o preguntar. Para 'symbol', usa el formato estándar (ej. EURUSD, USDJPY).\n"
        f"Información adicional del contexto: {prompt_complementario}\n"
        "Resume la info que hallaste y proporciona una recomendación final."
    )

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create Agent
    agent = create_tool_calling_agent(llm, tools, prompt_template)
    
    # Create Agent Executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    try:
        # We handle chat history in the Streamlit app, but here we pass an empty list for the single turn logic
        # or we could pass the full history if we wanted. For now, matching previous behavior.
        result = agent_executor.invoke({"input": prompt, "chat_history": []})
        return result["output"]
    except Exception as e:
        return f"Error interacting with {provider}: {str(e)}"
