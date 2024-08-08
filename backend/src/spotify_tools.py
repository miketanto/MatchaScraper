from langchain_core.tools import tool
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Dict, Optional, List
import os

def get_spotify_client():
    """Initialize and return a Spotify client with automatic authentication."""
    cache_path = ".spotify_cache"
    
    auth_manager = SpotifyOAuth(
        scope="playlist-modify-public playlist-modify-private",
        cache_path=cache_path,
        open_browser=False
    )

    # # Check if we have a cached token
    # if os.path.exists(cache_path):
    #     token_info = auth_manager.get_cached_token()
    #     if token_info and not auth_manager.is_token_expired(token_info):
    #         return spotipy.Spotify(auth_manager=auth_manager)

    # If we don't have a valid cached token, start the auth flow
    auth_url = auth_manager.get_authorize_url()
    print(f"Please navigate to this URL in your browser: {auth_url}")
    print("After authorizing, you'll be redirected to a localhost URL. Copy that entire URL and paste it here:")
    response = input("Enter the URL you were redirected to: ")
    
    code = auth_manager.parse_response_code(response)
    token_info = auth_manager.get_access_token(code)
    
    return  spotipy.Spotify(auth_manager=auth_manager)


@tool
def search_and_add_songs_to_spotify_playlist(auth_info:str, playlist_id: str, song_names: List[str], song_artists:List[str]) -> Dict:
    """Search for songs by name and add the top result for each to a specified Spotify playlist.

    Args:
        auth_info: Authenticated access token for Spotify client api calls.
        playlist_id (str): The ID of the playlist to add songs to.
        song_names (List[str]): A list of song names with artist appended to the end to search for and add.
        song_artists (List[str]): A list of artists that correspond to each song in its appropriate index

    Returns:
        A dictionary containing the result of the operation.
    """
    added_tracks = []
    not_found_tracks = []
    try:
        sp = spotipy.Spotify(auth=auth_info)
    except Exception as e:
            print(f"Error processing Spotify Client")
    for i in range(len(song_names)):
        try:
            query = song_names[i] + " " + song_artists[i]
            # Search for the track
            results = sp.search(q=query, type='track', limit=1)
            #print(results)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_uri = track['uri']
                
                # Add the track to the playlist
                sp.playlist_add_items(playlist_id, [track_uri])
                
                added_tracks.append({
                    "name": track['name'],
                    "artist": track['artists'][0]['name'],
                    "uri": track_uri
                })
            else:
                not_found_tracks.append(song_names[i])
        
        except Exception as e:
            not_found_tracks.append(song_names[i])
            print(f"Error processing '{song_names[i]}': {str(e)}")

    return {
        "success": True,
        "message": f"Added {len(added_tracks)} out of {len(song_names)} requested tracks to playlist {playlist_id}",
        "added_tracks": added_tracks,
        "not_found_tracks": not_found_tracks
    }

@tool
def remove_songs_from_spotify_playlist(auth_info:str, playlist_id: str, track_uris: List[str]) -> Dict:
    """Remove one or more songs from a specified Spotify playlist.

    Args:
        sp (Dict): An authenticated Spotify client dictionary.
        playlist_id (str): The ID of the playlist to remove songs from.
        track_uris (List[str]): A list of Spotify track URIs to remove from the playlist.

    Returns:
        A dictionary containing the result of the operation.
    """
    try:
        sp = spotipy.Spotify(auth=auth_info)
        sp.playlist_remove_all_occurrences_of_items(playlist_id, track_uris)
        return {
            "success": True,
            "message": f"Successfully removed {len(track_uris)} track(s) from playlist {playlist_id}",
            "tracks_removed": len(track_uris)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to remove tracks from playlist: {str(e)}",
            "tracks_removed": 0
        }

@tool
def create_empty_spotify_playlist(auth_info:str, name: str, public: Optional[bool] = True, description: Optional[str] = "") -> Dict:
    """Create an empty Spotify playlist for the authenticated user.

    Args:
        sp (Dict): An authenticated Spotify client dictionary.
        name (str): The name of the playlist to create.
        public (bool, optional): Whether the playlist should be public. Defaults to True.
        description (str, optional): A description for the playlist. Defaults to an empty string.

    Returns:
        A dictionary containing the details of the created playlist, including its name and ID.
    """
    try:
        sp = spotipy.Spotify(auth=auth_info)
        user_id = sp.me()['id']
        playlist = sp.user_playlist_create(user_id, name, public=public, description=description)

        return {
            "success": True,
            "name": playlist['name'],
            "id": playlist['id'],
            "public": playlist['public'],
            "description": playlist['description'],
            "url": playlist['external_urls']['spotify']
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create playlist: {str(e)}"
        }