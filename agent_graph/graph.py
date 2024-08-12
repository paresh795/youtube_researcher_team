import json
import os
import ast
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from models.openai_models import get_open_ai_json
from langgraph.checkpoint.sqlite import SqliteSaver

from agents1.agents import (
    PlannerAgent,
    SelectorAgent,
    TranscriptAnalysisAgent,
    SummaryAggregatorAgent,
    EndNodeAgent
)

from prompts1.prompts import (
    planner_prompt_template,
    selector_prompt_template,
    planner_guided_json,
    selector_guided_json
)

from tools1.get_youtube_search import get_youtube_search
from tools1.get_youtube_transcription import get_youtube_transcription
from states.state import AgentGraphState, get_agent_graph_state, state

def create_graph(server=None, model=None, stop=None, model_endpoint=None, temperature=0):
    graph = StateGraph(AgentGraphState)
     
    graph.add_node(
        "planner", 
        lambda state: PlannerAgent(
            state=state,
            model=model,
            server=server,
            guided_json=planner_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            prompt=planner_prompt_template
        )
    )

    graph.add_node(
        "selector",
        lambda state: SelectorAgent(
            state=state,
            model=model,
            server=server,
            guided_json=selector_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            previous_selections=lambda: get_agent_graph_state(state=state, state_key="selector_all"),
            ytsearch=lambda: get_agent_graph_state(state=state, state_key="youtube_search_latest"),
            prompt=selector_prompt_template,
        )
    )    
    
    
    graph.add_node(
        "transcript_analysis",
        lambda state: TranscriptAnalysisAgent(
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            transcriptions=lambda: get_agent_graph_state(state=state, state_key="youtube_transcription_all")
        )
    )
 
 
    graph.add_node(
        "summary_aggregator",
        lambda state: SummaryAggregatorAgent(
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            transcript_analysis=lambda: get_agent_graph_state(state=state, state_key="transcript_analysis_latest")
        )
    )
 
    
    graph.add_node(
        "get_youtube_Search_tool",
        lambda state: get_youtube_search(
            state=state,
            plan=lambda: get_agent_graph_state(state=state, state_key="planner_latest")
        )
    )

    graph.add_node(
        "get_youtube_transcription_tool",
        lambda state: {
            "youtube_transcription_response": [
                get_youtube_transcription(state, video_id) for video_id in get_video_ids(state)
            ]
        }
    )
    
    graph.add_node("end", lambda state: EndNodeAgent(state).invoke())
    
    graph.set_entry_point("planner")
    graph.set_finish_point("end")
    graph.add_edge("planner", "get_youtube_Search_tool")
    graph.add_edge("get_youtube_Search_tool", "selector")
    graph.add_edge("selector", "get_youtube_transcription_tool") 
    graph.add_edge("get_youtube_transcription_tool", "transcript_analysis")
    graph.add_edge("transcript_analysis", "summary_aggregator")
    graph.add_edge("summary_aggregator", "end")

    return graph

def get_video_ids(state):
    try:
        selector_content = get_agent_graph_state(state=state, state_key="selector_latest").content
        parsed_content = json.loads(selector_content)
        video_ids = [value for key, value in parsed_content.items() if key.startswith("VideoID")]
        return video_ids
    except Exception as e:
        print(f"Error parsing video IDs: {e}")
        return []

def compile_workflow(graph):
    workflow = graph.compile()
    return workflow