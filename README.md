# YouTube Researcher Team with LangGraph

An AI-powered research assistant that leverages YouTube content to answer user queries using a multi-agent system built with LangChain and LangGraph.

### Agent Schema:
![Agent Schema](schema_diagram/LanGraph.png)

## Features
- Intelligent YouTube search planning
- Automated video selection
- Transcript analysis
- Comprehensive summary generation
- Support for multiple language models (OpenAI, Gemini, Claude, Groq, and local models)

## Prerequisites
- Python 3.11+
- Anaconda or Miniconda

## Installation

### Environment Setup
1. **Install Anaconda:**  
   Download Anaconda from [https://www.anaconda.com/](https://www.anaconda.com/).

2. **Create a Virtual Environment:**
   ```bash
   conda create -n youtube_researcher_env python=3.11 pip
3. **Activate the Virtual Environment:**
   ```bash
   conda activate youtube_researcher_env
   ```

### Clone and Navigate to the Repository
1. **Clone the Repo:**
   ```bash
   git clone https://github.com/paresh795/youtube_researcher_team.git
   ```

2. **Navigate to the Repo:**
   ```bash
   cd youtube_researcher_team
   ```

3. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

### Configure API Keys
1. **Open the `config.yaml`:**
   ```bash
   nano config/config.yaml
   ```

2. **Enter API Keys:**
RAPIDAPI_KEY: "your_rapidapi_key_here"
OPENAI_API_KEY: "your_openai_api_key_here"
GEMINI_API_KEY: "your_gemini_api_key_here"
CLAUD_API_KEY: "your_claude_api_key_here"
GROQ_API_KEY: "your_groq_api_key_here"

<!-- Get API keys from:

RapidAPI 
OpenAI
Google AI (Gemini)
Anthropic (Claude)
Groq -->


## If you want to work with Ollama

### Setup Ollama Server
1. **Download Ollama:**
   Download [https://ollama.com/download](https://ollama.com/download)

2. **Download an Ollama Model:**
   ```bash
   curl http://localhost:11434/api/pull -d "{\"name\": \"llama3\"}"
   ```



**Run the Application:**
**Modify the app.py file to use the Ollama model:**

server = 'ollama'
model = 'llama3:instruct'
model_endpoint = "http://localhost:11434/api/generate"

<!-- Then run the application as usual. -->

For more details on Ollama API, refer to the Ollama API documentation.
Ollama [API documentation](https://github.com/ollama/ollama/blob/main/docs/api.md#list-local-models)





<!-- Project Structure

agent_graph/: Graph structure for the multi-agent system
agents1/: Agent definitions
app/: Main application code
config/: Configuration files
models/: Model configurations for various LLMs
prompts1/: Prompt templates
states/: State management
tools1/: Utility functions for API interactions
utils/: General utility functions -->



**Contributing**
Contributions are welcome! Please feel free to submit a Pull Request.

**License**
This project is licensed under the MIT License - see the LICENSE file for details.