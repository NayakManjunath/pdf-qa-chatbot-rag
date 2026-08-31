import logging

import html
import requests
import streamlit as st

try:
    from ui.api_client import APIClient
    from ui.config import API_TIMEOUT, APP_ICON, APP_TITLE
except ModuleNotFoundError:
    from api_client import APIClient
    from config import API_TIMEOUT, APP_ICON, APP_TITLE

logger = logging.getLogger(__name__)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PROFESSIONAL CHATBOT CSS
# ============================================================

CUSTOM_CSS = """
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

.stApp {
    background: #eef3f8;
}

.main .block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}


/* ============================================================
   MAIN APPLICATION HEADER
   ============================================================ */

.chat-header {
    background: linear-gradient(
        135deg,
        #243746 0%,
        #304b5b 55%,
        #38596a 100%
    );

    border-radius: 22px;
    padding: 22px 26px;
    margin-bottom: 18px;

    box-shadow:
        0 12px 30px rgba(31, 52, 65, 0.18);

    color: white;
}

.chat-header-inner {
    display: flex;
    align-items: center;
    gap: 16px;
}

.chat-avatar {
    width: 56px;
    height: 56px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 16px;

    background: rgba(255,255,255,0.13);
    border: 1px solid rgba(255,255,255,0.18);

    font-size: 28px;

    flex-shrink: 0;
}

.chat-header-text {
    flex: 1;
}

.chat-title {
    font-size: 1.55rem;
    font-weight: 750;
    color: #ffffff;
    line-height: 1.2;
}

.chat-subtitle {
    margin-top: 5px;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.75);
}

.chat-header-badge {
    padding: 7px 11px;

    border-radius: 999px;

    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.16);

    color: rgba(255,255,255,0.82);

    font-size: 0.68rem;
    font-weight: 700;
}


/* ============================================================
   BACKEND STATUS
   ============================================================ */

.status-wrapper {
    display: flex;
    align-items: center;
    gap: 10px;

    margin-bottom: 24px;
}

.status-pill {
    flex: 1;

    min-height: 40px;

    display: flex;
    align-items: center;

    padding: 0 15px;

    border-radius: 12px;

    font-size: 0.78rem;
    font-weight: 600;
}

.status-online {
    background: #dcfce7;
    border: 1px solid #bbf7d0;
    color: #166534;
}

.status-offline {
    background: #fee2e2;
    border: 1px solid #fecaca;
    color: #991b1b;
}

.status-idle {
    background: #e8eef5;
    border: 1px solid #d5dee8;
    color: #526273;
}

.status-dot {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    margin-right: 8px;
}

.status-dot-online {
    background: #22c55e;
}

.status-dot-offline {
    background: #ef4444;
}

.status-dot-idle {
    background: #94a3b8;
}


/* ============================================================
   CONVERSATION HEADER
   ============================================================ */

.conversation-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    margin-bottom: 10px;
}

.conversation-title {
    color: #1d3342;
    font-size: 0.86rem;
    font-weight: 800;

    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.conversation-subtitle {
    margin-top: 3px;

    color: #6d8191;
    font-size: 0.72rem;
}

.message-count {
    padding: 6px 10px;

    border-radius: 999px;

    background: #ffffff;
    border: 1px solid #d8e1e9;

    color: #647789;

    font-size: 0.68rem;
    font-weight: 700;
}


/* ============================================================
   CHAT AREA
   ============================================================ */

.chat-surface {
    background: #e4ebf1;

    border: 1px solid #d1dce5;

    border-radius: 20px;

    padding: 20px 18px;

    margin-bottom: 22px;

    box-shadow:
        0 8px 25px rgba(37, 55, 70, 0.06);
}


/* ============================================================
   EMPTY CHAT
   ============================================================ */

.empty-chat {
    min-height: 235px;

    display: flex;
    flex-direction: column;

    align-items: center;
    justify-content: center;

    text-align: center;

    padding: 30px 20px;
}

.empty-icon {
    width: 62px;
    height: 62px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 20px;

    background: #d9eaf5;
    border: 1px solid #c8dce9;

    font-size: 28px;

    margin-bottom: 15px;
}

.empty-title {
    color: #203747;

    font-size: 1rem;
    font-weight: 750;

    margin-bottom: 7px;
}

.empty-description {
    max-width: 500px;

    color: #64798a;

    font-size: 0.78rem;
    line-height: 1.6;
}


/* ============================================================
   NATIVE STREAMLIT CHAT MESSAGES
   ============================================================ */

[data-testid="stChatMessage"] {
    border-radius: 18px !important;

    margin-top: 10px !important;
    margin-bottom: 10px !important;

    padding: 10px 13px !important;
}


/* USER MESSAGE */

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarUser"]
) {
    background: #1677e8 !important;

    border: 0 !important;

    margin-left: 25% !important;
    margin-right: 0 !important;

    color: white !important;

    box-shadow:
        0 5px 14px rgba(22,119,232,0.18);
}


/* ASSISTANT MESSAGE */

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarAssistant"]
) {
    background: #ffffff !important;

    border: 1px solid #dce5ec !important;

    margin-left: 0 !important;
    margin-right: 18% !important;

    color: #263b49 !important;

    box-shadow:
        0 5px 16px rgba(30,50,65,0.07);
}


/* MESSAGE TEXT */

[data-testid="stChatMessageContent"] {
    color: inherit !important;
}

[data-testid="stChatMessageContent"] p {
    line-height: 1.65 !important;
}


/* USER TEXT */

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarUser"]
) [data-testid="stChatMessageContent"] {
    color: white !important;
}


/* ASSISTANT TEXT */

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarAssistant"]
) [data-testid="stChatMessageContent"] {
    color: #263b49 !important;
}


/* ============================================================
   ASSISTANT LABEL
   ============================================================ */

.assistant-label {
    color: #4b6475;

    font-size: 0.68rem;
    font-weight: 800;

    text-transform: uppercase;
    letter-spacing: 0.05em;

    margin-bottom: 5px;
}


/* ============================================================
   CONFIDENCE
   ============================================================ */

.confidence-box {
    margin-top: 13px;

    padding: 10px 12px;

    border-radius: 11px;

    background: #f5f8fa;
    border: 1px solid #e4ebf0;
}

.confidence-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    color: #647887;

    font-size: 0.67rem;
    font-weight: 750;

    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.confidence-value {
    color: #29485b;
}

.confidence-track {
    width: 100%;
    height: 5px;

    background: #dfe7ed;

    border-radius: 999px;

    margin-top: 7px;

    overflow: hidden;
}

.confidence-fill {
    height: 100%;

    background: linear-gradient(
        90deg,
        #1677e8,
        #21a4f3
    );

    border-radius: 999px;
}


/* ============================================================
   SOURCES
   ============================================================ */

.sources-title {
    margin-top: 14px;
    margin-bottom: 7px;

    color: #647887;

    font-size: 0.67rem;
    font-weight: 800;

    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.source-card {
    display: flex;
    align-items: center;

    gap: 9px;

    padding: 8px 10px;

    margin-bottom: 6px;

    background: #f6f9fb;

    border: 1px solid #e2e9ee;

    border-radius: 10px;
}

.source-icon {
    width: 28px;
    height: 28px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 8px;

    background: #e5f1fb;

    font-size: 14px;

    flex-shrink: 0;
}

.source-name {
    color: #334b5b;

    font-size: 0.73rem;
    font-weight: 650;

    word-break: break-word;
}

.source-page {
    margin-top: 1px;

    color: #8293a0;

    font-size: 0.64rem;
}


/* ============================================================
   TECHNICAL DETAILS
   ============================================================ */

[data-testid="stExpander"] {
    border: 1px solid #dbe4ea !important;
    border-radius: 11px !important;
    background: #f8fafb !important;
}


/* ============================================================
   COMPOSER
   ============================================================ */

.composer-title {
    color: #1d3342;

    font-size: 0.9rem;
    font-weight: 800;
}

.composer-subtitle {
    margin-top: 3px;

    color: #708392;

    font-size: 0.7rem;
}


/* ============================================================
   STREAMLIT CHAT INPUT
   ============================================================ */

[data-testid="stChatInput"] {
    margin-top: 4px !important;
}

[data-testid="stChatInput"] > div {
    border-radius: 18px !important;

    background: #ffffff !important;

    border: 1px solid #cdd9e2 !important;

    box-shadow:
        0 8px 25px rgba(30, 52, 67, 0.10) !important;
}

[data-testid="stChatInput"] textarea {
    color: #263b49 !important;

    font-size: 0.86rem !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #8798a6 !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    border-radius: 11px !important;

    border: 1px solid #ccd8e1 !important;

    background: #ffffff !important;

    color: #405667 !important;

    font-size: 0.74rem !important;
}

.stButton > button:hover {
    border-color: #9fb4c3 !important;

    color: #203747 !important;
}


/* ============================================================
   FOOTER NOTE
   ============================================================ */

.footer-note {
    margin-top: 12px;

    text-align: center;

    color: #81919d;

    font-size: 0.66rem;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 768px) {

    .main .block-container {
        padding: 1rem 0.75rem 6rem;
    }

    .chat-header {
        padding: 18px;
        border-radius: 18px;
    }

    .chat-header-inner {
        align-items: flex-start;
    }

    .chat-avatar {
        width: 48px;
        height: 48px;
        font-size: 23px;
    }

    .chat-title {
        font-size: 1.25rem;
    }

    .chat-header-badge {
        display: none;
    }

    .chat-surface {
        padding: 13px 10px;
        border-radius: 16px;
    }

    [data-testid="stChatMessage"]:has(
        [data-testid="stChatMessageAvatarUser"]
    ) {
        margin-left: 8% !important;
    }

    [data-testid="stChatMessage"]:has(
        [data-testid="stChatMessageAvatarAssistant"]
    ) {
        margin-right: 8% !important;
    }
}

</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    if "backend_health" not in st.session_state:
        st.session_state.backend_health = None


# ============================================================
# API RESPONSE VALIDATION
# ============================================================

def validate_api_response(response):
    if not isinstance(response, dict):
        return False

    answer = response.get("answer")

    if not isinstance(answer, str) or not answer.strip():
        return False

    confidence = response.get("confidence")

    if not isinstance(confidence, (int, float)):
        return False

    confidence = float(confidence)

    if not 0.0 <= confidence <= 1.0:
        return False

    citations = response.get("citations", [])

    if not isinstance(citations, list):
        return False

    metadata = response.get("metadata", {})

    if not isinstance(metadata, dict):
        return False

    return True


# ============================================================
# HEADER
# ============================================================

def render_header():
    # IMPORTANT:
    # HTML starts at column 0.
    # Do NOT indent this HTML block.

    st.markdown(
"""<div class="chat-header">
<div class="chat-header-inner">
<div class="chat-avatar">📄</div>
<div class="chat-header-text">
<div class="chat-title">PDF Q&A Assistant</div>
<div class="chat-subtitle">Document-grounded conversational assistant powered by RAG</div>
</div>
<div class="chat-header-badge">RAG • PDF</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )


# ============================================================
# BACKEND STATUS
# ============================================================

def render_backend_status(api_client):

    health = st.session_state.backend_health

    if health is None:

        status_html = """
<div class="status-pill status-idle">
<span class="status-dot status-dot-idle"></span>
Backend status not checked
</div>
"""

    elif health:

        version = html.escape(
            str(health.get("version", "unknown"))
        )

        status_html = f"""
<div class="status-pill status-online">
<span class="status-dot status-dot-online"></span>
Backend online&nbsp; • &nbsp;v{version}
</div>
"""

    else:

        status_html = """
<div class="status-pill status-offline">
<span class="status-dot status-dot-offline"></span>
Backend unavailable
</div>
"""

    col1, col2 = st.columns([6, 1])

    with col1:
        st.markdown(
            status_html,
            unsafe_allow_html=True,
        )

    with col2:

        if st.button(
            "Refresh",
            use_container_width=True,
        ):

            try:
                st.session_state.backend_health = (
                    api_client.health_check()
                )

            except requests.RequestException:
                st.session_state.backend_health = None

            st.rerun()


# ============================================================
# CONFIDENCE
# ============================================================

def render_confidence(confidence):

    confidence = min(
        max(float(confidence), 0.0),
        1.0,
    )

    percentage = confidence * 100

    st.markdown(
f"""<div class="confidence-box">
<div class="confidence-header">
<span>Confidence</span>
<span class="confidence-value">{percentage:.1f}%</span>
</div>
<div class="confidence-track">
<div class="confidence-fill" style="width:{percentage:.1f}%"></div>
</div>
</div>""",
        unsafe_allow_html=True,
    )


# ============================================================
# SOURCES
# ============================================================

def render_sources(citations):

    if not citations:
        return

    st.markdown(
        '<div class="sources-title">Sources</div>',
        unsafe_allow_html=True,
    )

    for citation in citations:

        if not isinstance(citation, dict):
            continue

        file_name = html.escape(
            str(
                citation.get(
                    "file",
                    "Unknown document",
                )
            )
        )

        page = html.escape(
            str(
                citation.get(
                    "page",
                    "Unknown",
                )
            )
        )

        st.markdown(
f"""<div class="source-card">
<div class="source-icon">📄</div>
<div>
<div class="source-name">{file_name}</div>
<div class="source-page">Page {page}</div>
</div>
</div>""",
            unsafe_allow_html=True,
        )


# ============================================================
# TECHNICAL METADATA
# ============================================================

def render_metadata(metadata):

    if not metadata:
        return

    with st.expander(
        "Technical details",
        expanded=False,
    ):

        retrieved_documents = metadata.get(
            "retrieved_documents"
        )

        retrieval_distance = metadata.get(
            "retrieval_distance"
        )

        llm_model = metadata.get(
            "llm_model"
        )

        embedding_model = metadata.get(
            "embedding_model"
        )

        col1, col2 = st.columns(2)

        with col1:

            if retrieved_documents is not None:
                st.caption("Retrieved documents")
                st.write(retrieved_documents)

            if retrieval_distance is not None:
                st.caption("Retrieval score")
                st.write(retrieval_distance)

        with col2:

            if llm_model:
                st.caption("LLM model")
                st.write(llm_model)

            if embedding_model:
                st.caption("Embedding model")
                st.write(embedding_model)


# ============================================================
# EMPTY STATE
# ============================================================

def render_empty_state():

    st.markdown(
"""<div class="empty-chat">
<div class="empty-icon">💬</div>
<div class="empty-title">Hi! 👋 Ask me anything about your documents.</div>
<div class="empty-description">
I can answer questions using the configured PDF knowledge base
and provide supporting document sources for the answer.
</div>
</div>""",
        unsafe_allow_html=True,
    )


# ============================================================
# CONVERSATION
# ============================================================

def render_conversation():

    conversation = st.session_state.conversation

    count = len(conversation) * 2

    st.markdown(
f"""<div class="conversation-header">
<div>
<div class="conversation-title">Conversation</div>
<div class="conversation-subtitle">Your document-grounded chat</div>
</div>
<div class="message-count">{count} messages</div>
</div>""",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # No artificial min-height here.
    # The conversation grows naturally.
    # --------------------------------------------------------

    st.markdown(
        '<div class="chat-surface">',
        unsafe_allow_html=True,
    )

    if not conversation:

        render_empty_state()

    else:

        for turn in conversation:

            # ------------------------------------------------
            # USER
            # ------------------------------------------------

            with st.chat_message(
                "user",
                avatar="👤",
            ):

                st.markdown(
                    turn["question"]
                )

            # ------------------------------------------------
            # ASSISTANT
            # ------------------------------------------------

            with st.chat_message(
                "assistant",
                avatar="📄",
            ):

                st.markdown(
                    '<div class="assistant-label">PDF Assistant</div>',
                    unsafe_allow_html=True,
                )

                # Let Streamlit render the actual answer.
                # This is important because the answer may contain
                # Markdown, lists, headings, etc.
                st.markdown(
                    turn["answer"]
                )

                render_confidence(
                    turn["confidence"]
                )

                render_sources(
                    turn["citations"]
                )

                render_metadata(
                    turn["metadata"]
                )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# ASK QUESTION
# ============================================================

def ask_question(
    api_client,
    question,
):

    question = question.strip()

    if not question:
        return

    try:

        with st.spinner(
            "Searching your documents..."
        ):

            result = api_client.ask_question(
                question
            )

    except requests.HTTPError as exc:

        st.error(
            "The backend rejected the request."
        )

        if exc.response is not None:

            try:

                error_data = (
                    exc.response.json()
                )

                message = error_data.get(
                    "message",
                    "The backend returned an error.",
                )

                st.caption(message)

            except ValueError:

                st.caption(str(exc))

        return

    except requests.RequestException as exc:

        st.error(
            "Unable to connect to the FastAPI backend."
        )

        st.caption(str(exc))

        return

    if not validate_api_response(result):

        st.error(
            "The FastAPI backend returned an invalid response."
        )

        st.caption(
            "The answer was not added to the conversation."
        )

        return

    st.session_state.conversation.append(
        {
            "question": question,
            "answer": result["answer"],
            "confidence": float(
                result["confidence"]
            ),
            "citations": result.get(
                "citations",
                [],
            ),
            "metadata": result.get(
                "metadata",
                {},
            ),
        }
    )


# ============================================================
# MAIN
# ============================================================

def main():

    initialize_session_state()

    api_client = APIClient(
        timeout=API_TIMEOUT
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    render_header()

    # --------------------------------------------------------
    # Backend
    # --------------------------------------------------------

    render_backend_status(
        api_client
    )

    # --------------------------------------------------------
    # Conversation
    # --------------------------------------------------------

    render_conversation()

    # --------------------------------------------------------
    # Composer heading
    # --------------------------------------------------------

    st.markdown(
"""<div class="composer-title">
Write a message
</div>
<div class="composer-subtitle">
Ask a question about your PDF documents and receive a grounded answer from the RAG knowledge base.
</div>""",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Native Streamlit chat input
    # --------------------------------------------------------

    question = st.chat_input(
        "Ask a question about your PDF documents..."
    )

    # --------------------------------------------------------
    # Process question
    # --------------------------------------------------------

    if question:

        ask_question(
            api_client,
            question,
        )

        st.rerun()

    # --------------------------------------------------------
    # Bottom actions
    # --------------------------------------------------------

    col1, col2 = st.columns(
        [1, 5]
    )

    with col1:

        if st.button(
            "Clear chat",
            use_container_width=True,
        ):

            st.session_state.conversation = []

            st.rerun()

    with col2:

        st.markdown(
"""<div class="footer-note">
Answers are generated from the configured PDF knowledge base.
</div>""",
            unsafe_allow_html=True,
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
