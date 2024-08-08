from googleapiclient.discovery import build
from typing import Optional, List, Dict
from langchain_core.tools import tool
import os

@tool
def get_search_videos(query:Optional[str])->list[dict]:
    """Search youtube videos based on the given query"""
    youtube = build('youtube', 'v3', developerKey=os.environ.get("YOUTUBE_API_KEY"))
    request = youtube.search().list(
        part="snippet",
        maxResults=25,
        q=query
    )
    response = request.execute()
    return response



@tool
def get_video_by_id(video_ids: List[str]) -> Dict:
    """Get details of YouTube videos by their IDs, including top 3 pinned and top 3 regular comments.

    Args:
        video_ids (List[str]): A list of YouTube video IDs to retrieve details for.

    Returns:
        A dictionary containing the result of the operation.
    """
    youtube = build('youtube', 'v3', developerKey=os.environ.get("YOUTUBE_API_KEY"))
    
    video_details = []
    not_found_videos = []
    
    for video_id in video_ids:
        try:
            # Get video details
            video_request = youtube.videos().list(
                part="snippet,contentDetails",
                id=video_id
            )
            video_response = video_request.execute()
            
            if video_response['items']:
                video = video_response['items'][0]
                video_info = {
                    "title": video['snippet']['title'],
                    "description": video['snippet']['description'],
                    "comments": []
                }
                
                # Get top 3 pinned comments
                comments_request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=3,
                    order="relevance",
                    textFormat="plainText"
                )
                comments_response = comments_request.execute()
                comments = comments_response['items']
                for comment in comments:
                        comment_data = comment["snippet"]["topLevelComment"]["snippet"]
                        video_info["comments"].append({
                            "author": comment_data['authorDisplayName'],
                            "text": comment_data['textDisplay'],
                            "likeCount": comment_data['likeCount'],
                            "publishedAt": comment_data['publishedAt']
                        })
                
                video_details.append(video_info)
            else:
                not_found_videos.append(video_id)
        
        except Exception as e:
            not_found_videos.append(video_id)
            print(f"Error processing video ID '{video_id}': {str(e)}")

    return {
        "success": True,
        "message": f"Retrieved details for {len(video_details)} out of {len(video_ids)} requested videos",
        "video_details": video_details,
        "not_found_videos": not_found_videos
    }

@tool
def get_playlist_song_titles(playlist_id:Optional[str])->list[dict]:
    """Search youtube playlist based on a given playlist_id and return a list of video titles"""
    youtube = build('youtube', 'v3', developerKey=os.environ.get("YOUTUBE_API_KEY"))
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=25,
        playlistId=playlist_id
    )
    response = request.execute()
    videos = response['items']
    title_list = []
    for vid in videos:
         title_list.append(vid["snippet"]["title"])
    return title_list
