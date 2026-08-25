from llm.model import get_model

from rag.document_loader import load_docs
from rag.text_splitter import split_documents
from rag.embeddings import get_embeddings
from rag.vector_store import create_vector_store
from rag.retriver import get_retriver
from rag.rag_service import generate_rag_response
from agents.agent import create_secure_agent
from guardrails.retrieval_guard import (
    check_retrieved_documents,
)

from guardrails.grounding_guard import (
    check_grounding,
)
from evalution.llm_evaluator import (
    evaluate_llm_response,
)


def main():

    docs=load_docs("data/document/SecureRAG_Sample_Employee_Handbook.pdf")
    chunks=split_documents(docs)
    embedding=get_embeddings()
    vector_store=create_vector_store(chunks,embedding)
    retriver=get_retriver(vector_store)
    agent=create_secure_agent(retriver)
    question=( "My email is john@example.com. "
    "What is the vacation policy?")
    #answer=generate_rag_response(question,retriver,model)
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    answer=result['messages'][-1].content

    retrived_documents=retriver.invoke(question)

    safe_documents,blocked_documents=(
        check_retrieved_documents(retrived_documents)
    )

    grounding_result=check_grounding(
        question=question,
        answer=answer,
        documents=safe_documents
    )

    llm_evaluation = evaluate_llm_response(
    question=question,
    answer=answer,
    context=safe_documents
    )

    if (not grounding_result.grounded or grounding_result.score<0.80):
        final_answer=(
            "I could not verify the complete answer from the company documents"
        )
    elif not llm_evaluation.passed:
        final_answer=(
            "The generated response did not pass the LLM quality evaluation"
        )
    else:
        final_answer=answer

    print('\nFinal Answer')
    print(final_answer) 

if __name__=="__main__":
    main()