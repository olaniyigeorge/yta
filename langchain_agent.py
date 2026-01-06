from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from config import AppConfig
import json
import os
import uuid


# TODO : Setup a dict of models with thier params and 
# strengths/weaknesses and let user's(and superagents) pick from them

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=AppConfig.GEMINI_API_KEY,
    temperature=1.0, 
    max_tokens=500,
    timeout=None,
    max_retries=2,
)

# In-memory storage for feedbacks
feedbacks = {}
feedback_id_counter = 1



def save_feedbacks_to_file():
    """Save feedbacks to a JSON file."""
    with open('feedbacks.json', 'w') as f:
        json.dump(list(feedbacks.values()), f)

def delete_feedback(feedback_id: str) -> str:
    """Delete a feedback and remove it from the file gracefully."""
    if feedback_id not in feedbacks:
        return f"Feedback {feedback_id} not found."
    
    del feedbacks[feedback_id]
    save_feedbacks_to_file()  # Save changes to the file
    return f"Feedback {feedback_id} deleted successfully."


def get_feedback(feedback_id: str = None, body: str = None) -> str:
    """Get feedback by ID or filter by body."""
    if feedback_id:
        feedback = feedbacks.get(feedback_id)
        return feedback if feedback else f"Feedback {feedback_id} not found."
    
    if body:
        filtered_feedbacks = {k: v for k, v in feedbacks.items() if body in v['body']}
        return filtered_feedbacks if filtered_feedbacks else "No feedback found with that body."

    return "Please provide either an ID or body to filter."


def create_feedback(body: str, type: str, status: str = "open") -> str:
    """Create a new feedback with a UUID as ID."""
    feedback_id = str(uuid.uuid4())
    feedbacks[feedback_id] = {
        "id": feedback_id,
        "body": body,
        "type": type,
        "status": status
    }
    save_feedbacks_to_file()
    return f"Feedback {feedback_id} created successfully."


def update_feedback(feedback_id: str, body: str = None, type: str = None, status: str = None) -> str:
    """Update an existing feedback."""
    if feedback_id not in feedbacks:
        return f"Feedback {feedback_id} not found."
    
    if body:
        feedbacks[feedback_id]["body"] = body
    if type:
        feedbacks[feedback_id]["type"] = type
    if status:
        feedbacks[feedback_id]["status"] = status
    
    save_feedbacks_to_file()  # Save changes to the file
    return f"Feedback {feedback_id} updated successfully."


reviewer_agent = create_agent(
    model=model,
    tools=[create_feedback, update_feedback, delete_feedback, get_feedback],
    system_prompt="You are a helpful assistant",
)

# Run the agent with custom message
message = "Create a feedback saying 'Profile image upload doesn't work' with an appropriate type and status'. Create 4 other feedbacks talking about the perfomance of the app with random types and status. Then delete feedbacks including the word \"Profile image\"."
result = reviewer_agent.invoke(
    {"messages": [{"role": "user", "content": message}]}
)

# Access the last message
last_message = result["messages"][-1]
print("\n\n", last_message.content, "\n\n")


