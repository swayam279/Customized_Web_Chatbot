from langchain_core.documents import Document

# from crawler import scrape

def build_documents(crawled_data: list[dict]) -> list[Document]:
    documents = []

    for item in crawled_data:
        doc = Document(
            page_content=item["content"],
            metadata={
                "url": item["url"],
                "base_url": item["base_url"]
            }
        )
        documents.append(doc)

    return documents

if __name__ == "__main__":
    print("this code works hehe")
    # crawler_data= scrape(["https://docs.langchain.com/oss/python/integrations/tools"], "https://docs.langchain.com/")
    # crawled_documents= build_documents(crawler_data)
    # print(crawled_documents[0].metadata)