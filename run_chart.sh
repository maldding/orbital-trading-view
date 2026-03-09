#!/bin/bash

# Move to the project directory
cd /home/orbital/setups/binance-chart-app

# 1. Kill any existing process on port 8501 to avoid 'port in use' errors
fuser -k 8501/tcp 2>/dev/null

# 2. Run the Binance Chart App
# Streamlit will automatically try to open your default browser.
# We use the virtual environment's python/streamlit to ensure all dependencies are found.
./venv/bin/streamlit run app.py --server.port 8501
