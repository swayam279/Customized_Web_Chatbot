from urllib.parse import urlparse

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_mistralai import MistralAIEmbeddings

load_dotenv()

embedding_model= MistralAIEmbeddings(model='mistral-embed')

PERSIST_DIR = "./chroma_web_chatbot"

def get_collection_name(base_url: str) -> str:
    """ 
    This creates a collection for each independant website based on its base url.
    """
    
    parsed= urlparse(base_url)
    
    cleaned_collection_name= parsed.netloc.replace('.', '_').replace('-', '_')
    
    return f'website_{cleaned_collection_name}'

def make_vector_store(chunks: list, base_url: str) -> Chroma:
    """
    Stores chunks into chromadb vector database.
    """
    
    collection_name= get_collection_name(base_url)
    
    print(f" adding {len(chunks)} into chromadb")
    
    vectorstore= Chroma.from_documents(
        documents= chunks,
        embedding= embedding_model,
        collection_name= collection_name,
        persist_directory= PERSIST_DIR,
    )
    
    return vectorstore

def get_retriever(base_url: str):
    """ 
    This returns a retriever for each independant website based on its base url.
    """
    
    collection_name= get_collection_name(base_url)
    
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIR
    )
    # Fetch top 5 chunks
    return vectorstore.as_retriever(search_type='mmr', search_kwargs={'k': 5, 'lambda_mult': 0.5})

if __name__ == "__main__":
    print("This code works right now.")