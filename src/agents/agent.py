"""
数据分析与报表生成Agent
支持文档问答、SQL生成、图表推荐、报表生成
"""
import os
import json
import logging
from typing import Annotated, Dict, Any, List, Optional
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from coze_coding_utils.runtime_ctx.context import default_headers, Context, new_context

from storage.memory.memory_saver import get_memory_saver
from tools import (
    extract_text_from_file,
    parse_natural_language_to_sql,
    analyze_data_and_recommend_charts,
    generate_comprehensive_report,
    generate_mock_data,
    generate_mock_script,
    format_sql_output,
    format_chart_recommendations,
    format_report_output,
    format_mock_data_output,
    generate_install_script,
    generate_requirements_txt,
    generate_api_documentation,
    get_mock_data_info
)
from tools.document_parser import get_file_info
from tools.chart_recommender import ChartRecommendation

logger = logging.getLogger(__name__)

# 配置文件路径
LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40


def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    merged = add_messages(old, new)
    # 确保返回的是列表
    if not isinstance(merged, list):
        merged = list(merged) if merged else []
    return merged[-MAX_MESSAGES:]


class AgentState(MessagesState):
    """Agent状态管理"""
    pass


def build_agent(ctx: Context = None):
    """
    构建数据分析Agent
    
    Returns:
        配置好的Agent实例
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)

    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 获取API配置
    api_key = os.getenv("LLM_API_KEY") or os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("LLM_BASE_URL") or os.getenv("COZE_INTEGRATION_MODEL_BASE_URL", "https://api.deepseek.com")

    # 创建LLM实例
    llm = ChatOpenAI(
        model=cfg['config'].get("model", "deepseek-v3-2-251201"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )

    # 创建Agent
    agent = create_agent(
        model=llm,
        system_prompt=cfg.get("sp", ""),
        tools=[
            analyze_document,
            generate_sql,
            recommend_charts,
            generate_report,
            generate_mock_data_tool,
            generate_env_scripts
        ],
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )

    return agent


def _parse_llm_response(response_content: Any) -> str:
    """解析LLM响应内容"""
    if isinstance(response_content, str):
        return response_content.strip()
    elif isinstance(response_content, list):
        if response_content and isinstance(response_content[0], str):
            return " ".join(response_content).strip()
        else:
            text_parts = [
                item.get("text", "") 
                for item in response_content 
                if isinstance(item, dict) and item.get("type") == "text"
            ]
            return " ".join(text_parts).strip()
    return str(response_content)


# ==================== 工具定义 ====================

def analyze_document(file_path: str, query: str = "") -> str:
    """
    解析文档内容并回答问题
    
    Args:
        file_path: 文档路径或URL
        query: 用户查询问题
        
    Returns:
        解析后的文档内容和问答结果
    """
    try:
        # 提取文档内容
        content = extract_text_from_file(file_path)
        
        if not content or content.startswith("[解析失败]"):
            return f"文档解析失败: {content}"
        
        # 获取文件信息
        file_info = get_file_info(file_path)
        
        # 构建结果
        result = {
            "status": "success",
            "file_name": file_info.get("file_name", "unknown"),
            "content_preview": content[:2000] if len(content) > 2000 else content,
            "content_length": len(content),
            "query": query,
            "analysis": ""
        }
        
        # 如果有查询，进行简要分析
        if query:
            result["analysis"] = f"基于文档内容，已准备好回答与「{query}」相关的问题。文档包含{len(content)}个字符。"
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"文档分析失败: {e}")
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False)


def generate_sql(
    query: str,
    schema: str = "",
    tables: str = ""
) -> str:
    """
    根据自然语言生成SQL查询语句
    
    Args:
        query: 自然语言查询
        schema: 数据库表结构（可选）
        tables: 使用的表名列表（可选）
        
    Returns:
        SQL生成结果
    """
    try:
        # 解析表名列表
        table_list = []
        if tables:
            table_list = [t.strip() for t in tables.split(",")]
        
        # 生成SQL
        result = parse_natural_language_to_sql(
            query=query,
            schema=schema,
            available_tables=table_list
        )
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"SQL生成失败: {e}")
        return json.dumps({
            "sql_status": "failed",
            "sql_error": str(e),
            "sql_fix_suggestion": "请检查查询语句的语法"
        }, ensure_ascii=False)


def recommend_charts(
    data_type: str = "sales",
    dimensions: str = "region",
    metrics: str = "sales_amount",
    query: str = ""
) -> str:
    """
    根据数据特征推荐图表
    
    Args:
        data_type: 数据类型
        dimensions: 维度字段
        metrics: 指标字段
        query: 用户查询（用于上下文理解）
        
    Returns:
        推荐的图表配置
    """
    try:
        # 解析字段列表
        dim_list = [d.strip() for d in dimensions.split(",")]
        met_list = [m.strip() for m in metrics.split(",")]
        
        # 构造数据对象
        data = {
            "dimensions": dim_list,
            "metrics": met_list,
            "values": []  # 实际值由后续查询填充
        }
        
        # 分析并推荐图表
        recommendations = analyze_data_and_recommend_charts(
            data=data,
            query=query,
            existing_sql=""
        )
        
        # 转换为输出格式
        charts_output = []
        for rec in recommendations:
            charts_output.append({
                "type": rec.type,
                "title": rec.title,
                "description": rec.description,
                "echarts_option": rec.echarts_option
            })
        
        return json.dumps({
            "status": "success",
            "charts": charts_output,
            "count": len(charts_output)
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"图表推荐失败: {e}")
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False)


def generate_report(
    query: str,
    sql_result: str = "",
    charts_data: str = "",
    format: str = "markdown"
) -> str:
    """
    生成数据报表
    
    Args:
        query: 报表主题/查询
        sql_result: SQL查询结果（JSON字符串）
        charts_data: 图表数据（JSON字符串）
        format: 输出格式 (markdown/json)
        
    Returns:
        生成的报表内容
    """
    try:
        # 解析SQL结果
        sql_data = {}
        if sql_result:
            try:
                sql_data = json.loads(sql_result)
            except json.JSONDecodeError:
                sql_data = {"query_sql": sql_result, "sql_status": "unknown"}
        
        # 解析图表数据
        charts = []
        if charts_data:
            try:
                charts = json.loads(charts_data)
                if isinstance(charts, dict) and "charts" in charts:
                    charts = charts["charts"]
            except json.JSONDecodeError:
                charts = []
        
        # 生成报表
        report = generate_comprehensive_report(
            sql_result=sql_data,
            charts=charts,
            query=query
        )
        
        # 根据格式返回
        if format == "json":
            return report.get("json", "")
        else:
            return report.get("markdown", "")
        
    except Exception as e:
        logger.error(f"报表生成失败: {e}")
        return f"报表生成失败: {str(e)}"


def generate_mock_data_tool(
    data_type: str = "sales",
    row_count: int = 100
) -> str:
    """
    生成Mock测试数据
    
    Args:
        data_type: 数据类型 (sales/customers/products/orders)
        row_count: 数据行数
        
    Returns:
        Mock数据内容
    """
    try:
        # 生成数据
        csv_data = generate_mock_data(
            data_type=data_type,
            row_count=row_count
        )
        
        # 生成脚本
        script = generate_mock_script(
            data_type=data_type,
            output_file=f"mock_{data_type}_data.csv",
            row_count=row_count
        )
        
        return json.dumps({
            "status": "success",
            "data_type": data_type,
            "row_count": row_count,
            "data_preview": "\n".join(csv_data.split("\n")[:6]),
            "script": script,
            "data_info": get_mock_data_info()
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Mock数据生成失败: {e}")
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False)


def generate_env_scripts() -> str:
    """
    生成环境安装脚本和配置文件
    
    Returns:
        包含所有脚本的字典
    """
    try:
        scripts = {
            "install_env.sh": generate_install_script(),
            "requirements.txt": generate_requirements_txt(),
            "api.md": generate_api_documentation()
        }
        
        return json.dumps({
            "status": "success",
            "files": list(scripts.keys()),
            "content": scripts
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"环境脚本生成失败: {e}")
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False)


# ==================== Agent入口函数 ====================

def run_agent(
    user_input: str,
    ctx: Context = None,
    file_path: str = None
) -> str:
    """
    运行Agent处理用户请求
    
    Args:
        user_input: 用户输入
        ctx: 上下文
        file_path: 可选的文件路径
        
    Returns:
        Agent响应
    """
    if ctx is None:
        ctx = new_context(method="agent_run")

    agent = build_agent(ctx)

    # 构建输入
    if file_path:
        # 有文件上传的情况
        input_data = {
            "messages": [
                HumanMessage(content=f"{user_input}\n\n[附加文件: {file_path}]")
            ]
        }
    else:
        input_data = {
            "messages": [
                HumanMessage(content=user_input)
            ]
        }

    # 运行Agent
    try:
        result = agent.invoke(input_data, config={"configurable": {"thread_id": ctx.run_id}})
        
        # 提取响应
        if result and "messages" in result:
            last_message = result["messages"][-1]
            if isinstance(last_message, AIMessage):
                return _parse_llm_response(last_message.content)
        
        return str(result)
        
    except Exception as e:
        logger.error(f"Agent运行失败: {e}")
        return f"处理失败: {str(e)}"


# ==================== 便捷函数 ====================

def quick_analyze(
    query: str,
    data_type: str = "sales",
    include_charts: bool = True,
    include_report: bool = True
) -> Dict[str, Any]:
    """
    快速分析 - 一键完成查询、图表、报表
    
    Args:
        query: 分析查询
        data_type: 数据类型
        include_charts: 是否生成图表
        include_report: 是否生成报表
        
    Returns:
        完整分析结果
    """
    # 1. 生成SQL
    sql_result = parse_natural_language_to_sql(query)
    
    # 2. 推荐图表
    charts = []
    if include_charts:
        recommendations = analyze_data_and_recommend_charts(
            data={"dimensions": ["region"], "metrics": ["value"]},
            query=query
        )
        charts = [
            {
                "type": r.type,
                "title": r.title,
                "echarts_option": r.echarts_option
            }
            for r in recommendations
        ]
    
    # 3. 生成报表
    report = None
    if include_report:
        report = generate_comprehensive_report(
            sql_result=sql_result,
            charts=charts,
            query=query
        )
    
    return {
        "sql": sql_result,
        "charts": charts,
        "report": report
    }
