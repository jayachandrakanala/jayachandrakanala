from typing import Annotated
from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import END, START
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv

import os
load_dotenv()
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["LANGSMITH_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")

class State(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

model=ChatGroq(model="qwen/qwen3.8-27b", max_tokens=200)

def build_model_graph():
    graph_workflow=StateGraph(State)

    def call_model(state):
        return {"messages":[model.invoke(state['messages'])]}
    
    graph_workflow.add_node("agent", call_model)
    graph_workflow.add_edge(START, "agent")
    graph_workflow.add_edge("agent", END)

    agent=graph_workflow.compile()
    return agent

def build_model_with_tools_graph():
    """Make a tool-calling agent"""

    @tool
    def add(a: float, b: float):
        """Adds two numbers."""
        return a + b

    @tool
    def sub(a: float, b: float):
        """Substracts two numbers."""
        return a - b

    tools_node = ToolNode([add, sub])
    model_with_tools = model.bind_tools([add, sub])    
    def call_model(state):
        return {"messages": [model_with_tools.invoke(state["messages"])]}

    def should_continue(state: State):
        if state["messages"][-1].tool_calls:
            return "tools"
        else:
            return END

    graph_workflow = StateGraph(State)
    graph_workflow.add_node("agent", call_model)
    graph_workflow.add_node("tools", tools_node)

    graph_workflow.add_edge(START, "agent")
    graph_workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  # maps return value "tools" -> "tools" node
            END: END           # maps return value END -> __end__ node
        }
    )
    graph_workflow.add_edge("tools", "agent")

    agent = graph_workflow.compile()
    return agent

agent=build_model_with_tools_graph()