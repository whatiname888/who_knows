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
import re

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
你为用户生成的关键词要放到arxiv上搜索，
请考虑用户需求和平台特性生成搜索关键词。
请根据用户的输入判断用户是否需要搜索，
如用户需要搜索则返回以","为分隔的搜索词，
如用户不需要搜索则返回NNNN。"""}
        ]


class ArxivCrawler:
    def __init__(self):
        self.base_url = "https://arxiv.org/search/"
        self.abs_url = "https://arxiv.org/abs/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    
    def search(self, keyword, max_papers=20):
        """
        搜索ArXiv上的论文
        
        参数:
            keyword (str): 搜索关键词
            max_papers (int): 最大获取论文数量
            
        返回:
            list: 包含论文编号、标题、URL和摘要的列表
        """
        results = []
        page = 0
        
        while len(results) < max_papers:
            # 构建搜索URL
            search_url = f"https://arxiv.org/search/?query={keyword}&searchtype=all&source=header&size=25&start={page*25}"
            
            try:
                print(f"正在爬取第 {page+1} 页...")
                response = requests.get(search_url, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"请求失败，状态码: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 获取论文列表
                paper_items = soup.select("li.arxiv-result")
                
                if not paper_items:
                    print("未找到论文或页面结构可能已更改")
                    break
                
                # 解析每篇论文的信息
                for item in paper_items:
                    if len(results) >= max_papers:
                        break
                    
                    try:
                        # 获取论文标题和URL
                        title_element = item.select_one("p.title")
                        title = title_element.text.strip() if title_element else "未知标题"
                        
                        # 获取摘要 - 首先尝试短摘要
                        abstract_element = item.select_one("span.abstract-short")
                        abstract = ""
                        if abstract_element:
                            # 移除 "▽ More" 链接
                            for a in abstract_element.select('a'):
                                a.decompose()
                            
                            # 清理摘要文本
                            abstract = abstract_element.get_text(strip=True)
                            # 去掉开头的省略号，如果存在
                            abstract = abstract.lstrip('…').strip()
                        
                        # 获取论文ID - 尝试多种可能的选择器
                        id_element = (
                            item.select_one("p.list-title a[href^='/abs/']") or 
                            item.select_one("a[href^='/abs/']") or
                            item.select_one("a.list-identifier")
                        )
                        
                        paper_id = ""
                        paper_url = ""
                        
                        if id_element and 'href' in id_element.attrs:
                            href = id_element['href']
                            # 提取论文ID
                            if '/abs/' in href:
                                paper_id = href.split('/abs/')[-1]
                                paper_url = f"https://arxiv.org{href}"
                            else:
                                # 尝试其他格式
                                match = re.search(r'(\d+\.\d+)', href)
                                if match:
                                    paper_id = match.group(1)
                                    paper_url = f"https://arxiv.org/abs/{paper_id}"
                        else:
                            # 尝试从文本中提取ID
                            text_content = item.get_text()
                            match = re.search(r'(\d+\.\d+)', text_content)
                            if match:
                                paper_id = match.group(1)
                                paper_url = f"https://arxiv.org/abs/{paper_id}"
                        
                        if paper_id:
                            results.append({
                                "id": paper_id,
                                "title": title,
                                "url": paper_url,
                                "abstract": abstract
                            })
                        
                    except Exception as e:
                        print(f"解析论文信息时出错: {str(e)}")
                
                print(f"第 {page+1} 页爬取完成，目前获取 {len(results)} 篇论文")
                
                page += 1
                # 添加延时，避免请求频率过高
                time.sleep(0.5)
                
            except Exception as e:
                print(f"爬取过程中出错: {str(e)}")
                break
        
        # 截取指定数量的论文
        return results[:max_papers]
    
    def search_keywords(self, keywords, max_papers_per_keyword=20):
        """新增方法：支持多个关键词搜索，每个关键词最多获取指定数量的论文"""
        all_results = []
        for keyword in keywords:
            print(f"\n开始搜索关键词: {keyword}")
            results = self.search(keyword, max_papers=max_papers_per_keyword)
            all_results.extend(results)
            time.sleep(0.5)  # 关键词之间间隔
        return all_results
    
    def save_results(self, results, filename=None):
        """新增保存方法"""
        if not filename:
            filename = f"arxiv_results.json"
        
        # 获取脚本所在目录路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"结果已保存至: {filepath}")


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
        agent.send_output(agent_output_name='arxiv_search_LLM_result', agent_result="出现错误，已暂停")
        return
    #判断继续搜索
    if "NNNN" in keywords:
        #不需要搜索
        agent.send_output(agent_output_name='arxiv_search_LLM_result', agent_result="空闲中")
        return
    
    agent.send_output(agent_output_name='arxiv_search_LLM_result', agent_result="正在搜索ing")

    #启动搜索
    # t=threading.Thread(target=search_thread,args=(keywords,user_query))
    # t.start()
    #根据关键词列表查询关键词并用大模型筛选
    crawler = ArxivCrawler()
    # 执行搜索（每关键词最多20篇）
    results = crawler.search_keywords(keywords, max_papers_per_keyword=20)
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
    agent.send_output(agent_output_name='arxiv_search_LLM_result', agent_result=results_json)
    
        





def main():
    agent = MofaAgent(agent_name='arxiv_search_LLM')
    run(agent=agent)

if __name__ == "__main__":
    main() 