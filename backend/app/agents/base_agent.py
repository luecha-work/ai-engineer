from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    PromptTemplate,
    AIMessagePromptTemplate,
)
from langchain.memory.chat_memory import BaseChatMemory


class BaseAgent:
    def __init__(
        self,
        llm,
        tools,
        memory: BaseChatMemory,
        system_prompt: str,
        messages_placeholder: str = "athena_history_store",
    ):
        """PromptTemplate แบบง่าย: role: message (LangChain Expression Language (LCEL)"""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name=messages_placeholder),
                ("human", "{question}"),
                ("placeholder", "{agent_scratchpad}"),
                #    ( "ai", "The capital of France is Paris.")
            ]
        )
        """template engine เต็มรูปแบบ เช่น .from_template() ใช้ str.format() ได้ -> vesion เก่า"""
        # prompt = ChatPromptTemplate.from_messages(
        #     [
        #         SystemMessagePromptTemplate.from_template(
        #             "คุณคือผู้ช่วย AI ที่เชี่ยวชาญเรื่องทั่วไป"
        #         ),
        #         MessagesPlaceholder(variable_name="chat_history"),
        #         HumanMessagePromptTemplate.from_template("{question}"),
        #         ("placeholder", "{agent_scratchpad}"),
        #         AIMessagePromptTemplate.from_template(
        #             "The capital of France is Paris."
        #         ),
        #     ]
        # )

        """ตัวอื่นที่คล้ายกับ create_tool_calling_agent"""
        # create_tool_calling_agent -> Agent แบบ function/tool calling (เช่น Gemini, GPT-4)
        # create_openai_functions_agent -> สำหรับ OpenAI function calling โดยเฉพาะ
        # create_structured_chat_agent -> แบบ structured output (ใช้ JSON schema)
        # create_react_agent -> Agent แบบ ReAct (reasoning + action)
        # create_self_ask_with_search_agent -> Agent ที่ถามซ้อนและค้นข้อมูล
        # create_xml_agent -> Agent ที่รับ/ส่งข้อมูลในรูปแบบ XML
        # create_multi_function_agent -> Agent ที่เรียกหลาย tool พร้อมกัน (multi-action agent)

        agent = create_tool_calling_agent(llm, tools, prompt)

        self.executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            handle_parsing_errors=True,
            verbose=True,
        )

    # def ask(self, input: str) -> str:
    #     response = self.executor.invoke({"input": input})
    #     return response.get("output", "")

    def ask(self, question: str) -> str:
        try:
            response = self.executor.invoke({"question": question})
            return response["output"]
        except Exception as e:
            return f"error: {e}"
