"""
环境安装脚本生成工具 - 生成开发环境安装脚本和依赖配置
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def generate_install_script(
    python_version: str = "3.12",
    include_database: bool = True,
    include_frontend: bool = True
) -> str:
    """
    生成环境安装脚本
    
    Args:
        python_version: Python版本
        include_database: 是否包含数据库配置
        include_frontend: 是否包含前端依赖
        
    Returns:
        安装脚本内容
    """
    script = f'''#!/bin/bash
# ==========================================
# 数据分析报表系统 - 环境安装脚本
# Python {python_version}
# ==========================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "数据分析报表系统 - 环境安装"
echo "=========================================="

# 1. 检查Python版本
echo "[1/6] 检查Python版本..."
python_version_check=$(python3 --version 2>&1 | grep -oP '\\d+\\.\\d+' | head -1)
if [[ "$(echo "$python_version_check >= {python_version}" | bc)" == "0" ]]; then
    echo "错误: 需要Python {python_version}或更高版本，当前版本: $python_version_check"
    echo "请先安装Python {python_version}: https://www.python.org/downloads/"
    exit 1
fi
echo "✓ Python版本检查通过: $(python3 --version)"

# 2. 创建虚拟环境
echo "[2/6] 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
source venv/bin/activate

# 3. 升级pip
echo "[3/6] 升级pip..."
pip install --upgrade pip
echo "✓ pip升级完成"

# 4. 安装Python依赖
echo "[4/6] 安装Python依赖..."
'''

    # Python依赖列表
    python_deps = [
        "pandas>=2.2.0",
        "SQLAlchemy>=2.0.0",
        "pypdf>=6.4.0",
        "docx2python>=3.5.0",
        "openpyxl>=3.1.0",
        "python-pptx>=1.0.0",
        "psycopg2-binary>=2.9.0",
        "bcrypt>=4.0.0",
        "python-dotenv>=1.2.0",
    ]
    
    script += f'''
pip install {' '.join(python_deps)}
echo "✓ Python依赖安装完成"
'''

    if include_database:
        script += '''
# 5. 数据库配置
echo "[5/6] 数据库配置..."
export PGDATABASE_URL="${PGDATABASE_URL:-postgresql://user:password@localhost:5432/dbname}"
echo "✓ 数据库配置完成 (请确保PGDATABASE_URL环境变量已设置)"
'''

    if include_frontend:
        script += '''
# 6. 前端依赖（可选）
echo "[6/6] 前端依赖..."
echo "如需使用前端可视化，请安装以下依赖："
echo "  - ECharts: https://echarts.apache.org/handbook/zh/get-started/"
echo "  - npm install echarts"
echo "✓ 前端配置说明已提供"
'''

    script += '''
echo ""
echo "=========================================="
echo "✓ 环境安装完成!"
echo "=========================================="
echo ""
echo "后续步骤:"
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 配置数据库: export PGDATABASE_URL='postgresql://...'"
echo "3. 配置LLM: export LLM_API_KEY='your-api-key'"
echo "4. 运行测试: python test.py"
echo "5. 启动服务: python main.py"
echo ""
'''

    return script


def generate_requirements_txt() -> str:
    """生成requirements.txt文件内容"""
    requirements = """# 数据分析报表系统依赖
# Python >= 3.12

# 核心框架
pandas>=2.2.0
SQLAlchemy>=2.0.0

# Web服务
fastapi>=0.121.0
uvicorn>=0.38.0

# LLM集成
coze-coding-dev-sdk>=0.5.0

# 文档解析
pypdf>=6.4.0
docx2python>=3.5.0
openpyxl>=3.1.0
python-pptx>=1.0.0

# 数据库
psycopg2-binary>=2.9.0

# 工具库
python-dotenv>=1.2.0
bcrypt>=4.0.0
chardet>=5.2.0
"""

    return requirements


def generate_env_example() -> str:
    """生成.env.example文件内容"""
    env_template = """# ==========================================
# 数据分析报表系统 - 环境变量配置
# 复制此文件为 .env 并填入实际值
# ==========================================

# 数据库配置
PGDATABASE_URL=postgresql://user:password@localhost:5432/dbname

# LLM API配置 (使用火山方舟或DeepSeek)
LLM_API_KEY=sk-your-api-key-here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=doubao-seed-1-6-251015

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=app.log
"""

    return env_template


def generate_docker_compose() -> str:
    """生成Docker Compose配置"""
    docker_compose = """version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: analytics_postgres
    environment:
      POSTGRES_USER: analytics
      POSTGRES_PASSWORD: analytics_secret
      POSTGRES_DB: analytics_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U analytics"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 应用服务
  app:
    build: .
    container_name: analytics_app
    environment:
      - PGDATABASE_URL=postgresql://analytics:analytics_secret@postgres:5432/analytics_db
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_BASE_URL=${LLM_BASE_URL:-https://api.deepseek.com}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./app:/app
      - ./data:/data

volumes:
  postgres_data:
"""

    return docker_compose


def generate_api_documentation() -> str:
    """生成API接口文档"""
    api_doc = """# 数据分析报表系统 - API接口文档

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
      "content": "# 2024年销售分析报告\n\n## 摘要\n...",
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
"""

    return api_doc


def generate_all_scripts() -> Dict[str, str]:
    """生成所有脚本"""
    return {
        "install_env.sh": generate_install_script(),
        "requirements.txt": generate_requirements_txt(),
        ".env.example": generate_env_example(),
        "docker-compose.yml": generate_docker_compose(),
        "api.md": generate_api_documentation()
    }


def format_env_script_output() -> str:
    """格式化环境脚本输出"""
    output = """🔧 **环境安装脚本已生成**

## 生成的文件

| 文件名 | 说明 |
|--------|------|
| `install_env.sh` | 一键安装脚本 |
| `requirements.txt` | Python依赖清单 |
| `.env.example` | 环境变量模板 |
| `docker-compose.yml` | Docker部署配置 |
| `api.md` | API接口文档 |

## 快速开始

```bash
# 1. 运行安装脚本
chmod +x install_env.sh
./install_env.sh

# 2. 配置环境变量
cp .env.example .env
# 编辑.env填入实际配置

# 3. 启动服务
python main.py
```

## Docker部署

```bash
docker-compose up -d
```

## API文档

详见生成的 `api.md` 文件
"""
    return output
