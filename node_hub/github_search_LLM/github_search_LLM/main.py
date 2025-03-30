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
你为用户生成的关键词要放到GitHub上搜索，
请考虑用户需求和平台特性生成搜索关键词。
请根据用户的输入判断用户是否需要搜索，
如用户需要搜索则返回以","为分隔的搜索词，
如用户不需要搜索则返回NNNN。"""}
        ]

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


class GitHubCrawler:
    def __init__(self, max_threads=5):
        # 初始化GitHub搜索的基本URL和请求头
        self.base_url = "https://github.com/search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        # 多线程相关设置，用于并行获取README内容
        self.max_threads = max_threads
        self.repo_queue = queue.Queue()
        self.results_with_readme = []
        self.results_lock = threading.Lock()  # 用于线程安全地更新结果列表
        self.should_stop_threads = False  # 控制线程停止的标志
    
    def search(self, keyword, search_type="repositories", max_pages=1, get_readme=True):
        """
        抓取GitHub搜索结果
        
        参数:
            keyword (str): 搜索关键词
            search_type (str): 搜索类型，可选值: 'repositories', 'code', 'issues', 'users'
            max_pages (int): 最大页数
            get_readme (bool): 是否同时获取README内容，默认为True
        
        返回:
            list: 搜索结果列表
        """
        # 初始化结果列表和页码
        results = []
        page = 1
        
        # 如果需要获取README，启动工作线程
        if get_readme and search_type == "repositories":
            self.should_stop_threads = False
            self.results_with_readme = []
            
            # 启动线程池获取README内容
            readme_executor = ThreadPoolExecutor(max_workers=self.max_threads)
            readme_futures = []
            
            print(f"启动{self.max_threads}个线程处理README内容...")
        
        # 对每个关键词进行搜索
        for kw in keyword:
            # 重置页码
            page = 1

            while page <= max_pages:
                # 构建搜索参数
                params = {
                    "q": kw,
                    "type": search_type,
                    "p": page
                }

                try:
                    print(f"正在爬取关键词 '{kw}' 的第 {page} 页...")
                    # 发送HTTP请求获取搜索页面
                    response = requests.get(self.base_url, params=params, headers=self.headers)

                    if response.status_code != 200:
                        print(f"请求失败，状态码: {response.status_code}")
                        break

                    # 使用BeautifulSoup解析页面内容
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # 根据不同的搜索类型解析结果
                    if search_type == "repositories":
                        page_results = self._parse_repositories(soup)
                    elif search_type == "code":
                        page_results = self._parse_code(soup)
                    elif search_type == "issues":
                        page_results = self._parse_issues(soup)
                    elif search_type == "users":
                        page_results = self._parse_users(soup)
                    else:
                        page_results = []

                    # 检查是否有搜索结果
                    if not page_results:
                        print("没有更多结果或解析失败")
                        # 检查是否需要登录或有验证码
                        if soup.select_one('.blankslate') or soup.select_one('.auth-form'):
                            print("GitHub可能需要登录或出现了验证码，请稍后再试")
                        break

                    # 将当前页的结果添加到总结果列表中
                    results.extend(page_results)
                    print(f"关键词 '{kw}' 的第 {page} 页爬取完成，获取 {len(page_results)} 条结果")

                    # 如果需要获取README，立即提交任务到线程池
                    if get_readme and search_type == "repositories":
                        for repo in page_results:
                            if 'url' in repo and repo['url']:
                                # 提交任务到线程池
                                future = readme_executor.submit(
                                    self._get_repo_readme,
                                    repo.copy()  # 传递仓库对象的副本
                                )
                                readme_futures.append(future)

                    # 判断是否有下一页
                    next_button = soup.select_one("a.next_page") or soup.select_one("a[rel='next']")
                    if not next_button:
                        print("已到达关键词 '{kw}' 的最后一页")
                        break

                    page += 1
                    # 添加延时，避免请求频率过高
                    time.sleep(1)

                except Exception as e:
                    print(f"关键词 '{kw}' 的第 {page} 页爬取时出错: {str(e)}")
                    break
                
        # 如果有README获取任务，等待所有任务完成
        if get_readme and search_type == "repositories":
            print("等待所有README获取任务完成...")
            
            for future in readme_futures:
                try:
                    future.result()  # 等待任务完成
                except Exception as e:
                    print(f"处理README任务时出错: {str(e)}")
            
            readme_executor.shutdown()
            print("所有README获取任务已完成")
            
            # 返回带有README的结果列表
            return self.results_with_readme
        else:
            # 返回不带README的结果列表
            return results
    
    def _get_repo_readme(self, repo):
        """处理单个仓库的README获取任务"""
        try:
            if 'url' in repo and repo['url']:
                readme_content = self.get_readme(repo['url'])
                repo['readme'] = readme_content
            else:
                repo['readme'] = "无仓库URL"
                
            # 使用锁安全地更新结果列表
            with self.results_lock:
                self.results_with_readme.append(repo)
                
            # 打印进度
            with self.results_lock:
                current_count = len(self.results_with_readme)
            print(f"已完成 {current_count} 个仓库的README获取: {repo.get('name', '未知仓库')}")
                
        except Exception as e:
            print(f"获取仓库 {repo.get('name', '未知')} 的README时出错: {str(e)}")
            # 即使出错，也添加到结果中
            repo['readme'] = f"获取失败: {str(e)}"
            with self.results_lock:
                self.results_with_readme.append(repo)
    

    def get_readme(self, repo_url):
        """获取仓库的README内容"""
        try:
            readme_url = f"{repo_url}"
            response = requests.get(readme_url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                readme_content_tag = soup.select_one('article.markdown-body')
                if readme_content_tag:
                    readme_content = readme_content_tag.get_text()
                    max_length = 1888 # 设置最大长度，可以根据需要调整
                    return readme_content[:max_length] if len(readme_content) > max_length else readme_content
                return "无README内容"
            else:
                return f"获取README失败，状态码: {response.status_code}"
        except Exception as e:
            return f"获取README时出错: {str(e)}"

    def _parse_repositories(self, soup):
        """解析仓库搜索结果"""
        results = []
        # 更新选择器 - 尝试多个可能的选择器
        repo_list = soup.select('li.repo-list-item') or soup.select('div[data-testid="results-list"] > div')
        
        if not repo_list:
            print("未找到仓库列表元素，尝试检查页面结构")
            return results
        
        for repo in repo_list:
            try:
                # 尝试多种可能的选择器
                name_element = (
                    repo.select_one('a.v-align-middle') or 
                    repo.select_one('a[data-testid="result-heading-title"]') or
                    repo.select_one('h3 a')
                )
                
                description_element = (
                    repo.select_one('p.mb-1') or 
                    repo.select_one('p[itemprop="description"]') or
                    repo.select_one('div[data-testid="result-description"]')
                )
                
                stars_element = (
                    repo.select_one('a[href*="/stargazers"]') or
                    repo.select_one('span[data-view-component="true"][title*="stars"]') or
                    repo.select_one('a[href*="/star"]')
                )
                
                language_element = (
                    repo.select_one('span[itemprop="programmingLanguage"]') or
                    repo.select_one('span[data-view-component="true"].d-inline-block')
                )
                
                name = name_element.text.strip() if name_element else "未知"
                url = "https://github.com" + name_element['href'] if name_element and 'href' in name_element.attrs else ""
                description = description_element.text.strip() if description_element else "无描述"
                stars = stars_element.text.strip() if stars_element else "0"
                language = language_element.text.strip() if language_element else "未知"
                
                results.append({
                    "name": name,
                    "url": url,
                    "description": description,
                    "stars": stars,
                    "language": language
                })
                
            except Exception as e:
                print(f"解析仓库信息时出错: {str(e)}")
        
        return results


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
        agent.send_output(agent_output_name='github_search_LLM_result', agent_result="出现错误，已暂停")
        return
    #判断继续搜索
    if "NNNN" in keywords:
        #不需要搜索
        agent.send_output(agent_output_name='github_search_LLM_result', agent_result="空闲中")
        return
    
    agent.send_output(agent_output_name='github_search_LLM_result', agent_result="正在搜索ing")

    #启动搜索
    # t=threading.Thread(target=search_thread,args=(keywords,user_query))
    # t.start()
    #根据关键词列表查询关键词并用大模型筛选
    crawler = GitHubCrawler()
    search_results = crawler.search(
                keyword=keywords,
                search_type="repositories",
                max_pages=2,
                get_readme=True
            )
    #print(search_results)
    print("找到了，让我看看")
    #filltered_content=filter_results_with_model(search_results,user_query)
    #print(filltered_content)
    #if filltered_content is None or filltered_content==[]:
    #   #result_queue.put("未搜索到结果")
    #    agent.send_output(agent_output_name='github_search_LLM_result', agent_result="未搜索到结果")

    #result_queue.put(filltered_content)
    agent.send_output(agent_output_name='github_search_LLM_result', agent_result=search_results)
    
        





def main():
    agent = MofaAgent(agent_name='github_search_LLM')
    run(agent=agent)

if __name__ == "__main__":
    main() 

