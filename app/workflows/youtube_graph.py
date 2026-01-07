from langgraph.graph import StateGraph
from app.workflows.states import YouTubeAutomationState
from app.agents import (
    niche_agent,
    strategy_agent,
    script_agent,
    video_agent,
    publish_agent,
    analytics_agent,
)

graph = StateGraph(YouTubeAutomationState)

graph.add_node("niche", niche_agent.run)
graph.add_node("strategy", strategy_agent.run)
graph.add_node("script", script_agent.run)
graph.add_node("video", video_agent.run)
graph.add_node("publish", publish_agent.run)
graph.add_node("analytics", analytics_agent.run)

graph.set_entry_point("niche")

graph.add_edge("niche", "strategy")
graph.add_edge("strategy", "script")
graph.add_edge("script", "video")
graph.add_edge("video", "publish")
graph.add_edge("publish", "analytics")

youtube_workflow = graph.compile()
