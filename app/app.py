#app.py
from agent_graph.graph import create_graph, compile_workflow
from models.ollama_models import OllamaModel, OllamaJSONModel
from termcolor import colored
from states.state import state as initial_state

# server = 'ollama'
# model = 'llama3:instruct'
# model_endpoint = None

server = 'openai'
model = 'gpt-4o'
model_endpoint = None

# server = 'vllm'
# model = 'meta-llama/Meta-Llama-3-70B-Instruct' # full HF path
# model_endpoint = 'https://kcpqoqtjz0ufjw-8000.proxy.runpod.net/' 
# #model_endpoint = runpod_endpoint + 'v1/chat/completions'
# stop = "<|end_of_text|>"

iterations = 40

print ("Creating graph and compiling workflow...")
graph = create_graph(server=server, model=model, model_endpoint=model_endpoint)
workflow = compile_workflow(graph)
print ("Graph and workflow created.")

if __name__ == "__main__":
    verbose = False

    while True:
        query = input("Please enter your research question: ")
        if query.lower() == "exit":
            break

        # Reset the state for each new query
        current_state = initial_state.copy()
        current_state["research_question"] = query

        dict_inputs = {"research_question": query}
        limit = {"recursion_limit": iterations}

        # Execute the workflow once for each query
        for event in workflow.stream(dict_inputs, limit):
            if verbose:
                print("\nState Dictionary:", event)
            else:
                print("\n")

        # Print the final summary
        if "summary_aggregator_response" in current_state:
            print(colored("\nFinal Summary:", 'cyan', attrs=['bold']))
            print(colored(current_state["summary_aggregator_response"], 'cyan'))
        else:
            print(colored("\nNo summary generated.", 'red'))

        print("\n" + "="*50 + "\n")









# if __name__ == "__main__":

#     verbose = False

#     while True:
#         query = input("Please enter your research question: ")
#         if query.lower() == "exit":
#             break

#         dict_inputs = {"research_question": query}
#         # thread = {"configurable": {"thread_id": "4"}}
#         limit = {"recursion_limit": iterations}

#         # for event in workflow.stream(
#         #     dict_inputs, thread, limit, stream_mode="values"
#         #     ):
#         #     if verbose:
#         #         print("\nState Dictionary:", event)
#         #     else:
#         #         print("\n")

#         for event in workflow.stream(
#             dict_inputs, limit
#             ):
#             if verbose:
#                 print("\nState Dictionary:", event)
#             else:
#                 print("\n")



    