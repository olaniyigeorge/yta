from app.workflows.states import YouTubeAutomationState
from app.workflows.youtube_graph import youtube_workflow


def main():
    """Run the YouTube Automation Workflow"""
    print("\n🤖 YouTube Automation Workflow Started!\n")
    yta_graph = youtube_workflow

    # Initialize state
    initial_state = YouTubeAutomationState()

    # Run the graph
    final_state = yta_graph.invoke(initial_state)

    print("\n✅ YouTube Automation Workflow Completed.")
    print(f"workflow final state: \n{final_state}")


if __name__ == "__main__":
    main()
