"""
图表推荐工具 - 根据数据特征推荐合适的图表类型并生成ECharts配置
"""
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """支持的图表类型"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    AREA = "area"
    RADAR = "radar"
    DOUGHNUT = "doughnut"


@dataclass
class ChartRecommendation:
    """图表推荐结果"""
    type: str
    title: str
    description: str
    echarts_option: Dict[str, Any]
    suitable_for: List[str]
    alternatives: List[str]


def analyze_data_and_recommend_charts(
    data: Dict[str, Any],
    query: str = "",
    existing_sql: str = ""
) -> List[ChartRecommendation]:
    """
    分析数据特征并推荐合适的图表
    
    Args:
        data: SQL查询结果数据
        query: 用户原始查询
        existing_sql: 执行的SQL语句
        
    Returns:
        推荐的图表列表
    """
    recommendations = []
    
    # 分析数据特征
    data_type = _analyze_data_type(data)
    dimensions = data.get('dimensions', [])
    metrics = data.get('metrics', [])
    
    # 基于数据特征生成图表推荐
    if len(dimensions) == 1 and len(metrics) >= 1:
        # 单维度单指标 - 推荐柱状图或折线图
        recommendations.append(_create_bar_chart(dimensions, metrics, data))
        recommendations.append(_create_line_chart(dimensions, metrics, data))
        
        # 如果数据适合饼图
        if _is_suitable_for_pie(dimensions, metrics, data):
            recommendations.append(_create_pie_chart(dimensions, metrics, data))
    
    elif len(dimensions) == 0 and len(metrics) >= 1:
        # 只有指标数据 - 推荐指标卡或饼图
        recommendations.append(_create_indicator_card(data))
        if len(metrics) <= 3:
            recommendations.append(_create_pie_chart_simple(metrics, data))
    
    elif len(dimensions) >= 2 and len(metrics) >= 1:
        # 多维度 - 推荐堆叠图或组合图
        recommendations.append(_create_stacked_bar_chart(dimensions, metrics, data))
        recommendations.append(_create_line_chart(dimensions, metrics, data))
        
        # 如果有时间维度
        if any('date' in d.lower() or '时间' in d for d in dimensions):
            recommendations.append(_create_area_chart(dimensions, metrics, data))
    
    # 检查是否有地理数据
    if any('region' in d.lower() or '地区' in d or '城市' in d for d in dimensions):
        recommendations.append(_create_map_chart(dimensions, metrics, data))
    
    # 检查是否有相关性分析需求
    if '关系' in query or 'correlation' in query.lower() or '散点' in query:
        recommendations.append(_create_scatter_chart(dimensions, metrics, data))
    
    # 确保至少有一个推荐
    if not recommendations:
        recommendations.append(_create_default_chart(dimensions, metrics, data))
    
    return recommendations[:4]  # 最多返回4个推荐


def _analyze_data_type(data: Dict[str, Any]) -> str:
    """分析数据类型"""
    dimensions = data.get('dimensions', [])
    metrics = data.get('metrics', [])
    
    if not dimensions and metrics:
        return "metric_only"
    elif any('date' in d.lower() or '时间' in d for d in dimensions):
        return "time_series"
    elif any('region' in d.lower() or '地区' in d for d in dimensions):
        return "geographic"
    elif len(dimensions) == 1:
        return "categorical"
    else:
        return "multi_dimensional"


def _is_suitable_for_pie(dimensions: List[str], metrics: List[str], data: Dict[str, Any]) -> bool:
    """判断数据是否适合饼图"""
    # 饼图适合展示占比，且维度值不超过10个
    if len(dimensions) != 1:
        return False
    
    values = data.get('values', [[]])
    if values and len(values) <= 10:
        return True
    
    return False


def _create_bar_chart(dimensions: List[str], metrics: List[str], data: Dict[str, Any]) -> ChartRecommendation:
    """创建柱状图配置"""
    dim_col = dimensions[0] if dimensions else 'category'
    met_col = metrics[0] if metrics else 'value'
    
    # 生成示例数据
    sample_data = _generate_sample_data(dimensions, metrics)
    
    option = {
        "title": {
            "text": f"{dim_col} vs {met_col} 统计图",
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"}
        },
        "legend": {
            "data": [met_col],
            "top": 30
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": sample_data['categories'],
            "axisLabel": {"rotate": 0}
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "name": met_col,
            "type": "bar",
            "data": sample_data['values'],
            "itemStyle": {
                "color": "#5470C6"
            },
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }],
        "responsive": True,
        "animation": True
    }
    
    return ChartRecommendation(
        type="bar",
        title=f"{dim_col} vs {met_col} 柱状图",
        description=f"展示每个{dim_col}对应的{met_col}数值对比，适合比较不同类别的数值差异",
        echarts_option=option,
        suitable_for=["类别对比", "数值比较", "Top N排名"],
        alternatives=["line", "horizontal_bar"]
    )


def _create_line_chart(dimensions: List[str], metrics: List[str], data: Dict[str, Any]) -> ChartRecommendation:
    """创建折线图配置"""
    dim_col = dimensions[0] if dimensions else 'date'
    met_col = metrics[0] if metrics else 'value'
    
    sample_data = _generate_sample_data(dimensions, metrics)
    
    option = {
        "title": {
            "text": f"{dim_col}趋势变化图",
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "legend": {
            "data": [met_col],
            "top": 30
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": sample_data['categories'],
            "boundaryGap": False,
            "axisLabel": {}
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "name": met_col,
            "type": "line",
            "data": sample_data['values'],
            "smooth": True,
            "itemStyle": {
                "color": "#5470C6"
            },
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(84, 112, 198, 0.5)"},
                        {"offset": 1, "color": "rgba(84, 112, 198, 0.1)"}
                    ]
                }
            },
            "emphasis": {
                "focus": "series"
            }
        }],
        "responsive": True,
        "animation": True
    }
    
    return ChartRecommendation(
        type="line",
        title=f"{dim_col}趋势折线图",
        description=f"展示{dim_col}的变化趋势，适合观察数据随时间或顺序的变化规律",
        echarts_option=option,
        suitable_for=["趋势分析", "时间序列", "变化监测"],
        alternatives=["area", "bar"]
    )


def _create_pie_chart(dimensions: List[str], metrics: List[str], data: Dict[str, Any]) -> ChartRecommendation:
    """创建饼图配置"""
    dim_col = dimensions[0] if dimensions else 'category'
    met_col = metrics[0] if metrics else 'value'
    
    sample_data = _generate_sample_data(dimensions, metrics, max_items=8)
    
    # 生成饼图数据
    pie_data = [
        {"value": v, "name": c} 
        for c, v in zip(sample_data['categories'][:8], sample_data['values'][:8])
    ]
    
    option = {
        "title": {
            "text": f"{met_col}占比分布",
            "left": "center",
            "top": 10
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{a} <br/>{b}: {c} ({d}%)"
        },
        "legend": {
            "orient": "vertical",
            "left": "left",
            "top": 50,
            "data": sample_data['categories'][:8]
        },
        "series": [{
            "name": met_col,
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#fff",
                "borderWidth": 2
            },
            "label": {
                "show": True,
                "formatter": "{b}: {d}%"
            },
            "emphasis": {
                "label": {
                    "show": True,
                    "fontSize": 14,
                    "fontWeight": "bold"
                }
            },
            "labelLine": {
                "show": True
            },
            "data": pie_data
        }],
        "responsive": True,
        "animation": True
    }
    
    return ChartRecommendation(
        type="pie",
        title=f"{met_col}占比饼图",
        description=f"展示各{dim_col}占{met_col}的比例分布，适合了解整体构成",
        echarts_option=option,
        suitable_for=["占比分析", "构成分析", "分布概览"],
        alternatives=["doughnut", "bar"]
    )


def _create_pie_chart_simple(metrics: List[str], data: Dict[str, Any]) -> ChartRecommendation:
    """创建简单的饼图（无维度，只有指标）"""
    met_col = metrics[0] if metrics else 'value'
    
    # 生成示例数据
    values = data.get('values', [[100]])
    if values and isinstance(values[0], list):
        val = values[0][0] if values[0] else 0
    else:
        val = values[0] if values else 0
    
    pie_data = [
        {"value": int(val * 0.4), "name": "项目A"},
        {"value": int(val * 0.35), "name": "项目B"},
        {"value": int(val * 0.25), "name": "项目C"}
    ]
    
    option = {
        "title": {
            "text": "指标构成分析",
            "left": "center",
            "top": 10
        },
        "tooltip": {
            "trigger": "item"
        },
        "legend": {
            "bottom": 10,
            "left": "center"
        },
        "series": [{
            "type": "pie",
            "radius": "50%",
            "data": pie_data,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }]
    }
    
    return ChartRecommendation(
        type="pie",
        title="指标构成饼图",
        description="展示指标的构成比例",
        echarts_option=option,
        suitable_for=["指标分解", "占比展示"],
        alternatives=["doughnut"]
    )


def _create_indicator_card(data: Dict[str, Any]) -> ChartRecommendation:
    """创建指标卡片"""
    metrics = data.get('metrics', ['value'])
    values = data.get('values', [[100]])
    
    if values and isinstance(values[0], list):
        val = values[0][0] if values[0] else 0
    else:
        val = values[0] if values else 0
    
    option = {
        "title": {
            "text": f"关键指标",
            "left": "center"
        },
        "series": [{
            "type": "gauge",
            "startAngle": 180,
            "endAngle": 0,
            "min": 0,
            "max": "auto",
            "splitNumber": 5,
            "itemStyle": {
                "color": "#5470C6"
            },
            "progress": {
                "show": True,
                "width": 30
            },
            "pointer": {
                "show": True
            },
            "axisLine": {
                "lineStyle": {
                    "width": 30
                }
            },
            "axisTick": {
                "show": False
            },
            "splitLine": {
                "show": False
            },
            "axisLabel": {
                "show": False
            },
            "title": {
                "show": True,
                "offsetCenter:": [0, "40%"]
            },
            "detail": {
                "valueAnimation": True,
                "formatter": "{value}",
                "color": "inherit",
                "offsetCenter": [0, "-20%"]
            },
            "data": [{
                "value": int(val),
                "name": metrics[0]
            }]
        }]
    }
    
    return ChartRecommendation(
        type="gauge",
        title="关键指标卡",
        description="突出展示核心指标数值",
        echarts_option=option,
        suitable_for=["KPI展示", "指标概览"],
        alternatives=["bar"]
    )


def _create_stacked_bar_chart(dimensions: List[str], metrics: List[str], data: Dict[str, Any]) -> ChartRecommendation:
    """创建堆叠柱状图"""
    dim_col = dimensions[0] if dimensions else 'category'
    
    sample_data = _generate_sample_data(dimensions, metrics)
    
    option = {
        "title": {
            "text": f"{dim_col}堆叠分析图",
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"}
        },
        "legend": {
            "data": metrics,
            "top": 30
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": sample_data['categories']
        },
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "name": m,
                "type": "bar",
                "stack": "total",
                "data": [v * (i + 1) / len(metrics) for v in sample_data['values']],
                "emphasis": {"focus": "series"}
            }
            for i, m in enumerate(metrics)
        ]
    }
    
    return ChartRecommendation(
        type="bar",
        title=f"{dim_col}堆叠柱状图",
        description="展示多个指标在各类别中的堆叠分布",
        echarts_option=option,
        suitable_for=["构成分析", "多指标对比"],
        alternatives=["line", "area"]
    )


def _create_area_chart(dimensions: List[str], metrics: List[str], data: Dict[str, Any]) -> ChartRecommendation:
    """创建面积图"""
    dim_col = dimensions[0] if dimensions else 'date'
    met_col = metrics[0] if metrics else 'value'
    
    sample_data = _generate_sample_data(dimensions, metrics)
    
    option = {
        "title": {
            "text": f"{dim_col}面积趋势图",
            "left": "center"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": sample_data['categories'],
            "boundaryGap": False
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "type": "line",
            "data": sample_data['values'],
            "smooth": True,
            "areaStyle": {},
            "itemStyle": {
                "color": "#73A0FA"
            }
        }]
    }
    
    return ChartRecommendation(
        type="area",
        title=f"{dim_col}面积图",
        description="以面积形式展示数据变化趋势",
        echarts_option=option,
        suitable_for=["趋势分析", "累计展示"],
        alternatives=["line"]
    )


def _create_scatter_chart(dimensions: List[str], metrics: List[str], data: Dict[str, Any]) -> ChartRecommendation:
    """创建散点图"""
    x_dim = dimensions[0] if len(dimensions) > 0 else 'x'
    y_dim = dimensions[1] if len(dimensions) > 1 else (metrics[0] if metrics else 'y')
    size_metric = metrics[0] if metrics else 'size'
    
    # 生成随机散点数据
    import random
    random.seed(42)
    scatter_data = [
        [random.randint(10, 100), random.randint(10, 100), random.randint(100, 500)]
        for _ in range(30)
    ]
    
    option = {
        "title": {
            "text": f"{x_dim}与{y_dim}相关性分析",
            "left": "center"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": lambda p: f"{x_dim}: {p.data[0]}<br/>{y_dim}: {p.data[1]}"
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": {
            "type": "value",
            "name": x_dim,
            "splitLine": {"show": True}
        },
        "yAxis": {
            "type": "value",
            "name": y_dim,
            "splitLine": {"show": True}
        },
        "series": [{
            "type": "scatter",
            "symbolSize": 20,
            "data": scatter_data,
            "itemStyle": {
                "color": "#5470C6",
                "opacity": 0.7
            },
            "emphasis": {
                "itemStyle": {
                    "borderColor:": "#fff",
                    "borderWidth": 1
                }
            }
        }]
    }
    
    return ChartRecommendation(
        type="scatter",
        title=f"{x_dim}-{y_dim}散点图",
        description="分析两个变量之间的相关性和分布规律",
        echarts_option=option,
        suitable_for=["相关性分析", "分布展示", "异常检测"],
        alternatives=["line"]
    )


def _create_map_chart(dimensions: List[str], metrics: List[str], data: Dict[str, Any]) -> ChartRecommendation:
    """创建地图图表"""
    dim_col = dimensions[0] if dimensions else 'region'
    met_col = metrics[0] if metrics else 'value'
    
    # 使用简单的中国地图示例
    sample_data = _generate_sample_data(dimensions, metrics)
    
    option = {
        "title": {
            "text": f"地区分布热力图",
            "left": "center"
        },
        "tooltip": {
            "trigger": "item"
        },
        "visualMap": {
            "min": 0,
            "max": max(sample_data['values']) if sample_data['values'] else 1000,
            "left": "left",
            "top": "bottom",
            "text": ["高", "低"],
            "calculable": True
        },
        "series": [{
            "name": met_col,
            "type": "map",
            "map": "china",
            "roam": True,
            "label": {
                "show": True
            },
            "data": [
                {"name": "北京", "value": sample_data['values'][0] if len(sample_data['values']) > 0 else 500},
                {"name": "上海", "value": sample_data['values'][1] if len(sample_data['values']) > 1 else 400},
                {"name": "广东", "value": sample_data['values'][2] if len(sample_data['values']) > 2 else 350},
                {"name": "浙江", "value": sample_data['values'][3] if len(sample_data['values']) > 3 else 300},
                {"name": "江苏", "value": sample_data['values'][4] if len(sample_data['values']) > 4 else 280}
            ]
        }]
    }
    
    return ChartRecommendation(
        type="map",
        title="地区分布地图",
        description="以地图形式展示各地区数据分布",
        echarts_option=option,
        suitable_for=["地理分析", "区域对比"],
        alternatives=["bar", "pie"]
    )


def _create_default_chart(dimensions: List[str], metrics: List[str], data: Dict[str, Any]) -> ChartRecommendation:
    """创建默认图表"""
    sample_data = _generate_sample_data(dimensions, metrics)
    
    option = {
        "title": {
            "text": "数据可视化",
            "left": "center"
        },
        "tooltip": {},
        "xAxis": {
            "type": "category",
            "data": sample_data['categories']
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "type": "bar",
            "data": sample_data['values']
        }]
    }
    
    return ChartRecommendation(
        type="bar",
        title="数据图表",
        description="默认图表展示",
        echarts_option=option,
        suitable_for=["通用展示"],
        alternatives=["line", "pie"]
    )


def _generate_sample_data(dimensions: List[str], metrics: List[str], max_items: int = 7) -> Dict[str, Any]:
    """生成示例数据"""
    import random
    random.seed(42)
    
    dim_col = dimensions[0] if dimensions else 'category'
    
    # 根据维度类型生成不同的类别标签
    if 'date' in dim_col.lower() or '时间' in dim_col or '月份' in dim_col:
        categories = ["1月", "2月", "3月", "4月", "5月", "6月", "7月"]
    elif 'region' in dim_col.lower() or '地区' in dim_col:
        categories = ["华北", "华东", "华南", "华中", "东北", "西南", "西北"]
    else:
        categories = ["类别A", "类别B", "类别C", "类别D", "类别E", "类别F", "类别G"]
    
    # 生成数值数据
    values = [random.randint(100, 1000) for _ in range(len(categories))]
    
    return {
        "categories": categories[:max_items],
        "values": values[:max_items]
    }


def generate_all_charts_json(recommendations: List[ChartRecommendation]) -> str:
    """生成所有图表的JSON格式输出"""
    charts_output = []
    
    for rec in recommendations:
        charts_output.append({
            "type": rec.type,
            "title": rec.title,
            "description": rec.description,
            "echarts_option": rec.echarts_option
        })
    
    return json.dumps(charts_output, ensure_ascii=False, indent=2)


def format_chart_recommendations(recommendations: List[ChartRecommendation]) -> str:
    """格式化图表推荐输出"""
    if not recommendations:
        return "未找到合适的图表推荐"
    
    output = "📊 **图表推荐结果**\n\n"
    
    for i, rec in enumerate(recommendations, 1):
        output += f"### {i}. {rec.title}\n"
        output += f"**类型**: `{rec.type}`\n"
        output += f"**说明**: {rec.description}\n"
        output += f"**适用场景**: {', '.join(rec.suitable_for)}\n"
        output += f"**替代方案**: {', '.join(rec.alternatives)}\n\n"
    
    output += "\n---\n\n**ECharts配置JSON已生成，可直接用于前端渲染。**\n"
    
    return output
