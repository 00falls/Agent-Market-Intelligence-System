# app.py
# ================= 前端交互层（B 端） =================
# 本文件负责竞品分析系统的用户交互与结果展示
# 设计目标：以最小成本构建一个可用于验证 AI 产品流程的 B 端 MVP
import streamlit as st
import time
import io
import sys
import contextlib

# 导入后端逻辑 (确保 agent_backend.py 在同一目录下)
try:
    from agent_backend import run_competitor_analysis
except ImportError:
    st.error("❌ 错误：找不到 agent_backend.py，请检查文件目录结构。")
    st.stop()

# ================= 1. 页面配置 (UI Design) =================
st.set_page_config(
    page_title="DeepSeek 竞品情报监测系统",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #4B4B4B; font-weight: 700;}
    .sub-header {font-size: 1.2rem; color: #666;}
    .stButton>button {width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white;}
    .report-box {border: 1px solid #ddd; padding: 20px; border-radius: 10px; background-color: #f9f9f9;}
</style>
""", unsafe_allow_html=True)

# ================= 2. 侧边栏：任务配置区 =================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/bot.png", width=80)
    st.title("监测配置台")
    st.markdown("---")
    
    # 2.1 用户输入：竞品名称
    competitor = st.text_input(
        "🔍 目标竞品名称",
        value="Kimi智能助手",
        placeholder="例如：美团、拼多多、DeepSeek"
    )
    
    # 2.2 用户输入：分析维度
    dimension_options = [
        "长文本处理与用户体验",
        "最新负面评价与槽点",
        "商业化变现模式",
        "核心功能迭代路径",
        "自定义输入..."
    ]
    selected_dimension = st.selectbox("维度选择", dimension_options)
    
    # 如果选择自定义，弹出文本框
    if selected_dimension == "自定义输入...":
        focus_topic = st.text_input("请输入自定义分析维度", value="市场占有率与增长策略")
    else:
        focus_topic = selected_dimension
        
    st.markdown("---")
    st.info("💡 **提示**：DeepSeek Agent 将自动联网搜索最新信息并生成报告。")
    
    # 2.3 开始按钮
    btn_start = st.button("🚀 开始自动化分析")

# ================= 3. 主界面：执行与展示 =================

st.markdown('<p class="main-header">🕵️‍♂️ 互联网竞品情报自动化监测系统</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">当前任务：分析 <b>{competitor}</b> 的 <b>{focus_topic}</b></p>', unsafe_allow_html=True)
st.divider()

if btn_start:
    if not competitor or not focus_topic:
        st.warning("⚠️ 请先在左侧完善竞品名称和分析维度。")
        st.stop()

    # --- 核心逻辑：捕获 Agent 思考过程并执行 ---
    
    # 创建两个容器：一个放进度条，一个放最终报告
    status_container = st.status("🤖 Agent 正在工作中...", expanded=True)
    report_container = st.empty()
    
    # 捕获 print 输出的“黑科技”
    # 交互层关键设计：
    # 实时捕获 Agent 的思考与工具调用日志（Chain of Thought）
    # 用于在模型执行期间向用户展示决策过程，
    # 降低大模型“黑盒感”，提升 B 端用户对系统的信任度
    log_output = io.StringIO()
    
    try:
        # 状态反馈设计：
        # 通过阶段性文案与进度提示，缓解用户在模型推理期间的等待焦虑，
        # 提升整体交互体验
        with status_container:
            st.write("正在连接 DeepSeek V3 大脑...")
            time.sleep(1) # 模拟连接延迟，增加真实感
            
            st.write("正在调用 Tavily 搜索最新互联网数据...")
            
            # 🔄 实时捕获标准输出 (stdout)
            # 这样你在 agent_backend.py 里 print 的内容都会显示在界面上
            with contextlib.redirect_stdout(log_output):
                final_report = run_competitor_analysis(competitor, focus_topic)
            
            # 将捕获到的日志显示在折叠面板里 (Agent 思考链可视化)
            st.text_area("🧠 Agent 思考链日志 (ReAct Trace)", value=log_output.getvalue(), height=200)
            
            st.write("✅ 分析完成！正在生成简报...")
            status_container.update(label="✨ 分析完成", state="complete", expanded=False)

        # --- 结果展示 ---
        if "❌" in final_report:
            st.error(final_report) # 如果后端报错，前端显示红色错误条
        else:
            # 使用 Markdown 渲染报告
            with report_container.container():
                st.markdown("### 📝 最终分析简报")
                st.markdown('<div class="report-box">', unsafe_allow_html=True)
                st.markdown(final_report)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # --- 导出功能 ---
                st.download_button(
                    label="📥 导出为 Markdown 报告",
                    data=final_report,
                    file_name=f"{competitor}_{focus_topic}_分析报告.md",
                    mime="text/markdown"
                )

    except Exception as e:
        st.error(f"系统发生未预期的错误: {str(e)}")

else:
    # 默认空状态页
    st.info("👈 请在左侧侧边栏输入信息，点击“开始自动化分析”启动任务。")
    
    # 展示一下支持的能力 (凑版面，显得专业)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🌐 全网实时搜索")
        st.caption("基于 Tavily 搜索2026最新数据")
    with col2:
        st.markdown("#### 🧠 深度逻辑推理")
        st.caption("DeepSeek V3 驱动的 ReAct 决策链")
    with col3:
        st.markdown("#### 📄 结构化输出")
        st.caption("自动生成 Markdown 格式的决策简报")