#!/usr/bin/env python3
"""
GPT-4o AI 冠脉造影分析报告生成脚本
使用OpenAI GPT-4o多模态能力分析医学影像
"""

import os
import sys
import argparse
import base64
import json
from pathlib import Path
import logging

# 尝试导入需要的库
try:
    import openai
    from openai import OpenAI
except ImportError:
    print("请安装 openai: pip install openai")
    sys.exit(1)

try:
    import pydicom
    from PIL import Image
    import numpy as np
except ImportError:
    print("请安装依赖: pip install pydicom pillow numpy")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def encode_image(image_path):
    """将图像编码为base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def load_dicom_images(folder_path, max_images=4):
    """加载DICOM图像并转换为PNG"""
    import tempfile
    
    images = []
    dicom_files = []
    
    # 查找DICOM文件
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.dcm'):
                dicom_files.append(os.path.join(root, file))
            else:
                # 也尝试非.dcm扩展名的文件
                try:
                    fpath = os.path.join(root, file)
                    ds = pydicom.dcmread(fpath, stop_before_pixels=True)
                    dicom_files.append(fpath)
                except:
                    continue
    
    dicom_files.sort()
    
    if not dicom_files:
        logger.error("未找到DICOM文件")
        return []
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    # 加载图像
    for i, dcm_path in enumerate(dicom_files[:max_images]):
        try:
            ds = pydicom.dcmread(dcm_path)
            pixel_array = ds.pixel_array
            
            # 处理多帧
            if pixel_array.ndim == 3:
                # 取中间帧
                frame_idx = pixel_array.shape[0] // 2
                pixel_array = pixel_array[frame_idx]
            
            # 自动窗宽窗位
            window_center = 128
            window_width = 256
            min_val = window_center - window_width // 2
            max_val = window_center + window_width // 2
            
            adjusted = np.clip(pixel_array, min_val, max_val)
            adjusted = ((adjusted - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            
            # 保存为PNG
            img = Image.fromarray(adjusted)
            png_path = os.path.join(temp_dir, f"image_{i}.png")
            img.save(png_path)
            
            images.append({
                'path': png_path,
                'base64': encode_image(png_path),
                'dicom': dcm_path
            })
            
            logger.info(f"处理图像: {dcm_path}")
            
        except Exception as e:
            logger.warning(f"处理失败 {dcm_path}: {e}")
            continue
    
    return images


def analyze_with_gpt4o(images, client, patient_info=None):
    """使用GPT-4o分析图像"""
    
    # 构建提示词
    system_prompt = """你是一位专业的心血管影像分析专家，负责分析冠脉造影（CAG）影像。

请分析提供的医学影像，并给出专业的分析报告。报告应该包括：

1. **影像质量评估** - 影像清晰度、对比度是否适合诊断
2. **血管走向描述** - 主要冠状动脉（LAD、LCX、RCA等）的走向和分布
3. **病变分析** - 如果发现狭窄或阻塞，描述位置、程度
4. **血流评估** - TIMI血流分级（如适用）
5. **诊疗建议** - 基于影像的临床建议

请用通俗易懂的中文表述，让患者也能理解。
"""

    user_prompt = """请分析以下冠脉造影影像："""

    # 构建消息
    messages = [
        {"type": "text", "text": system_prompt},
        {"type": "text", "text": user_prompt}
    ]
    
    # 添加图像
    for img in images:
        messages.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img['base64']}"
            }
        })
    
    # 如果有患者信息
    if patient_info:
        messages.append({
            "type": "text",
            "text": f"\n\n患者信息：{patient_info}"
        })
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": msg["role"], "content": msg["content"] if "text" in msg else msg["type"]}
                for msg in [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt + "\n" + 
                     "\n".join([f"[图像{i+1}]" for i in range(len(images))])}
                ]
            ] + [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img['base64']}"}
                        }
                    ]
                }
                for img in images
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"GPT-4o API调用失败: {e}")
        return None


def generate_report(images, api_key, patient_info=None, output_file=None):
    """生成分析报告"""
    
    # 初始化OpenAI客户端
    client = OpenAI(api_key=api_key)
    
    logger.info("正在调用GPT-4o分析图像...")
    
    report = analyze_with_gpt4o(images, client, patient_info)
    
    if report:
        print("\n" + "="*60)
        print("冠脉造影AI分析报告")
        print("="*60)
        print(report)
        print("="*60)
        
        # 保存报告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# 冠脉造影AI分析报告\n\n")
                f.write(report)
            logger.info(f"报告已保存到: {output_file}")
        
        return report
    else:
        logger.error("报告生成失败")
        return None


def main():
    parser = argparse.ArgumentParser(description='GPT-4o 冠脉造影分析')
    parser.add_argument('input', help='DICOM文件夹路径')
    parser.add_argument('--api-key', '-k', required=True, help='OpenAI API Key')
    parser.add_argument('--output', '-o', default='report.md', help='输出报告文件')
    parser.add_argument('--patient-info', '-p', help='患者信息（可选）')
    parser.add_argument('--max-images', '-n', type=int, default=4, help='最大图像数量')
    
    args = parser.parse_args()
    
    input_path = args.input
    
    if not os.path.exists(input_path):
        logger.error(f"路径不存在: {input_path}")
        return
    
    # 加载图像
    logger.info("正在加载DICOM图像...")
    images = load_dicom_images(input_path, args.max_images)
    
    if not images:
        logger.error("未能加载任何图像")
        return
    
    logger.info(f"成功加载 {len(images)} 幅图像")
    
    # 生成报告
    generate_report(images, args.api_key, args.patient_info, args.output)


if __name__ == '__main__':
    main()
