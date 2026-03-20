# 🫀 Cardiology Assistant — DICOM 医学影像分析 Skill

[![Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/openclaw/openclaw)
[![Python](https://img.shields.io/badge/python-3.8+-green)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> DICOM 医学影像处理与冠脉造影分析的 OpenClaw Skill。支持基础影像处理、AI 智能分析、术前术后对比、PDF 报告生成。

⚠️ **免责声明**：本技能仅提供影像技术分析，不能替代专业医疗诊断。所有医疗决策请遵医嘱。

---

## ✨ 功能特性

### A. DICOM 基础处理
| 能力 | 说明 | 脚本 |
|------|------|------|
| 元数据分析 | 读取患者/检查/设备信息，支持脱敏 | `dicom_read.py` |
| 批量扫描 | 文件夹级统计与处理 | `dicom_batch.py` |
| DICOM → PNG | 转图像，支持窗宽窗位调整 | `dicom_convert.py` |
| 关键帧提取 | 从多帧 DICOM 提取最佳显影帧 | `keyframe_extract.py` |

### B. 视频处理
| 能力 | 说明 | 脚本 |
|------|------|------|
| 视频导出 | DICOM → MP4，支持帧率控制 | `video_export.py` |
| 视频分析 | 血管追踪、狭窄标注、GIF 生成 | `video_analyze.py` |
| 视频压缩 | 压缩转码，控制目标大小 | `video_export.py --compress` |

### C. 报告生成
| 能力 | 说明 | 脚本 |
|------|------|------|
| 基础报告 | Markdown 格式分析报告 | `generate_report.py` |
| AI 智能分析 | GPT-4o 影像解读 | `ai_report.py` |
| 患者通俗报告 | 大白话解释病情 | `patient_report.py` |
| 术前术后对比 | 手术效果对比分析 | `compare_prepost.py` |
| PDF 报告 | 专业格式报告输出 | `generate_pdf.py` |

---

## 📦 安装

### 基础依赖
```bash
pip install pydicom pillow numpy
pip install opencv-python scipy  # 可选，用于视频处理
```

### AI 分析依赖（可选）
```bash
pip install openai      # GPT-4o 分析
pip install reportlab   # PDF 报告生成
```

---

## 🚀 快速开始

### 1. DICOM 元数据分析
```bash
# 基础分析
python scripts/dicom_read.py file.dcm

# 脱敏输出
python scripts/dicom_read.py file.dcm --anonymize

# JSON 格式输出
python scripts/dicom_read.py file.dcm --json
```

### 2. 图像转换
```bash
# 单文件转换
python scripts/dicom_convert.py input.dcm output.png

# 调整窗宽窗位
python scripts/dicom_convert.py input.dcm output.png --wc 128 --ww 256

# 批量转换
python scripts/dicom_convert.py /dicom/folder /output/dir --batch
```

### 3. 关键帧提取
```bash
python scripts/keyframe_extract.py /path/to/dicom -o frames/ -n 5
```

### 4. 视频导出与分析
```bash
# DICOM 转 MP4
python scripts/video_export.py /dicom/folder output.mp4 --fps 15

# 视频分析（血管追踪 + 狭窄标注 + GIF）
python scripts/video_analyze.py video.mp4 -o analysis/ --gif --track --stenosis

# 视频压缩
python scripts/video_export.py input.mp4 compressed.mp4 --compress --target-size 20
```

### 5. AI 智能分析
```bash
# GPT-4o 影像分析
python scripts/ai_report.py /path/to/dicom -k YOUR_API_KEY -o ai_report.md

# 患者通俗报告
python scripts/patient_report.py /path/to/dicom -k YOUR_API_KEY -o patient_report.txt

# 术前术后对比
python scripts/compare_prepost.py /pre_op_folder /post_op_folder -k YOUR_API_KEY

# PDF 报告生成
python scripts/generate_pdf.py --output report.pdf --patient-name "张三" --images img1.png img2.png --report ai_report.md
```

### 6. 生成分析报告
```bash
python scripts/generate_report.py /path/to/dicom -o report.md --anonymize -n 8
```

---

## 🔒 隐私安全

DICOM 文件包含患者敏感信息。使用 `--anonymize` 选项进行脱敏：

| 字段 | 脱敏方式 |
|------|----------|
| 姓名/ID/地址 | 替换为 `***` |
| 出生日期 | 仅保留年份 |
| 医生名/机构名 | 保留首字 + `***` |

**建议**：在非安全环境下默认启用脱敏。

---

## 📊 支持模态

| 模态 | 说明 |
|------|------|
| **XA** | X射线血管造影 (CAG) - 冠脉造影 |
| **CT** | 计算机断层扫描 (CTA) |
| **MR** | 磁共振成像 |
| **CR/DX** | 数字化X射线 |
| **US** | 超声检查 |

---

## 🏗️ 项目结构

```
cardiology-assistant/
├── scripts/           # 核心脚本
│   ├── dicom_read.py
│   ├── dicom_convert.py
│   ├── dicom_batch.py
│   ├── keyframe_extract.py
│   ├── video_export.py
│   ├── video_analyze.py
│   ├── generate_report.py
│   ├── ai_report.py          # AI 分析
│   ├── patient_report.py     # 患者报告
│   ├── compare_prepost.py    # 术前术后对比
│   └── generate_pdf.py       # PDF 生成
├── lib/               # 工具库
├── templates/         # 报告模板
├── SKILL.md          # Skill 定义
├── README.md         # 本文件
└── LICENSE.txt       # MIT 许可证
```

---

## 📝 设计理念

- **技术层**：Skill 负责 DICOM 解析、图像转换、关键帧提取等专业技术处理
- **AI 层**：支持 GPT-4o 等多模态模型进行智能分析
- **隐私优先**：内置脱敏功能，保护患者隐私
- **模块化**：各功能独立，按需使用

---

## 📄 License

MIT License - 详见 [LICENSE.txt](LICENSE.txt)
