import argparse
import json
import os
import ast
import sys

import click
import pyarrow as pa
from dora import Node
from mofa.utils.install_pkg.load_task_weaver_result import extract_important_content
RUNNER_CI = True if os.getenv("CI") == "true" else False

from flask import Flask, request, jsonify, render_template, Response
from threading import Thread, Lock, Event
import time
import random
import queue
from collections import defaultdict
import uuid
import json

app = Flask(__name__)
node = Node("serve")

# 线程安全的消息队列和聊天记录
message_queues = defaultdict(queue.Queue)
chat_histories = defaultdict(list)
system_lock = Lock()

# 活动会话管理
active_sessions = set()
monitor_threads = {}

# 外部消息模拟
external_messages = [
    "系统通知: 有新功能可用，输入'help'查看",
    "提醒: 服务器将在1小时后维护",
    "热点: 今日热门话题 - 人工智能",
    "更新: 你的请求已被处理",
    "提示: 试试问关于天气的问题"
]

class ChatAgent:
    def __init__(self):
        self.responses = [
            "分析中...\n请稍候",
            "已收到: {input}\n正在处理...",
            "根据我的知识:\n{result}",
            "查询结果:\n------\n{result}",
            "处理完成:\n------\n{result}"
        ]
        self.proactive_triggers = {
            "天气": "需要我提供天气预报吗?",
            "时间": "需要我告诉你当前时间吗?",
            "新闻": "要我获取最新新闻吗?",
            "help": "可用命令:\n- 天气\n- 时间\n- 新闻\n- exit"
        }
    
    def generate_response(self, user_input, context=None):
        """生成响应并更新上下文"""
        #time.sleep(random.uniform(0.5, 1.5))
        
        if user_input.lower() in ['exit', 'quit']:
            return "会话结束。输入任何消息重新开始。", None
        
        # 检查是否有触发词
        for trigger, response in self.proactive_triggers.items():
            if trigger in user_input.lower():
                return response, trigger
        
        # 默认响应
        result = f"已处理: {user_input}"
        response = random.choice(self.responses).format(input=user_input, result=result)
        return response, user_input

chat_agent = ChatAgent()

def monitor_external_changes(session_id, stop_event):
    """监控外部变化并决定是否发送消息"""
    
    while not stop_event.is_set() and session_id in active_sessions:
        try:
            # 模拟从外部获取消息 (实际应用中可以是API调用、数据库查询等)
            #time.sleep(random.uniform(5, 15))  # 随机间隔检查
            #external_msg = random.choice(external_messages)
            with system_lock:
                    history = chat_histories[session_id]
            
            event = node.next(timeout=200)
            print(f"监控线程接收到外部消息: {event}")

            if event is not None:
                print(f"监控线程接收到外部消息: {event}")
                node_results = json.loads(event['value'].to_pylist()[0])
                results = node_results.get('node_results')
                is_dataflow_end = node_results.get('dataflow_status', False)
                step_name = node_results.get('step_name', '')
                external_msg = f'-------------{step_name}---------------\n{results}\n---------------------------------------'
                if is_dataflow_end ==True or is_dataflow_end == 'true' or is_dataflow_end == 'True':
                        break
                event = node.next(timeout=200)
                
                
                # 根据聊天历史决定是否发送
                if len(history) > 0 :
                    message_queues[session_id].put(json.dumps({
                        'message': external_msg,
                        'sender': 'system'
                    }))
                    chat_histories[session_id].append({
                        'sender': 'system',
                        'message': external_msg,
                        'time': time.time()
                    })
            
                    
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
    
    # 发送欢迎消息
    welcome_msg = {
        'message': "欢迎来到智能聊天代理\n输入'help'查看帮助",
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
        node.send_output("data", pa.array([clean_string(message)]))
    
    print(f"发送消息: {message}")
    
    # 显示用户消息
    # message_queues[session_id].put(json.dumps({
    #    'message': f"> {message}",
    #    'sender': 'user'
    # }))
    
    # 生成响应
    def generate_response():
        history = chat_histories.get(session_id, [])
        context = [msg['message'] for msg in history[-3:] if msg['sender'] == 'user']
        
        response, new_context = chat_agent.generate_response(message, context)
        
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

    #node = Node(
    #    args.name
    #)  # provide the name to connect to the dataflow if dynamic node

    if data is None and os.getenv("DORA_NODE_CONFIG") is None:
        app.run(debug=False, threaded=True)
        #send_task_and_receive_data(node)


if __name__ == "__main__":
    main()
