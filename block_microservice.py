from multiprocessing import Process, Queue
import json
from time import time
from flask import Flask, jsonify, request
import requests

# Data Layer
def _load_ready_transactions():
    with open('transactions_ready.json', 'r') as infile:
        return json.load(infile)["transactions"]

# Bussiness Layer
def _create_block(transactions=None):
    if transactions is None:
        transactions = []
    block = {
        'timestamp': time(),
        'transactions': transactions,
    }

    return block

# API Layer
def _worker_main(queue_: Queue):
    while True:
        print("The Queue has {} items to be processed:".format(queue_.qsize()))

        queue_.get(True)

        transactions = _load_ready_transactions()

        block = _create_block(transactions)

        requests.post('http://localhost:5003/mine', json={"block":block})

        print("BackGround Process have finished processing ", transactions)


app = Flask(__name__)

@app.route('/block', methods=['GET'])
def mine():
    queue.put(1)

    response = {
        'message': "New Block Forged",
    }

    return jsonify(response), 200


@app.route('/genesis', methods=['GET'])
def create_genesis_block():
    try:
        response = {'message': "Genesis Block Already Created"}
    except FileNotFoundError:
        genesis_block = _create_block()
        response = {'message': "Genesis Block Created"}
        store_not_minned_blocks({"blocks":[genesis_block]})

    return jsonify(response), 200

if __name__ == "__main__":
    queue = Queue()
    p = Process(target=_worker_main, args=(queue,))
    p.start()
    app.run(port=5002)
