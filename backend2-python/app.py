from flask import Flask, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'service': 'Python Flask Backend',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'host': os.environ.get('HOSTNAME', 'python-backend')
    })

@app.route('/products')
def get_products():
    products = [
        {'id': 1, 'name': 'Laptop', 'price': 999.99},
        {'id': 2, 'name': 'Mouse', 'price': 29.99},
        {'id': 3, 'name': 'Keyboard', 'price': 79.99}
    ]
    return jsonify({'products': products})

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    return jsonify({'message': 'Product created', 'product': data}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)