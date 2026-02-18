from langchain_google_vertexai import ChatVertexAI

from app.memory.redis_memory import create_redis_memory
from app.agents.base_agent import BaseAgent


class SalesTechniqueAgent(BaseAgent):
    """docstring for SalesTechniqueAgent."""

    def __init__(self, session_id: str, sales_knowledge: str, gcp_project: str):
        llm = ChatVertexAI(
            model_name="gemini-2.5-flash-lite", project=gcp_project, temperature=0
        )
        tools = []
        memory = create_redis_memory(
            session_id=session_id,
            key_prefix=f"chat_history_{self.__class__.__name__}:",
            memory_key=f"chat_history_{self.__class__.__name__}",
        )
        system_prompt = self._build_system_prompt(sales_knowledge)

        super().__init__(
            llm=llm,
            tools=tools,
            memory=memory,
            system_prompt=system_prompt,
            messages_placeholder=f"chat_history_{self.__class__.__name__}",
        )

    def _build_system_prompt(self, context: str):
        system_prompt = f"""Use the following context as your learned knowledge, inside <context></context> XML tags.
                            <context>
                            {context}
                            </context>"""

        return system_prompt
