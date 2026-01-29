import os
import threading
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Armazenamento global (DICIONÁRIO MUTÁVEL)
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

ASSETS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD', 'ETHUSD', 'AUDUSD']

def get_signal_quality(rsi, trend):
    if (rsi < 30 and trend == 'UP') or (rsi > 70 and trend == 'DOWN'): return "ALTA (95%)"
    return "MÉDIA (85%)"

def generate_pro_signal():
    global latest_signal
    print("🚀 MOTOR INTERNO INICIADO...", flush=True)
    while True:
        try:
            asset = random.choice(ASSETS)
            rsi = random.uniform(20, 80)
            trend = random.choice(['UP', 'DOWN'])
            
            if (rsi < 40 and trend == 'UP') or (rsi > 60 and trend == 'DOWN'):
                direction = 'BUY' if trend == 'UP' else 'SELL'
                quality = get_signal_quality(rsi, trend)
                
                # ATUALIZAÇÃO EM VEZ DE REATRIBUIÇÃO (Melhor para Threads)
                latest_signal.update({
                    'Timestamp': datetime.now().strftime('%H:%M:%S'),
                    'Asset': asset,
                    'Direction': direction,
                    'Expiration': '1 min',
                    'Price': round(random.uniform(1.0, 1.25) if 'USD' in asset else random.uniform(20000, 60000), 5),
                    'Confidence': quality,
                    'rsi': round(rsi, 2),
                    'trend': trend,
                    'type': 'PRO_STRATEGY'
                })
                print(f"🔥 SINAL GERADO: {asset} [{direction}]", flush=True)
                time.sleep(30)
            else:
                time.sleep(10)
        except Exception as e:
            print(f"❌ ERRO: {e}", flush=True)
            time.sleep(10)

# Início do Thread
threading.Thread(target=generate_pro_signal, daemon=True).start()

@app.route('/latest', methods=['GET'])
def get_latest():
    # Log para ver o que o Flask está lendo
    print(f"📡 API lendo: {latest_signal['Asset']} | {latest_signal['Timestamp']}", flush=True)
    return jsonify(latest_signal)

@app.route('/', methods=['GET'])
def health():
    return f"Engine Alpha Live - {latest_signal['Timestamp']}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
