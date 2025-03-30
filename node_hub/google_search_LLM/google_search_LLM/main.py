from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from openai import OpenAI
import os
import yaml
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import time
import json

# 获取当前脚本所在目录  
script_dir = os.path.dirname(os.path.abspath(__file__))  
config_path = os.path.join(script_dir, 'config.yaml') 

# 读取YAML配置文件  
with open(config_path, 'r',encoding='utf-8') as file:  
    config = yaml.safe_load(file)

# 从配置中加载API密钥和基础URL  
api_key = config['api_key']  
base_url = config['base_url']
model = config['model']

messages = [
        {"role": "system", "content": """你是一个关键词生成助手，
你为用户生成的关键词要放到google上搜索，
请考虑用户需求和平台特性生成搜索关键词。
请根据用户的输入判断用户是否需要搜索，
如用户需要搜索则返回以","为分隔的搜索词，
如用户不需要搜索则返回NNNN。"""}
        ]




class SerperGoogleCrawler:
    def __init__(self, api_key='59e2efaff1580192159e38ed97a0e08acc13b37b'):
        self.base_url = "https://google.serper.dev/search"
        self.api_key = api_key
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

    def search_single(self, keyword, country_code='cn', language='zh-cn', num_results=20, page=1, search_type='search'):
        """
        使用Serper API进行单次Google搜索
        
        参数:
            keyword (str): 搜索关键词
            country_code (str): 国家代码，默认'cn'
            language (str): 语言代码，默认'zh-cn'
            num_results (int): 每页结果数量，最大100
            page (int): 页码
            search_type (str): 搜索类型，可选值: 'search'(普通搜索), 'images', 'news', 'places'
            
        返回:
            dict: 单次搜索结果
        """
        url = f"https://google.serper.dev/{search_type}"

        payload = json.dumps({
            "q": keyword,
            "gl": country_code,
            "hl": language,
            "num": num_results,
            "page": page
        })

        try:
            print(f"正在使用Serper API搜索: {keyword} (页码: {page})...")
            response = requests.request("POST", url, headers=self.headers, data=payload)

            if response.status_code != 200:
                print(f"API请求失败，状态码: {response.status_code}")
                return {"error": f"API请求失败，状态码: {response.status_code}"}

            # 解析返回的JSON数据
            results = response.json()

            return results

        except Exception as e:
            print(f"搜索过程中出错: {str(e)}")
            return {"error": str(e)}

    def search(self, keywords, country_code='cn', language='zh-cn', num_results=20, page=1, search_type='search'):
        """
        使用Serper API进行Google搜索，支持多个关键词并行搜索
        
        参数:
            keywords (list): 搜索关键词列表
            country_code (str): 国家代码，默认'cn'
            language (str): 语言代码，默认'zh-cn'
            num_results (int): 每页结果数量，最大100
            page (int): 页码
            search_type (str): 搜索类型，可选值: 'search'(普通搜索), 'images', 'news', 'places'
            
        返回:
            dict: 合并后的搜索结果
        """
        results = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.search_single, keyword, country_code, language, num_results, page, search_type): keyword for keyword in keywords}
            for future in futures:
                keyword = futures[future]
                result = future.result()
                results[keyword] = result
        return results

def generate_keywords_or_identify_need(query):  
    try:  
        messages_this_turn = messages
        
        messages_this_turn.append({
                "role": 'user',
                "content": query
            })
        client = OpenAI(api_key=api_key, base_url=base_url)
        response_agent = client.chat.completions.create(
            model=model,
            messages=messages_this_turn,
            max_tokens=88,
            temperature=0.2,
            stream=False
            )
        
        #print()
        generated_text=response_agent.choices[0].message.content

        # 假设返回格式是以逗号分隔的关键词  
        keywords = [kw.strip() for kw in generated_text.split(",") if kw.strip()]  

        return keywords  # 返回生成的关键词列表  
    except Exception as e:  
        print(f"Error generating keywords: {str(e)}")  
        return []  # 发生错误时返回空列表  

# 函数将搜索结果传递到大模型进行筛选
def filter_results_with_model(results,query):  
    try:  
        # 下面是使用 OpenAI 进行筛选的示例  
        messages_shai = [
        {"role": "system", "content": """你是一个筛选助手，
         负责根据用户的问题筛选出搜索结果中有用的部分，
         输出时请只输出你筛选出来的部分，
         输出格式保持搜索结果原格式"""},
        {"role": "user", "content": f"{query}"},
        {"role": "system", "content": f"""搜索结果：\n{results}\n"""}
        ] 

        client = OpenAI(api_key=api_key, base_url=base_url)

        response = client.chat.completions.create(
            model=model,
            messages=messages_shai
            ) 

        filtered_content = response.choices[0].message.content
        return filtered_content  # 返回筛选后的内容
    except Exception as e:  
        print(f"筛选时出错: {str(e)}")  
        return "筛选失败"


@run_agent
def run(agent: MofaAgent):
    user_query = agent.receive_parameter('query')
    #print("laile")

    if user_query is None:
        return
    
    #大模型根据问题生成关键词，如不需要搜索返回特定标识
    keywords=generate_keywords_or_identify_need(user_query)
    if not keywords:
        agent.send_output(agent_output_name='google_search_LLM_result', agent_result="出现错误，已暂停")
        return
    #判断继续搜索
    if "NNNN" in keywords:
        #不需要搜索
        agent.send_output(agent_output_name='google_search_LLM_result', agent_result="空闲中")
        return
    
    agent.send_output(agent_output_name='google_search_LLM_result', agent_result="正在搜索ing")

    #启动搜索
    # t=threading.Thread(target=search_thread,args=(keywords,user_query))
    # t.start()
    #根据关键词列表查询关键词并用大模型筛选
    crawler = SerperGoogleCrawler()
    results = crawler.search(keywords, country_code='cn', language='zh-cn', num_results=20, page=1, search_type='search')
    #print(search_results)
    print("找到了，让我看看")
    # 将结果转换为JSON格式
    results_json = json.dumps(results, ensure_ascii=False, indent=4)
    #filltered_content=filter_results_with_model(search_results,user_query)
    #print(filltered_content)
    #if filltered_content is None or filltered_content==[]:
    #   #result_queue.put("未搜索到结果")
    #    agent.send_output(agent_output_name='github_search_LLM_result', agent_result="未搜索到结果")

    #result_queue.put(filltered_content)
    agent.send_output(agent_output_name='google_search_LLM_result', agent_result=results_json)
    
        





def main():
    agent = MofaAgent(agent_name='google_search_LLM')
    run(agent=agent)

if __name__ == "__main__":
    main() 

