
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from config import AppConfig


# TODO : Setup a dict of models with thier params and 
# strengths/weaknesses and let user's(and superagents) pick from them

model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    api_key=AppConfig.GEMINI_API_KEY,
    temperature=1.0, 
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)



def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)






# from pydantic import BaseModel
# from langgraph.graph import START, StateGraph
# from pydantic import ConfigDict
# from langgraph.graph
# # Configure Gemini
# genai.configure(api_key="your-api-key")
# llm = genai.GenerativeModel("gemini-pro")

# class CommState(BaseModel):
#     text: str
#     model_config = ConfigDict(from_attributes=True)

# # Define tools
# def print_text(text: str) -> str:
#     """Print text to console."""
#     print(f"Output: {text}")
#     return text

# def node_a(state: CommState) -> dict:
#     response = llm.generate_content(state.text + " What was the last thing we discussed?")
#     result = response.text
#     print_text(result)
#     return {"text": result}

# def node_b(state: CommState) -> dict:
#     response = llm.generate_content(state.text)
#     result = response.text
#     print_text(result)
#     return {"text": result}

# graph = StateGraph(CommState)
# graph.add_node("node_a", node_a)
# graph.add_node("node_b", node_b)
# graph.add_edge(START, "node_a")
# graph.add_edge("node_a", "node_b")

# compiled_graph = graph.compile()
# print(compiled_graph.invoke({"text": "Hello, let's have a conversation"}))






















