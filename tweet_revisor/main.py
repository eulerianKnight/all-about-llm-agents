import os
from typing import List, Sequence
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph

from chains import generate_chain, reflect_chain

REFLECT = 'reflect'
GENERATE = 'generate'

def generation_node(state: Sequence[BaseMessage]):
    return generate_chain.invoke({'messages': state})

def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    response = reflect_chain.invoke({"messages": messages})
    return [HumanMessage(content=response.content)]

builder = MessageGraph()
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)
builder.set_entry_point(GENERATE)

def should_continue(state: List[BaseMessage]):
    if len(state) > 6:
        return END
    return REFLECT


builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)

graph = builder.compile()
print(graph.get_graph().draw_mermaid())

if __name__ == "__main__":
    print("Hello LangGraph")
    inputs = HumanMessage(content="""Consider being a labeler for an LLM.
    The prompt is "give me a random number between 1 and 10." What SFT and RM labels do you contribute?
    What does this do the network when trained on?
    In subtle way this problem is present in every prompt that does not have a single unique answer.
    """)
    response = graph.invoke(inputs)

