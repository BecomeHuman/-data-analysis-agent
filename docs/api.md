# 数据分析报表系统 - API接口文档

## 概述
本系统提供数据分析、SQL生成、图表渲染和报表生成功能。

## 基础信息
- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: API Key (Header: `X-API-Key`)

---

## 1. SQL查询接口

### POST /query
执行SQL查询

**请求示例**:
```json
{
  "query": "查询2024年各地区销售额",
  "use_mock_data": true
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "sql": "SELECT region, SUM(sales_amount) FROM sales WHERE date >= '2024-01-01' GROUP BY region",
    "status": "success",
    "results": [
      {"region": "华北", "total": 1250000},
      {"region": "华东", "total": 1580000}
    ]
  }
}
```

---

## 2. 文档分析接口

### POST /analyze/document
上传并分析文档

**请求**: `multipart/form-data`
- `file`: PDF/Word/Excel/CSV/TXT文件
- `query`: 分析问题 (可选)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "file_name": "report.pdf",
    "content_preview": "这是文档的前500个字符...",
    "extracted_data": {
      "tables": 3,
      "images": 5,
      "pages": 25
    }
  }
}
```

---

## 3. 图表生成接口

### POST /charts/recommend
根据数据推荐图表

**请求示例**:
```json
{
  "data": {
    "dimensions": ["region", "category"],
    "metrics": ["sales_amount", "quantity"],
    "values": [[...], [...]]
  },
  "chart_types": ["bar", "line", "pie"]
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "type": "bar",
        "title": "地区销售额对比",
        "echarts_option": { ... }
      }
    ]
  }
}
```

---

## 4. 报表生成接口

### POST /report/generate
生成完整报表

**请求示例**:
```json
{
  "query": "2024年销售分析报告",
  "include_charts": true,
  "format": "markdown",
  "sql_results": { ... },
  "charts": [ ... ]
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "report": {
      "format": "markdown",
      "content": "# 2024年销售分析报告

## 摘要
...",
      "charts": [ ... ]
    }
  }
}
```

---

## 5. Mock数据接口

### GET /mock/data
获取Mock数据

**查询参数**:
- `type`: 数据类型 (sales/customers/products/orders)
- `rows`: 行数 (默认100)

**响应**: CSV格式数据流

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数缺失 |
| 1002 | 参数格式错误 |
| 2001 | 数据库连接失败 |
| 2002 | SQL执行失败 |
| 3001 | 文件解析失败 |
| 3002 | 不支持的文件格式 |
| 4001 | LLM服务不可用 |
| 5001 | 内部服务器错误 |

---

## 调用示例

### Python调用示例
```python
import requests

# 查询数据
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={"query": "查询销售额"},
    headers={"X-API-Key": "your-api-key"}
)
print(response.json())

# 生成图表
response = requests.post(
    "http://localhost:8000/api/v1/charts/recommend",
    json={"data": {...}}
)
charts = response.json()["data"]["recommendations"]
```

### JavaScript调用示例
```javascript
// 查询数据
const response = await fetch('http://localhost:8000/api/v1/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({ query: '查询销售额' })
});
const data = await response.json();
```
