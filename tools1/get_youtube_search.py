import http.client
import json
import urllib.parse
import os
import yaml
from termcolor import colored
from states.state import AgentGraphState
from langchain_core.messages import HumanMessage

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_youtube_search(state: AgentGraphState, plan):
    config = load_config()
    rapidapi_key = config['RAPIDAPI_KEY']

    plan_data = json.loads(plan().content)
    search_term = plan_data.get("search_term")

    conn = http.client.HTTPSConnection("yt-api.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': "yt-api.p.rapidapi.com"
    }

    encoded_search_term = urllib.parse.quote(search_term)
    search_path = f"/search?query={encoded_search_term}"
    conn.request("GET", search_path, headers=headers)

    res = conn.getresponse()
    data = res.read()

    try:
        response_json = json.loads(data.decode("utf-8"))
        videos = []
        for item in response_json.get('data', []):
            if item.get('type') == 'video':
                videos.append({
                    'videoId': item.get('videoId'),
                    'title': item.get('title'),
                    'channelTitle': item.get('channelTitle'),
                    'viewCount': item.get('viewCount'),
                    'publishedText': item.get('publishedText')
                })
        response_content = {"search_term": search_term, "videos": videos}
        
        if "youtube_search_response" not in state:
            state["youtube_search_response"] = []
        state["youtube_search_response"].append(HumanMessage(content=str(response_content)))
        
        print(colored(f"YouTube Search Tool 🔍: {response_content}", 'blue'))

        return {"youtube_search_response": state["youtube_search_response"]}
    except json.JSONDecodeError as e:
        error_message = f"Error decoding JSON response: {str(e)}"
        if "youtube_search_response" not in state:
            state["youtube_search_response"] = []
        state["youtube_search_response"].append(HumanMessage(content=str({"error": error_message})))
        
        print(colored(f"YouTube Search Tool 🔍: {error_message}", 'red'))

        return {"youtube_search_response": state["youtube_search_response"]}