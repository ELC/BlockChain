from multiprocessing import Process, Queue
import json
from flask import Flask, jsonify, request

# Data Layer

def _load_transactions() -> list:
    try:
        with open('transactions.json', 'r') as infile:
            return json.load(infile)["transactions"]
    except FileNotFoundError:
        with open('transactions.json', 'w') as outfile:
            json.dump({"transactions":[]}, outfile)

def _store_transactions(transactions: list):
    with open('transactions.json', 'w') as outfile:
        json.dump({"transactions":transactions}, outfile)

def _flush_transactions():
    with open('transactions.json', 'w') as outfile:
        json.dump({"transactions":[]}, outfile)

def _prepare_transactions():
    transactions = _load_transactions()
    with open('transactions_ready.json', 'w') as outfile:
        json.dump({"transactions":transactions}, outfile)

# Bussiness Layer

def _create_transaction(sender: str, recipient: str, amount: float) -> dict:
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount,
        }

    return transaction

def _add_transaction(transaction: dict):
    transactions = _load_transactions()
    transactions.append(transaction)
    _store_transactions(transactions)


# API Layer

def _worker_main(queue_: Queue):
    while True:
        print("The Queue has {} items to be processed:".format(queue_.qsize()))

        body = queue_.get(True)

        if "flush" in body:
            _prepare_transactions()
            _flush_transactions()
            requests.get('http://localhost:5002/block')
            continue

        sender, recipient, amount = body['sender'], body['recipient'], body['amount']

        transaction = _create_transaction(sender, recipient, amount)

        _add_transaction(transaction)

        print("BackGround Process have finished processing ", body)

app = Flask(__name__)

@app.route('/transactions/new', methods=['POST'])
def transactions():
    body = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(parameter in body for parameter in required):
        return 'Missing values', 400

    queue.put(body)
    response = {'message': f'Transaction will be added to Block NNNNN'}
    return jsonify(response), 200

@app.route('/flush', methods=['POST'])
def flush():
    body = request.get_json()

    if "flush" not in body:
        return 'Missing values', 400

    queue.put(body)

    response = {'message': f'Transaction will be prepared for adding into Block NNNN'}

    return jsonify(response), 200

if __name__ == "__main__":
    queue = Queue()
    p = Process(target=_worker_main, args=(queue,))
    p.start()
    app.run(port=5001)