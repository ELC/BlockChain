import hashlib
import json
from uuid import uuid4
from flask import Flask, jsonify, request
from multiprocessing import Process, Queue

# Data Layer

def _store_chain(chain: dict):
    with open('chain.json', 'w') as outfile:
        json.dump({"chain":chain}, outfile)

    with open('chain_length.json', 'w') as outfile:
        json.dump({"length":len(chain["chain"])}, outfile)

    with open('last_block.json', 'w') as outfile:
        json.dump(chain["chain"][-1], outfile)

def _load_chain() -> dict:
    with open('chain.json', 'r') as infile:
        return json.load(infile)["chain"]

def _load_last_block() -> dict:
    with open('last_block.json', 'r') as infile:
        return json.load(infile)

# Bussiness Layer

def _update_chain(block: dict):
    chain = _load_chain()
    chain.append(block)
    _store_chain(chain)


def _proof_of_work(base_block: dict, condition: str="0000") -> int:
    new_block = base_block.copy()

    new_block["proof"] = 0

    while not _hash_block(new_block)[:len(condition)] == condition:
        new_block["proof"] += 1

    return new_block["proof"]

def _hash_block(block: dict) -> str:
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def _add_miner_transaction(base_block: dict, identifier) -> dict:
    new_block = base_block.copy()
    miner_transaction = {'sender': "0", 'recipient': identifier, 'amount': 1}
    new_block["transactions"].append(miner_transaction)
    return new_block

# API Layer

def _worker_main(queue_: Queue):
    while True:
        print("The Queue has {} items to be processed:".format(queue_.qsize()))

        body = queue_.get(True)

        block = body['block']

        last_block = _load_last_block()

        block['index'] = last_block['index'] + 1

        block['previous_hash'] = last_block['proof']

        block = _add_miner_transaction(block, node)

        proof = _proof_of_work(block)

        block["proof"] = proof

        _update_chain(block)

        print("BackGround Process have finished processing ", body)

app = Flask(__name__)

node = str(uuid4()).replace('-', '')

@app.route('/mine', methods=['POST'])
def mine():
    body = request.get_json()

    required = ['block']
    if not all(parameter in body for parameter in required):
        return 'Missing values', 400

    queue.put(body)

    response = {
        'message': "New Block Forged",
    }

    return jsonify(response), 200

if __name__ == "__main__":
    queue = Queue()
    p = Process(target=_worker_main, args=(queue,))
    p.start()
    app.run(port=5003)
