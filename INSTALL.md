# 安装指南

## 环境要求

- Python 3.8 或更高版本
- pip 包管理器

## 安装步骤

### 1. 创建虚拟环境（强烈推荐）

```bash
# Windows PowerShell
python -m venv venv
venv\Scripts\activate

# Windows CMD
python -m venv venv
venv\Scripts\activate.bat

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装基础依赖

```bash
pip install pydicom pillow numpy
```

### 3. 安装可选依赖（根据需要）

```bash
# 视频处理功能
pip install opencv-python scipy

# AI 分析功能
pip install openai

# PDF 报告生成
pip install reportlab
```

### 4. 安装所有依赖（一键安装）

```bash
pip install pydicom pillow numpy opencv-python scipy openai reportlab
```

## 验证安装

```bash
# 测试基础功能
python scripts/dicom_read.py --help

# 测试图像转换
python scripts/dicom_convert.py --help
```

## 常见问题

### 模块导入错误

如果出现 `ModuleNotFoundError: No module named 'lib'`，请确保你在项目根目录下运行脚本：

```bash
# 正确 - 在项目根目录下运行
cd medical-cardiology-assistant
python scripts/dicom_read.py file.dcm

# 错误 - 不要直接进入 scripts 目录
cd medical-cardiology-assistant/scripts
python dicom_read.py file.dcm  # 这会报错
```

### OpenAI API Key

使用 AI 分析功能时，需要提供 OpenAI API Key：

```bash
python scripts/ai_report.py /path/to/dicom -k YOUR_API_KEY -o report.md
```

**安全提示**：
- 不要将 API Key 硬编码到代码中
- 使用环境变量存储 API Key（推荐）
- 不要将包含 API Key 的代码上传到公开仓库

## 环境变量配置（推荐）

创建 `.env` 文件（已添加到 .gitignore）：

```env
OPENAI_API_KEY=your_api_key_here
```

然后使用 Python 的 `dotenv` 库加载：

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```

## 卸载

```bash
# 停用虚拟环境
deactivate  # Windows/macOS/Linux 相同

# 删除虚拟环境
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```
