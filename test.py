from app.workflows.youtube_graph import youtube_workflow


def main():
    """Run the YouTube Automation Workflow"""
    print("\n🤖 YouTube Automation Workflow Started!\n")
    youtube_workflow.run()
    print("\n✅ YouTube Automation Workflow Completed.")


if __name__ == "__main__":
    main()
