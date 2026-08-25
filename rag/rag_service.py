from langchain_core.messages import SystemMessage,HumanMessage

def generate_rag_response(question,retriver,model):
    documents=retriver.invoke(question)
    context="\n\n".join(doc.page_content for doc in documents)
    system_prompt= """
        You are a helpful enterprise assistant.

        Answer the user's question only using the provided context.

        If the answer is not available in the context, say:
        "I could not find that information in the provided documents."

        Do not make up information.
        """
    user_prompt = f"""
        Context:
        {context}

        Question:
        {question}
        """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = model.invoke(messages)

    return response.content
