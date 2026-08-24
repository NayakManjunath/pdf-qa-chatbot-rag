import requests
import streamlit as st

try:
    from ui.api_client import APIClient
    from ui.config import API_TIMEOUT, APP_ICON, APP_TITLE
except ModuleNotFoundError:
    from api_client import APIClient
    from config import API_TIMEOUT, APP_ICON, APP_TITLE


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)


def initialize_session_state() -> None:
    """Initialize Streamlit session state for conversation history."""

    if "conversation" not in st.session_state:
        st.session_state.conversation = []


def validate_api_response(response: dict) -> bool:
    """Validate the response structure returned by the FastAPI backend."""

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


def render_backend_status(api_client: APIClient) -> None:
    """Render the FastAPI backend health status."""

    st.subheader("Backend Status")

    if st.button("Check API Status"):
        try:
            health = api_client.health_check()

            st.success("FastAPI backend is healthy.")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Status", health["status"])

            with col2:
                st.metric("Version", health["version"])

            with col3:
                st.metric(
                    "Uptime",
                    f'{health["uptime_seconds"]} sec',
                )

        except requests.RequestException as exc:
            st.error(
                "Unable to connect to the FastAPI backend."
            )
            st.caption(str(exc))


def render_sources(citations: list[dict]) -> None:
    """Render document citations associated with an answer."""

    if not citations:
        st.caption("No document citations were returned.")
        return

    st.markdown("**Sources**")

    for citation in citations:
        file_name = citation.get(
            "file",
            "Unknown document",
        )

        page = citation.get(
            "page",
            "Unknown",
        )

        st.markdown(
            f"📄 **{file_name}**  \n"
            f"Page: {page}"
        )


def render_response_metadata(metadata: dict) -> None:
    """Render technical response metadata."""

    if not metadata:
        return

    with st.expander("Response Metadata"):

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

        if retrieved_documents is not None:
            st.write(
                f"**Retrieved Documents:** "
                f"{retrieved_documents}"
            )

        if retrieval_distance is not None:
            st.write(
                f"**Retrieval Score:** "
                f"{retrieval_distance}"
            )

        if llm_model:
            st.write(
                f"**LLM Model:** "
                f"{llm_model}"
            )

        if embedding_model:
            st.write(
                f"**Embedding Model:** "
                f"{embedding_model}"
            )


def render_answer(
    answer: str,
    confidence: float,
    citations: list[dict],
    metadata: dict,
) -> None:
    """Render an answer with confidence, sources, and metadata."""

    st.markdown("**Assistant**")

    st.write(answer)

    st.markdown("**Confidence**")

    confidence = min(
        max(float(confidence), 0.0),
        1.0,
    )

    confidence_percentage = confidence * 100

    st.progress(
        confidence,
        text=f"{confidence_percentage:.1f}%",
    )

    render_sources(citations)

    render_response_metadata(metadata)


def render_conversation_history() -> None:
    """Render the current conversation history."""

    conversation = st.session_state.conversation

    if not conversation:
        return

    st.subheader("Conversation")

    for turn in conversation:

        st.markdown("**You**")

        st.write(
            turn["question"]
        )

        render_answer(
            answer=turn["answer"],
            confidence=turn["confidence"],
            citations=turn["citations"],
            metadata=turn["metadata"],
        )

        st.divider()


def clear_conversation() -> None:
    """Clear the current conversation."""

    st.session_state.conversation = []


def render_question_interface(
    api_client: APIClient,
) -> None:
    """Render the PDF question-answering interface."""

    st.subheader("Ask a Question")

    question = st.text_area(
        "Enter your question",
        placeholder=(
            "Ask a question about your PDF documents..."
        ),
        height=120,
        key="question_input",
    )

    col1, col2 = st.columns([1, 5])

    with col1:
        ask_clicked = st.button(
            "Ask Question",
            type="primary",
        )

    with col2:
        clear_clicked = st.button(
            "Clear Conversation",
        )

    if clear_clicked:
        clear_conversation()
        st.rerun()

    if not ask_clicked:
        return

    question = question.strip()

    if not question:
        st.warning(
            "Please enter a question."
        )
        return

    with st.spinner(
        "Generating answer..."
    ):
        try:
            result = api_client.ask_question(
                question
            )

        except requests.HTTPError as exc:

            st.error(
                "The FastAPI backend rejected the request."
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
            "The FastAPI backend returned "
            "an invalid response."
        )

        st.caption(
            "The answer was not added "
            "to the conversation."
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

    st.rerun()


def main() -> None:
    """Run the Streamlit application."""

    initialize_session_state()

    st.title(
        "📄 PDF Q&A Chatbot"
    )

    st.write(
        "Ask questions about your uploaded PDF "
        "documents using Retrieval-Augmented Generation."
    )

    st.divider()

    api_client = APIClient(
        timeout=API_TIMEOUT,
    )

    render_backend_status(
        api_client
    )

    st.divider()

    render_conversation_history()

    render_question_interface(
        api_client
    )


if __name__ == "__main__":
    main()