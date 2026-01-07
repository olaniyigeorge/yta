import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from config import AppConfig


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

reviewer_agent = create_agent(
    model=model,
    tools=[],
    system_prompt="You are a helpful review assistant who manages user feedbacks. Use the provided tools to create, update, delete, and get feedbacks based on user requests. Ensure to confirm actions taken.",
)


class NicheDiscoveryAgent:
    """Agent to discover profitable YouTube niches"""

    def __init__(self):
        self.agent = reviewer_agent

    def run(self, state: dict) -> dict:
        # TODO: extract prompts to prompt.yaml to be easily modifiable
        prompt = f"""You are an expert YouTube niche researcher. 
        Given the following criteria, suggest a profitable YouTube niche:

        Criteria:
        - High viewer interest
        - Low competition
        - Good monetization potential

        Provide your response in JSON format with the following fields:
        {{
            "niche": "string",
            "reasoning": "string"
        }}

        Current State:
        {json.dumps(state, indent=2)}
        """

        response = self.agent.run(prompt)

        try:
            niche_data = json.loads(response)
            state["niche"] = niche_data.get("niche", "General")
            state["niche_reasoning"] = niche_data.get("reasoning", "")
        except json.JSONDecodeError:
            state["niche"] = "General"
            state["niche_reasoning"] = "Failed to parse agent response."

        return state
