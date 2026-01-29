import yfinance as yf
import pandas as pd
import time
import os
import threading
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

latest_signal = {
    'Timestamp': datetime.now().strftime('%H:%M:%S'),
    'Asset': 'CALIBRANDO',
    'Direction': 'AGUARDE',
    'Expiration': '1 min',
    'Price': 0.0,
    'Confidence': 'PROCESSANDO',
    'rsi': 50.0,
    'trend': 'NEUTRAL',
    'type': 'INITIAL'
}

ASSETS_MAP = {
    'EURUSD': 'EURUSD=X',
    'GBPUSD': 'GBPUSD=X',
    'USDJPY': 'USDJPY=X',
    'BTCUSD': 'BTC-USD',
    'ETHUSD': 'ETH-USD',
    'GOLD': 'GC=F'
}

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def generate_real_market_signals():
    global latest_signal
    print("MOTOR DE ANALISE REAL INICIADO...", flush=True)
    while True:
        try:
            asset_ids = list(ASSETS_MAP.keys())
            name = random.choice(asset_ids)
            symbol = ASSETS_MAP[name]
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1h", interval="1m")
            if df.empty or len(df) < 20:
                time.sleep(5)
                continue
            current_price = df['Close'].iloc[-1]
            df['RSI'] = calculate_rsi(df['Close'])
            current_rsi = df['RSI'].iloc[-1]
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            ema20 = df['EMA20'].iloc[-1]
            ema50 = df['EMA50'].iloc[-1]
            trend = 'UP' if ema20 > ema50 else 'DOWN'
            direction = "WAIT"
            confidence = "BAIXA"
            if current_rsi < 35 and trend == 'UP':
                direction = "BUY"
                confidence = "ALTA (95%)"
            elif current_rsi > 65 and trend == 'DOWN':
                direction = "SELL"
                confidence = "ALTA (95%)"
            elif current_rsi < 30:
                direction = "BUY"
                confidence = "MEDIA (85%)"
            elif current_rsi > 70:
                direction = "SELL"
                confidence = "MEDIA (85%)"
            if direction != "WAIT":
                latest_signal = {
                    'Timestamp': datetime.now().strftime('%H:%M:%S'),
                    'Asset': name,
                    'Direction': direction,
                    'Expiration': '1 min',
                    'Price': round(current_price, 5),
                    'Confidence': confidence,
                    'rsi': round(current_rsi, 2),
                    'trend': trend,
                    'type': 'REAL_MARKET'
                }
                print(f"SINAL REAL: {name} | {direction} | RSI: {current_rsi:.2f}", flush=True)
                time.sleep(40)
            else:
                time.sleep(10)
        except Exception as e:
            print(f"Erro na analise de mercado: {e}", flush=True)
            time.sleep(20)

@app.route('/latest', methods=['GET'])
def get_latest():
    return jsonify(latest_signal)
        return jsonify(latest_signal)

@app.route('/', methods=['GET'])
def health():
        return "Engine Real Market is Running!"

threading.Thread(target=generate_real_market_signals, daemon=True).start()

if __name__ == '__main__
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)

@app.route('/', methods=['GET'])
def health():
    return "Engine Real Market is Running!"

threading.Thread(target=generate_real_market_signals, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
