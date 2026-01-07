from pydantic import BaseModel, Field
from langgraph.graph import START, END, StateGraph
from typing import Annotated, List
from pydantic import ConfigDict
import operator
from config import AppConfig

# Configure your LLM - example with Google's Gemini
from google import genai
client = genai.Client(api_key=AppConfig.GEMINI_API_KEY)

# Or with OpenAI:
# from openai import OpenAI
# client = OpenAI(api_key="YOUR_API_KEY")

# Or with Anthropic Claude:
# from anthropic import Anthropic
# client = Anthropic(api_key="YOUR_API_KEY")


class ConversationState(BaseModel):
    """State for the conversation workflow"""
    messages: Annotated[List[dict], operator.add] = Field(default_factory=list)
    current_question: str = ""
    should_continue: bool = True
    model_config = ConfigDict(arbitrary_types_allowed=True)


def print_tool(text: str) -> str:
    """Print text to console with formatting."""
    print(f"\n{'='*50}")
    print(f"🤖 Assistant: {text}")
    print(f"{'='*50}\n")
    return text


def get_user_input(state: ConversationState) -> dict:
    """Get input from the user"""
    user_input = input("👤 You: ").strip()
    
    # Check if user wants to stop
    stop_words = ["stop", "quit", "exit", "bye", "goodbye"]
    should_continue = user_input.lower() not in stop_words
    
    return {
        "messages": [{"role": "user", "content": user_input}],
        "current_question": user_input,
        "should_continue": should_continue
    }


def answer_question(state: ConversationState) -> dict:
    """Use LLM to answer the user's question with conversation history"""
    
    # Build context from conversation history
    conversation_context = "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in state.messages
    ])
    
    # Create prompt with context
    prompt = f"""You are a helpful assistant. Here's our conversation so far:

        {conversation_context}

        Please provide a helpful and concise answer to the user's question.
    """

    # For Google Gemini:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    answer = response.text

    # For OpenAI:
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # answer = response.choices[0].message.content
    
    # For Anthropic Claude:
    # response = client.messages.create(
    #     model="claude-3-5-sonnet-20241022",
    #     max_tokens=1000,
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # answer = response.content[0].text

    # Mock answer for demonstration (replace with actual LLM call)
    answer = answer or f"This is a mock answer to: '{state.current_question}'. Please configure your LLM provider above."

    print_tool(answer)
    
    return {
        "messages": [{"role": "assistant", "content": answer}]
    }


def should_continue_conversation(state: ConversationState) -> str:
    """Determine if we should continue or end the conversation"""
    if state.should_continue:
        return "get_input"
    else:
        print_tool("Goodbye! Thanks for chatting!")
        return "end"


# Build the graph
def create_conversation_graph():
    """Create and compile the conversation graph"""
    graph = StateGraph(ConversationState)
    
    # Add nodes
    graph.add_node("get_input", get_user_input)
    graph.add_node("answer", answer_question)
    
    # Add edges
    graph.add_edge(START, "get_input")
    graph.add_edge("get_input", "answer")
    
    # Add conditional edge to loop or end
    graph.add_conditional_edges(
        "answer",
        should_continue_conversation,
        {
            "get_input": "get_input",
            "end": END
        }
    )
    
    return graph.compile()


def main():
    """Run the conversational agent"""
    print("\n🤖 Conversational Agent Started!")
    print("Ask me anything. Type 'stop', 'quit', or 'exit' to end the conversation.\n")
    
    # Create and run the graph
    graph = create_conversation_graph()
    
    # Initialize state
    initial_state = ConversationState(
        messages=[],
        current_question="",
        should_continue=True
    )
    
    # Run the graph
    final_state = graph.invoke(initial_state)
    
    print("\n✅ Conversation ended.")
    print(f"Total messages exchanged: {len(final_state['messages'])}")


if __name__ == "__main__":
    main()




# TODO Use google.genai client context managers in fastapi app lifespan