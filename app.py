
# A very simple Flask Hello World app for you to get started with...
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from pathlib import Path
from os.path import join

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://zetta-ai-checker.vercel.app"}})

# ROOT PATH

BASE_DIR = Path(__file__).resolve().parent


# Variabel global untuk menyimpan hasil pencocokan
matches_result = []

@app.route('/api/contract', methods=['POST'])
def process_contract():
    try:
        # Ambil contract address dari permintaan POST
        data = request.get_json()
        contract_address = data.get('contract_address')

        # Jalankan skrip Selenium dengan contract address sebagai argumen
        subprocess.run(['python', join(BASE_DIR, "scrape_tron.py"), contract_address])

        response_data = {"message": "Contract address sent and processed successfully"}

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/contract/matches', methods=['GET', 'POST'])  # Ubah metode menjadi GET dan POST
def receive_matches():
    global matches_result
    global basic_info
    try:
        if request.method == 'POST':
            # Jika metode adalah POST, terima data hasil pencocokan
            data = request.json  # Menerima data JSON dari request
            matches_result = data.get('matches', [])
            basic_info = data.get('basic_info', {})
            response_data = {"message": "Matches received successfully"}
        elif request.method == 'GET':
            # Jika metode adalah GET, kirimkan data hasil pencocokan
            response_data = {"matches": matches_result, "basic_info": basic_info}

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})
