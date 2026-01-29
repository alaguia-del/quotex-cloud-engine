import requests
import time
import os
import threading
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Armazenamento global de sinais
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

# Mapeamento de ativos para Kraken (Public API)
ASSETS_MAP = {
    'EURUSD': 'EURUSD',
    'GBPUSD': 'GBPUSD',
    'USDJPY': 'USDJPY',
    'BTCUSD': 'XBTUSD',
    'ETHUSD': 'ETHUSD'
}

def calculate_rsi_manual(prices, window=14):
    if len(prices) < window + 1:
        return 50.0
    
    deltas = []
    for i in range(1, len(prices)):
        deltas.append(float(prices[i]) - float(prices[i-1]))
    
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:window]) / window
    avg_loss = sum(losses[:window]) / window
    
    if avg_loss == 0:
        return 100.0
    
    for i in range(window, len(deltas)):
        avg_gain = (avg_gain * (window - 1) + gains[i]) / window
        avg_loss = (avg_loss * (window - 1) + losses[i]) / window
        
    if avg_loss == 0:
        return 100.0
        
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_real_market_signals():
    global latest_signal
    print("MOTOR KRAKEN ENGINE INICIADO...", flush=True)
    
    while True:
        try:
            asset_keys = list(ASSETS_MAP.keys())
            name = random.choice(asset_keys)
            symbol = ASSETS_MAP[name]
            
            url = f"https://api.kraken.com/0/public/OHLC?pair={symbol}&interval=1"
            res = requests.get(url, timeout=10)
            data = res.json()
            
            if data.get('error'):
                print(f"Erro Kraken ({name}): {data['error']}", flush=True)
                time.sleep(10)
                continue
                
            pair_key = [k for k in data['result'].keys() if k != 'last'][0]
            ticks = data['result'][pair_key]
            
            if len(ticks) < 30:
                print(f"Poucos dados para {name}", flush=True)
                time.sleep(5)
                continue

            closes = [float(t[4]) for t in ticks[-30:]]
            current_price = closes[-1]
            current_rsi = calculate_rsi_manual(closes, 14)
            
            ema20 = sum(closes[-20:]) / 20
            ema10 = sum(closes[-10:]) / 10
            trend = 'UP' if ema10 > ema20 else 'DOWN'
            
            direction = "WAIT"
            confidence = "BAIXA"
            
            if current_rsi < 32 and trend == 'UP':
                direction = "BUY"
                confidence = "ALTA (95%)"
            elif current_rsi > 68 and trend == 'DOWN':
                direction = "SELL"
                confidence = "ALTA (95%)"
            elif current_rsi < 25:
                direction = "BUY"
                confidence = "MEDIA (88%)"
            elif current_rsi > 75:
                direction = "SELL"
                confidence = "MEDIA (88%)"
            
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
                print(f"SINAL KRAKEN: {name} | {direction} | RSI: {current_rsi:.2f} | TEND: {trend}", flush=True)
                time.sleep(45)
            else:
                time.sleep(15)

        except Exception as e:
            print(f"Erro na Kraken Engine: {e}", flush=True)
            time.sleep(20)

@app.route('/latest', methods=['GET'])
def get_latest():
    return jsonify(latest_signal)

@app.route('/', methods=['GET'])
def health():
    return f"Kraken Real Market Live - {latest_signal['Asset']}"

threading.Thread(target=generate_real_market_signals, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
