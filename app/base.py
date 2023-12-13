import os

from dotenv import load_dotenv

load_dotenv()

from app.bot.bot import Bot
from app.file_processor.chunker import Chunker
from app.file_processor.vectorizer import Vectorizer

file = f'{os.getcwd()}/files/{input("filename: ")}'
chunk = Chunker(file)
vectors = Vectorizer(file_path='ardu')
bot = Bot()

doc_chunks = chunk.chunker(loader_type='text')
vec = vectors.vector(split_docs=doc_chunks)


while KeyboardInterrupt:
    response = bot.get_response(vectorIndex=vec)
    
    print("Answer: ", response['answer'])
    print("Sources: ", response['sources'])