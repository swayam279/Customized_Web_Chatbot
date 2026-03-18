import os
from urllib.parse import urlparse

import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_mistralai import MistralAIEmbeddings

load_dotenv()

embedding_model= MistralAIEmbeddings(model='mistral-embed')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
PERSIST_DIR = os.path.join(PROJECT_ROOT, "chroma_web_chatbot")

def get_collection_name(base_url: str) -> str:
    """ 
    This makes a collection name for each independant website based on its base url.
    """
    
    parsed= urlparse(base_url)
    
    cleaned_collection_name= parsed.netloc.replace('.', '_').replace('-', '_')
    
    return f'website_{cleaned_collection_name}'

def collection_exists(collection_name: str) -> bool:
    """ 
    To check if a website has already been added to chromadb.
    """
    
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    existing = [c.name for c in client.list_collections()]
 
    if collection_name not in existing:
        return False
 
    # Collection exists — verify it actually has content
    col = client.get_collection(collection_name)
    return col.count() > 0

def make_vector_store(chunks: list, collection_name: str) -> Chroma:
    """
    Stores chunks into chromadb vector database.
    """
    
    if collection_exists(collection_name):
        print("This website has already been added. Fetching it.")
        vectorstore= Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIR
        )
        return vectorstore
    else:
        print(f" adding {len(chunks)} into chromadb")
        
        vectorstore= Chroma.from_documents(
            documents= chunks,
            embedding= embedding_model,
            collection_name= collection_name,
            persist_directory= PERSIST_DIR,
        )
        
        return vectorstore

def get_retriever(base_url: str, k: int=8):
    """ 
    This returns a retriever for each independant website based on its base url.
    """
    
    collection_name= get_collection_name(base_url)
    
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIR
    )

    return vectorstore.as_retriever(search_type='mmr', search_kwargs={'k': k, 'fetch_k': k*3, 'lambda_mult': 0.5})

if __name__ == "__main__":
    # print("This code works right now.")
    print(get_collection_name("https://docs.langchain.com/"))