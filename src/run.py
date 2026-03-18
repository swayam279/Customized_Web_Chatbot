import time
from urllib.parse import urlparse

from langchain_core.documents import Document

from crawler import scrape
from document_generator import build_documents
from sitemap import create_sitemap
from text_splitter import split_documents_in_chunks
from vector_store import (
    collection_exists,
    get_collection_name,
    get_retriever,
    make_vector_store,
)


def get_url() -> str:
    base_url= input("Enter a url to generate custom chatbot: ")
    parser= urlparse(base_url)
    return f"{parser.scheme}://{parser.netloc}"

def get_sitemap(base_url: str) -> list[str]:
    return create_sitemap(base_url)

def scrape_complete_website(urls: list[str], base_url: str) -> list[dict]:
    return scrape(urls, base_url)

def convert_to_documents(scraped_data: list[dict]) -> list[Document]:
    return build_documents(scraped_data)

def split_all_documents(documents: list[Document]) -> list[Document]:
    return split_documents_in_chunks(documents)

if __name__ == "__main__":
    start= time.time()
    
    base_url= get_url()
    
    
    collection_name= get_collection_name(base_url)
    if collection_exists(collection_name):
        retriever= get_retriever(base_url)
        print("Chatbot is ready to chat with you!")
    
    else:
        sitemap= get_sitemap(base_url)
        scraped_data= scrape_complete_website(sitemap, base_url)
        converted_documents= convert_to_documents(scraped_data)
        chunks= split_all_documents(converted_documents)
        vectorstore= make_vector_store(chunks, collection_name)
        retriever= get_retriever(base_url)
        print("Chatbot is ready to chat with you!")
    
    end= time.time()
    print(f'Probably completed in {end-start} seconds.')