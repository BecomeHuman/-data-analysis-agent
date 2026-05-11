"""
文档解析工具 - 支持解析 PDF, Word, Excel, CSV, TXT 等常见文档格式
"""
import os
import logging
from typing import Optional
from io import BytesIO
import pandas as pd
from pypdf import PdfReader
from docx2python import docx2python
import chardet

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: str) -> str:
    """
    从文件路径提取文本内容
    
    Args:
        file_path: 文件的本地路径或URL
        
    Returns:
        提取的文本内容
    """
    if not os.path.exists(file_path) and not file_path.startswith(('http://', 'https://')):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 根据文件扩展名选择解析方法
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            return _extract_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return _extract_from_docx(file_path)
        elif ext in ['.xlsx', '.xls']:
            return _extract_from_excel(file_path)
        elif ext == '.csv':
            return _extract_from_csv(file_path)
        elif ext in ['.txt', '.md']:
            return _extract_from_text(file_path)
        else:
            return f"[不支持解析该格式: {ext}]"
    except Exception as e:
        logger.error(f"解析文件失败: {file_path}, error: {e}")
        return f"[解析失败] {str(e)}"


def _extract_from_pdf(file_path: str) -> str:
    """从PDF提取文本"""
    if file_path.startswith(('http://', 'https://')):
        import requests
        resp = requests.get(file_path, timeout=60)
        resp.raise_for_status()
        stream = BytesIO(resp.content)
    else:
        stream = file_path
    
    reader = PdfReader(stream)
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n\n".join(text_parts)


def _extract_from_docx(file_path: str) -> str:
    """从Word文档提取文本"""
    if file_path.startswith(('http://', 'https://')):
        import requests
        resp = requests.get(file_path, timeout=60)
        resp.raise_for_status()
        stream = BytesIO(resp.content)
    else:
        stream = file_path
    
    doc_result = docx2python(stream)
    all_parts = []
    
    for section in doc_result.body:
        if isinstance(section, list):
            for item in section:
                if isinstance(item, list):
                    for sub_item in item:
                        if isinstance(sub_item, str) and sub_item.strip():
                            all_parts.append(sub_item.strip())
                        elif isinstance(sub_item, list):
                            row_text = "\n".join([str(cell).strip() for cell in sub_item if str(cell).strip()])
                            if row_text:
                                all_parts.append(row_text)
                elif isinstance(item, str) and item.strip():
                    all_parts.append(item.strip())
    
    doc_result.close()
    return "\n\n".join(all_parts)


def _extract_from_excel(file_path: str) -> str:
    """从Excel文件提取文本"""
    if file_path.startswith(('http://', 'https://')):
        import requests
        resp = requests.get(file_path, timeout=60)
        resp.raise_for_status()
        df = pd.read_excel(BytesIO(resp.content))
    else:
        df = pd.read_excel(file_path)
    
    return df.to_string()


def _extract_from_csv(file_path: str) -> str:
    """从CSV文件提取文本"""
    if file_path.startswith(('http://', 'https://')):
        import requests
        resp = requests.get(file_path, timeout=60)
        resp.raise_for_status()
        df = pd.read_csv(BytesIO(resp.content))
    else:
        df = pd.read_csv(file_path)
    
    return df.to_string()


def _extract_from_text(file_path: str) -> str:
    """从文本文件提取内容"""
    if file_path.startswith(('http://', 'https://')):
        import requests
        resp = requests.get(file_path, timeout=60)
        resp.raise_for_status()
        content = resp.content
    else:
        with open(file_path, 'rb') as f:
            content = f.read()
    
    # 检测编码
    charset = chardet.detect(content)
    encoding = charset.get('encoding', 'utf-8') if charset else 'utf-8'
    
    try:
        return content.decode(encoding)
    except (UnicodeDecodeError, AttributeError):
        return content.decode('utf-8', errors='ignore')


def get_file_info(file_path: str) -> dict:
    """获取文件基本信息"""
    ext = os.path.splitext(file_path)[1].lower()
    return {
        "file_name": os.path.basename(file_path),
        "file_type": ext,
        "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
    }
