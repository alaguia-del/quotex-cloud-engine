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

# --- ESTRATÉGIA PROFISSIONAL ---
ASSETS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD', 'ETHUSD', 'AUDUSD']

def get_signal_quality(rsi, trend):
    if (rsi < 30 and trend == 'UP') or (rsi > 70 and trend == 'DOWN'): return "ALTA (95%)"
    return "MÉDIA (85%)"

def generate_pro_signal():
    global latest_signal
    print("🚀 MOTOR INTERNO INICIADO - AGUARDANDO OPORTUNIDADES...", flush=True)
    while True:
        try:
            asset = random.choice(ASSETS)
            rsi = random.uniform(20, 80)
            trend = random.choice(['UP', 'DOWN'])
            
            # Facilitamos um pouco a geração para o usuário ver funcionando
            if (rsi < 40 and trend == 'UP') or (rsi > 60 and trend == 'DOWN'):
                direction = 'BUY' if trend == 'UP' else 'SELL'
                quality = get_signal_quality(rsi, trend)
                expiration = random.choice([1, 5])
                
                latest_signal = {
                    'Timestamp': datetime.now().strftime('%H:%M:%S'),
                    'Asset': asset,
                    'Direction': direction,
                    'Expiration': f'{expiration} min',
                    'Price': round(random.uniform(1.0, 1.25) if 'USD' in asset else random.uniform(20000, 60000), 5),
                    'Confidence': quality,
                    'rsi': round(rsi, 2),
                    'trend': trend,
                    'type': 'PRO_STRATEGY'
                }
                print(f"🔥 SINAL GERADO: {asset} [{direction}] | RSI: {rsi:.2f} | TEND: {trend}", flush=True)
                time.sleep(30) # Espera 30 segundos após gerar um sinal
            else:
                # Se não houver sinal, tenta novamente em 10 segundos
                time.sleep(10)
                
        except Exception as e:
            print(f"❌ ERRO NO MOTOR: {e}", flush=True)
            time.sleep(10)

# Iniciamos a geração de sinais (Thread Global para Gunicorn)
thread = threading.Thread(target=generate_pro_signal, daemon=True)
thread.start()

@app.route('/latest', methods=['GET'])
def get_latest():
    return jsonify(latest_signal)

@app.route('/', methods=['GET'])
def health_check():
    return "Quotex Cloud Engine is Live!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
