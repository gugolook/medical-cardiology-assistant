# 使用指南

## 快速开始

### 1. DICOM 元数据分析

```bash
# 基础分析（读取患者信息、检查信息、设备信息等）
python scripts/dicom_read.py file.dcm

# 脱敏输出（隐藏敏感信息）
python scripts/dicom_read.py file.dcm --anonymize

# JSON 格式输出（便于程序处理）
python scripts/dicom_read.py file.dcm --json

# 批量分析文件夹
python scripts/dicom_batch.py /path/to/folder --anonymize --json
```

### 2. DICOM → PNG 图像转换

```bash
# 单文件转换
python scripts/dicom_convert.py input.dcm output.png

# 调整窗宽窗位
python scripts/dicom_convert.py input.dcm output.png --wc 128 --ww 256

# 批量转换整个文件夹
python scripts/dicom_convert.py /dicom/folder /output/dir --batch
```

### 3. 关键帧提取

从多帧 DICOM 文件中提取最佳质量的帧：

```bash
# 提取 5 个关键帧
python scripts/keyframe_extract.py /path/to/dicom -o frames/ -n 5

# 提取 10 个关键帧
python scripts/keyframe_extract.py /path/to/dicom -o frames/ -n 10
```

### 4. 视频导出

```bash
# DICOM 序列转 MP4 视频
python scripts/video_export.py /dicom/folder output.mp4 --fps 15

# 视频压缩（控制目标大小）
python scripts/video_export.py input.mp4 compressed.mp4 --compress --target-size 20

# 视频格式转换
python scripts/video_export.py input.avi output.mp4
```

### 5. 视频分析

```bash
# 完整分析（血管追踪 + 狭窄标注 + GIF 生成）
python scripts/video_analyze.py video.mp4 -o analysis/ --gif --track --stenosis

# 仅生成 GIF
python scripts/video_analyze.py video.mp4 -o analysis/ --gif

# 仅血管追踪
python scripts/video_analyze.py video.mp4 -o analysis/ --track
```

### 6. AI 智能分析

**注意：需要 OpenAI API Key**

```bash
# GPT-4o 影像分析
python scripts/ai_report.py /path/to/dicom -k YOUR_API_KEY -o ai_report.md

# 限制处理的图像数量
python scripts/ai_report.py /path/to/dicom -k YOUR_API_KEY --max-images 4

# 包含患者信息
python scripts/ai_report.py /path/to/dicom -k YOUR_API_KEY --patient-info "患者：张三，年龄：65岁" -o report.md
```

### 7. 患者通俗报告

生成用大白话解释病情的报告，适合患者阅读：

```bash
python scripts/patient_report.py /path/to/dicom -k YOUR_API_KEY -o patient_report.txt
```

### 8. 术前术后对比分析

```bash
# 对比两次检查
python scripts/compare_prepost.py /pre_op_folder /post_op_folder -k YOUR_API_KEY

# 指定输出文件
python scripts/compare_prepost.py /pre_op_folder /post_op_folder -k YOUR_API_KEY -o comparison.md
```

### 9. PDF 报告生成

```bash
# 基础 PDF 报告
python scripts/generate_pdf.py --output report.pdf --patient-name "张三" --images img1.png img2.png --report ai_report.md

# 包含患者 ID
python scripts/generate_pdf.py --output report.pdf --patient-name "张三" --patient-id "P12345" --images img1.png img2.png --report ai_report.md

# 指定检查日期
python scripts/generate_pdf.py --output report.pdf --patient-name "张三" --date "2026年3月20日" --images img1.png img2.png --report ai_report.md
```

### 10. 生成 Markdown 报告

```bash
# 基础报告
python scripts/generate_report.py /path/to/dicom -o report.md

# 脱敏报告
python scripts/generate_report.py /path/to/dicom -o report.md --anonymize

# 指定关键帧数量
python scripts/generate_report.py /path/to/dicom -o report.md --num-frames 8
```

## 典型工作流程

### 工作流 1：基础 DICOM 分析

```bash
# 1. 批量读取元数据
python scripts/dicom_batch.py /path/to/dicom --json > metadata.json

# 2. 批量转换为 PNG
python scripts/dicom_convert.py /path/to/dicom /output/png --batch

# 3. 提取关键帧
python scripts/keyframe_extract.py /path/to/dicom -o keyframes/ -n 10
```

### 工作流 2：AI 辅助诊断

```bash
# 1. 转换图像
python scripts/dicom_convert.py /path/to/dicom /output/png --batch

# 2. GPT-4o 分析
python scripts/ai_report.py /path/to/dicom -k YOUR_API_KEY -o ai_report.md

# 3. 生成患者通俗报告
python scripts/patient_report.py /path/to/dicom -k YOUR_API_KEY -o patient_report.txt

# 4. 生成专业 PDF 报告
python scripts/generate_pdf.py --output final_report.pdf --patient-name "张三" --images keyframes/*.png --report ai_report.md
```

### 工作流 3：视频分析

```bash
# 1. DICOM 转视频
python scripts/video_export.py /path/to/dicom output.mp4 --fps 15

# 2. 视频分析
python scripts/video_analyze.py output.mp4 -o analysis/ --gif --track --stenosis

# 3. 查看生成的文件
# analysis/keyframe_*.png - 关键帧
# analysis/vessel_analysis.png - 血管追踪结果
# analysis/stenosis_marked.png - 狭窄标注结果
# analysis/angiography.gif - 动态 GIF
```

### 工作流 4：术前术后对比

```bash
# 1. 术前影像分析
python scripts/ai_report.py /pre_op_folder -k YOUR_API_KEY -o pre_op.md

# 2. 术后影像分析
python scripts/ai_report.py /post_op_folder -k YOUR_API_KEY -o post_op.md

# 3. 对比分析
python scripts/compare_prepost.py /pre_op_folder /post_op_folder -k YOUR_API_KEY -o comparison.md

# 4. 生成 PDF 报告
python scripts/generate_pdf.py --output comparison_report.pdf --patient-name "张三" --report comparison.md
```

## 常用参数说明

### 窗宽窗位（Window Center/Width）

用于调整医学图像的对比度和亮度：

- `--wc`: 窗位（Window Center），控制亮度
- `--ww`: 窗宽（Window Width），控制对比度

常用预设：
- 肺窗：WC = -600, WW = 1500
- 骨窗：WC = 500, WW = 2000
- 软组织窗：WC = 40, WW = 400

### 脱敏选项

`--anonymize`: 隐藏患者敏感信息
- 姓名、ID、地址 → `***`
- 出生日期 → 仅保留年份（如：1990年**月**日）
- 医生姓名、机构名称 → 首字 + `***`

### API Key 管理

推荐使用环境变量：

```bash
# Windows CMD
set OPENAI_API_KEY=your_key_here

# Windows PowerShell
$env:OPENAI_API_KEY="your_key_here"

# macOS/Linux
export OPENAI_API_KEY=your_key_here

# 然后在脚本中引用
python scripts/ai_report.py /path/to/dicom -k %OPENAI_API_KEY%  # Windows CMD
python scripts/ai_report.py /path/to/dicom -k $env:OPENAI_API_KEY  # PowerShell
python scripts/ai_report.py /path/to/dicom -k $OPENAI_API_KEY  # macOS/Linux
```

## 故障排除

### 错误：ModuleNotFoundError: No module named 'lib'

**原因**：脚本需要从项目根目录运行

**解决方案**：
```bash
# 错误示例
cd medical-cardiology-assistant/scripts
python dicom_read.py file.dcm  # ❌

# 正确示例
cd medical-cardiology-assistant
python scripts/dicom_read.py file.dcm  # ✅
```

### 错误：pydicom.errors.InvalidDicomError

**原因**：文件不是有效的 DICOM 文件

**解决方案**：
- 检查文件扩展名是否为 `.dcm`
- 使用 `find_dicom_files()` 函数自动识别 DICOM 文件
- 部分影像设备生成的 DICOM 文件没有标准扩展名

### 错误：OpenAI API 调用失败

**原因**：
- API Key 无效或过期
- 账户余额不足
- 网络连接问题

**解决方案**：
- 检查 API Key 是否正确
- 确认 OpenAI 账户状态
- 检查网络连接和代理设置

### 错误：无法读取多帧 DICOM

**原因**：多帧 DICOM 文件处理方式不同

**解决方案**：
- 使用 `--frame` 参数指定帧索引
- 或使用 `keyframe_extract.py` 自动提取最佳帧
- 对于多帧视频，先转换为视频格式再分析

## 性能优化建议

### 大批量处理

对于包含大量 DICOM 文件的文件夹：

1. 使用 `--batch` 选项批量处理
2. 考虑并行处理（需要修改脚本）
3. 使用 SSD 存储提高读取速度

### 内存管理

处理大文件或大量文件时：

1. 逐个处理，避免一次性加载所有文件
2. 使用 `stop_before_pixels=True` 仅读取元数据
3. 及时关闭和释放文件句柄

### GPU 加速

如果需要处理大量视频：

1. 安装支持 GPU 的 OpenCV
2. 使用 CUDA 加速视频处理
3. 批量处理时监控 GPU 内存使用

## 安全注意事项

1. **隐私保护**
   - 使用 `--anonymize` 脱敏患者信息
   - 不要上传未脱敏的 DICOM 文件到云服务
   - 遵守当地医疗数据保护法规（如 HIPAA）

2. **API Key 管理**
   - 不要将 API Key 硬编码到代码中
   - 使用环境变量或配置文件
   - 定期轮换 API Key

3. **医疗诊断免责**
   - AI 分析结果仅供参考
   - 所有医疗决策需经专业医生确认
   - 不要仅依赖自动报告做诊断

## 进阶用法

### 自定义窗口函数

修改 `lib/dicom_utils.py` 中的 `auto_windowing` 函数：

```python
def custom_windowing(pixel_array, window_center, window_width):
    # 自定义窗宽窗位逻辑
    min_val = window_center - window_width / 2
    max_val = window_center + window_width / 2
    # ... 你的自定义逻辑
    return adjusted
```

### 扩展脱敏规则

在 `SENSITIVE_TAGS` 中添加更多标签：

```python
SENSITIVE_TAGS = {
    # ... 现有标签
    'AccessionNumber',  # 检查号
    'StudyInstanceUID',  # 研究 UID
}
```

### 集成到其他应用

```python
from lib.dicom_utils import get_dicom_metadata

metadata = get_dicom_metadata('file.dcm')
print(metadata['patient_name'])
print(metadata['modality'])
```

## 获取帮助

```bash
# 查看脚本帮助
python scripts/dicom_read.py --help
python scripts/dicom_convert.py --help
python scripts/ai_report.py --help
# ... 其他脚本同理
```

## 参考资源

- [pydicom 官方文档](https://pydicom.github.io/)
- [OpenAI API 文档](https://platform.openai.com/docs/)
- [DICOM 标准说明](https://www.dicomstandard.org/)
- [reportlab 文档](https://docs.reportlab.com/)
