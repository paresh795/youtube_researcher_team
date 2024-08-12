import http.client
import json
import yaml
import os
from termcolor import colored  # Add this import
from langchain_core.messages import HumanMessage

def load_config():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(current_dir)
    # Construct the path to config.yaml in the config folder
    config_path = os.path.join(project_root, 'config', 'config.yaml')
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_youtube_transcription(state, video_id):
    
    config = load_config()
    rapidapi_key = config['RAPIDAPI_KEY']
    
    conn = http.client.HTTPSConnection("youtube-transcriptor.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': "youtube-transcriptor.p.rapidapi.com"
    }

    conn.request("GET", f"/transcript?video_id={video_id}&lang=en", headers=headers)
    res = conn.getresponse()
    data = res.read()

    try:
        response_json = json.loads(data.decode("utf-8"))
        
        # Check if the response is a list (as seen in the example output)
        if isinstance(response_json, list) and len(response_json) > 0:
            first_item = response_json[0]
            if "transcriptionAsText" in first_item:
                transcription_text = first_item["transcriptionAsText"]
            else:
                raise KeyError("transcriptionAsText not found in the response")
        else:
            raise ValueError("Unexpected response format")

        # Update state with the transcription text
        if "youtube_transcription_response" not in state:
            state["youtube_transcription_response"] = []

        state["youtube_transcription_response"].append(
            HumanMessage(content=f"Transcription for video ID {video_id}: {transcription_text}")
        )

        print(f"Successfully extracted transcription for video ID {video_id}")
        print(colored(f"\nTranscription for video ID {video_id}:", 'yellow'))
        print(colored(f"{transcription_text[:500]}...", 'yellow')) 
        return {
            "role": "system",
            "content": transcription_text,
            "video_id": video_id
        }

    except json.JSONDecodeError:
        error_message = f"Error: Unable to decode JSON response for video ID {video_id}"
    except KeyError as e:
        error_message = f"Error: {str(e)} for video ID {video_id}"
    except ValueError as e:
        error_message = f"Error: {str(e)} for video ID {video_id}"
    except Exception as e:
        error_message = f"Unexpected error occurred for video ID {video_id}: {str(e)}"

    print(error_message)
    
    if "youtube_transcription_response" not in state:
        state["youtube_transcription_response"] = []
    
    state["youtube_transcription_response"].append(
        HumanMessage(content=error_message)
    )

    return {
        "role": "system",
        "content": error_message,
        "video_id": video_id
    }