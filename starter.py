import os
import pickle
import time
import logging
from pprint import pprint
from dotenv import load_dotenv
import langchain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI, GooglePalm
from langchain.chains import LLMChain, RetrievalQAWithSourcesChain, AnalyzeDocumentChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.document_loaders import TextLoader, UnstructuredURLLoader, UnstructuredFileLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import StrOutputParser

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# llm = GooglePalm()
llm = OpenAI(temperature=0.7, max_tokens=1024)

embeddings = OpenAIEmbeddings()

urls = ['https://lewibelayneh.com']
file_path = 'vectors/vector_index.pkl'

if not os.path.exists(file_path):
        
    loader_url = UnstructuredURLLoader(urls=urls)
    url_load = loader_url.load()
    logger.info('URL loaded')
    
    loader_text = UnstructuredFileLoader(file_path=['files/Ardupilot.md', 'files/Facial Recognition.md'])
    text_load = loader_text.load()
    logger.info('Text loaded')

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    docs_url  = text_splitter.split_documents(text_load)
    # logger.info('URL split')
    logger.info('Documents split')

    vector_index = FAISS.from_documents(docs_url, embeddings)
    logger.info('Vetcor embedding created')

    with open(file_path, 'wb') as f:
        pickle.dump(vector_index, f)
        logger.info('Vector index saved')

if os.path.exists(file_path):
    with open(file_path, 'rb') as f:
        vectorIndex = pickle.load(f)
    logger.info('Vector index loaded')

while KeyboardInterrupt:
    query = input("Inquire: ")

    retrieval_chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorIndex.as_retriever())# | StrOutputParser()
    response = retrieval_chain({'question': query}) 

    pprint(response, indent=4)