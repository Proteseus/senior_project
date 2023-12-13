import os

from .chunker import Chunker
from .vectorizer import Vectorizer

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return jsonify({'msg': 'hi'})

# @app.route('', methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)