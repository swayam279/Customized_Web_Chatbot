import uuid
from urllib.parse import urlparse

import streamlit as st

from Agent import build_chat_history, run_agent_stream, strip_sources_block
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

# ── In-memory store ───────────────────────────────────────────────────────────

def _store() -> dict:
    if "agent_conversations" not in st.session_state:
        st.session_state.agent_conversations = {}
    return st.session_state.agent_conversations


def load_conversations() -> list[dict]:
    return [{"session_id": sid, **data} for sid, data in _store().items()]


def create_conversation(base_url: str) -> str:
    sid = str(uuid.uuid4())
    _store()[sid] = {"title": "New chat", "base_url": base_url, "messages": []}
    return sid


def load_messages(session_id: str) -> list[dict]:
    return _store().get(session_id, {}).get("messages", [])


def save_message(session_id: str, role: str, content: str):
    _store()[session_id]["messages"].append({"role": role, "content": content})


def rename_conversation(session_id: str, title: str):
    _store()[session_id]["title"] = title


def delete_conversation(session_id: str):
    _store().pop(session_id, None)


def get_active_base_url() -> str | None:
    """Always derive base_url from the active conversation — never a separate var."""
    sid = st.session_state.get("agent_session_id")
    return _store().get(sid, {}).get("base_url") if sid else None


def auto_title(session_id: str, first_message: str):
    """Name the conversation from the first user message, like ChatGPT does."""
    if _store().get(session_id, {}).get("title") == "New chat":
        title = first_message.strip()[:42]
        if len(first_message.strip()) > 42:
            title += "…"
        _store()[session_id]["title"] = title



# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="Website Chatbot — Agent", page_icon="🤖", layout="wide")

# ── Session state init ────────────────────────────────────────────────────────

if "agent_session_id" not in st.session_state:
    st.session_state.agent_session_id = None
if "agent_show_rename" not in st.session_state:
    st.session_state.agent_show_rename = False

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* ── Sidebar background ── */
    section[data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }

    /* ── App main background ── */
    .stApp {
        background-color: #16213e;
    }

    /* ── Sidebar title ── */
    section[data-testid="stSidebar"] h1 {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    /* ── Sidebar subheadings ── */
    section[data-testid="stSidebar"] h3 {
        color: #94a3b8;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
        margin-top: 0rem;
    }

    /* ── Sidebar conversation buttons ── */
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: transparent;
        border: none;
        color: #cbd5e1;
        font-size: 0.83rem;
        text-align: left;
        padding: 0.35rem 0.5rem;
        border-radius: 6px;
        width: 100%;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #0f3460;
        color: #f1f5f9;
    }

    /* ── Active conversation button ── */
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:focus {
        background-color: #0f3460;
    }

    /* ── Start button ── */
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background-color: #e94560;
        border: none;
        color: white;
        font-weight: 600;
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
        background-color: #c73652;
    }

    /* ── URL text input in sidebar ── */
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
        background-color: #0f3460;
        border: 1px solid #1e4d8c;
        color: #e2e8f0;
        border-radius: 8px;
        font-size: 0.82rem;
    }
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input:disabled {
        background-color: #12294d;
        color: #64748b;
        border-color: #1e3a5f;
        cursor: not-allowed;
    }

    /* ── Main area chat messages ── */
    div[data-testid="stChatMessage"] {
        background-color: #1e2d45;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }

    /* ── Dividers ── */
    hr {
        border-color: #1e3a5f;
    }

    /* ── Caption text ── */
    .stCaption {
        color: #64748b;
    }

    /* ── Delete buttons — subtle ── */
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        color: #475569;
        font-size: 0.75rem;
        padding: 0.3rem 0.4rem;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        color: #e94560;
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🤖  Website Chatbot — Agent")
    st.divider()

    st.subheader("Website")

    active_base_url   = get_active_base_url()
    url_is_locked     = active_base_url is not None
    url_display_value = active_base_url if url_is_locked else ""

    url_input = st.text_input(
        "url_field",
        value=url_display_value,
        placeholder="https://example.com/",
        disabled=url_is_locked,
        label_visibility="collapsed",
        help="Locked to the active chat's website. Switch website to change." if url_is_locked else "Enter a website URL to index.",
    )

    if st.button("Start", use_container_width=True, type="primary", disabled=url_is_locked):
        raw = url_input.strip()
        if raw:
            parsed   = urlparse(raw)
            base_url = f"{parsed.scheme}://{parsed.netloc}/"
            col_name = get_collection_name(base_url)

            if collection_exists(col_name):
                st.session_state.agent_session_id = create_conversation(base_url)
                st.success("Already indexed! Chat is ready.")
                st.rerun()
            else:
                with st.spinner("Indexing… this may take a few minutes."):
                    sitemap = get_sitemap(base_url)
                    scraped = scrape_complete_website(sitemap, base_url)
                    docs    = convert_to_documents(scraped)
                    chunks  = split_all_documents(docs)
                    make_vector_store(chunks, col_name)

                st.session_state.agent_session_id = create_conversation(base_url)
                st.success("Indexed! Chat is ready.")
                st.rerun()
        else:
            st.warning("Please enter a URL.")

    if url_is_locked:
        if st.button("↩  Switch website", use_container_width=True):
            st.session_state.agent_session_id = None
            st.session_state.agent_show_rename = False
            st.rerun()

    st.divider()

    hcol, pcol = st.columns([5, 1])
    with hcol:
        st.subheader("Conversations")
    with pcol:
        if active_base_url:
            if st.button("＋", help="New chat", use_container_width=True):
                st.session_state.agent_session_id = create_conversation(active_base_url)
                st.session_state.agent_show_rename = False
                st.rerun()

    conversations = load_conversations()

    if conversations:
        for conv in conversations:
            is_active = conv["session_id"] == st.session_state.agent_session_id
            domain    = urlparse(conv["base_url"]).netloc

            c1, c2 = st.columns([5, 1])
            with c1:
                marker = "▶  " if is_active else "    "
                if st.button(
                    f"{marker}{conv['title']}",
                    key=f"conv_{conv['session_id']}",
                    use_container_width=True,
                    help=domain,
                ):
                    st.session_state.agent_session_id  = conv["session_id"]
                    st.session_state.agent_show_rename = False
                    st.rerun()
            with c2:
                if st.button("✕", key=f"del_{conv['session_id']}", help="Delete"):
                    delete_conversation(conv["session_id"])
                    if conv["session_id"] == st.session_state.agent_session_id:
                        st.session_state.agent_session_id  = None
                        st.session_state.agent_show_rename = False
                    st.rerun()

        if st.session_state.agent_session_id and st.session_state.agent_show_rename:
            st.divider()
            new_name = st.text_input(
                "Rename chat",
                placeholder="New name…",
                label_visibility="collapsed",
                key="rename_field",
            )
            rcol1, rcol2 = st.columns([3, 1])
            with rcol1:
                if st.button("Save", use_container_width=True) and new_name.strip():
                    rename_conversation(st.session_state.agent_session_id, new_name.strip())
                    st.session_state.agent_show_rename = False
                    st.rerun()
            with rcol2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.agent_show_rename = False
                    st.rerun()
    else:
        st.caption("No conversations yet.")


# ── Main area ─────────────────────────────────────────────────────────────────

if not st.session_state.agent_session_id:
    st.markdown("## Welcome — Agent Mode")
    st.markdown(
        "Paste a website URL in the sidebar and click **Start**. "
        "The agent indexes every page once, then dynamically retrieves "
        "across multiple past queries to answer follow-ups accurately."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**Step 1**\nPaste a URL in the sidebar")
    with c2:
        st.info("**Step 2**\nWait for one-time indexing")
    with c3:
        st.info("**Step 3**\nAsk anything — agent retrieves smartly")

else:
    session_id  = st.session_state.agent_session_id
    base_url    = get_active_base_url()
    conv_data   = _store().get(session_id, {})
    conv_title  = conv_data.get("title", "Chat")

    if not base_url:
        st.error("Conversation not found. Please start a new chat.")
        st.stop()

    # ── Header ────────────────────────────────────────────────────────────────

    h1, h2 = st.columns([8, 1])
    with h1:
        st.markdown(f"### {conv_title}")
        st.caption(f"🌐 {base_url}  ·  🤖 Agent mode")
    with h2:
        if st.button("✏️", help="Rename this chat", key="toggle_rename"):
            st.session_state.agent_show_rename = not st.session_state.agent_show_rename
            st.rerun()

    st.divider()

    # ── Message history ───────────────────────────────────────────────────────

    messages = load_messages(session_id)

    if not messages:
        st.markdown(
            f"*Ask me anything about **{base_url}**. "
            "Answers are grounded strictly in that site's content.*"
        )

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Chat input ────────────────────────────────────────────────────────────

    user_input = st.chat_input("Ask a question…")

    if user_input:
        auto_title(session_id, user_input)

        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Build chat history from stored messages before this turn
        history_pairs = [
            (messages[i]["content"], messages[i + 1]["content"])
            for i in range(0, len(messages) - 1, 2)
            if messages[i]["role"] == "user"
            and messages[i + 1]["role"] == "assistant"
        ]
        chat_history = build_chat_history(history_pairs)
        retriever    = get_retriever(base_url)

        with st.chat_message("assistant"):
            # Stream the answer — model prints Sources inline per system prompt.
            # No expander needed — sources appear naturally in the streamed text.
            streamed_answer = st.write_stream(
                run_agent_stream(retriever, base_url, user_input, chat_history)
            )

        # Strip Sources block before saving so it isn't re-sent to the model
        # as conversational content in future turns.
        clean_answer = strip_sources_block(streamed_answer)
        save_message(session_id, "user", user_input)
        save_message(session_id, "assistant", clean_answer)