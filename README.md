# Forex Dashboard con Asistencia Inteligente (Gemini)

Una aplicación web interactiva construida con Streamlit que combina un grafico de velas (candlestick charts) para pares de divisas en tiempo real con un analista de Forex impulsado por Inteligencia Artificial (Se puede usar con Gemini o OpenAI).

## Características

### 📊 Dashboard Financiero
- **Datos en tiempo real:** Visualización de velas (Candlestick charts) para:
    - **Oro (Futures)** (`GC=F`) - Proxy para XAU/USD
    - **EUR/USD**
    - **USD/JPY**
- **Filtros de Tiempo:** Ajusta los gráficos por 1 mes, 3 meses, 1 año, YTD o Max.
- **Auto-actualización:** Botón dedicado para refrescar los datos de mercado.

### 🤖 AI Financial Analyst
- **Chat Inteligente:** Integrado con **Google Gemini** (modelo `gemini-2.5-flash` o superior).
- **Herramientas Avanzadas (Alpha Vantage):** El agente tiene acceso a 11 herramientas financieras reales para responder tus preguntas con datos precisos:
    - **Precios:** `FX_DAILY`, `FX_INTRADAY`, `FX_WEEKLY`, `FX_MONTHLY`.
    - **Sentimiento:** `NEWS_SENTIMENT` (Noticias y análisis de sentimiento).
    - **Indicadores Técnicos:**
        - `SMA` (Simple Moving Average)
        - `EMA` (Exponential Moving Average)
        - `MACD` (Moving Average Convergence Divergence)
        - `RSI` (Relative Strength Index)
        - `ADX` (Average Directional Index)
        - `BBANDS` (Bollinger Bands)

## Requisitos Previos

- **Python 3.12+**
- **uv**: Un gestor de paquetes de Python extremadamente rápido.
- **API Keys**:
    - [Google Gemini API Key](https://aistudio.google.com/app/apikey)
    - [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key)

## Instalación

Este proyecto utiliza `uv` para la gestión de dependencias.

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/freddxvill/Forex-Dashboard-and-AI-chat-with-tools-Streamlit-App.git
    cd Forex-Dashboard-and-AI-chat-with-tools-Streamlit-App
    ```

2.  **Instalar dependencias:**
    ```bash
    uv sync
    ```

## Ejecución

Para iniciar la aplicación localmente:

```bash
uv run streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`.

## Docker

El proyecto incluye un `Dockerfile` optimizado. Para construir y ejecutar con Docker:

```bash
# Construir la imagen
docker build -t forex-dashboard .

# Ejecutar el contenedor
docker run -d -p 8501:8501 forex-dashboard
```

## Configuración en la App
Una vez abierta la aplicación, usa la barra lateral ("Settings") para ingresar tus API Keys. Estas no se guardan en disco, solo viven en la sesión del navegador/servidor.
