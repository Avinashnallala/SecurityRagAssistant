from pydantic import BaseModel, Field

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from llm.model import get_model


class GroundingResult(BaseModel):

    grounded: bool

    score: float = Field(
        ge=0.0,
        le=1.0
    )

    unsupported_claims: list[str] = Field(
        default_factory=list
    )

    reason: str


def check_grounding(
    question: str,
    answer: str,
    documents
) -> GroundingResult:

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    model = get_model()

    evaluator = model.with_structured_output(
        GroundingResult
    )

    system_prompt = """
You are a grounding evaluator for a secure
Retrieval-Augmented Generation system.

Determine whether the generated answer is supported
by the retrieved context.

Rules:

1. Use only the retrieved context.
2. Do not use outside knowledge.
3. Every important factual claim must be supported.
4. If the answer contains unsupported claims,
   grounded must be false.
5. Score groundedness from 0.0 to 1.0.
6. List unsupported claims.
7. Explain the decision briefly.
"""

    user_prompt = f"""
USER QUESTION:

{question}


RETRIEVED CONTEXT:

{context}


GENERATED ANSWER:

{answer}
"""

    result = evaluator.invoke(
        [
            SystemMessage(
                content=system_prompt
            ),

            HumanMessage(
                content=user_prompt
            )
        ]
    )

    return result