from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from dora import Node
import pyarrow as pa
import json
from typing import Any, Dict, Union



print("在外")
@run_agent
def run(agent: MofaAgent):
    user_query = agent.receive_parameter('query')
    agent.send_output(agent_output_name='google_search_LLM_result', agent_result=user_query)
    if user_query is not None:
        print(f"user_query: {user_query}")
        agent.send_output(agent_output_name='google_search_LLM_result', agent_result=user_query)


def create_agent_output(agent_name:str, agent_result:Union[str,dict,list], dataflow_status:bool):
    if isinstance(agent_result, dict) or isinstance(agent_result, list):
        agent_result = json.dumps(agent_result, ensure_ascii=False)
    return json.dumps({'step_name':agent_name, 'node_results':agent_result, 'dataflow_status':dataflow_status}, ensure_ascii=False)


def clean_string(input_string:str):
    return input_string.encode('utf-8', 'replace').decode('utf-8')

def main():
    agent = MofaAgent(agent_name='google_search_LLM')
    run(agent=agent)


if __name__ == "__main__":
    main()