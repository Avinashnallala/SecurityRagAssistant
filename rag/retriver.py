def get_retriver(vector_store):
    retriver=vector_store.as_retriever(
        search_kwargs={"k":3}
    )

    return retriver