from langchain.agents.middleware import PIIMiddleware

def get_pii_guardrails():
    pii_guardrails=[
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
            apply_to_output=True
        ),
        PIIMiddleware(
            'credit_card',
            strategy="mask",
            apply_to_input=True,
            apply_to_output=True

        ),
        PIIMiddleware(
            'ip',
            strategy="redact",
            apply_to_input=True,
            apply_to_output=True

        ),
        PIIMiddleware(
            'ssn',
            detector=r"\b\d{3}-\d{2}-\d{4}\b",
            strategy="redact",
            apply_to_input=True,
            apply_to_output=True

        )

    ]
    return pii_guardrails