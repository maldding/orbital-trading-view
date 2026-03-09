import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_provider import DataProvider
from indicators import IndicatorCalculator

# Page config
st.set_page_config(page_title="Binance Chart App Pro", layout="wide")

st.title("📈 Binance Advanced Chart")

# Sidebar for controls
st.sidebar.header("Data Settings")
coin = st.sidebar.selectbox("Select Coin", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"])
timeframe = st.sidebar.selectbox("Select Timeframe", ["1m", "5m", "1h", "4h", "1d"], index=2)
limit = st.sidebar.slider("Number of Candles", min_value=100, max_value=1500, value=500)

st.sidebar.markdown("---")
st.sidebar.header("Indicator Settings")

# EMA Settings
with st.sidebar.expander("EMA Settings", expanded=False):
    col1, col2 = st.columns([2, 1])
    ema1_p = col1.number_input("EMA 1 Period", value=20, min_value=0, key="ema1_p")
    ema1_on = col2.checkbox("On", value=True, key="ema1_on")
    
    col1, col2 = st.columns([2, 1])
    ema2_p = col1.number_input("EMA 2 Period", value=50, min_value=0, key="ema2_p")
    ema2_on = col2.checkbox("On", value=True, key="ema2_on")
    
    col1, col2 = st.columns([2, 1])
    ema3_p = col1.number_input("EMA 3 Period", value=200, min_value=0, key="ema3_p")
    ema3_on = col2.checkbox("On", value=False, key="ema3_on")
    
    ema_configs = []
    if ema1_on and ema1_p > 0: ema_configs.append(ema1_p)
    if ema2_on and ema2_p > 0: ema_configs.append(ema2_p)
    if ema3_on and ema3_p > 0: ema_configs.append(ema3_p)

# Bollinger Bands Settings
with st.sidebar.expander("Bollinger Bands Settings", expanded=False):
    bb_on = st.checkbox("BB On", value=True)
    bb_length = st.number_input("BB Period", value=20, min_value=1)
    bb_std = st.number_input("BB Std Dev", value=2.0, min_value=0.1, step=0.1)
    col1, col2, col3 = st.columns(3)
    bb_up_on = col1.checkbox("Upper", value=True)
    bb_mid_on = col2.checkbox("Middle", value=True)
    bb_low_on = col3.checkbox("Lower", value=True)

# Sub-charts configuration
st.sidebar.header("Sub-charts Settings")
sub_chart_options = ["Volume", "MACD", "RSI", "ATR"]
active_sub_charts = st.sidebar.multiselect("Active Sub-charts & Order", 
                                          options=sub_chart_options, 
                                          default=sub_chart_options)

# Detailed sub-chart params
with st.sidebar.expander("Indicator Details", expanded=False):
    rsi_length = st.number_input("RSI Period", value=14, min_value=1)
    st.markdown("---")
    macd_fast = st.number_input("MACD Fast", value=12, min_value=1)
    macd_slow = st.number_input("MACD Slow", value=26, min_value=1)
    macd_signal = st.number_input("MACD Signal", value=9, min_value=1)
    st.markdown("---")
    atr_length = st.number_input("ATR Period", value=14, min_value=1)
    st.markdown("---")
    vol_ema_on = st.checkbox("Volume EMA On", value=True)
    vol_ema_length = st.number_input("Volume EMA Period", value=20, min_value=0)

# Collect all params for calculator
params = {
    'ema_periods': ema_configs,
    'bb_length': bb_length,
    'bb_std': bb_std,
    'rsi_length': rsi_length,
    'macd_fast': macd_fast,
    'macd_slow': macd_slow,
    'macd_signal': macd_signal,
    'atr_length': atr_length,
    'vol_ema_length': vol_ema_length if vol_ema_on else 0
}

@st.cache_data(ttl=60)
def get_data(symbol, tf, lim, p):
    provider = DataProvider()
    try:
        df = provider.fetch_ohlcv(symbol, timeframe=tf, limit=lim)
        if df is not None:
            calc = IndicatorCalculator()
            df = calc.add_indicators(df, p)
        return df, None
    except Exception as e:
        return None, str(e)

data, error_msg = get_data(coin, timeframe, limit, params)

if data is not None and not data.empty:
    # Build dynamic layout
    rows = 1 + len(active_sub_charts)
    row_heights = [0.5] + [0.5 / len(active_sub_charts) if active_sub_charts else 0] * len(active_sub_charts)
    
    # Adjust heights to look better
    if len(active_sub_charts) == 4:
        row_heights = [0.4, 0.15, 0.15, 0.15, 0.15]
    elif len(active_sub_charts) == 3:
        row_heights = [0.5, 0.17, 0.17, 0.16]
    elif len(active_sub_charts) == 2:
        row_heights = [0.6, 0.2, 0.2]
    elif len(active_sub_charts) == 1:
        row_heights = [0.7, 0.3]
        
    titles = ["Main Chart"] + active_sub_charts
    
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=row_heights,
                        subplot_titles=titles)

    # 1. Main Chart
    fig.add_trace(go.Candlestick(x=data['timestamp'],
                                 open=data['open'], high=data['high'],
                                 low=data['low'], close=data['close'],
                                 name='Candlesticks'), row=1, col=1)
    
    # EMAs
    colors = ['orange', 'cyan', 'magenta']
    for i, period in enumerate(params['ema_periods']):
        col_name = f'EMA_{period}'
        if col_name in data.columns:
            fig.add_trace(go.Scatter(x=data['timestamp'], y=data[col_name], 
                                     line=dict(color=colors[i % len(colors)], width=1.5), 
                                     name=f'EMA {period}'), row=1, col=1)
    
    # BB
    if bb_on:
        bbl_col = f'BBL_{bb_length}'
        bbm_col = f'BBM_{bb_length}'
        bbu_col = f'BBU_{bb_length}'
        if bbu_col in data.columns:
            if bb_up_on:
                fig.add_trace(go.Scatter(x=data['timestamp'], y=data[bbu_col], line=dict(color='rgba(128, 128, 128, 0.5)', dash='dash'), name='BB Upper'), row=1, col=1)
            if bb_low_on:
                fill = 'tonexty' if bb_up_on else None
                fig.add_trace(go.Scatter(x=data['timestamp'], y=data[bbl_col], line=dict(color='rgba(128, 128, 128, 0.5)', dash='dash'), fill=fill, name='BB Lower'), row=1, col=1)
            if bb_mid_on:
                fig.add_trace(go.Scatter(x=data['timestamp'], y=data[bbm_col], line=dict(color='rgba(173, 216, 230, 0.8)'), name='BB Middle'), row=1, col=1)

    # Add active sub-charts
    for idx, chart_name in enumerate(active_sub_charts):
        row_idx = idx + 2
        
        if chart_name == "Volume":
            fig.add_trace(go.Bar(x=data['timestamp'], y=data['volume'], name='Volume', marker_color='rgba(100, 149, 237, 0.6)'), row=row_idx, col=1)
            vol_ema_col = f'VOL_EMA_{vol_ema_length}'
            if vol_ema_on and vol_ema_col in data.columns:
                fig.add_trace(go.Scatter(x=data['timestamp'], y=data[vol_ema_col], line=dict(color='yellow', width=1.5), name=f'Vol EMA {vol_ema_length}'), row=row_idx, col=1)
        
        elif chart_name == "MACD":
            m_col = f'MACD_{macd_fast}_{macd_slow}_{macd_signal}'
            ms_col = f'MACDs_{macd_fast}_{macd_slow}_{macd_signal}'
            mh_col = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal}'
            if m_col in data.columns:
                fig.add_trace(go.Scatter(x=data['timestamp'], y=data[m_col], name='MACD', line=dict(color='blue', width=1.5)), row=row_idx, col=1)
                fig.add_trace(go.Scatter(x=data['timestamp'], y=data[ms_col], name='Signal', line=dict(color='orange', width=1.5)), row=row_idx, col=1)
                colors_hist = ['red' if val < 0 else 'green' for val in data[mh_col]]
                fig.add_trace(go.Bar(x=data['timestamp'], y=data[mh_col], name='Histogram', marker_color=colors_hist), row=row_idx, col=1)
        
        elif chart_name == "RSI":
            rsi_col = f'RSI_{rsi_length}'
            if rsi_col in data.columns:
                fig.add_trace(go.Scatter(x=data['timestamp'], y=data[rsi_col], name='RSI', line=dict(color='purple', width=1.5)), row=row_idx, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="rgba(255, 0, 0, 0.5)", row=row_idx, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="rgba(0, 255, 0, 0.5)", row=row_idx, col=1)
        
        elif chart_name == "ATR":
            atr_col = f'ATR_{atr_length}'
            if atr_col in data.columns:
                fig.add_trace(go.Scatter(x=data['timestamp'], y=data[atr_col], name='ATR', line=dict(color='cyan', width=1.5)), row=row_idx, col=1)

    fig.update_layout(height=1400, showlegend=True, 
                      xaxis_rangeslider_visible=False,
                      template="plotly_dark",
                      hovermode='x unified',
                      dragmode='pan')
    
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
    
    st.info("💡 팁: 설정을 변경하면 실시간으로 차트가 업데이트되며, 보조지표 순서도 드래그하여 조정할 수 있습니다.")
else:
    st.error("데이터를 불러오지 못했습니다. 인터넷 연결을 확인하거나 잠시 후 다시 시도해 주세요.")
    if error_msg:
        st.warning(f"Error Details: {error_msg}")
