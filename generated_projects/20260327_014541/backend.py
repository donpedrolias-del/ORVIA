"""
Application générée par ORVIA
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

data = []
counter = 1

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify({"items": data, "total": len(data)})

@app.route('/api/items', methods=['POST'])
def create_item():
    global counter
    item_data = request.get_json()
    item = {"id": counter, "data": item_data, "created_at": datetime.now().isoformat()}
    counter += 1
    data.append(item)
    return jsonify(item), 201

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global data
    new_data = []
    for item in data:
        if item['id'] != item_id:
            new_data.append(item)
    data = new_data
    return jsonify({"message": "Supprimé"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5009))
    app.run(host='0.0.0.0', port=port, debug=True)
