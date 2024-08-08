from graph import graph
from utils import _print_event
import uuid


# sp= get_spotify_client()
# auth_info = {'access_token': sp.auth_manager.get_access_token(as_dict=False)}
def convert_playlist(access_token, youtube_url):
    #set_env_var()
    tutorial_questions = [
        "Hi there can you make me a playlist with songs from the youtube video with id {youtube_url}. If the youtube url is invalid return that you can't do it. If the process is successful return the playlist URL".format(youtube_url = youtube_url)
    ]
    thread_id = str(uuid.uuid4())
    auth_info = {'access_token': access_token}
    config = {
        "configurable": {
            # The passenger_id is used in our flight tools to
            # fetch the user's flight information
            "spotify_client": auth_info,
            "thread_id": thread_id,
        }
    }
    #_printed = set()
    return_event = None
    for question in tutorial_questions:
        events = graph.stream(
            {"messages": ("user", question)}, config, stream_mode="values"
        )
        for event in events:
            return_message = event["messages"][-1]
    return return_message
