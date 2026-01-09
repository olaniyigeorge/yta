"""
AI Agent for Feedback Management
Demonstrates autonomous feedback handling with LangChain agents
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from config import AppConfig
import json
import uuid


class FeedbackManager:
    """Manages feedback storage and operations"""

    def __init__(self, storage_file="feedbacks.json"):
        self.storage_file = storage_file
        self.feedbacks = self._load_feedbacks()

    def _load_feedbacks(self):
        """Load existing feedbacks from file"""
        try:
            with open(self.storage_file, "r") as f:
                feedback_list = json.load(f)
                return {fb["id"]: fb for fb in feedback_list}
        except FileNotFoundError:
            return {}

    def _save_feedbacks(self):
        """Persist feedbacks to file"""
        with open(self.storage_file, "w") as f:
            json.dump(list(self.feedbacks.values()), f, indent=2)

    def create_feedback(self, body: str, type: str, status: str = "open") -> str:
        """Create new feedback entry"""
        feedback_id = str(uuid.uuid4())
        self.feedbacks[feedback_id] = {
            "id": feedback_id,
            "body": body,
            "type": type,
            "status": status,
        }
        self._save_feedbacks()
        return f"\nFeedback {feedback_id} created successfully."

    def notify_admin(self, feedback_id: str) -> str:
        """Notify admin for urgent feedback"""
        # Placeholder for notification logic (e.g., send email)
        return f"\nAdmin notified for urgent feedback {feedback_id}."

    def escalate_feedback(self, feedback_id: str) -> str:
        """Escalate feedback priority"""
        if feedback_id in self.feedbacks:
            self.feedbacks[feedback_id]["status"] = "urgent"
            self._save_feedbacks()
            return f"\nFeedback {feedback_id} escalated to urgent."
        return f"\nFeedback {feedback_id} not found."

    def update_feedback(
        self, feedback_id: str, body: str = None, type: str = None, status: str = None
    ) -> str:
        """Update existing feedback"""
        if feedback_id not in self.feedbacks:
            return f"\nFeedback {feedback_id} not found."

        if body:
            self.feedbacks[feedback_id]["body"] = body
        if type:
            self.feedbacks[feedback_id]["type"] = type
        if status:
            self.feedbacks[feedback_id]["status"] = status

        self._save_feedbacks()
        return f"\nFeedback {feedback_id} updated successfully."

    def delete_feedback(self, feedback_id: str) -> str:
        """Remove feedback entry"""
        if feedback_id not in self.feedbacks:
            return f"❌ Feedback {feedback_id} not found."

        del self.feedbacks[feedback_id]
        self._save_feedbacks()
        return f"\nFeedback {feedback_id} deleted successfully."

    def get_feedback(self, feedback_id: str = None, body: str = None) -> str:
        """Retrieve feedback by ID or filter by body content"""
        if feedback_id:
            feedback = self.feedbacks.get(feedback_id)
            return feedback if feedback else f"\nFeedback {feedback_id} not found."

        if body:
            filtered = {
                k: v
                for k, v in self.feedbacks.items()
                if body.lower() in v["body"].lower()
            }
            return filtered if filtered else "No matching feedback found."

        return "Please provide either an ID or body to filter."


def create_feedback_agent():
    """Initialize the feedback management agent"""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=AppConfig.GEMINI_API_KEY,
        temperature=0.7,
        max_tokens=500,
        max_retries=2,
    )

    feedback_mgr = FeedbackManager()

    feedback_agent = create_agent(
        model=model,
        tools=[
            feedback_mgr.notify_admin,
            feedback_mgr.update_feedback,
            feedback_mgr.create_feedback,
            feedback_mgr.delete_feedback,
            feedback_mgr.get_feedback,
        ],
        system_prompt="""You are an intelligent feedback management assistant.
        
        Your responsibilities:
        - Create, update, and organize user feedback
        - Prioritize critical issues automatically
        - Flag urgent matters for admin review
        - Maintain organized feedback records
        
        Always confirm actions taken and provide clear status updates.""",
    )

    return feedback_agent


def main():
    """Run the feedback management agent"""
    print("\n🤖 Feedback Management Agent Started!\n")

    agent = create_feedback_agent()

    # Example: Autonomous feedback handling
    message = """
    Create a feedback: 'Profile image upload doesn't work' (type: bug, status: urgent).
    Create 4 more feedbacks about app performance with varying priorities.
    Then delete any feedbacks mentioning 'Profile image'.
    """

    result = agent.invoke({"messages": [{"role": "user", "content": message}]})

    # Display agent response
    last_message = result["messages"][-1]
    print(f"\n🤖 Agent Response:\n{last_message.content}\n")

    print(f"\n✅ Task completed. Total messages: {len(result['messages'])}")


if __name__ == "__main__":
    main()
