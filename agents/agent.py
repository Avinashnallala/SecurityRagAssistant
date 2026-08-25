from langchain.agents import create_agent

from llm.model import get_model
from guardrails.pii_guard import get_pii_guardrails
from guardrails.prompt_injection_guard import PromptInjectionGuard
from guardrails.jailbreak_guard import JailbreakGuard
from guardrails.topic_guard import TopicGuard
from tools.policy_tools import create_policy_tool

def create_secure_agent(retriever,tools=None):
    if tools is None:
        tools=[]
    model=get_model()
    policy_tool = create_policy_tool(
        retriever
    )
    all_tools=[policy_tool,*tools]
    pii_guardrails=get_pii_guardrails()
    middleware=[
        PromptInjectionGuard(),
        JailbreakGuard(),
        TopicGuard(),
        *pii_guardrails,
    ]

    agent=create_agent(
        model=model,
        tools=all_tools,
        middleware=middleware,
        system_prompt="""
            You are SecureRAG Assistant.

            You are an enterprise AI assistant for answering questions
            about company policies, HR, employee benefits, leave,
            IT support, and information security.

            Use the available company-policy search tool when company
            information is required.

            Do not invent company policies.

            If information is unavailable in the retrieved documents,
            say that the information could not be found.
            """
    )

    return agent