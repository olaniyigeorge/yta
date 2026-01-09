from langgraph.graph import StateGraph
from app.workflows.states import YouTubeAutomationState
from app.agents import (
    niche_agent,
    # strategy_agent,
)

graph = StateGraph(YouTubeAutomationState)

graph.add_node("niche", niche_agent.NicheDiscoveryAgent().run)
# graph.add_node("strategy", strategy_agent.run)

graph.set_entry_point("niche")

# graph.add_edge("niche", "strategy")
# graph.add_edge("strategy", "script")
# graph.add_edge("script", "video")
# graph.add_edge("video", "publish")
# graph.add_edge("publish", "analytics")

youtube_workflow = graph.compile()
