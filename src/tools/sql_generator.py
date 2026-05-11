"""
SQL生成工具 - 根据自然语言生成SQL查询语句
"""
import json
import re
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# 默认的数据库表结构信息（用于生成SQL的参考）
DEFAULT_SCHEMA = """
可用表结构参考:
- sales_table: (id, date, product_name, category, region, sales_amount, quantity, customer_id)
- customers: (id, name, email, region, registration_date, vip_level)
- products: (id, name, category, price, stock, supplier_id)
- orders: (id, customer_id, order_date, status, total_amount)
- order_items: (id, order_id, product_id, quantity, unit_price)

常见SQL模式:
- 聚合查询: SELECT column, AGG(column) FROM table GROUP BY column
- 条件过滤: SELECT * FROM table WHERE condition
- 多表联合: SELECT * FROM t1 JOIN t2 ON t1.id = t2.t1_id
- 时间筛选: WHERE date BETWEEN '2024-01-01' AND '2024-12-31'
"""

def parse_natural_language_to_sql(
    query: str,
    schema: Optional[str] = None,
    available_tables: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    将自然语言转换为SQL查询语句
    
    Args:
        query: 用户自然语言查询
        schema: 数据库表结构信息
        available_tables: 可用的表名列表
        
    Returns:
        包含SQL状态和查询结果的字典
    """
    result = {
        "query_sql": "",
        "sql_status": "success",
        "sql_error": "",
        "sql_fix_suggestion": "",
        "explanation": ""
    }
    
    try:
        # 基础验证
        if not query or not query.strip():
            result["sql_status"] = "failed"
            result["sql_error"] = "查询内容不能为空"
            result["sql_fix_suggestion"] = "请提供有效的自然语言查询"
            return result
        
        # 使用模式匹配进行基础SQL生成
        sql = _generate_sql_from_pattern(query, schema or DEFAULT_SCHEMA)
        
        # 验证生成的SQL
        validation = _validate_sql(sql)
        
        if not validation["is_valid"]:
            result["sql_status"] = "failed"
            result["sql_error"] = validation["error"]
            result["sql_fix_suggestion"] = validation["suggestion"]
        else:
            result["query_sql"] = sql
            result["explanation"] = _explain_sql(sql, query)
            
    except Exception as e:
        logger.error(f"SQL生成失败: {e}")
        result["sql_status"] = "failed"
        result["sql_error"] = str(e)
        result["sql_fix_suggestion"] = "请检查查询语句的语法和表名是否正确"
    
    return result


def _generate_sql_from_pattern(query: str, schema: str) -> str:
    """基于模式匹配生成SQL"""
    query_lower = query.lower()
    sql = "SELECT "
    
    # 检测聚合需求
    if any(keyword in query_lower for keyword in ['总计', '总数', 'total', 'sum', 'count', '平均', 'average', 'avg']):
        if '平均' in query_lower or 'average' in query_lower or 'avg' in query_lower:
            sql += "AVG("
        elif any(k in query_lower for k in ['总计', '总和', 'total', 'sum']):
            sql += "SUM("
        else:
            sql += "COUNT(*)"
    else:
        sql += "*"
    
    # 确定表名
    table_name = _detect_table_name(query_lower, schema)
    sql += f" FROM {table_name}"
    
    # 添加WHERE条件
    conditions = _extract_conditions(query_lower)
    if conditions:
        sql += f" WHERE {conditions}"
    
    # 添加GROUP BY
    if any(keyword in query_lower for keyword in ['按', 'by', '分组', 'group']):
        group_col = _extract_group_by(query_lower)
        if group_col:
            sql += f" GROUP BY {group_col}"
    
    # 添加ORDER BY
    if any(keyword in query_lower for keyword in ['排序', 'order', '降序', 'desc', '升序', 'asc']):
        order_col = _extract_order_by(query_lower)
        if order_col:
            sql += f" ORDER BY {order_col}"
    
    # 添加LIMIT
    if any(keyword in query_lower for keyword in ['前', 'top', 'limit', '最近', 'latest']):
        limit_num = _extract_limit(query_lower)
        sql += f" LIMIT {limit_num}"
    
    return sql


def _detect_table_name(query: str, schema: str) -> str:
    """检测要查询的表名"""
    # 基于关键词推断表名
    if any(k in query for k in ['销售', 'sales']):
        return 'sales_table'
    elif any(k in query for k in ['客户', 'customer']):
        return 'customers'
    elif any(k in query for k in ['产品', 'product']):
        return 'products'
    elif any(k in query for k in ['订单', 'order']):
        return 'orders'
    
    # 默认返回第一个表
    tables = re.findall(r'(\w+):\s*\(', schema)
    return tables[0] if tables else 'sales_table'


def _extract_conditions(query: str) -> str:
    """提取WHERE条件"""
    conditions = []
    
    # 日期条件
    date_match = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)', query)
    if date_match:
        date_str = date_match.group(1).replace('年', '-').replace('月', '-').replace('日', '')
        conditions.append(f"date = '{date_str}'")
    
    # 地区条件
    regions = ['华北', '华东', '华南', '华中', '东北', '西南', '西北', 'North', 'South', 'East', 'West']
    for region in regions:
        if region in query:
            conditions.append(f"region = '{region}'")
            break
    
    # 类别条件
    categories = ['电子产品', '服装', '食品', '家居', '图书', '电子产品', 'electronic', 'food', 'clothing']
    for cat in categories:
        if cat in query:
            conditions.append(f"category = '{cat}'")
            break
    
    return ' AND '.join(conditions) if conditions else ''


def _extract_group_by(query: str) -> str:
    """提取GROUP BY字段"""
    if '地区' in query or 'region' in query:
        return 'region'
    elif '日期' in query or 'date' in query or '月份' in query:
        return 'date'
    elif '类别' in query or 'category' in query:
        return 'category'
    elif '产品' in query or 'product' in query:
        return 'product_name'
    return 'region'


def _extract_order_by(query: str) -> str:
    """提取ORDER BY字段"""
    if any(k in query for k in ['金额', 'amount', 'sales']):
        return 'sales_amount DESC'
    elif any(k in query for k in ['数量', 'quantity', 'count']):
        return 'quantity DESC'
    elif any(k in query for k in ['日期', 'date', '时间', 'time']):
        return 'date DESC'
    return 'sales_amount DESC'


def _extract_limit(query: str) -> int:
    """提取LIMIT值"""
    match = re.search(r'(前|top|limit)\s*(\d+)', query)
    if match:
        return int(match.group(2))
    return 10


def _validate_sql(sql: str) -> Dict[str, Any]:
    """验证SQL语句的有效性"""
    result = {
        "is_valid": True,
        "error": "",
        "suggestion": ""
    }
    
    if not sql or sql.strip() == "SELECT ":
        result["is_valid"] = False
        result["error"] = "SQL语句为空或不完整"
        result["suggestion"] = "请提供有效的查询内容"
        return result
    
    # 基本语法检查
    if not sql.strip().upper().startswith('SELECT'):
        result["is_valid"] = False
        result["error"] = "SQL必须以SELECT开头"
        result["suggestion"] = "请确保SQL语句以SELECT关键字开始"
        return result
    
    # 检查FROM子句
    if ' FROM ' not in sql.upper():
        result["is_valid"] = False
        result["error"] = "缺少FROM子句"
        result["suggestion"] = "请在SELECT后添加FROM子句指定查询的表"
        return result
    
    # 检查引号配对
    single_quotes = sql.count("'")
    if single_quotes % 2 != 0:
        result["is_valid"] = False
        result["error"] = "引号未正确配对"
        result["suggestion"] = "请检查SQL中的单引号是否成对出现"
        return result
    
    return result


def _explain_sql(sql: str, original_query: str) -> str:
    """解释SQL语句的含义"""
    return f"根据您的查询「{original_query}」，生成了SQL语句：\n{sql}\n\n该查询将从数据库中检索符合条件的数据。"


def generate_join_query(
    tables: List[str],
    join_columns: Dict[str, str],
    select_columns: List[str],
    conditions: Optional[str] = None
) -> str:
    """
    生成多表联合查询
    
    Args:
        tables: 表名列表
        join_columns: 表连接关系，格式为 {表名: 连接条件}
        select_columns: 要选择的列
        conditions: WHERE条件
        
    Returns:
        生成的SQL语句
    """
    if not tables:
        return ""
    
    # 构建SELECT子句
    sql = f"SELECT {', '.join(select_columns) if select_columns else '*'}"
    
    # 构建FROM子句
    sql += f" FROM {tables[0]}"
    
    # 构建JOIN子句
    for i, table in enumerate(tables[1:], 1):
        if table in join_columns:
            sql += f" JOIN {table} ON {join_columns[table]}"
    
    # 添加WHERE条件
    if conditions:
        sql += f" WHERE {conditions}"
    
    return sql


def format_sql_output(result: Dict[str, Any]) -> str:
    """格式化SQL输出为可读字符串"""
    if result["sql_status"] == "failed":
        output = f"❌ SQL生成失败\n\n"
        output += f"错误信息: {result.get('sql_error', '未知错误')}\n"
        if result.get('sql_fix_suggestion'):
            output += f"修正建议: {result['sql_fix_suggestion']}\n"
        return output
    
    output = f"✅ SQL生成成功\n\n"
    output += f"```sql\n{result.get('query_sql', '')}\n```\n\n"
    
    if result.get('explanation'):
        output += f"{result['explanation']}\n"
    
    return output
