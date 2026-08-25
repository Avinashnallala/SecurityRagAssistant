from typing import Any

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    hook_config,
)

from langgraph.runtime import Runtime


class JailbreakGuard(AgentMiddleware):

    def __init__(self):

        super().__init__()

        self.jailbreak_patterns = [

            "dan mode",
            "developer mode",
            "unrestricted mode",
            "jailbreak mode",
            "pretend you have no rules",
            "pretend there are no rules",
            "act without restrictions",
            "disable safety",
            "disable guardrails",
            "bypass guardrails",
            "ignore safety rules",
            "ignore your safety policy",
            "you are now unrestricted",
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

        for pattern in self.jailbreak_patterns:

            if pattern in content:

                return {
                    "messages": [
                        {
                            "role": "assistant",
                            "content": (
                                "This request was blocked because a "
                                "jailbreak attempt was detected."
                            ),
                        }
                    ],
                    "jump_to": "end",
                }

        return None