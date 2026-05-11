#!/bin/bash
# ==========================================
# 数据分析报表系统 - 环境安装脚本
# Python 3.12
# ==========================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "数据分析报表系统 - 环境安装"
echo "=========================================="

# 1. 检查Python版本
echo "[1/6] 检查Python版本..."
python_version_check=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
if [[ "$(echo "$python_version_check >= 3.12" | bc)" == "0" ]]; then
    echo "错误: 需要Python 3.12或更高版本，当前版本: $python_version_check"
    echo "请先安装Python 3.12: https://www.python.org/downloads/"
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

pip install pandas>=2.2.0 SQLAlchemy>=2.0.0 pypdf>=6.4.0 docx2python>=3.5.0 openpyxl>=3.1.0 python-pptx>=1.0.0 psycopg2-binary>=2.9.0 bcrypt>=4.0.0 python-dotenv>=1.2.0
echo "✓ Python依赖安装完成"

# 5. 数据库配置
echo "[5/6] 数据库配置..."
export PGDATABASE_URL="${PGDATABASE_URL:-postgresql://user:password@localhost:5432/dbname}"
echo "✓ 数据库配置完成 (请确保PGDATABASE_URL环境变量已设置)"

# 6. 前端依赖（可选）
echo "[6/6] 前端依赖..."
echo "如需使用前端可视化，请安装以下依赖："
echo "  - ECharts: https://echarts.apache.org/handbook/zh/get-started/"
echo "  - npm install echarts"
echo "✓ 前端配置说明已提供"

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
