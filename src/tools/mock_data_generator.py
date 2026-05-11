"""
Mock数据生成工具 - 生成测试用的示例数据
"""
import csv
import json
import random
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from io import StringIO

logger = logging.getLogger(__name__)


def generate_mock_data(
    data_type: str = "sales",
    row_count: int = 100,
    include_headers: bool = True
) -> str:
    """
    生成Mock测试数据
    
    Args:
        data_type: 数据类型 (sales, customers, products, orders)
        row_count: 数据行数
        include_headers: 是否包含表头
        
    Returns:
        CSV格式的Mock数据字符串
    """
    generators = {
        "sales": _generate_sales_data,
        "customers": _generate_customers_data,
        "products": _generate_products_data,
        "orders": _generate_orders_data,
    }
    
    generator = generators.get(data_type, _generate_sales_data)
    return generator(row_count, include_headers)


def _generate_sales_data(row_count: int = 100, include_headers: bool = True) -> str:
    """生成销售数据"""
    output = StringIO()
    
    # 定义数据选项
    regions = ["华北", "华东", "华南", "华中", "东北", "西南", "西北"]
    categories = ["电子产品", "服装", "食品", "家居", "图书", "美妆", "运动"]
    products = {
        "电子产品": ["手机", "电脑", "平板", "耳机", "相机"],
        "服装": ["T恤", "牛仔裤", "连衣裙", "外套", "运动服"],
        "食品": ["零食", "饮料", "水果", "肉类", "海鲜"],
        "家居": ["沙发", "床", "衣柜", "餐桌", "椅子"],
        "图书": ["小说", "技术书", "童书", "漫画", "杂志"],
        "美妆": ["护肤", "彩妆", "香水", "护发", "沐浴"],
        "运动": ["跑步鞋", "篮球", "瑜伽垫", "健身器材", "骑行装备"]
    }
    
    # 写CSV
    fieldnames = ["id", "date", "product_name", "category", "region", "sales_amount", "quantity", "customer_id"]
    
    if include_headers:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
    else:
        writer = csv.writer(output)
        writer.writerow(fieldnames)
    
    # 生成数据
    start_date = datetime(2024, 1, 1)
    for i in range(1, row_count + 1):
        # 随机日期
        random_days = random.randint(0, 365)
        sale_date = start_date + timedelta(days=random_days)
        
        # 随机选择类别和产品
        category = random.choice(categories)
        product = random.choice(products[category])
        
        # 生成销售数据
        quantity = random.randint(1, 50)
        unit_price = _get_unit_price(category)
        sales_amount = quantity * unit_price * random.uniform(0.8, 1.2)
        
        record = {
            "id": i,
            "date": sale_date.strftime("%Y-%m-%d"),
            "product_name": product,
            "category": category,
            "region": random.choice(regions),
            "sales_amount": round(sales_amount, 2),
            "quantity": quantity,
            "customer_id": random.randint(1001, 2000)
        }
        
        if include_headers:
            writer.writerow(record)
        else:
            writer.writerow(record.values())
    
    return output.getvalue()


def _generate_customers_data(row_count: int = 100, include_headers: bool = True) -> str:
    """生成客户数据"""
    output = StringIO()
    
    regions = ["北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", "西安", "重庆"]
    vip_levels = ["普通", "银卡", "金卡", "白金", "钻石"]
    vip_weights = [0.5, 0.25, 0.15, 0.07, 0.03]
    
    fieldnames = ["id", "name", "email", "phone", "region", "registration_date", "vip_level", "total_orders"]
    
    if include_headers:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
    else:
        writer = csv.writer(output)
        writer.writerow(fieldnames)
    
    start_date = datetime(2020, 1, 1)
    for i in range(1, row_count + 1):
        reg_days = random.randint(0, 1460)  # 4年内
        reg_date = start_date + timedelta(days=reg_days)
        
        record = {
            "id": 1000 + i,
            "name": f"用户{i:04d}",
            "email": f"user{i:04d}@example.com",
            "phone": f"138{random.randint(10000000, 99999999)}",
            "region": random.choice(regions),
            "registration_date": reg_date.strftime("%Y-%m-%d"),
            "vip_level": random.choices(vip_levels, weights=vip_weights)[0],
            "total_orders": random.randint(1, 200)
        }
        
        if include_headers:
            writer.writerow(record)
        else:
            writer.writerow(record.values())
    
    return output.getvalue()


def _generate_products_data(row_count: int = 50, include_headers: bool = True) -> str:
    """生成产品数据"""
    output = StringIO()
    
    categories = ["电子产品", "服装", "食品", "家居", "图书", "美妆", "运动"]
    products_by_cat = {
        "电子产品": ["手机", "电脑", "平板", "耳机", "相机", "音箱", "键盘", "鼠标"],
        "服装": ["T恤", "牛仔裤", "连衣裙", "外套", "运动服", "裙子", "衬衫", "毛衣"],
        "食品": ["零食", "饮料", "水果", "肉类", "海鲜", "蔬菜", "奶制品", "坚果"],
        "家居": ["沙发", "床", "衣柜", "餐桌", "椅子", "书桌", "灯具", "窗帘"],
        "图书": ["小说", "技术书", "童书", "漫画", "杂志", "绘本", "教材", "传记"],
        "美妆": ["护肤", "彩妆", "香水", "护发", "沐浴", "面膜", "眼霜", "口红"],
        "运动": ["跑步鞋", "篮球", "瑜伽垫", "健身器材", "骑行装备", "球拍", "泳镜", "手套"]
    }
    
    fieldnames = ["id", "name", "category", "price", "stock", "supplier_id", "create_date"]
    
    if include_headers:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
    else:
        writer = csv.writer(output)
        writer.writerow(fieldnames)
    
    start_date = datetime(2023, 1, 1)
    for i in range(1, row_count + 1):
        category = random.choice(categories)
        product = random.choice(products_by_cat[category])
        
        record = {
            "id": 5000 + i,
            "name": f"{product}-{random.choice(['标准版', '升级版', '豪华版', '青春版', '旗舰版'])}",
            "category": category,
            "price": round(random.uniform(9.9, 9999.9), 2),
            "stock": random.randint(0, 1000),
            "supplier_id": random.randint(100, 200),
            "create_date": (start_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        }
        
        if include_headers:
            writer.writerow(record)
        else:
            writer.writerow(record.values())
    
    return output.getvalue()


def _generate_orders_data(row_count: int = 100, include_headers: bool = True) -> str:
    """生成订单数据"""
    output = StringIO()
    
    statuses = ["待支付", "已支付", "已发货", "已完成", "已取消"]
    status_weights = [0.1, 0.2, 0.3, 0.35, 0.05]
    
    fieldnames = ["id", "customer_id", "order_date", "status", "total_amount", "items_count", "shipping_address"]
    
    if include_headers:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
    else:
        writer = csv.writer(output)
        writer.writerow(fieldnames)
    
    start_date = datetime(2024, 1, 1)
    addresses = [
        "北京市朝阳区XXX街道1号",
        "上海市浦东新区XXX路100号",
        "广州市天河区XXX大道200号",
        "深圳市南山区XXX北路50号",
        "杭州市西湖区XXX路300号"
    ]
    
    for i in range(1, row_count + 1):
        order_date = start_date + timedelta(days=random.randint(0, 180))
        items_count = random.randint(1, 10)
        avg_item_price = random.uniform(50, 500)
        total_amount = round(items_count * avg_item_price * random.uniform(0.8, 1.5), 2)
        
        record = {
            "id": 20000 + i,
            "customer_id": random.randint(1001, 1100),
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": random.choices(statuses, weights=status_weights)[0],
            "total_amount": total_amount,
            "items_count": items_count,
            "shipping_address": random.choice(addresses)
        }
        
        if include_headers:
            writer.writerow(record)
        else:
            writer.writerow(record.values())
    
    return output.getvalue()


def _get_unit_price(category: str) -> float:
    """获取各类别的参考单价"""
    price_ranges = {
        "电子产品": (500, 5000),
        "服装": (50, 500),
        "食品": (5, 100),
        "家居": (100, 3000),
        "图书": (20, 100),
        "美妆": (30, 500),
        "运动": (50, 1000)
    }
    price_range = price_ranges.get(category, (10, 500))
    return random.uniform(price_range[0], price_range[1])


def generate_mock_script(
    data_type: str = "sales",
    output_file: str = "mock_data.csv",
    row_count: int = 100
) -> str:
    """
    生成Mock数据生成脚本
    
    Args:
        data_type: 数据类型
        output_file: 输出文件名
        row_count: 数据行数
        
    Returns:
        Python脚本内容
    """
    script = f'''#!/usr/bin/env python3
"""
Mock数据生成脚本 - {data_type}数据
自动生成{row_count}条测试数据
"""

import csv
import random
from datetime import datetime, timedelta

# 设置随机种子（可选，保证结果可复现）
# random.seed(42)

# 数据配置
ROW_COUNT = {row_count}
OUTPUT_FILE = "{output_file}"

def generate_{data_type}_data():
    """生成{data_type}类型的数据"""
    
    # 定义数据选项
    regions = ["华北", "华东", "华南", "华中", "东北", "西南", "西北"]
    categories = ["电子产品", "服装", "食品", "家居", "图书"]
    
    # 生成数据
    data = []
    start_date = datetime(2024, 1, 1)
    
    for i in range(1, ROW_COUNT + 1):
        random_days = random.randint(0, 365)
        sale_date = start_date + timedelta(days=random_days)
        
        record = {{
            "id": i,
            "date": sale_date.strftime("%Y-%m-%d"),
            "category": random.choice(categories),
            "region": random.choice(regions),
            "sales_amount": round(random.uniform(100, 10000), 2),
            "quantity": random.randint(1, 100)
        }}
        data.append(record)
    
    return data

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        print("没有数据可保存")
        return
    
    fieldnames = list(data[0].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"已生成{{len(data)}}条数据到 {{filename}}")

if __name__ == "__main__":
    print("开始生成Mock数据...")
    data = generate_{data_type}_data()
    save_to_csv(data, OUTPUT_FILE)
    print("生成完成!")
'''
    
    return script


def generate_all_mock_data() -> Dict[str, str]:
    """生成所有类型的Mock数据"""
    return {
        "sales_data.csv": generate_mock_data("sales", 100),
        "customers_data.csv": generate_mock_data("customers", 50),
        "products_data.csv": generate_mock_data("products", 30),
        "orders_data.csv": generate_mock_data("orders", 100)
    }


def get_mock_data_info() -> Dict[str, Any]:
    """获取Mock数据信息"""
    return {
        "available_types": [
            {
                "type": "sales",
                "description": "销售数据",
                "fields": ["id", "date", "product_name", "category", "region", "sales_amount", "quantity", "customer_id"],
                "typical_rows": "100-10000"
            },
            {
                "type": "customers",
                "description": "客户数据",
                "fields": ["id", "name", "email", "phone", "region", "registration_date", "vip_level", "total_orders"],
                "typical_rows": "50-5000"
            },
            {
                "type": "products",
                "description": "产品数据",
                "fields": ["id", "name", "category", "price", "stock", "supplier_id", "create_date"],
                "typical_rows": "30-1000"
            },
            {
                "type": "orders",
                "description": "订单数据",
                "fields": ["id", "customer_id", "order_date", "status", "total_amount", "items_count", "shipping_address"],
                "typical_rows": "100-10000"
            }
        ],
        "usage": {
            "description": "使用说明",
            "steps": [
                "1. 选择要生成的数据类型",
                "2. 指定数据行数",
                "3. 调用generate_mock_data()函数",
                "4. 将返回的CSV内容保存到文件"
            ]
        }
    }


def format_mock_data_output(data: str, data_type: str) -> str:
    """格式化Mock数据输出"""
    output = f"📊 **Mock数据生成完成**\n\n"
    output += f"**数据类型**: {data_type}\n"
    output += f"**数据格式**: CSV\n"
    output += f"**数据预览** (前5行):\n\n"
    
    lines = data.strip().split('\n')
    preview_lines = lines[:6]  # 表头 + 5行数据
    
    output += "```\n"
    output += "\n".join(preview_lines)
    if len(lines) > 6:
        output += f"\n... (共{len(lines)-1}行数据)"
    output += "\n```\n"
    
    output += "\n\n💡 **使用建议**: 将上述数据保存为CSV文件，导入数据库进行测试。\n"
    
    return output
