# agent_backend.py
import os
import warnings


warnings.filterwarnings("ignore")

# ================= Agent 决策层 =================
# 本文件负责系统核心智能体（Agent）的初始化与任务执行
# 角色定位：作为产品的“决策大脑”，负责理解用户目标、拆解任务并调度工具
from langchain_openai import ChatOpenAI


try:
    # 新版 langchain 1.2.x：从 langgraph 体系导入
    from langgraph.prebuilt import create_react_agent
except ImportError:
    try:
        # 旧版 langchain 0.x：从 langchain.agents 导入
        from langchain.agents import create_react_agent
    except ImportError:
        print("❌ 错误：无法导入 create_react_agent，请检查 langchain 或 langgraph 版本")
        exit()

#从tools.py 中导入工具加载函数
try:
    from tool import get_tools_list
except ImportError:
    print("❌ 错误：找不到 tools.py！请确保它在当前目录下。")
    exit()

# ================= 配置区域 =================
DEEPSEEK_API_KEY = "sk-"

# ================= 核心逻辑 =================
def init_agent():
    """
    Agent 系统初始化函数（系统级入口）

    职责说明：
    - 组装 Agent 的「决策大脑」（LLM）
    - 挂载 Agent 可调用的外部工具（搜索 / 网页读取）
    - 构建基于 ReAct 范式的任务决策与执行流程

    该函数对应产品架构中的「智能决策层」。
    """
    # 1. 加载工具 (The Hands)
    tools = get_tools_list()

    # 2. 加载大模型 (The Brain) - DeepSeek 适配版
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
        temperature=0,
        max_tokens=4000
    )

    # 3. 核心决策逻辑构建
    # 基于 ReAct（Reasoning + Acting）范式创建 Agent：
    # - Reasoning：让模型先思考“需要做什么”
    # - Acting：再自主决定是否调用搜索 / 网页读取等工具
    # 该机制适用于竞品分析这类「信息不确定、多步骤」的业务场景
    #    新版 create_react_agent 直接返回一个可执行的 agent，不再需要 hub.pull prompt
    print("⏳ 正在组装 Agent...")
    agent_executor = create_react_agent(llm, tools)

    return agent_executor

# ================= 任务执行入口 =================
def run_competitor_analysis(competitor_name: str, focus_topic: str):
    """
    执行竞品分析任务的主函数
    """
    """
    竞品情报分析的核心业务流程入口

    业务流程说明：
    1. 接收用户定义的竞品名称与分析维度
    2. 由 Agent 自主拆解分析任务
    3. 根据需要调用搜索与网页读取工具获取外部信息
    4. 汇总分析结果并输出结构化的竞品分析简报（Markdown）

    该函数作为前端（Streamlit）与 Agent 系统之间的唯一业务接口。
    """
    query = (
        f"## 角色设定\n你是一名资深的互联网商业分析师，擅长通过数据挖掘进行竞品调研。\n\n"
        f"## 任务目标\n请深入分析竞品【{competitor_name}】在【{focus_topic}】维度的表现。\n\n"
        f"## 执行动作\n"
        f"1. Search: 利用搜索工具查找2024-2025年的最新用户评价、媒体报道及官方发布。\n"
        f"2. Read: 遇到高价值网页（如深度测评、财报分析）必须读取全文。\n"
        f"3. Analyze: 提炼核心优劣势，排除营销号软文干扰。\n\n"
        f"## 输出要求\n"
        f"请以结构化的 Markdown 简报格式输出，包含：'核心结论'、'市场表现'、'Top3 优缺点'。"
    )

    print(f"\n🚀 Agent 启动！目标：分析 {competitor_name} - {focus_topic}")

    try:
        agent_executor = init_agent()

        # 新版 langgraph 的 create_react_agent 返回的是一个 graph
        # 调用方式使用 invoke，输入格式为 {"messages": [...]}
        from langchain_core.messages import HumanMessage
        result = agent_executor.invoke({"messages": [HumanMessage(content=query)]})

        # 提取最终输出：最后一条消息的内容
        final_message = result["messages"][-1]
        return final_message.content

    except Exception as e:
        return f"❌ 任务执行中断: {str(e)}"

# ================= 本地测试代码 =================
if __name__ == "__main__":
    if "sk-" not in DEEPSEEK_API_KEY:
        print("❌ 错误：请在配置区域填入 DeepSeek API Key")
        exit()

    target_competitor = "Kimi智能助手"
    topic = "长文本处理与用户体验"

    final_report = run_competitor_analysis(target_competitor, topic)

    print("\n" + "=" * 30)
    print("📝 最终分析报告")
    print("=" * 30)
    print(final_report)