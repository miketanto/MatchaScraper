from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from state import State
from spotify_tools import create_empty_spotify_playlist, search_and_add_songs_to_spotify_playlist
from youtube_tools import get_video_by_id

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            spotify_auth_info = configuration.get("spotify_auth_info", None)
            state = {**state, "spotify_auth_info": spotify_auth_info}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


# Haiku is faster and cheaper, but less accurate
llm = ChatAnthropic(model="claude-3-haiku-20240307")
#llm = ChatAnthropic(model="claude-3-s-20240229", temperature=1)
# You could swap LLMs, though you will likely want to update the prompts when
# doing so!
# from langchain_openai import ChatOpenAI

# llm = ChatOpenAI(model="gpt-4-turbo-preview")

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that knows a lot about music and helps with spotify tasks"
            " Use the provided tools to help make an empty playlist in spotify and search and add the songs  based on a youtube video"
            " Use the auth info provided in the configuration to authorize spotify actions"
            " Name the playlist with inspiration from the title of the Youtube video, take into consideration only the English words. Format it [PLAYLIST] then the title"
            " Give the playlist a description based on what you think and credit the author of the Youtube video and include the youtube link "
            " When searching the songs in the video, check the description first if there seems to be no song titles, check the comments"
            " Before adding songs, create an empty playlist first and add the songs to this empty playlist"
            " If the artist is ambiguous, infer the artist of the songs based on context of the other songs on the playlist."
            " If the video is not found or if there are no songs found from the video, give up and don't search for the songs on the spotify API"
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            "\n\nCurrent Spotify Authorization Token:\n\n{spotify_auth_info}\n",
        ),
        ("placeholder", "{messages}"),
    ]
)

tools = [
   create_empty_spotify_playlist,
   search_and_add_songs_to_spotify_playlist,
   get_video_by_id
]
assistant_runnable = primary_assistant_prompt | llm.bind_tools(tools)