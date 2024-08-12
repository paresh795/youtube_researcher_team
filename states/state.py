from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# Define the state object for the agent graph
class AgentGraphState(TypedDict):
    research_question: str
    planner_response: Annotated[list, add_messages]
    selector_response: Annotated[list, add_messages]
    youtube_search_response: Annotated[list, add_messages]  # Add this line
    youtube_transcription_response: Annotated[list, add_messages]# Add this line
    transcript_analysis_response: Annotated[list, add_messages]
    summary_aggregator_response: Annotated[list, add_messages]
    # Add other responses as needed

# Define the nodes in the agent graph
def get_agent_graph_state(state: AgentGraphState, state_key: str):
    if state_key == "planner_all":
        return state["planner_response"]
    elif state_key == "planner_latest":
        if state["planner_response"]:
            return state["planner_response"][-1]
        else:
            return state["planner_response"]
    
    elif state_key == "selector_all":
        return state["selector_response"]
    elif state_key == "selector_latest":
        if state["selector_response"]:
            return state["selector_response"][-1]
        else:
            return state["selector_response"]

    elif state_key == "transcript_analysis_all":
        return state["transcript_analysis_response"]
    elif state_key == "transcript_analysis_latest":
        if state["transcript_analysis_response"]:
            return state["transcript_analysis_response"][-1]
        else:
            return state["transcript_analysis_response"]

    elif state_key == "summary_aggregator_all":
        return state["summary_aggregator_response"]
    elif state_key == "summary_aggregator_latest":
        if state["summary_aggregator_response"]:
            return state["summary_aggregator_response"][-1]
        else:
            return state["summary_aggregator_response"]

    elif state_key == "youtube_search_all":
        return state["youtube_search_response"]
    elif state_key == "youtube_search_latest":
        if state["youtube_search_response"]:
            return state["youtube_search_response"][-1]
        else:
            return state["youtube_search_response"]

    elif state_key == "youtube_transcription_all":
        return state["youtube_transcription_response"]
    elif state_key == "youtube_transcription_latest":
        if state["youtube_transcription_response"]:
            return state["youtube_transcription_response"][-1]
        else:
            return state["youtube_transcription_response"]

    else:
        return None
    
state = {
    "research_question": "",
    "planner_response": [],
    "selector_response": [],
    "youtube_search_response": [],  # Initialize this key
    "youtube_transcription_response": [],  # Initialize this key
    "transcript_analysis_response": [],
    "summary_aggregator_response": [],
    # Initialize other responses as needed
}
