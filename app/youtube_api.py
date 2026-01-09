




async def get_trending_videos():
    """
    Fetch trending videos from YouTube.
    """
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        chart="mostPopular",
        regionCode="US",
        maxResults=10,
    )
    response = request.execute()
    return response.get("items", [])