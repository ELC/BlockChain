import json
from flask import Flask, jsonify, redirect

# Data Layer
def _load_chain() -> list:
    with open('chain.json', 'r') as infile:
        return json.load(infile)["chain"]

def _load_chain_length() -> int:
    with open('chain_length.json', 'r') as infile:
        return json.load(infile)["length"]

# API Layer

app = Flask(__name__)

@app.route('/transactions/new', methods=['GET', 'POST'])
def new_transaction():
    return redirect('http://localhost:5001/transactions/new', code=307)

@app.route('/chain', methods=['GET'])
def full_chain():
    chain = _load_chain()

    length = _load_chain_length()

    response = {
        'chain': chain,
        'length': length,
        }
    return jsonify(response), 200
