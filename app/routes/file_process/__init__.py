import os
import sys
import logging

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

sys.path.append(os.getcwd())

# from bot.bot import Bot
from app.file_processor.chunker import Chunker
from app.file_processor.vectorizer import Vectorizer

fileProcessRoute = Blueprint('file_process', __name__)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=[logging.INFO, logging.ERROR])
logger.addHandler(logging.StreamHandler())

@fileProcessRoute.route('/', methods=['GET'])
def index():
    return jsonify({'hi': 'asdasdasd'})

@fileProcessRoute.route('/upload/', methods=['POST'])
def upload_file():
    try:
        bot_id = request.form.get('chat_id')

        file = request.files['file']
        file_path = f'{os.getcwd()}/files/{bot_id}/{file.filename}'
        with open(file_path, 'wb') as uploaded_file:
            file.save(uploaded_file)
        
        logger.info(f"File uploaded: {file.filename} | Chat ID: {bot_id}")

        if os.path.exists(file_path):
            target_path = f'{os.getcwd()}/vectors/{bot_id}/{file.filename[:-4]}.pkl'

            while not os.path.exists(target_path):
                chunk = Chunker(file_path=file_path)
                vectors = Vectorizer(file_path=f'{bot_id}/{file.filename}')

                doc_chunks = chunk.chunker(loader_type='text')
                vectors.vector(split_docs=doc_chunks)

                return jsonify({'message': 'File uploaded successfully'})
        else:
            return jsonify({'message': 'File not found'})
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return jsonify({'message': str(e)})
