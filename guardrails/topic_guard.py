from typing import Any

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    hook_config,
)

from langgraph.runtime import Runtime


class TopicGuard(AgentMiddleware):

    def __init__(self):

        super().__init__()

        self.allowed_topics = [

            "employee",
            "company",
            "policy",
            "vacation",
            "leave",
            "sick",
            "benefits",
            "insurance",
            "401k",
            "401(k)",
            "parental",
            "remote work",
            "work from home",
            "security",
            "password",
            "information security",
            "it support",
            "technical issue",
            "confidential",
            "hr",
            "human resources",
        ]

    @hook_config(can_jump_to=["end"])
    def before_agent(
        self,
        state: AgentState,
        runtime: Runtime,
    ) -> dict[str, Any] | None:

        if not state["messages"]:
            return None

        user_message = None

        for message in reversed(state["messages"]):

            if message.type == "human":
                user_message = message
                break

        if user_message is None:
            return None

        content = str(user_message.content).lower()

        allowed = any(
            topic in content
            for topic in self.allowed_topics
        )

        if not allowed:

            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": (
                            "I can only assist with company policies, "
                            "HR, benefits, leave, IT, and information "
                            "security questions."
                        ),
                    }
                ],
                "jump_to": "end",
            }

        return None