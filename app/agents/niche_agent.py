import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from config import AppConfig
from app.workflows.states import YouTubeAutomationState, NicheCandidate, NicheAgentState


class NicheDiscoveryAgent:
    """Agent to discover profitable YouTube niches"""

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=AppConfig.GEMINI_API_KEY,
            temperature=1.0,
            max_tokens=500,
            timeout=None,
            max_retries=2,
        )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert YouTube niche researcher. 
                You help find profitable YouTube niches based on given criteria.
                Always respond with valid JSON only, no markdown formatting.""",
                ),
                (
                    "human",
                    """Given the following criteria, suggest a profitable YouTube niche:

                Criteria:
                - High viewer interest
                - Low competition
                - Good monetization potential

                Provide your response in JSON format with the following fields:
                {{
                    "niche": "string",
                    "reasoning": "string"
                }}""",
                ),
            ]
        )

        self.chain = self.prompt_template | self.model

    def run(self, state: YouTubeAutomationState) -> YouTubeAutomationState:
        """
        Return a new state object with updates.
        """
        response = self.chain.invoke({})
        response_text = response.content

        # Parse response
        response_text = response_text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        try:
            niche_data = json.loads(response_text)
            niche_name = niche_data.get("niche", "General")
            reasoning = niche_data.get("reasoning", "")

            # Create a NicheCandidate
            candidate = NicheCandidate(
                name=niche_name,
                search_demand=0.7,
                trend_velocity=0.5,
                competition_score=0.3,
                estimated_rpm=5.0,
                monetization_score=0.8,
                final_score=0.75,
                metadata={"reasoning": reasoning},
            )

            # Create updated niche state
            updated_niche_state = NicheAgentState(
                llm_candidates=[candidate], selected_niche=candidate
            )

            # Create a copy of the state with updates
            return state.model_copy(
                update={
                    "niche_state": updated_niche_state,
                    "current_stage": "niche_discovery_complete",
                }
            )

        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Response was: {response_text}")

            # Return state with error
            error_log = state.error_log + [f"Failed to parse niche response: {str(e)}"]
            return state.model_copy(
                update={
                    "current_stage": "niche_discovery_failed",
                    "error_log": error_log,
                }
            )
