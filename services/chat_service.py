from rag.document_loader import load_docs
from rag.text_splitter import split_documents
from rag.embeddings import get_embeddings
from rag.vector_store import create_vector_store
from rag.retriver import get_retriver

from tools.policy_tools import create_policy_tool
from agents.agent import create_secure_agent

from guardrails.retrieval_guard import check_retrieved_documents
from guardrails.grounding_guard import check_grounding

from evalution.llm_evaluator import evaluate_llm_response


PDF_PATH = (
    "data/document/"
    "SecureRAG_Sample_Employee_Handbook.pdf"
)


def initialize_secure_rag():

    documents = load_docs(PDF_PATH)

    chunks = split_documents(documents)

    embeddings = get_embeddings()

    vector_store = create_vector_store(
        chunks,
        embeddings
    )

    retriever = get_retriver(
        vector_store
    )

    policy_tool = create_policy_tool(
        retriever
    )

    agent = create_secure_agent(
        retriever=retriever
    )

    return {
        "retriever": retriever,
        "agent": agent
    }


def process_question(
    question: str,
    system: dict
):

    retriever = system["retriever"]
    agent = system["agent"]

    # -----------------------------
    # Agent
    # -----------------------------

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
    )

    answer = result["messages"][-1].content


    # -----------------------------
    # Retrieve documents
    # -----------------------------

    retrieved_documents = retriever.invoke(
        question
    )


    # -----------------------------
    # Retrieval Guard
    # -----------------------------

    safe_documents, blocked_documents = (
        check_retrieved_documents(
            retrieved_documents
        )
    )


    if not safe_documents:

        return {
            "final_answer":
                "The retrieved documents failed security validation.",

            "generated_answer":
                answer,

            "retrieved_count":
                len(retrieved_documents),

            "safe_count":
                0,

            "blocked_count":
                len(blocked_documents),

            "grounded":
                False,

            "grounding_score":
                0.0,

            "unsupported_claims":
                [],

            "evaluation_passed":
                False,

            "answer_relevance":
                0.0,

            "instruction_following":
                0.0,

            "evaluation_groundedness":
                0.0,

            "completeness":
                0.0,

            "clarity":
                0.0,

            "safety":
                0.0,

            "hallucination_risk":
                1.0,

            "overall_score":
                0.0,

            "issues": [
                "Retrieved context failed security validation."
            ]
        }


    # -----------------------------
    # Grounding Guard
    # -----------------------------

    grounding_result = check_grounding(
        question=question,
        answer=answer,
        documents=safe_documents
    )


    # -----------------------------
    # LLM Evaluation
    # -----------------------------

    llm_evaluation = evaluate_llm_response(
        question=question,
        answer=answer,
        context=safe_documents
    )


    # -----------------------------
    # Final Quality Gate
    # -----------------------------

    if (
        not grounding_result.grounded
        or grounding_result.score < 0.80
    ):

        final_answer = (
            "I could not verify the complete answer "
            "from the company documents."
        )

    elif not llm_evaluation.passed:

        final_answer = (
            "The generated response did not pass "
            "the LLM quality evaluation."
        )

    else:

        final_answer = answer


    # -----------------------------
    # Return data to UI
    # -----------------------------

    return {

        "final_answer":
            final_answer,

        "generated_answer":
            answer,

        "retrieved_count":
            len(retrieved_documents),

        "safe_count":
            len(safe_documents),

        "blocked_count":
            len(blocked_documents),

        "grounded":
            grounding_result.grounded,

        "grounding_score":
            grounding_result.score,

        "unsupported_claims":
            grounding_result.unsupported_claims,

        "grounding_reason":
            grounding_result.reason,

        "evaluation_passed":
            llm_evaluation.passed,

        "answer_relevance":
            llm_evaluation.answer_relevance,

        "instruction_following":
            llm_evaluation.instruction_following,

        "evaluation_groundedness":
            llm_evaluation.groundedness,

        "completeness":
            llm_evaluation.completeness,

        "clarity":
            llm_evaluation.clarity,

        "safety":
            llm_evaluation.safety,

        "hallucination_risk":
            llm_evaluation.hallucination_risk,

        "overall_score":
            llm_evaluation.overall_score,

        "issues":
            llm_evaluation.issues,

        "evaluation_reason":
            llm_evaluation.reason
    }