from langchain.tools import tool
from guardrails.retrieval_guard import (check_retrieved_documents)


def create_policy_tool(retriever):

    @tool
    def search_company_policy(
        query: str
    ) -> str:
        """
        Search company documents for HR, employee benefits,
        leave, IT, security, and company policy information.
        """

        documents = retriever.invoke(
            query
        )

        if not documents:

            return (
                "No relevant information was found "
                "in the company documents."
            )

        safe_documents,blocked_documents=(
            check_retrieved_documents(documents)
        )

        if not safe_documents:
            return(
                "The retrieved documents failed"
            )
        context="\n\n".join(document.page_content for document in safe_documents)

        return context

    return search_company_policy