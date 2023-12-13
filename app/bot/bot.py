from langchain.llms import OpenAI, GooglePalm
from langchain.chains import RetrievalQAWithSourcesChain
from pprint import pprint
from dotenv import load_dotenv

class Bot():
    llm: any
    
    def __init__(self) -> None:
        # self.llm = OpenAI(temperature=0.7, max_tokens=1024)
        self.llm = GooglePalm()
    
    def get_response(self, vectorIndex, query) -> dict:
        retrieval_chain = RetrievalQAWithSourcesChain.from_llm(llm=self.llm, retriever=vectorIndex.as_retriever())# | StrOutputParser()
        response = retrieval_chain({'question': query})

        return response