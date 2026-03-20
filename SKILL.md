---
name: cardiology-assistant
description: |
  DICOM 医学影像分析与冠脉造影助手。处理 DICOM 文件：读取元数据（含脱敏）、转 PNG 图像、批量扫描文件夹、关键帧提取、视频分析（血管追踪/狭窄标注/GIF）、DICOM→视频导出、AI智能分析（GPT-4o）、患者通俗报告、术前术后对比、PDF报告生成。触发词：DICOM、医学影像、冠脉造影、CAG、CT、MRI、X光、心脏、支架、PCI、冠脉、心血管、胸闷、胸痛。
---

# 心脏病医学影像与诊疗助手

> ⚠️ 免责声明：本技能仅提供影像技术分析，不能替代专业医疗诊断。所有医疗决策请遵医嘱。

## 依赖安装

**基础依赖：**

    pip install pydicom pillow numpy
    pip install opencv-python scipy  # 可选

**AI 分析依赖（可选）：**

    pip install openai  # GPT-4o 分析
    pip install reportlab  # PDF 报告生成

## 功能与用法

### A. DICOM 元数据分析

    python scripts/dicom_read.py /path/to/file
    python scripts/dicom_read.py /path/to/file --anonymize
    python scripts/dicom_read.py /path/to/file --json
    python scripts/dicom_batch.py /path/to/folder --anonymize --json

### B. DICOM → 图像转换

    python scripts/dicom_convert.py input.dcm output.png
    python scripts/dicom_convert.py input.dcm output.png --wc 128 --ww 256
    python scripts/dicom_convert.py /dicom/folder /output/dir --batch

### B. 关键帧提取

    python scripts/keyframe_extract.py /path/to/input -o frames/ -n 5

### B. 视频分析

    python scripts/video_analyze.py video.avi -o analysis/ --gif --track --stenosis
    python scripts/video_export.py /dicom/folder output.mp4 --fps 15
    python scripts/video_export.py input.avi compressed.mp4 --compress --target-size 20

### C. 生成分析报告

    python scripts/generate_report.py /path/to/dicom -o report.md --anonymize -n 8

### D. AI 智能分析（新增）

**GPT-4o 影像分析：**

    python scripts/ai_report.py /path/to/dicom -k YOUR_API_KEY -o ai_report.md
    python scripts/ai_report.py /path/to/dicom --api-key YOUR_API_KEY --max-images 4

**患者通俗报告（大白话）：**

    python scripts/patient_report.py /path/to/dicom -k YOUR_API_KEY -o patient_report.txt

**术前术后对比分析：**

    python scripts/compare_prepost.py /pre_op_folder /post_op_folder -k YOUR_API_KEY

**PDF 报告生成：**

    python scripts/generate_pdf.py --output report.pdf --patient-name "张三" --images img1.png img2.png --report ai_report.md

## 隐私安全

- `--anonymize` 参数对所有敏感字段脱敏
- 建议在非安全环境下默认启用脱敏

## 支持模态

- XA → X射线血管造影 (CAG)
- CT → 计算机断层扫描 (CTA)
- MR → 磁共振成像
- CR/DX → 数字化X射线
- US → 超声检查
