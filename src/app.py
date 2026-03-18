import uuid
from urllib.parse import urlparse

import streamlit as st

# from langchain_core.messages import AIMessage, HumanMessage
from chatbot import Chat, build_chat_history
from run import (
    convert_to_documents,
    get_sitemap,
    scrape_complete_website,
    split_all_documents,
)
from vector_store import (
    collection_exists,
    get_collection_name,
    get_retriever,
    make_vector_store,
)

# ── In-memory conversation store ─────────────────────────────────────────────
#
# Replaces MongoDB for testing. Everything lives in st.session_state and is
# lost when the browser tab closes or the app restarts — that's expected.
#
# Structure of st.session_state.conversations:
# {
#   "session_id": {
#       "title":    str,
#       "base_url": str,
#       "messages": [{"role": "user"|"assistant", "content": str}, ...]
#   }
# }
 
def _store() -> dict:
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    return st.session_state.conversations
 
 
def load_conversations() -> list[dict]:
    return [
        {"session_id": sid, **data}
        for sid, data in _store().items()
    ]
 
 
def create_conversation(base_url: str) -> str:
    session_id = str(uuid.uuid4())
    _store()[session_id] = {
        "title": "New chat",
        "base_url": base_url,
        "messages": [],
    }
    return session_id
 
 
def load_messages(session_id: str) -> list[dict]:
    return _store().get(session_id, {}).get("messages", [])
 
 
def save_message(session_id: str, role: str, content: str):
    _store()[session_id]["messages"].append({"role": role, "content": content})
 
 
def rename_conversation(session_id: str, title: str):
    _store()[session_id]["title"] = title
 
 
def delete_conversation(session_id: str):
    _store().pop(session_id, None)
 
 
# ── Streamlit setup ───────────────────────────────────────────────────────────
 
st.set_page_config(page_title="Website Chatbot", page_icon="🌐", layout="wide")
 
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "base_url" not in st.session_state:
    st.session_state.base_url = None
 
# ── Sidebar ───────────────────────────────────────────────────────────────────
 
with st.sidebar:
    st.title("Website Chatbot")
    st.divider()
 
    # URL input
    st.subheader("Index a website")
    url_input = st.text_input("Website URL", placeholder="https://docs.langchain.com/")
 
    if st.button("Start", use_container_width=True, type="primary"):
        if url_input.strip():
            parsed = urlparse(url_input.strip())
            base_url = f"{parsed.scheme}://{parsed.netloc}/"
            collection_name = get_collection_name(base_url)
 
            if collection_exists(collection_name):
                st.session_state.base_url = base_url
                st.session_state.session_id = create_conversation(base_url)
                st.success("Already indexed! Chat is ready.")
                st.rerun()
            else:
                with st.spinner("Indexing website... this may take a few minutes."):
                    sitemap = get_sitemap(base_url)
                    scraped = scrape_complete_website(sitemap, base_url)
                    docs = convert_to_documents(scraped)
                    chunks = split_all_documents(docs)
                    make_vector_store(chunks, collection_name)
 
                st.session_state.base_url = base_url
                st.session_state.session_id = create_conversation(base_url)
                st.success("Indexed! Chat is ready.")
                st.rerun()
 
    st.divider()
 
    # Past conversations
    st.subheader("Conversations")
    conversations = load_conversations()
 
    if conversations:
        for conv in conversations:
            is_active = conv["session_id"] == st.session_state.session_id
            c1, c2 = st.columns([5, 1])
            with c1:
                label = f"{'> ' if is_active else ''}{conv['title']}"
                if st.button(label, key=f"conv_{conv['session_id']}", use_container_width=True):
                    st.session_state.session_id = conv["session_id"]
                    st.session_state.base_url = conv["base_url"]
                    st.rerun()
            with c2:
                if st.button("X", key=f"del_{conv['session_id']}"):
                    delete_conversation(conv["session_id"])
                    if conv["session_id"] == st.session_state.session_id:
                        st.session_state.session_id = None
                        st.session_state.base_url = None
                    st.rerun()
    else:
        st.caption("No conversations yet.")
 
    if st.session_state.base_url:
        st.divider()
        if st.button("+ New chat", use_container_width=True):
            st.session_state.session_id = create_conversation(st.session_state.base_url)
            st.rerun()
 
# ── Main area ─────────────────────────────────────────────────────────────────
 
if not st.session_state.session_id:
    st.markdown("## Welcome")
    st.markdown("Enter a website URL in the sidebar to get started.")
else:
    session_id = st.session_state.session_id
    base_url   = st.session_state.base_url
 
    # Rename widget
    col1, col2 = st.columns([6, 2])
    with col2:
        new_name = st.text_input("Rename", label_visibility="collapsed", placeholder="Rename chat...")
        if st.button("Rename") and new_name.strip():
            rename_conversation(session_id, new_name.strip())
            st.rerun()
    with col1:
        st.caption(f"Chatting with: **{base_url}**")
 
    st.divider()
 
    # Load and display message history
    messages = load_messages(session_id)
 
    if not messages:
        st.markdown(f"*Ask me anything about **{base_url}**.*")
 
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
 
    # Chat input
    user_input = st.chat_input("Ask a question...")
 
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
 
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                # Pair up stored messages into (human, ai) tuples for history
                history_pairs = [
                    (messages[i]["content"], messages[i + 1]["content"])
                    for i in range(0, len(messages) - 1, 2)
                    if messages[i]["role"] == "user"
                    and messages[i + 1]["role"] == "assistant"
                ]
                chat_history = build_chat_history(history_pairs)
 
                retriever = get_retriever(base_url)
                result = Chat(retriever, base_url, user_input, chat_history)
 
            answer  = result["answer"]
            # sources = result["source_urls"]
 
            st.markdown(answer)
 
            # if sources and "**Sources:**" not in answer:
            #     with st.expander("Sources"):
            #         for url in sources:
            #             st.markdown(f"- [{url}]({url})")
 
        save_message(session_id, "user", user_input)
        save_message(session_id, "assistant", answer)