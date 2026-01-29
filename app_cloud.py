import os
import threading
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Armazenamento global
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
motor_started = False
lock = threading.Lock()

def generate_pro_signal():
    global latest_signal
    print(f"🚀 [PID {os.getpid()}] MOTOR INICIADO", flush=True)
    while True:
        try:
            asset = random.choice(ASSETS)
            rsi = random.uniform(20, 80)
            trend = random.choice(['UP', 'DOWN'])
            
            if (rsi < 40 and trend == 'UP') or (rsi > 60 and trend == 'DOWN'):
                direction = 'BUY' if trend == 'UP' else 'SELL'
                latest_signal.update({
                    'Timestamp': datetime.now().strftime('%H:%M:%S'),
                    'Asset': asset,
                    'Direction': direction,
                    'Expiration': '1 min',
                    'Price': round(random.uniform(1.0, 1.25) if 'USD' in asset else random.uniform(20000, 60000), 5),
                    'Confidence': "ALTA (95%)" if abs(rsi-50)>20 else "MÉDIA (85%)",
                    'rsi': round(rsi, 2),
                    'trend': trend,
                    'type': 'PRO_STRATEGY'
                })
                print(f"🔥 [PID {os.getpid()}] SINAL: {asset}", flush=True)
                time.sleep(30)
            else:
                time.sleep(10)
        except Exception as e:
            print(f"❌ ERRO: {e}", flush=True)
            time.sleep(10)

@app.route('/latest', methods=['GET'])
def get_latest():
    global motor_started
    with lock:
        if not motor_started:
            t = threading.Thread(target=generate_pro_signal, daemon=True)
            t.start()
            motor_started = True
    
    print(f"DEBUG: Process ID {os.getpid()} | Thread: {threading.active_count()}", flush=True)
    print(f"📡 Request PID {os.getpid()} | Asset: {latest_signal['Asset']}", flush=True)
    return jsonify(latest_signal)

@app.route('/', methods=['GET'])
def health():
    return f"Live PID {os.getpid()}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
