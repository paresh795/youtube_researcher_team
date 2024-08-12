#agents.py:

import json
import yaml
import os
from termcolor import colored
from models.openai_models import get_open_ai, get_open_ai_json
from models.ollama_models import OllamaModel, OllamaJSONModel
from models.vllm_models import VllmJSONModel, VllmModel
from models.groq_models import GroqModel, GroqJSONModel
from models.claude_models import ClaudModel, ClaudJSONModel
from models.gemini_models import GeminiModel, GeminiJSONModel

from prompts1.prompts import (
    planner_prompt_template,
    selector_prompt_template,
    transcript_analysis_prompt_template,
    summary_aggregator_prompt_template,
)
from utils.helper_functions import get_current_utc_datetime, check_for_content
from states.state import AgentGraphState

class Agent:
    def __init__(self, state: AgentGraphState, model=None, server=None, temperature=0, model_endpoint=None, stop=None, guided_json=None):
        self.state = state
        self.model = model
        self.server = server
        self.temperature = temperature
        self.model_endpoint = model_endpoint
        self.stop = stop
        self.guided_json = guided_json

    def get_llm(self, json_model=True):
        if self.server == 'openai':
            return get_open_ai_json(model=self.model, temperature=self.temperature) if json_model else get_open_ai(model=self.model, temperature=self.temperature)
        if self.server == 'ollama':
            return OllamaJSONModel(model=self.model, temperature=self.temperature) if json_model else OllamaModel(model=self.model, temperature=self.temperature)
        if self.server == 'vllm':
            return VllmJSONModel(
                model=self.model,  
                guided_json=self.guided_json,
                stop=self.stop,
                model_endpoint=self.model_endpoint,
                temperature=self.temperature
            ) if json_model else VllmModel(
                model=self.model,
                model_endpoint=self.model_endpoint,
                stop=self.stop,
                temperature=self.temperature
            )
        if self.server == 'groq':
            return GroqJSONModel(
                model=self.model,
                temperature=self.temperature
            ) if json_model else GroqModel(
                model=self.model,
                temperature=self.temperature
            )
        if self.server == 'claude':
            return ClaudJSONModel(
                model=self.model,
                temperature=self.temperature
            ) if json_model else ClaudModel(
                model=self.model,
                temperature=self.temperature
            )
        if self.server == 'gemini':
            return GeminiJSONModel(
                model=self.model,
                temperature=self.temperature
            ) if json_model else GeminiModel(
                model=self.model,
                temperature=self.temperature
            )      

    def update_state(self, key, value):
        self.state = {**self.state, key: value}

class PlannerAgent(Agent):
    def invoke(self, research_question, prompt=planner_prompt_template, feedback=None):
        feedback_value = feedback() if callable(feedback) else feedback
        feedback_value = check_for_content(feedback_value)

        planner_prompt = prompt.format(
            feedback=feedback_value,
            datetime=get_current_utc_datetime()
        )

        messages = [
            {"role": "system", "content": planner_prompt},
            {"role": "user", "content": f"research question: {research_question}"}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        self.update_state("planner_response", response)
        print(colored(f"Planner 👩🏿‍💻: {response}", 'cyan'))
        return self.state


class SummaryAggregatorAgent(Agent):
    def invoke(self, research_question, prompt=summary_aggregator_prompt_template, transcript_analysis=None):
        transcript_analysis_value = transcript_analysis() if callable(transcript_analysis) else transcript_analysis
        transcript_analysis_value = check_for_content(transcript_analysis_value)

        # Extract video IDs and titles from the transcript analysis
        video_info = self.extract_video_info(transcript_analysis_value)

        summary_aggregator_prompt = prompt.format(
            research_question=research_question,
            transcript_analysis=transcript_analysis_value,
            datetime=get_current_utc_datetime()
        )

        messages = [
            {"role": "system", "content": summary_aggregator_prompt},
            {"role": "user", "content": f"Provide a final summary for the research question: {research_question}"}
        ]

        llm = self.get_llm(json_model=False)
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        # Replace video IDs with full YouTube URLs
        response = self.replace_video_ids_with_urls(response, video_info)

        print(colored("\n" + "="*50, 'cyan'))
        print(colored("Summary Aggregator Agent Output:", 'cyan', attrs=['bold']))
        print(colored("="*50, 'cyan'))
        print(colored(f"Final Summary:\n{response}", 'cyan'))
        print(colored("="*50 + "\n", 'cyan'))

        self.update_state("summary_aggregator_response", response)
        return self.state

    def extract_video_info(self, transcript_analysis):
        video_info = {}
        lines = transcript_analysis.split('\n')
        for line in lines:
            if line.startswith("Video ID:"):
                parts = line.split(':')
                if len(parts) > 1:
                    video_id = parts[1].strip()
                    title = lines[lines.index(line) - 1].strip()  # Assume title is on the previous line
                    video_info[video_id] = title
        return video_info

    def replace_video_ids_with_urls(self, response, video_info):
        for video_id, title in video_info.items():
            old_text = f"Video ID: {video_id}"
            new_text = f"[{title}](https://www.youtube.com/watch?v={video_id})"
            response = response.replace(old_text, new_text)
        return response



class SelectorAgent(Agent):
    def invoke(self, research_question, prompt=selector_prompt_template, feedback=None, previous_selections=None, ytsearch=None):
        feedback_value = feedback() if callable(feedback) else feedback
        previous_selections_value = previous_selections() if callable(previous_selections) else previous_selections
        ytsearch_value = ytsearch() if callable(ytsearch) else ytsearch

        feedback_value = check_for_content(feedback_value)
        previous_selections_value = check_for_content(previous_selections_value)
        ytsearch_value = check_for_content(ytsearch_value)

        selector_prompt = prompt.format(
            feedback=feedback_value,
            previous_selections=previous_selections_value,
            youtube_search_response=ytsearch_value,
            datetime=get_current_utc_datetime()
        )

        messages = [
            {"role": "system", "content": selector_prompt},
            {"role": "user", "content": f"research question: {research_question}"}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        print(colored(f"selector 🧑🏼‍💻: {response}", 'green'))
        self.update_state("selector_response", response)
        return self.state
    
    
    
class TranscriptAnalysisAgent(Agent):
    def invoke(self, research_question, prompt=transcript_analysis_prompt_template, transcriptions=None):
        transcriptions_value = transcriptions() if callable(transcriptions) else transcriptions
        transcriptions_value = check_for_content(transcriptions_value)

        transcript_analysis_prompt = prompt.format(
            transcriptions=transcriptions_value,
            datetime=get_current_utc_datetime()
        )

        messages = [
            {"role": "system", "content": transcript_analysis_prompt},
            {"role": "user", "content": f"research question: {research_question}"}
        ]

        llm = self.get_llm(json_model=False)  # We're not expecting JSON output for this agent
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        print(colored(f"Transcript Analysis 📊: {response}", 'magenta'))
        self.update_state("transcript_analysis_response", response)
        return self.state

class SummaryAggregatorAgent(Agent):
    def invoke(self, research_question, prompt=summary_aggregator_prompt_template, transcript_analysis=None):
        transcript_analysis_value = transcript_analysis() if callable(transcript_analysis) else transcript_analysis
        transcript_analysis_value = check_for_content(transcript_analysis_value)

        summary_aggregator_prompt = prompt.format(
            research_question=research_question,
            transcript_analysis=transcript_analysis_value,
            datetime=get_current_utc_datetime()
        )

        messages = [
            {"role": "system", "content": summary_aggregator_prompt},
            {"role": "user", "content": f"Provide a final summary for the research question: {research_question}"}
        ]

        llm = self.get_llm(json_model=False)
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        # Remove duplicate sections and tables
        cleaned_response = self.clean_response(response)

        print(colored("\n" + "="*50, 'cyan'))
        print(colored("Summary Aggregator Agent Output:", 'cyan', attrs=['bold']))
        print(colored("="*50, 'cyan'))
        print(colored(f"Final Summary:\n{cleaned_response}", 'cyan'))
        print(colored("="*50 + "\n", 'cyan'))

        self.update_state("summary_aggregator_response", cleaned_response)
        return self.state

    def clean_response(self, response):
        sections = response.split('\n\n')
        unique_sections = []
        seen = set()
        for section in sections:
            if section not in seen:
                unique_sections.append(section)
                seen.add(section)
        return '\n\n'.join(unique_sections)

# Define other agents as needed


class EndNodeAgent(Agent):
    def invoke(self):
        self.update_state("end_chain", "end_chain")
        return self.state