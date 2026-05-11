"""
工具模块 - 包含文档解析、SQL生成、图表推荐、报表生成等功能
"""
from .document_parser import extract_text_from_file, get_file_info
from .sql_generator import parse_natural_language_to_sql, generate_join_query, format_sql_output
from .chart_recommender import (
    analyze_data_and_recommend_charts,
    generate_all_charts_json,
    format_chart_recommendations,
    ChartType,
    ChartRecommendation
)
from .report_generator import (
    generate_comprehensive_report,
    generate_simple_report,
    format_report_output
)
from .mock_data_generator import (
    generate_mock_data,
    generate_mock_script,
    generate_all_mock_data,
    get_mock_data_info,
    format_mock_data_output
)
from .env_script_generator import (
    generate_install_script,
    generate_requirements_txt,
    generate_env_example,
    generate_docker_compose,
    generate_api_documentation,
    generate_all_scripts,
    format_env_script_output
)

__all__ = [
    # 文档解析
    "extract_text_from_file",
    "get_file_info",
    
    # SQL生成
    "parse_natural_language_to_sql",
    "generate_join_query",
    "format_sql_output",
    
    # 图表推荐
    "analyze_data_and_recommend_charts",
    "generate_all_charts_json",
    "format_chart_recommendations",
    "ChartType",
    "ChartRecommendation",
    
    # 报表生成
    "generate_comprehensive_report",
    "generate_simple_report",
    "format_report_output",
    
    # Mock数据
    "generate_mock_data",
    "generate_mock_script",
    "generate_all_mock_data",
    "get_mock_data_info",
    "format_mock_data_output",
    
    # 环境脚本
    "generate_install_script",
    "generate_requirements_txt",
    "generate_env_example",
    "generate_docker_compose",
    "generate_api_documentation",
    "generate_all_scripts",
    "format_env_script_output",
]
