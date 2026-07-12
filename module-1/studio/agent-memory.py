import os

from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode

def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiplies a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b

tools = [add, multiply, divide]

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with writing performing arithmetic on a set of inputs.")

# Node
def assistant(state: MessagesState):
    llm = ChatGroq(model="openai/gpt-oss-120b")
    llm_with_tools = llm.bind_tools(tools)
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

def _should_use_platform_persistence() -> bool:
    return any(
        os.getenv(name)
        for name in (
            "LANGGRAPH_API_URL",
            "LANGGRAPH_RUNTIME_EDITION",
            "LANGSMITH_LANGGRAPH_API_VARIANT",
        )
    )


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

# Compile graph with memory for local SDK usage, but avoid custom checkpointers in hosted LangGraph runtimes.
react_graph_memory = builder.compile(
    checkpointer=MemorySaver()
) if not _should_use_platform_persistence() else builder.compile()

graph = react_graph_memory
