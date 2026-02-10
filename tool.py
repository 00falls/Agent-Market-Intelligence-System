# tools.py
# ================= Agent 工具层 =================
# 本文件定义 Agent 可调用的外部能力（搜索 / 网页读取）
# 工具以“能力模块”的形式暴露给 Agent，而非直接写死在决策逻辑中
import os
import warnings


my_tavily_key = "tvly-" 

# 将 Key 设置到环境变量
os.environ["TAVILY_API_KEY"] = my_tavily_key


warnings.filterwarnings("ignore")


from langchain_community.tools import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import Tool

# ================= 1. 定义搜索工具 (Eye) =================
def get_search_tool():
    """
    初始化搜索工具。
    使用 Tavily 社区版接口，稳定可靠。
    """
    # k=5 表示每次搜索返回 5 条最相关的结果
    return TavilySearchResults(k=5)

# ================= 2. 定义网页抓取工具 (Hand) =================
def scrape_web_content(url: str) -> str:
    """
    用于读取具体网页的详细内容。
    DeepSeek 适配版：增加了去噪和截断逻辑。
    """
    """
    网页内容读取与清洗工具

    设计目的：
    - 为 Agent 提供高质量、低噪声的外部信息输入
    - 通过内容清洗与长度截断，降低无关信息对模型推理的干扰
    - 控制上下文长度，提升整体推理稳定性
    """
    try:
        print(f"🕵️ Agent 正在抓取: {url} ...") 
        
        # 伪装成浏览器（User-Agent）
        # 这里模拟一个标准的 Windows Chrome 浏览器
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        loader = WebBaseLoader(url, header_template=headers)
        docs = loader.load()
        
        if not docs:
            return "❌ 未抓取到内容，可能是网页反爬或为空。"

        content = docs[0].page_content
        
        # --- DeepSeek 适配优化 ---
        # 1. 清洗多余的换行符和空格
        cleaned_content = " ".join(content.split())
        
        # 2. 强制截断 (保留前 4000 字符)
        max_length = 4000
        if len(cleaned_content) > max_length:
            return cleaned_content[:max_length] + "...(内容过长已截断)"
        
        return cleaned_content

    except Exception as e:
        return f"❌ 读取网页失败，错误信息: {str(e)}"

# ================= 3. 工具导出 =================
def get_tools_list():
    """
    返回所有工具的列表，供 Agent 绑定使用。
    """
    search_tool = get_search_tool()
    
    tools = [
        Tool(
            name="web_search",
            func=search_tool.invoke, 
            description="当需要了解最新的市场动态、竞品新闻、实时用户评价时使用。输入应为搜索关键词。"
        ),
        Tool(
            name="read_web_page",
            func=scrape_web_content,
            description="当需要深入阅读某个具体网页的详细内容时使用。输入必须是一个 http 开头的 URL。"
        )
    ]
    return tools

# ================= 测试代码 =================
if __name__ == "__main__":
    print("🚀 开始测试工具集 (DeepSeek适配 + 稳定版)...")
    
    # 简单的 Key 检查
    if "tvly-" not in my_tavily_key:
        print("\n❌ 错误：请填写正确的 Tavily API Key！")
        exit()

    # 1. 测试搜索能力
    print("\n--- 测试 1: 联网搜索 'Kimi智能助手 评价' ---")
    try:
        search = get_search_tool()
        results = search.invoke("Kimi智能助手 2025年 用户评价")
        
        if results:
            print(f"✅ 搜索成功！返回了 {len(results)} 条结果。")
            print(f"🔍 第一条结果: {str(results[0])[:100]}...")
        else:
            print("⚠️ 搜索成功但无结果返回 (可能是关键词太偏)。")
            
    except Exception as e:
        print(f"❌ 搜索失败: {e}")

    # 2. 测试抓取能力
    print("\n--- 测试 2: 抓取网页内容 ---")
    test_url = "https://baike.baidu.com/item/人工智能/9180" 
    try:
        content = scrape_web_content(test_url)
        print(f"✅ 抓取成功，内容长度: {len(content)}")
    except Exception as e:
        print(f"❌ 抓取失败: {e}")