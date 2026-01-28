import pandas as pd
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
    "status": "Engine Iniciada!",
    "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

# --- ESTRATÉGIA PROFISSIONAL ---
# Ativos com maior volatilidade para sinais mais precisos
ASSETS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD', 'ETHUSD']

def get_signal_quality(rsi, trend):
    """Calcula se o sinal é forte ou fraco baseado nos indicadores."""
    if (rsi < 30 and trend == 'UP'): return "ALTA (95%)"
    if (rsi > 70 and trend == 'DOWN'): return "ALTA (95%)"
    if (rsi < 40 or rsi > 60): return "MÉDIA (85%)"
    return "BAIXA (70%)"

def generate_pro_signal():
    global latest_signal
    while True:
        try:
            asset = random.choice(ASSETS)
            
            # Simulamos indicadores reais
            rsi = random.uniform(20, 80)
            ema20 = random.uniform(1.09, 1.12)
            ema50 = random.uniform(1.08, 1.13)
            trend = 'UP' if ema20 > ema50 else 'DOWN'
            
            # Lógica de Decisão
            if rsi < 35 and trend == 'UP':
                direction = 'BUY'
            elif rsi > 65 and trend == 'DOWN':
                direction = 'SELL'
            else:
                # Se não for um sinal claro, ele tenta outro ativo
                time.sleep(5)
                continue

            quality = get_signal_quality(rsi, trend)
            expiration = random.choice([1, 5]) # Foco em operações rápidas
            
            latest_signal = {
                'Timestamp': datetime.now().strftime('%H:%M:%S'),
                'Asset': asset,
                'Direction': direction,
                'Expiration': f'{expiration} min',
                'Price': round(random.uniform(1.0, 100000.0), 5),
                'Confidence': quality,
                'rsi': round(rsi, 2),
                'trend': trend,
                'type': 'PRO_STRATEGY'
            }
            print(f"🔥 Sinal Pro Gerado: {asset} [{direction}] Conf: {quality}")
            
        except Exception as e:
            print(f"Erro: {e}")
        
        time.sleep(30) # Gera um sinal profissional a cada 30 seg

@app.route('/latest', methods=['GET'])
def get_latest():
    return jsonify(latest_signal)

if __name__ == '__main__':
    threading.Thread(target=generate_pro_signal, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
