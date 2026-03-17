from langchain_text_splitters import RecursiveCharacterTextSplitter

from crawler import scrape
from document_generator import build_documents


def split_documents_in_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    filtered_chunks = []

    for chunk in chunks:
        text = chunk.page_content

        if len(text.strip()) < 100:
            continue


        filtered_chunks.append(chunk)

    return filtered_chunks

if __name__ == "__main__":
#   print("This code works right now.")
  crawler_data= scrape(["https://docs.langchain.com/oss/python/integrations/tools"], "https://docs.langchain.com/")
  crawled_documents= build_documents(crawler_data)
  docs= split_documents_in_chunks(crawled_documents)
  print(docs[-2].metadata)