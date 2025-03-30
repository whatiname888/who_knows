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

- [项目简介](#项目简介)
- [Getting_started](#Getting_started)
  - [环境依赖配置](#环境依赖配置)
  - [运行说明](#运行说明)
- [创新点与突破点](#创新点与突破点)
  - [创新点：大小脑设计](#创新点大小脑设计)
  - [突破点：Deepsearch 策略](#突破点deepsearch-策略)
- [技术难点与解决方案](#技术难点与解决方案)
  - [技术难点](#技术难点)
  - [解决方案](#解决方案)
- [运行案例](#运行案例)
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
  - Who_Knows是一个以智能体驱动的搜索引擎，利用创新的**左右脑设计**与**Deepsearch 策略**实现高效的信息检索和数据分析，为用户提供一个智能、动态、深度且友好的信息获取平台
- **使用场景**  
  - 用户厌倦了传统搜索引擎中良萎不齐的信息来源、铺天盖地的广告宣传与繁琐至极的挨个浏览，希望有一款自动收集信息、自动整理分析的准确高效的新一代搜索引擎。
---
**whoknows-agent搜索引擎架构图**

![1728992177018](https://github.com/whatiname888/who_knows/blob/main/image/81baf620ccb5b39bb81e213ce3a48cf.png?raw=true)

**agent数据流框图**
```mermaid
flowchart TB
  arxvi_search_LLM["**arxvi_search_LLM**"]
  github_search_LLM["**github_search_LLM**"]
  google_search_LLM["**google_search_LLM**"]
  serve["**serve**"]
  serve -- data as query --> arxvi_search_LLM
  serve -- data as query --> github_search_LLM
  serve -- data as query --> google_search_LLM
  arxvi_search_LLM -- arxvi_search_LLM_result as agent_response_arxvi --> serve
  github_search_LLM -- github_search_LLM_result as agent_response_github --> serve
  google_search_LLM -- google_search_LLM_result as agent_response_google --> serve
```

## Getting_started

### 环境依赖配置

> 注：请在Linux和MacOS系统上运行，本项目依赖框架暂不支持Windows

**本项目所需框架及语言版本如下**

* Python 3.11.10
  pip 24.2
  Rust 1.81.0
  dora-cli 0.3.6


1. 克隆此项目:

 ```bash
 git clone https://github.com/whatiname888/who_knows.git
 ```

2. 使用Python 3.10或以上环境：

- 如果出现环境版本不匹配，请检查python和pip版本并重新配置,建议使用虚拟环境。

```bash
pip --version
python --version
```

3. 项目环境部署(安装)

- 安装python环境的依赖：

```bash
# 安装 UV 包管理器 加快mofa安装
pip install uv
#安装python后端框架
pip install flask
```

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# 安装 Dora
cargo install dora-cli
# 验证安装
rustc --version
cargo --version
dora --version
```

```bash
cd mofa/python
# 安装依赖，以下两个命令建议都执行一遍，因为有时uv安装会失败，但是uv的安装速度更快
uv pip install -e .
pip install -e .
```
安装完毕之后，可以使用`mofa --help`命令查看Cli帮助信息

恭喜你，在上述步骤后你已经成功搭建好了运行who_knows的全部基础！！

### 运行说明

在这部分我将讲解如何在你的设备上配置并运行who_knows

由于我们的程序需要使用在线大模型API运行的，因此在启动前要将你的API密钥，模型名称，API接口URL填入配置文件。

以下是我们的项目文件结构：
```
 who_knows/
 ├── image/ # 图片
 ├── mofa/ # mofa框架仓库
 ├── node_hub/ # 各节点代码
 ├── who_knows_search/ # dataflow配置文件
 │ ├── data/# 视频，照片，实例测试结果
 │ ├── README.md
 │ ├── who_knows_dataflow.yml
 │ └── who_knows_dataflow-graph.html
 ├── .gitignore # Git 忽略文件
 ├── .gitmodules # 项目配置文件
 ├── LICENSE# 许可证
 └── README.md # readme文件
```

在相应目录建立以下配置文件并填写你的API密钥，模型名称，API接口URL：

```bash
who_knows/node_hub/serve/serve/config.yaml
who_knows/node_hub/arxiv_search_LLM/arxiv_search_LLM/config.yaml
who_knows/node_hub/github_search_LLM/github_search_LLM/config.yaml
who_knows/node_hub/google_search_LLM/google_search_LLM/config.yaml
```

本项目使用**Openai**API框架，以下为config.yaml文件内容示例：

```yaml
api_key:   #您的API密钥
base_url: https://api.deepseek.com  #API的基础URL
model: deepseek-chat #模型名称
```

- 顺序执行以下命令以启动智能体流程：

>注：请确保在项目根目录下运行以下命令，并确保运行前进入了虚拟环境
```bash
cd who_knows_search
dora up
dora build who_knows_dataflow.yml
dora start who_knows_dataflow.yml
```

等待显示以下内容后，表示数据流启动成功：
```bash
INFO  dataflow `xxxx-xxx-xxx` on daemon `xxxx-xxx-xxx` google_search_LLM daemon: node is ready
INFO  dataflow `xxxx-xxx-xxx` on daemon `xxxx-xxx-xxx` github_search_LLM daemon: node is ready
INFO  dataflow `xxxx-xxx-xxx` on daemon `xxxx-xxx-xxx` arxiv_search_LLM daemon: node is ready
INFO  dataflow `xxxx-xxx-xxx` on daemon `xxxx-xxx-xxx` daemon: all nodes are ready, starting dataflow
```


打开一个新的终端窗口，进入相同虚拟环境后运行 `whos_serve`

```bash
whos_serve
```
看到以下输出即为yun_serve启动成功：
```bash
 * Serving Flask app 'serve.main'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with watchdog (inotify)
 * Debugger is active!
 * Debugger PIN: xxx-xxx-xxx
```
>此示例仅作演示使用，实际部署请使用Nginx或其他Web服务器托管。


由于dora启动速度的原因若刚刚执行完 `dora start who_knows_dataflow.yml`立马执行 `whos_serve`可能会报错，如遇报错请等待几秒后再次执行`whos_serve`命令。

打开浏览器，输入`http://localhost:5000/`，进入到搜索引擎主页，输入查询内容，点击搜索按钮，即可看到搜索结果。

> 注：由于网络及电脑性能等原因，输出可能有不同程度延迟，请耐心等待模型输出结果。

## 创新点与突破点

###  创新点：左右脑设计

- **右脑（交互模块）**  
  负责与用户实时沟通，通过自然语言理解技术获取查询意图，并实时反馈交互状态。

- **左脑（任务代理模块）**  
  分工明确、协同工作的智能代理集合，负责处理所有后端任务，包括数据的初步抓取和深层次的关联搜索，确保输出的结果准确而全面。

- **总结**  
  我们设计的实时交互中继架构，采用双模型协同工作机制：前端轻量化交互模型专责对话流维持与结果渲染，在用户发起请求的瞬间即开始生成交互反馈信号；后端智能路由模型同步执行多模态语义解析，通过动态关键词提取引擎并行检索GitHub/arXiv/Google三大知识库。两套模型通过事件驱动型信息流实现解耦，使得界面响应延迟与后端计算耗时完全隔离。该架构确保每个用户查询经历「交互保障→语义解析」两次独立模型处理阶段，在维持零停顿对话体验的同时，为后续扩展自定义爬虫接口预留了标准化接入点。



###  突破点：Deepsearch 策略

- **初步搜索：**  
  用户输入查询内容后，系统将会首先提取关键信息，通过爬虫技术抓取互联网数据形成初步搜索结果。

- **深层关联分析：**  
  根据初步结果进一步提炼关键词，开展第二轮更深层次的搜索，从而精细挖掘出隐藏的价值和关联信息。


## 技术难点与解决方案

### 技术难点
Dora框架对并发的支持不佳，无法充分利用多核CPU性能，导致处理能力受限，高并发场景下容易出现性能瓶颈，并且长时间运行的任务会阻塞整个系统。
### 解决方案
我们通过Flask的多线程和消息队列机制实现了类似并发的效果。具体来说，它使用线程安全的队列(message_queues)来管理不同会话的消息，并通过独立的监控线程(monitor_external_changes)处理外部事件，同时利用全局锁(system_lock, search_lock)来保证数据一致性，从而在Dora框架的单线程限制下实现了多会话并发处理。



## 运行案例

### 案例一

**用户：**
```
帮我找个叫mofa的智能体框架
```

**DeepSeek-R1：**
```markdown
</think>
好的，用户让我帮忙找一个叫“mofa”的智能体框架。首先，我需要仔细看看用户提供的搜索结果，看看有没有提到这个框架。

先看第一个网页，是关于GOSIM超级智能体黑客马拉松大赛的。里面提到参赛者使用了开源的MoFA框架，看来这个MoFA可能和智能体相关。不过网页里没有详细说明MoFA是什么，但结合比赛内容，应该是一个智能体开发框架，可能用于构建多层次的动态反思智能体。这个信息挺重要的，需要记下来。2

接下来是第二个网页，标题是“探秘多组学数据分析:MOFA,一种综合集成框架”。这里提到的MOFA全称是Multi-Omics Factor Analysis，用于多组学数据整合，看起来是生物信息学领域的工具，不是智能体框架。不过用户可能拼写错误，把MOFA写成mofa，但根据用户的问题，应该是要找智能体相关的框架，所以这个可能不是用户需要的，但需要留意。3

第三个网页列举了11个流行的AI智能体框架，里面没有提到MOFA，不过有AutoGPT、BabyAGI、SuperAGI等，可能用户提到的mofa不在其中。8

第四个和第五个网页对比了五大多智能体框架，包括AutoGen、CrewAI、LangGraph等，同样没有MOFA的踪影。910

第六个网页介绍魔搭社区开源的AgentScope，也没有提到MOFA。11

第七个网页继续对比多智能体框架，同样没有MOFA的信息。12

第八个网页是关于金属有机框架（MOF）的，显然和用户的问题无关。13

现在回到第一个网页，里面明确提到了MoFA框架，参赛者用它来开发项目。结合用户可能的大小写错误，比如MoFA和mofa其实是同一个，这个可能就是用户要找的框架。另外，在网页1里，MoFA和xMind框架一起被提及，都是开源的，用于构建智能体项目，挑战ChatGPT。所以可以确定，MoFA是一个开源的智能体框架，应用于黑客松比赛中，可能具有动态反思和多层次优化的能力。而第二个网页的MOFA虽然名称相似，但属于生物信息学工具，不是用户需要的。

需要确认用户是否拼写错误，但根据搜索结果，MoFA是存在的智能体框架。因此，回答应重点介绍网页1提到的MoFA框架，并指出可能存在的拼写差异，同时排除生物信息学的MOFA。另外，如果用户需要更多信息，可以建议查阅网页1提供的比赛详情或相关开源社区。
</think>
根据搜索结果，名为“MoFA”的智能体框架在 **GOSIM超级智能体黑客马拉松编程大赛** 中被多次提及。以下是关于该框架的关键信息梳理：

### 1. **MoFA框架的基本信息**
- **用途**：MoFA是一个开源的模块化智能体框架，主要用于构建多层次动态反思智能体，优化大语言模型的输出结果，提升准确性和可靠性。
- **技术特点**：
  - 结合多智能体协作能力，支持动态任务编排。
  - 在比赛中，参赛团队通过MoFA与其他开源工具（如xMind智能体框架）结合，开发了涉及教育、医疗、科研等领域的创新项目。
  - 其设计可能包含灵活的任务分配和智能体间通信机制（参考类似框架如AutoGen的协作特性）。

### 2. **相关应用案例**
在黑客松大赛中，多个项目基于MoFA实现：
- **冠军项目**：通过MoFA框架优化大模型的动态反思能力，显著提升输出的专业性和准确性，例如在医疗和法律领域的应用。
- **教育科研类项目**：如“MATH_Coder”通过MoFA整合数学运算与代码生成，辅助复杂问题的解决。

### 3. **与其他框架的对比**
虽然搜索结果中未直接对比MoFA与其他主流智能体框架（如AutoGen、LangGraph等），但根据其应用场景和技术描述，可推测其定位：
- **优势**：专注于动态反思和多层次优化，适合需要高可靠性和专业性的任务。
- **适用场景**：与需要结合大模型进行复杂逻辑处理的领域（如专业问答、科研辅助）更契合。

### 4. **获取方式**
- **开源信息**：MoFA作为开源框架，可能在GitCode等平台公开（参考GOSIM大赛的主办方为GitCode社区）。建议通过比赛官网或相关开源社区（如GitCode）进一步查找代码仓库和文档。

### 5. **注意事项**
- **名称拼写差异**：需注意与另一个同名工具 **MOFA（Multi-Omics Factor Analysis）** 区分，后者是生物信息学中用于多组学数据整合的工具，与AI智能体无关。

若需进一步了解MoFA的技术细节或代码实现，可参考GOSIM大赛的获奖项目说明或联系GitCode社区获取资源。
```

**用户：**
```
帮我找个叫mofa的智能体框架
```

**who_knows(最终汇总结果)：**

```markdown
嘿，网络搜索agent们已经把搜索结果都带回来啦，下面就按照咱之前说的相关度从高到低给你整理呈现哦。

排序方案
先根据搜索结果与“mofa智能体框架”这个主题的直接相关性进行排序，相关性越强越靠前。对于同样相关性较强的结果，再按照搜索平台（github、arxiv、google）的顺序依次排列来自不同平台的内容，以便你能更全面清晰地查看各个方面的信息呀。

具体搜索结果
来自github的搜索结果：
名称：moxin-org/mofa

描述：MoFA: Modular Framework for Agent，MoFA是一个软件框架，用于通过基于组合的方法构建AI智能体。使用MoFA，可以通过模板构建AI智能体，并分层组合以形成更强大的超级智能体。

链接：https://github.com/moxin-org/mofa

星星数（stars）：54

名称：bioFAM/MOFA

描述：MOFA: Multi-Omics Factor Analysis，MOFA是一种因子分析模型，它提供了以完全无监督的方式集成多组学数据集的通用框架。

链接：https://github.com/bioFAM/MOFA

星星数（stars）：239

名称：bioFAM/MOFA2

描述：Multi-Omics Factor Analysis，MOFA是一个因子分析模型，为以无监督方式集成多组学数据集提供了通用框架。

链接：https://github.com/bioFAM/MOFA2

星星数（stars）：326

名称：MyNiuuu/MOFA-Video

描述：MOFA-Video: Controllable Image Animation via Generative Motion Field Adaptions in Frozen Image-to-Video Diffusion Model (ECCV 2024)

链接：https://github.com/MyNiuuu/MOFA-Video

星星数（stars）：733

名称：waxz/MoFA

描述：MoFA: Model-based Deep Convolutional Face Autoencoder for Unsupervised Monocular Reconstruction

链接：https://github.com/waxz/MoFA

星星数（stars）：35

来自arxiv的搜索结果：
标题：MOFA: Discovering Materials for Carbon Capture with a GenAI- and Simulation-Based Workflow

摘要：We presentMOFA, an open-source generative AI (GenAI) plus simulation workflow for high-throughput generation of metal-organic frameworks (MOFs) on large-scale high-performance computing (HPC) systems.…

链接：https://arxiv.org/abs/2501.10651

标题：MOFA-Video: Controllable Image Animation via Generative Motion Field Adaptions in Frozen Image-to-Video Diffusion Model

摘要：We presentMOFA-Video, an advanced controllable image animation method that generates video from the given image using various additional controllable signals (such as human landmarks reference, manual trajectories, and another even provided video) or their combinations. This is different from previous methods which only can work on a specific motion domain…

链接：https://arxiv.org/abs/2405.20222

标题：On Test Sequence Generation using Multi-Objective Particle Swarm Optimization

摘要：sequences with the highest priority and the lowest Oracle cost as optimal. The performance of the implemented approach is compared with the Multi-Objective Firefly Algorithm (MOFA) for generating test sequences. The MOPSO-based solution outperforms theMOFA-based approach and simultaneously provides the optimal solutio…

链接：https://arxiv.org/abs/2404.06568

标题：MOFA: A Model Simplification Roadmap for Image Restoration on Mobile Devices

摘要：of parameters by up to 23%, while increasing PSNR and SSIM on several image restoration datasets. Source Code of our method is available at \href{https://github.com/xiangyu8/MOFA}{https://github.com/xiangyu8/MOFA}.

链接：https://arxiv.org/abs/2308.12494

标题：DRKF: Distilled Rotated Kernel Fusion for Efficient Rotation Invariant Descriptors in Local Feature Matching

摘要：processed by the subsequent re-parameterization, no extra computational costs will be introduced in the inference stage. Moreover, we present Multi-oriented Feature Aggregation (MOFA) which aggregates features extracted from multiple rotated versions of the input image and can provide auxiliary knowledge for the training of RKF by leveraging the distillation…

链接：https://arxiv.org/abs/2209.10907

来自google的搜索结果：
标题：MoFA: 迈向AIOS 原创 - CSDN博客

简介：MoFA (Modular Framework for Agents)是一个独特的模块化AI智能体框架。MoFA以组合（Composition)的逻辑和编程（Programmable）的方法构建AI智能体。开发者通过模版的继承、编程、定制智能体，通过堆叠和组合，形成更强大的超级智能体（Super Agent)。

链接：https://blog.csdn.net/vastgrassland/article/details/142408978

标题：MOFA: 你好，世界！ 原创 - CSDN博客

简介：我们的MoFA智能体编程框架也将随之发布。今天，我们掀起MoFA面纱的一角，来介绍一下如何用MoFA来写一个最简单的智能体：Hello, World!程序员们都知道...

链接：https://blog.csdn.net/vastgrassland/article/details/142753620

标题：2025 MoFA 超级智能体大赛- 黑客马拉松编程大赛- 训练营

简介：2025 Mofa 大赛MoFA (Modular Framework for Agents)是一个独特的模块化AI智能体框架。MoFA以组合（Composition)的逻辑和编程（Programmable）的方法构建AI智能体。

链接：https://opencamp.cn/gosim/camp/mofa-2025

标题：Agent 智能体开发框架选型指南 - 53AI

简介：开发人员在构建智能体时，不仅要决定使用何种模型、应用场景和技术架构，还要挑选合适的开发框架。是坚持较为早期的LangGraph，还是转向新兴的LlamaIndex...

链接：https://www.53ai.com/news/langchain/2024110531870.html

标题：2025 MoFA Search AI 搜索引擎大赛- 黑客马拉松编程... - opencamp.cn

简介：MoFA搜索引擎是一款去中心化、保护隐私的组合搜索引擎，无需爬虫，实时返回深网和本地信息，尊重内容权益，由开发者集体协作实现高效搜索。 讲师：吴老师.

链接：https://opencamp.cn/gosim/camp/MoFA2025/stage/0

另外呢，我这儿之前还提到过一个我记忆里的内容呀，就是MOFA（Multimodal Factor Analysis），它是一种多模态因子分析框架，常用于分析多种数据模态之间的关系，不过这只是我记忆的，不一定完全准确哦，你就当个参考先。

这下关于“mofa智能体框架”的相关信息就都给你整理好啦，希望能对你有所帮助呀，如果还有其他需要搜索的，尽管说哦。
```

>以上案例是who_knows和DeepSeek-R1模型对同一问题回答的对比
>通过对比不难看出小模型加上深度搜索在搜索方面的结果要好于深度思考加上浅层搜索
>who_knows采用深度搜索和前后端模型使模型平衡了回答速度和搜索深度以及精准度
>若将主节点换成带有思考过程的更大参数量模型效果将会进一步提高


### 案例二

**用户：**
```markdown
我想学习机器学习和神经网络
```

**who_knows(全流程展示)：**

```markdown
嘿呀，先别急哈，搜索结果正在赶来的路上呢。

排序方案：我打算按照内容的基础入门程度到进阶程度这样来排序，方便你循序渐进地学习哦。

以下是目前我记忆里的一些相关内容供你参考哈（注意哦，这可不是网络搜索结果，就是我记着的一些大概情况，仅供参考呀）：

机器学习呢，简单说就是让计算机能像人一样去学习、去从数据里发现规律啥的。比如可以通过一些算法让机器去识别图片里是猫还是狗呀。
神经网络呢，是机器学习里很重要的一部分啦，它是模仿人类大脑神经元的连接方式构建的模型，能处理很复杂的任务，像语音识别、自然语言处理这些领域都常用到神经网络。
等网络搜索agent那边有了确切结果，我马上就给你详细又准确的搜索内容哈。
---
agent_response_arxiv : 正在搜索ing...
---
agent_response_google : 正在搜索ing...
---
agent_response_github : 正在搜索ing...
---
agent_response_google : {
"机器学习入门教程": {
"searchParameters": {
"q": "机器学习入门教程",
...
---
agent_response_github : [{"name": "girls-in-ai/Girls-In-AI", "url": "https://github.com/girls-in-ai/Girls-In-AI"...
---
agent_response_arxiv : [
{
"id": "2503.21777",
"title": "Test-Time Visual In-Context Tuning...
---
搜索完毕,生成结果ing
---
嘿，搜索结果都来啦，下面就按照咱之前说的，从基础入门程度到进阶程度这样给你排好序咯。

一、基础入门相关（适合刚接触机器学习和神经网络，想要先了解基本概念、学习路线等方面的内容）

来源：我的记忆内容
具体信息：机器学习呢，简单说就是让计算机能像人一样去学习、去从数据里发现规律啥的。比如可以通过一些算法让机器去识别图片里是猫还是狗呀。神经网络呢，是机器学习里很重要的一部分啦，它是模仿人类大脑神经元的连接方式构建的模型，能处理很复杂的任务，像语音识别、自然语言处理这些领域都常用到神经网络。（注意哦，这可不是网络搜索结果，就是我记着的一些大概情况，仅供参考呀）
来源：菜鸟教程 - http://www.runoob.com/ml/ml-tutorial.html
具体信息：机器学习（Machine Learning）是人工智能（AI）的一个分支，它使计算机系统能够利用数据和算法自动学习和改进其性能。机器学习是让机器通过经验（数据）来做决策和预测。
来源：《如何学习机器学习》 - https://qiankunli.github.io/2019/08/23/learn_machine_learning.html
具体信息：学习路线与材料方面，如果以理论为中心，要扎扎实实从数学基础开始，把数据科学、机器学习大基础夯实，然后顺势向上学习Deep Learning，再往前既可以做研究，也可以做其他相关拓展。其中提到需要重点温习的包括向量、线性空间、线性方程组、矩阵、矩阵运算及其性质、向量微积分等数学知识。当提到Jacobian矩阵和Hessian矩阵的时候，得知道确切的数学形式；当给出一个相关数学场景，要能有对应的理解。另外还提到学会python就行，R也可以用用，还有英语起码能基本的听和读也是有帮助的。
来源：谷歌开发者 - https://developers.google.com/machine-learning/crash-course?hl=zh-cn
具体信息：这是Google提供的快节奏、实用的机器学习简介课程，包含一系列包含视频讲座、互动式可视化内容和实操练习的课程，可以帮助你快速入门机器学习的一些基础知识哦。
二、进阶学习相关（在有了一定基础后，适合深入学习具体算法、应用实践等方面的内容）

来源：《机器学习实践案例》 - https://zhuanlan.zhihu.com/p/27283616
具体信息：介绍了一种利用深度学习实现的图片识别案例，这种功能可以应用到图片的检黄、人脸识别、物体检测等各个领域。并且提到了可以通过阿里云机器学习平台产品等来进行相关实践操作哦。
来源：ShowMeAI - https://www.showmeai.tech/article-detail/202
具体信息：在前面的机器学习案例中，使用了Python机器学习工具库Scikit-Learn ，它建立在NumPy、SciPy、Pandas和Matplotlib之上，也是最常用的Python机器学习库之一。文章通过具体案例讲解了相关应用实践过程呢。
来源：《神经网络应用领域》 - https://cloud.google.com/discover/what-is-a-neural-network?hl=zh-CN
具体信息：介绍了神经网络应用广泛，包括图像识别（图像中的物体识别可用在汽车自动驾驶、社交媒体平台和医疗诊断等应用场景）、自然语言处理(NLP)（可以实现机器翻译、文本总结和情感分析，为谷歌翻译和聊天机器人等工具提供支持）、金融建模、医疗诊断、机器人学、Self-driving vehicles、欺诈检测、垃圾数据过滤等诸多领域哦。
来源：《怎样掌握神经网络》 - https://zhuanlan.zhihu.com/p/392363532
具体信息：讲解了一些神经网络训练技巧，比如首先输入单个数据批次，并且保证这个batch数据对应的标签是正确的（如果需要标签的话），然后重复在这个batch数据上进行训练，直到损失函数数值达到稳定等内容，有助于深入掌握神经网络的训练环节呢。
目前网络搜索agent的状态是：已经全部完成搜索任务并成功返回了结果哦，你可以放心参考这些内容啦，要是在学习过程中有啥新的疑问，随时说哈。
```

>通过各节点同时多进程生成关键词,抓取网络信息
>达成短时间内快速广泛地收集互联网上的信息的效果，
>从以上示例可以看出来经过了深度搜索反馈的结果配合上主节点的分析整理能力极大地减少了大模型的幻觉问题，使大模型提供的内容更加可信精准

### 案例三

**用户：**
```markdown
我想了解下注意力机制
```

**who_knows(最终汇总结果)：**

```markdown
好啦，关于注意力机制的搜索结果已经来啦，来看看吧。

排序方案：我先给你呈现一些比较通俗易懂的基础介绍内容，让你能快速对注意力机制有个大概的认识，然后是一些涉及具体应用和技术细节的内容，最后再给出一些相关的代码资源等，方便你循序渐进地深入了解。

具体搜索结果如下：

基础介绍类
标题：注意力机制- 维基百科，自由的百科全书
链接：https://zh.wikipedia.org/zh-cn/%E6%B3%A8%E6%84%8F%E5%8A%9B%E6%9C%BA%E5%88%B6
简介：介绍了注意力机制是人工神经网络中一种模仿认知注意力的技术，它可以增强神经网络输入数据中某些部分的权重，同时减弱其他部分的权重，以此将网络的关注点聚焦于数据中最重要的一小部分。还提到可以通过梯度下降法对注意力机制进行训练。
标题：一文搞定注意力机制（Attention） 原创 - CSDN博客
链接：https://blog.csdn.net/weixin_42110638/article/details/134011134
简介：将注意力机制类比人类的神经系统处理复杂感知信息的方式，即通过选择性关注和集中注意力来处理特定刺激，帮助过滤掉不相关或无用的信息。基于注意力机制的深度学习，核心在于让机器学会去感知数据中的重要和不重要的部分。
标题：注意力机制（attention）和自注意力机制（self-attention）的学习总结
链接：https://blog.csdn.net/weixin_43610114/article/details/126684999
简介：指出注意力机制源自于人对于外部信息的处理能力，由于人接受的信息庞大复杂远超人脑处理能力，所以人会有选择性地关注信息，该机制就是模拟这种能力，而自注意力机制在同一个模型中可以使用多次，作为网络结构的一部分。
原理及应用类
标题：注意力机制（Attention mechanism）基本原理详解及应用 - 博客园
链接：https://www.cnblogs.com/jins-note/p/13056604.html
简介：先以视觉注意力机制是人类视觉所特有的大脑信号处理机制为例，阐述人类视觉会先快速扫描全局图像获得需重点关注的目标区域，即注意力焦点，而后对其重点处理。接着说明注意力模型在深度学习各个领域如图像处理、语音识别、自然语言处理等各种任务中被广泛使用。
标题：一文看懂Attention（本质原理+3大优点+5大类型）
链接：https://easyaitech.medium.com/%E4%B8%80%E6%96%87%E7%9C%8B%E6%87%82-attention-%E6%9C%AC%E8%B4%A8%E5%8E%9F%E7%90%86-3%E5%A4%A7%E4%BC%98%E7%82%B9-5%E5%A4%A7%E7%B1%BB%E5%9E%8B-e4fbe4b6d030
简介：通过将Attention机制类比人类看图片的逻辑，即不会看清图片全部内容而是聚焦在焦点上，来解释其本质原理。还提到该机制最早在计算机视觉里应用，随后在NLP领域发扬光大，以及它的一些优点和类型等，并介绍了其在不同领域的应用情况。
标题：注意力机制在医学上的应用综述 - 汉斯出版社
链接：https://www.hanspub.org/journal/paperinformation?paperid=58869
简介：文章介绍了注意力机制并总结了其在医学上的主要应用，包括医学图像检测与分割、医学图像分类、疾病预测、行为识别等方面，说明了在医学领域引入注意力机制的意义和作用。
代码及资源类
标题：datalogue/keras-attention - GitHub
链接：https://github.com/datalogue/keras-attention
简介：提供了在Keras中带有注意力机制的自定义RNN层的实现和可视化，用于翻译日期等任务，还给出了设置仓库、创建数据集、运行模型等的具体操作步骤和相关参数说明。
标题：uzaymacar/attention-mechanisms - GitHub
链接：https://github.com/uzaymacar/attention-mechanisms
简介：包含了一系列注意力机制的自定义层实现，兼容TensorFlow和Keras集成，可用于多种自然语言处理任务如情感分类、文本生成、机器翻译等，还介绍了不同类型的注意力机制及相关的对齐函数等内容。
标题：xmu-xiaoma666/External-Attention-pytorch - GitHub
链接：https://github.com/xmu-xiaoma666/External-Attention-pytorch
简介：致力于实现一个既能让深度学习小白也能搞懂，又能服务科研和工业社区的代码库，包含了多种注意力机制相关的模块，如External Attention、Self Attention等的使用示例，可通过pip安装或克隆仓库的方式使用。
```

> 多元搜索结果有机结合，由浅及深
> 排除传统搜索会遇到的大量干扰信息直达权威信源
> 后期可根据需要动态扩充信息源节点
> 多进程的信息搜索使搜索响应时间无限接近常数

---

## 团队介绍
### 团队分工

- 胡宇桥：负责所有agent的代码编写和最终应用调试作业、markdown文档主要撰写者。
- 杨淏森：负责模型的提示词工程，搜索爬虫实现及测试，markdown文档撰写者。

## 鸣谢

- [Mofa](https://github.com/moxin-org/mofa)
- [吴宗寰老师](https://china2024.gosim.org/zh/speakers/zonghuan-wu)
- [陈成老师](https://github.com/chengzi0103)
- [赵志举老师](https://github.com/ketty-zzj)
- [阿图教育]

