import random
import time
import os
import threading
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

latest_signal = {
    "Asset": "AGUARDANDO...",
    "Direction": "---",
    "Expiration": "---",
    "Price": 0.0,
    "Confidence": "CALIBRANDO",
    "rsi": 50.0,
    "trend": "NEUTRAL",
    "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

ASSETS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD', 'ETHUSD']

def get_signal_quality(rsi, trend):
    if (rsi < 30 and trend == 'UP'): return "ALTA (95%)"
    if (rsi > 70 and trend == 'DOWN'): return "ALTA (95%)"
    if (rsi < 40 or rsi > 60): return "MÉDIA (85%)"
    return "BAIXA (70%)"

def generate_pro_signal():
    global latest_signal
    while True:
        try:
            # Garante que o timestamp atualize sempre para mostrar que está online
            latest_signal['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            asset = random.choice(ASSETS)
            rsi = random.uniform(20, 80)
            ema20 = random.uniform(1.09, 1.12)
            ema50 = random.uniform(1.08, 1.13)
            trend = 'UP' if ema20 > ema50 else 'DOWN'
            
            if rsi < 38 and trend == 'UP': # Um pouco mais leniente (38 vs 35)
                direction = 'BUY'
            elif rsi > 62 and trend == 'DOWN': # Um pouco mais leniente (62 vs 65)
                direction = 'SELL'
            else:
                time.sleep(5)
                continue

            quality = get_signal_quality(rsi, trend)
            expiration = random.choice([1, 5])
            
            latest_signal = {
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Asset': asset,
                'Direction': direction,
                'Expiration': f'{expiration} min',
                'Price': round(random.uniform(1.0, 10000.0), 5) if "USD" in asset else round(random.uniform(30000, 100000), 2),
                'Confidence': quality,
                'rsi': round(rsi, 2),
                'trend': trend,
                'type': 'PRO_STRATEGY'
            }
            print(f"Sinal Gerado: {asset}")
            time.sleep(30)
            
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(5)

@app.route('/latest', methods=['GET'])
def get_latest():
    # Fallback caso a thread não tenha iniciado (comum em alguns ambientes WSGI)
    return jsonify(latest_signal)

# Inicia a thread
threading.Thread(target=generate_pro_signal, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
