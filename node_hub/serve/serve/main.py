import argparse
import json
import os
import ast
import sys
from queue import Queue
import click
import pyarrow as pa
from dora import Node
from mofa.utils.install_pkg.load_task_weaver_result import extract_important_content
RUNNER_CI = True if os.getenv("CI") == "true" else False

import yaml

from flask import Flask, request, jsonify, render_template, Response
from threading import Thread, Lock, Event
import time
import random
import queue
from collections import defaultdict
import uuid
import json
from openai import OpenAI


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
        {"role": "system", "content": """***主要任务***
你的名字是who_konws,是一个搜索助手，
你的任务是根据对话记录和其他agent收集到的信息为用户整理搜索结果,
你需要提供一个搜索结果的排序方案，并给出具体的搜索结果,
如果有些你知道的信息但是其他agent未搜索到的也可以经过整理后提供给用户,
不过要记得讲清楚这是你记忆的内容并非来自网络搜索，
并告知用户网络搜索agent的状态，
每一条搜索结果都要标注出处并给出网页链接（如有）

***对话风格***
请口语化的表达，
表现出极其专业干练的态度，
没有一句废话，
回复用户时不要僵化死板地重复，
要照顾到用户的感受，
在用户等待时间长时安抚用户,
保持专业中立理性
使用正常文本回答不要用readme格式"""},
        {"role": "assistant", "content": f"今天想知道点什么?\ntime:{time.strftime('%H:%M:%S', time.localtime())}"}
        ]




node=Node("serve")

app = Flask(__name__)



# 线程安全的消息队列和聊天记录
message_queues = defaultdict(queue.Queue)
chat_histories = defaultdict(list)
system_lock = Lock()
dora_lock = Lock()

# 初始化全局锁
search_lock = Lock()

# 活动会话管理
active_sessions = set()
monitor_threads = {}

# 创建双工通信队列
send_queue = Queue()
receive_queue = Queue()
stop_flag = False


#搜索结果
search_results = {
    'agent_response_github': '正在搜索ing',
    'agent_response_arxiv': '正在搜索ing',
    'agent_response_google': '正在搜索ing'
}


def dora_worker():
    global stop_flag
    while not stop_flag:
        try:
            # 处理发送任务
            if not send_queue.empty():
                message = send_queue.get()
                print(f"Dora worker received message: {message}")
                with dora_lock:  # 仍建议保留锁机制
                    node.send_output("data", pa.array([clean_string(message)]))
                send_queue.task_done()
            
            # 处理接收事件
            with dora_lock:
                event = node.next(timeout=0.001)  # 适当调整超时时间
                
            if event is None:
                continue
            if event['type'] == 'ERROR':
                continue
            receive_queue.put(event)
            print(f"Dora worker received event: {event}")
                
                
        except Exception as e:
            print(f"Dora worker error: {str(e)}")


class ChatAgent:
    def __init__(self):
        pass
        # self.responses = [
        #     "分析中...\n请稍候",
        #     "已收到: {input}\n正在处理...",
        #     "根据我的知识:\n{result}",
        #     "查询结果:\n------\n{result}",
        #     "处理完成:\n------\n{result}"
        # ]
        # self.proactive_triggers = {
        #     "天气": "需要我提供天气预报吗?",
        #     "时间": "需要我告诉你当前时间吗?",
        #     "新闻": "要我获取最新新闻吗?",
        #     "help": "可用命令:\n- 天气\n- 时间\n- 新闻\n- exit"
        # }
    
    def format_search_results(self,search_results):
        """将search_results字典格式化为大语言模型可以接受的文本数据"""
        formatted_results = "\n".join(f"{key}: {value}" for key, value in search_results.items())
        return formatted_results
    
    def generate_response(self, user_input, context=None):
        """生成响应并更新上下文"""
        #time.sleep(random.uniform(0.5, 1.5))
        
        if user_input.lower() in ['exit', 'quit']:
            return "会话结束。输入任何消息重新开始。", None
        #获取搜索结果
        with search_lock:
            search_context = self.format_search_results(search_results)
        
        #获取历史记录
        with system_lock:
            #加入搜索结果
            messages_this_turn = messages
        
        messages_this_turn.append({
                "role": 'system',
                "content": search_context
            })
        #调用模型
        client = OpenAI(api_key=api_key, base_url=base_url)
        response_agent = client.chat.completions.create(
            model=model,
            messages=messages_this_turn,
            stream=False
            )
        
        #print()
        response=response_agent.choices[0].message.content
        
        # 默认响应
        result = f"已处理: {user_input}"
        #response = random.choice(self.responses).format(input=user_input, result=result)
        return response, user_input

chat_agent = ChatAgent()

def monitor_external_changes(session_id, stop_event):
    """监控外部变化并决定是否发送消息"""
    while not stop_event.is_set() and session_id in active_sessions:
        try:
            # 模拟从外部获取消息 (实际应用中可以是API调用、数据库查询等)
            
            
            # with system_lock:
            #         history = chat_histories[session_id]
            
            if not receive_queue.empty():
                event=receive_queue.get()
                node_results = json.loads(event['value'].to_pylist()[0])
                event_id = event['id']
                results = node_results.get('node_results')
                #is_dataflow_end = node_results.get('dataflow_status', False)
                #step_name = node_results.get('step_name', '')
                # 加锁更新全局变量
                with search_lock:
                    if event_id in search_results:
                       # 将结果转换为字符串存储
                       result_str = str(node_results.get('node_results', '正在搜索ing'))
                       search_results[event_id] = result_str
                       external_msg = f" {event_id} : {result_str[:50]}..."
                       print(f" {event_id} : {result_str[:50]}...")  # 截短显示

                #系统消息发送到网页
                message_queues[session_id].put(json.dumps({
                        'message': external_msg,
                        'sender': 'system'
                    }))
                chat_histories[session_id].append({
                        'sender': 'system',
                        'message': external_msg,
                        'time': time.time()
                    })    
                receive_queue.task_done()
                #                           调用大模型
            
                    
        except Exception as e:
            print(f"监控线程错误: {e}")

@app.route('/')
def home():
    return render_template('enhanced_chat.html')

@app.route('/chat_stream/<session_id>')
def chat_stream(session_id):
    def event_stream():
        while session_id in active_sessions:
            try:
                with search_lock:
                    if not message_queues[session_id].empty():
                        message = message_queues[session_id].get()
                        yield f"data: {message}\n\n"
                        time.sleep(0.1)
            except:
                break
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/start_session', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())
    active_sessions.add(session_id)
    
    # 初始化聊天历史
    with system_lock:
        chat_histories[session_id] = []
    
    # 启动监控线程
    stop_event = Event()
    monitor_threads[session_id] = stop_event
    Thread(target=monitor_external_changes, args=(session_id, stop_event)).start()
    #print("真的启动了起来了吗？")
    
    # 发送欢迎消息
    welcome_msg = {
        'message': "今天想知道点什么?",
        'sender': 'system'
    }
    message_queues[session_id].put(json.dumps(welcome_msg))

    chat_histories[session_id].append({
        'sender': 'system',
        'message': welcome_msg['message'],
        'time': time.time()
    })
    
    return jsonify({"session_id": session_id})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message', '').strip()
    
    if session_id not in active_sessions:
        return jsonify({"error": "无效会话"}), 400
    

    
    # 添加到聊天历史
    with system_lock:
        chat_histories[session_id].append({
            'sender': 'user',
            'message': message,
            'time': time.time()
        })
        messages.append({
                "role": 'user',
                "content": message
            })
    
    #给查询agent发送消息
    clean_message = clean_string(message)
    print(f"发送消息: {clean_message}")
    send_queue.put(clean_message)



    # 生成响应
    def generate_response():
        history = chat_histories.get(session_id, [])
        context = [msg['message'] for msg in history[-8:] if msg['sender'] == 'user']
        response, new_context = chat_agent.generate_response(message, context)
        #                      调用大模型
        #response = "正在处理..."
        #new_context = None
        # 发送响应
        message_queues[session_id].put(json.dumps({
            'message': response,
            'sender': 'ai'
        }))
            
        
        # 更新上下文
        with system_lock:
            chat_histories[session_id].append({
                'sender': 'ai',
                'message': response,
                'time': time.time()
            })
            messages.append({
                "role": 'assistant',
                "content": response
            })
            
            if new_context:
                chat_histories[session_id][-1]['context'] = new_context
    
    Thread(target=generate_response).start()
    return jsonify({"status": "已接收"})

@app.route('/end_session/<session_id>', methods=['POST'])
def end_session(session_id):
    if session_id in active_sessions:
        active_sessions.remove(session_id)
        if session_id in monitor_threads:
            monitor_threads[session_id].set()
            del monitor_threads[session_id]
    return jsonify({"status": "会话结束"})




def clean_string(input_string:str):
    return input_string.encode('utf-8', 'replace').decode('utf-8')






def main():

    # Handle dynamic nodes, ask for the name of the node in the dataflow, and the same values as the ENV variables.
    parser = argparse.ArgumentParser(description="Simple arrow sender")

    parser.add_argument(
        "--name",
        type=str,
        required=False,
        help="The name of the node in the dataflow.",
        default="serve",
    )
    parser.add_argument(
        "--data",
        type=str,
        required=False,
        help="Arrow Data as string.",
        default=None,
    )

    args = parser.parse_args()

    data = os.getenv("DATA", args.data)

    
    # node = Node(
    #     args.name
    # )  # provide the name to connect to the dataflow if dynamic node
    

    if data is None and os.getenv("DORA_NODE_CONFIG") is None:
        dora_thread = Thread(target=dora_worker, daemon=True)
        dora_thread.start()
        app.run(debug=True, threaded=True)
        dora_thread.join()




if __name__ == "__main__":
    main()
