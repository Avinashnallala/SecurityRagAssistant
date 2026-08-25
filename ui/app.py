import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.chat_service import (
    initialize_secure_rag,
    process_question,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SecureRAG Assistant",
    page_icon="🛡️",
    layout="wide",
)


# ============================================================
# TITLE
# ============================================================

st.title("🛡️ SecureRAG Assistant")

st.caption(
    "Secure Enterprise RAG Assistant using "
    "LangChain Guardrails and LLM Evaluation"
)


# ============================================================
# INITIALIZE SECURE RAG
# ============================================================

@st.cache_resource
def load_secure_rag():

    return initialize_secure_rag()


with st.spinner(
    "Initializing SecureRAG Assistant..."
):

    system = load_secure_rag()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🛡️ SecureRAG")

    st.write(
        "Enterprise document assistant protected "
        "with multiple AI safety layers."
    )

    st.divider()

    st.subheader("Guardrails")

    st.write("✅ PII Protection")
    st.write("✅ Prompt Injection Guard")
    st.write("✅ Jailbreak Guard")
    st.write("✅ Topic Guard")
    st.write("✅ Retrieval Guard")
    st.write("✅ Grounding Guard")
    st.write("✅ LLM Evaluation")

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about company policies..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Display user message
    with st.chat_message("user"):

        st.markdown(question)


    # ========================================================
    # ASSISTANT RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching documents and running security checks..."
        ):

            try:

                result = process_question(
                    question=question,
                    system=system
                )

            except Exception as error:

                st.error(
                    f"SecureRAG encountered an error: {error}"
                )

                st.stop()


        # ====================================================
        # FINAL ANSWER
        # ====================================================

        final_answer = result.get(
            "final_answer",
            "Unable to generate a response."
        )

        st.markdown(final_answer)


        # ====================================================
        # SAVE RESPONSE
        # ====================================================

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": final_answer
            }
        )


        # ====================================================
        # SECURITY + EVALUATION PANEL
        # ====================================================

        with st.expander(
            "🛡️ Security & Evaluation Details"
        ):

            # =================================================
            # RETRIEVAL SECURITY
            # =================================================

            st.subheader(
                "📚 Retrieval Security"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Retrieved Chunks",
                    result.get(
                        "retrieved_count",
                        0
                    )
                )

            with col2:

                st.metric(
                    "Safe Chunks",
                    result.get(
                        "safe_count",
                        0
                    )
                )

            with col3:

                st.metric(
                    "Blocked Chunks",
                    result.get(
                        "blocked_count",
                        0
                    )
                )


            st.divider()


            # =================================================
            # GROUNDING
            # =================================================

            st.subheader(
                "🎯 Grounding Evaluation"
            )

            grounded = result.get(
                "grounded",
                False
            )

            grounding_score = result.get(
                "grounding_score",
                0.0
            )

            col1, col2 = st.columns(2)

            with col1:

                if grounded:

                    st.success(
                        "✅ Grounded"
                    )

                else:

                    st.error(
                        "❌ Not Grounded"
                    )

            with col2:

                st.metric(
                    "Grounding Score",
                    f"{grounding_score:.2f}"
                )


            grounding_reason = result.get(
                "grounding_reason"
            )

            if grounding_reason:

                st.write(
                    "**Reason:**",
                    grounding_reason
                )


            unsupported_claims = result.get(
                "unsupported_claims",
                []
            )

            if unsupported_claims:

                st.warning(
                    "Unsupported claims were detected:"
                )

                for claim in unsupported_claims:

                    st.write(
                        f"- {claim}"
                    )


            st.divider()


            # =================================================
            # LLM EVALUATION
            # =================================================

            st.subheader(
                "🧠 LLM Evaluation"
            )

            evaluation_passed = result.get(
                "evaluation_passed",
                False
            )

            if evaluation_passed:

                st.success(
                    "✅ LLM Evaluation Passed"
                )

            else:

                st.error(
                    "❌ LLM Evaluation Failed"
                )


            # =================================================
            # METRICS ROW 1
            # =================================================

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Answer Relevance",
                    f"{result.get('answer_relevance', 0.0):.2f}"
                )

            with col2:

                st.metric(
                    "Instruction Following",
                    f"{result.get('instruction_following', 0.0):.2f}"
                )

            with col3:

                st.metric(
                    "Groundedness",
                    f"{result.get('evaluation_groundedness', 0.0):.2f}"
                )


            # =================================================
            # METRICS ROW 2
            # =================================================

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Completeness",
                    f"{result.get('completeness', 0.0):.2f}"
                )

            with col2:

                st.metric(
                    "Clarity",
                    f"{result.get('clarity', 0.0):.2f}"
                )

            with col3:

                st.metric(
                    "Safety",
                    f"{result.get('safety', 0.0):.2f}"
                )


            # =================================================
            # HALLUCINATION + OVERALL
            # =================================================

            col1, col2 = st.columns(2)

            with col1:

                hallucination_risk = result.get(
                    "hallucination_risk",
                    0.0
                )

                st.metric(
                    "Hallucination Risk",
                    f"{hallucination_risk:.2f}"
                )

            with col2:

                st.metric(
                    "Overall LLM Score",
                    f"{result.get('overall_score', 0.0):.2f}"
                )


            st.divider()


            # =================================================
            # EVALUATION ISSUES
            # =================================================

            issues = result.get(
                "issues",
                []
            )

            if issues:

                st.subheader(
                    "⚠️ Evaluation Issues"
                )

                for issue in issues:

                    st.write(
                        f"- {issue}"
                    )

            else:

                st.success(
                    "No significant LLM evaluation issues detected."
                )


            # =================================================
            # EVALUATION REASON
            # =================================================

            evaluation_reason = result.get(
                "evaluation_reason"
            )

            if evaluation_reason:

                st.subheader(
                    "Evaluation Explanation"
                )

                st.write(
                    evaluation_reason
                )


            # =================================================
            # RAW GENERATED ANSWER
            # =================================================

            st.divider()

            st.subheader(
                "🤖 Original Generated Answer"
            )

            st.write(
                result.get(
                    "generated_answer",
                    ""
                )
            )