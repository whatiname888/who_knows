# **Who_Knows**

<!-- PROJECT LOGO -->

<br />

<p align="center">
  <a href="https://github.com/whatiname888/who_knows">
    <img src="https://github.com/whatiname888/who_knows/blob/main/image/haha.png?raw=true" alt="Logo" width="188" height="188">
  </a>

<h3 align="center">Who_Knows</h3>
  <p align="center">
    基于MoFA的深度智能搜索引擎
    <br />
    <a href="https://github.com/whatiname888/who_knows"><strong>本项目的Github仓库链接 »</strong></a>
    <br />本项目由[爱北京，来工大]团队制作
    <br />
    <a href="https://github.com/whatiname888/who_knows/blob/main/who_knows_search/README.md">查看使用文档</a>
    ·
    <a href="https://github.com/whatiname888/who_knows/issues">报告Bug</a>
    ·
    <a href="https://github.com/whatiname888/who_knows/pulls">提出新特性</a>
  </p>

</p>

# 目录

- [项目简介](##项目简介)
- [Getting_started](##Getting_started)
  - [环境依赖配置](###环境依赖配置)
  - [运行说明](###运行说明)
- [创新点与突破点](##创新点与突破点)
  - [创新点](###创新点)
  - [突破点](###突破点)
- [技术难点与解决方案](##技术难点与解决方案)
  - [技术难点](###技术难点)
  - [解决方案](###解决方案)
- [运行案例](##运行案例)
- [团队介绍](#团队介绍)
- [鸣谢](#鸣谢)

项目环境：
Python 3.11.10
rust
pip 24.2

## 项目简介
who_knows 是一个基于 mofa 框架，使用 dora 组织数据流的搜索项目。它通过大模型与小模型的协同工作来提炼和过滤海量搜索结果，自动拓展关键词，帮助用户从繁琐的信息中快速找到关键信息，使搜索过程更加高效、直接。

- **核心特点**  
  - 基于智能体协作的架构设计，将用户交互和任务执行分为独立模块
  - 实现动态调整搜索策略，逐层提炼关键信息，保证数据输出的精准与全面
- **功能说明**  
  - xiaowang是一个以智能体驱动的搜索引擎，利用创新的**左右脑设计**与**Deepsearch 策略**实现高效的信息检索和数据分析，为用户提供一个智能、动态、深度且友好的信息获取平台
- **使用场景**  
  - 用户厌倦了传统搜索引擎中良萎不齐的信息来源、铺天盖地的广告宣传与繁琐至极的挨个浏览，希望有一款自动收集信息、自动整理分析的准确高效的新一代搜索引擎。
---
**多层次动态反思智能体原理框图**

![1728992177018](https://github.com/whatiname888/xiaowang/blob/main_code/xiaowang_start/data/1.png?raw=true)

**agent数据流框图**

![](https://github.com/whatiname888/xiaowang/blob/main_code/xiaowang_start/data/2.png?raw=true)

## Getting_started

### 环境依赖配置

> 注：建议在Linux系统运行，Windows下会有兼容问题。

**本项目所需框架及语言版本如下**

* Python 3.12.16
  pip 24.2
  Rust 1.81.0
  dora-cli 0.3.6
1. 搭建虚拟环境:

   ```sh
   python3.12 -m venv myenv 
   ```
   ```sh
   source myenv/bin/activate  
   ```
   你可以将myenv更改为你喜欢的名字

2. 克隆仓库:

   ```sh
   git clone https://gitcode.com/BJF_17812135905/xiaowang.git
   ```

3. 运行dabao.py:

   dabao.py为你准备了安装依赖等的自动化操作

   ```sh
   python dabao.py
   ```

恭喜你，在上述步骤后你已经成功搭建好了运行who_knows的全部基础！！

### 运行说明

在这部分我将讲解如何在你的设备上配置并运行who_knows

由于我们的程序需要使用在线大模型API运行的，因此在启动前要将你的API密钥，模型名称，API接口URL填入配置文件。

以下是我们的项目文件结构：

> who_knows/
> ├── mofa/ # mofa代码目录
> ├── xiaowang_start/ # 主要节点代码
> │ ├── configs/ # agent配置文件
> │ ├── scripts/# agent代码
> │ ├── data/# 视频，照片，实例测试结果
> │ ├── README.md
> │ ├── xiaowang_start_dataflow.yml
> │ └── xiaowang_start_dataflow-graph.html
> ├── xiaowang_terminal/ # xiaowang主程序
> ├── .gitignore # Git 忽略文件
> ├── HISTORY.rst # 项目配置文件
> ├── LICENSE# 许可证
> ├── README.md # readme文件
> ├── setup.py # mofa包安装文件
> ├── README.rst # 项目配置文件
> └── requirements.txt # mofa依赖

打开文件夹`xiaowang/xiaowang_start/configs/`

配置该文件夹中以下文件内大语言模型推理 API部分：

- `agent_DLC.yml`   -动态规划节点
- `agent_generate.yml`   -生成节点
- `agent_reflaction.yml`  -反思节点

大语言模型推理 Api配置示例：
使用**Openai**API：

~~~
MODEL:
  MODEL_API_KEY:  
  MODEL_NAME: gpt-4o-mini
  MODEL_MAX_TOKENS: 2048
~~~

配置完成后，可使用Dora-rs命令行命令运行 `xiaowang_start_dataflow.yml` 文件

- 顺序执行以下命令以启动智能体流程：

```bash
dora up
dora build xiaowang_start_dataflow.yml
dora start xiaowang_start_dataflow.yml
```

打开一个新的终端窗口，运行 `xiaowang`，

```bash
xiaowang
```

由于dora启动速度的原因若刚刚执行完 `dora start xiaowang_start_dataflow.yml`立马执行 `xiaowang`可能会导致程序不输出，不要慌张等待片刻即可看到程序输出`说吧，什么事:`的提示。
当看到`说吧，什么事:`时，输入提问内容回车即可。

> 注：由于网络及电脑性能等原因，输出可能有不同程度延迟，请耐心等待模型输出结果，当输出完成后程序会打印`回答结束`，随后进入下一轮对话。

## 创新点与突破点

###  创新点：大小脑设计

- **小脑（交互模块）**  
  负责与用户实时沟通，通过自然语言理解技术获取查询意图，并实时反馈交互状态。

- **大脑（任务代理模块）**  
  分工明确、协同工作的智能代理集合，负责处理所有后端任务，包括数据的初步抓取和深层次的关联搜索，确保输出的结果准确而全面。

- 总结**  
  我们设计的实时交互中继架构，采用双模型协同工作机制：前端轻量化交互模型专责对话流维持与结果渲染，在用户发起请求的瞬间即生成交互反馈信号（<200ms）；后端智能路由模型同步执行多模态语义解析，通过动态关键词提取引擎并行检索GitHub/arXiv/Google三大知识库。两套模型通过事件驱动型信息流实现解耦，使得界面响应延迟与后端计算耗时完全隔离。该架构确保每个用户查询经历「交互保障→语义解析」两次独立模型处理阶段，在维持零停顿对话体验的同时，为后续扩展自定义爬虫接口预留了标准化接入点。



###  突破点：Deepsearch 策略

- **初步搜索：**  
  用户输入查询内容后，系统将会首先提取关键信息，通过爬虫技术抓取互联网数据形成初步搜索结果。

- **深层关联分析：**  
  根据初步结果进一步提炼关键词，开展第二轮更深层次的搜索，从而精细挖掘出隐藏的价值和关联信息。


## 技术难点与解决方案

### 技术难点
123
### 解决方案
123



## 运行案例

### 案例一

**用户：**
```

```

**who_knows：**
```
答案
```
---

## 团队介绍
### 团队分工

- 胡宇桥：负责两个agent的代码编写和最终应用调试作业、markdown文档主要撰写者
- 杨淏森：负责反思模型的提示词工程，markdown文档撰写者。

## 鸣谢

- [Mofa](https://github.com/moxin-org/mofa)
- [吴宗寰老师](https://china2024.gosim.org/zh/speakers/zonghuan-wu)
- [陈成老师]