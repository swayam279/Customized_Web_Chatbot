from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mistralai import ChatMistralAI

load_dotenv()


#for follow up questions:
Rephrase_Prompt= ChatPromptTemplate.from_messages(
    [
        ("system",
        "Given the conversation history and the user's latest message, rewrite the latest message as a fully self-contained question. Do NOT answer it. If it is already self-contained, return it unchanged."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# system prompt for the chatbot
QA_System_Prompt= ChatPromptTemplate.from_messages(
    [
        ("system",
        "You are an assistant for {base_url}.\n\n"
        "Rules:\n"
        "1. Answer ONLY using the context below. Never use outside knowledge.\n"
        "2. If the answer is not in the context, say: "
        "'I could not find that information from the website.'\n"
        "3. At the end of your answer, always list the source URLs you used:\n"
        "   **Sources:**\n"
        "   - <url>\n\n"
        "Context:\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

def get_llm_model():
    """ 
    Fetch llm model for the chatbot.
    """
    
    model= ChatMistralAI(model='mistral-medium-latest')
    return model

def format_docs(docs) -> str:
    """Formats retrieved docs into a numbered context block for the prompt."""
    parts = []
    for i, doc in enumerate(docs, 1):
        url = doc.metadata.get("url", "unknown")
        parts.append(f"[{i}] Source: {url}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)

def get_source_urls(docs) -> list[str]:
    """Extracts unique source URLs from retrieved docs for the UI."""
    seen = set()
    urls = []
    for doc in docs:
        url = doc.metadata.get("url", "")
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls

def build_chat_history(pairs: list[tuple[str, str]]) -> str:
    """ 
    Converts the conversation pairs into langchain message object for placeholders.
    """
    
    messages=[]
    for human_message, ai_message in pairs:
        messages.append(HumanMessage(content=human_message))
        messages.append(AIMessage(content=ai_message))
    return messages

def Chat(retriever, base_url: str, user_input: str, chat_history: list) -> dict:
    """ 
    The main Chatbot function.
    """
    
    model= get_llm_model()
    
    if chat_history:
        retriever_query= (Rephrase_Prompt | model | StrOutputParser()).invoke({'input': user_input, 'chat_history': chat_history})
    
    else:
        retriever_query= user_input
        
    docs= retriever.invoke(retriever_query)
    
    context= format_docs(docs)
    
    # chat_history= build_chat_history(chat_history)
    
    #model reply
    answer= (QA_System_Prompt | model | StrOutputParser()).invoke({
        'input': user_input,
        'chat_history': chat_history,
        'context': context,
        'base_url': base_url
    })
    
    return {
        'answer': answer,
        'source_urls': get_source_urls(docs)
    }
    
if __name__ == "__main__":
    from vector_store import get_retriever
    
    base_url='https://webscraper.io/'
    
    retriever= get_retriever(base_url)
    
    Question= 'What are the test sites available?'
    
    result= Chat(retriever, base_url, Question, chat_history=[])
    
    print("Answer:\n", result["answer"])
    print("\nSources:")
    for s in result["source_urls"]:
        print(" -", s)