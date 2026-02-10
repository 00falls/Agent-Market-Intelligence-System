# 基于 Agent 的互联网竞品情报自动化监测系统

## 一、项目背景（Why）

在 AI 产品 / 运营 / 策略分析工作中，**竞品调研**是一项高频但低效的任务：
- 信息来源分散（媒体报道、用户评价、评测文章）
- 依赖人工搜索与筛选，耗时长、重复劳动多
- 非结构化文本难以快速转化为可决策的信息

为此，本项目尝试引入 **LLM + Agent（智能体）机制**，构建一套可自动完成  
**“信息搜索 → 内容读取 → 归纳分析 → 结构化输出”** 的竞品情报自动化系统，  
用于验证 **Agent 在真实商业情报场景中的落地可行性**。

---

## 二、目标用户与使用场景（Who & When）

**目标用户**
- AI 产品经理 / 策略产品经理
- 数据运营 / AI 运营
- 需要进行竞品分析的产品或市场人员

**典型使用场景**
- 快速了解某竞品在特定维度（如用户体验、商业化模式）的最新表现
- 替代人工完成初步竞品信息收集与整理
- 为后续人工深度分析提供结构化参考材料

---

## 三、系统整体架构（How）

```mermaid
graph TD
    %% 定义样式类
    classDef user fill:#FF6B6B,stroke:#333,stroke-width:2px,color:white,font-weight:bold;
    classDef ui fill:#4ECDC4,stroke:#2A9D8F,stroke-width:2px,color:white;
    classDef brain fill:#FFE66D,stroke:#D4A373,stroke-width:2px,color:#333;
    classDef tools fill:#1A535C,stroke:#333,stroke-width:0px,color:white;
    classDef data fill:#F7FFF7,stroke:#333,stroke-dasharray: 5 5;

    %% 1. 用户交互层
    subgraph User_Layer ["💻 用户交互层 (Streamlit Frontend)"]
        User((🙍‍♂️ 用户 User))
        Input["📝 输入: 竞品名称 + 分析维度"]
        Display["🖥️ 界面展示: 实时思考日志 + Markdown 简报"]
    end

    %% 2. 核心决策层
    subgraph Agent_Layer ["🧠 Agent 核心决策层 (LangChain + DeepSeek)"]
        direction TB
        Agent{{"🤖 ReAct 智能体"}}
        Memory[("思维链 Log")]
        Prompt["结构化 Prompt"]
        
        %% LLM 交互
        LLM["⚡ DeepSeek V3 API"]
    end

    %% 3. 工具执行层
    subgraph Tool_Layer ["🛠️ 工具执行层 (Tools)"]
        Search["🔍 Tavily 联网搜索"]
        Scrape["📄 网页内容抓取 & 清洗"]
    end

    %% 4. 数据源
    World((🌐 互联网实时数据))

    %% 连线逻辑
    User --> Input
    Input --> Agent
    
    %% ReAct 循环逻辑
    Agent -- "1. 任务拆解 & 推理" --> LLM
    LLM -- "返回行动计划" --> Agent
    
    Agent -- "2. 调用工具" --> Search
    Agent -- "2. 调用工具" --> Scrape
    
    Search <--> World
    Scrape <--> World
    
    Search -- "返回搜索摘要" --> Agent
    Scrape -- "返回网页全文" --> Agent

    %% 输出逻辑
    Agent -- "3. 实时日志流 (Stream)" --> Display
    Agent -- "4. 最终分析报告" --> Display

    %% 应用样式
    class User user;
    class Input,Display ui;
    class Agent,LLM,Prompt brain;
    class Search,Scrape tools;
    class World,Memory data;

## 四、核心功能模块（What）

### 1. Agent 决策与工具调用
- 基于 **ReAct（Reasoning + Acting）范式** 构建智能体
- Agent 可根据任务需要，自主决定：
  - 是否进行联网搜索
  - 是否读取具体网页内容
- 支持多轮思考与工具调用，避免一次性 Prompt 的信息不足问题

### 2. 实时联网搜索与内容抓取
- 使用 Tavily Search 获取最新互联网信息
- 对网页内容进行清洗与截断，降低噪声与无效信息干扰

### 3. 思维链（Chain of Thought）可视化
- 在前端实时展示 Agent 的思考与工具调用日志
- 提升 B 端用户对模型决策过程的**可解释性与信任感**

### 4. 结构化竞品分析报告输出
- 自动生成 Markdown 格式竞品分析简报
- 输出内容包含：
  - 核心结论
  - 市场 / 用户表现
  - Top 3 优缺点总结
- 支持一键导出，便于复用与沉淀

---

## 五、技术选型说明（Tech Stack）

- **大模型**：DeepSeek API（中文理解能力强，适合商业情报场景）
- **Agent 框架**：LangChain + LangGraph（ReAct 范式）
- **搜索工具**：Tavily Search（实时联网能力）
- **前端展示**：Streamlit（快速构建 B 端 MVP）
- **输出格式**：Markdown（结构化、可复用）

---

## 六、项目价值与实践意义（Value）

- 从 0 到 1 验证了 **Agent 在竞品分析场景中的可用性**
- 将原本高度依赖人工的竞品调研流程，转化为可自动化执行的工作流
- 体现了将 LLM 技术转化为 **业务生产力工具** 的实践能力
- 项目以 MVP 形态完成，具备进一步扩展为企业级情报系统的可能性

---

## 七、后续可扩展方向（Future Work）

- 引入数据库或向量库，实现历史竞品分析结果的沉淀与复用
- 设计多 Agent 协作机制（搜索 Agent / 分析 Agent / 评估 Agent）
- 增加定时任务，实现竞品动态的自动追踪与推送
- 接入更多数据源（如应用商店评论、社交媒体舆情）

---

## 八、运行方式（Local）

```bash
pip install -r requirements.txt
streamlit run app.py
