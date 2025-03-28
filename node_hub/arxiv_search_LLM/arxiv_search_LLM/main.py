from mofa.agent_build.base.base_agent import MofaAgent, run_agent
@run_agent
def run(agent: MofaAgent):
    user_query = agent.receive_parameter('query')
    if user_query is not None:
        print(f"user_query: {user_query}")
        agent.send_output(agent_output_name='arxiv_search_LLM_result', agent_result=user_query)

def main():
    agent = MofaAgent(agent_name='arxiv_search_LLM')
    run(agent=agent)

if __name__ == "__main__":
    main()
