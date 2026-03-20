#!/usr/bin/env python3
"""
术前术后对比分析脚本
对比两次冠脉造影检查，评估手术效果
"""

import os
import sys
import argparse
import base64
import json
import tempfile
from pathlib import Path
import logging

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


def auto_windowing(pixel_array):
    """自动窗宽窗位调整"""
    window_center = 128
    window_width = 256
    min_val = window_center - window_width // 2
    max_val = window_center + window_width // 2
    
    adjusted = np.clip(pixel_array, min_val, max_val)
    adjusted = ((adjusted - min_val) / (max_val - min_val) * 255).astype(np.uint8)
    return adjusted


def load_images_from_folder(folder_path, max_images=3):
    """从文件夹加载图像"""
    images = []
    dicom_files = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                fpath = os.path.join(root, file)
                ds = pydicom.dcmread(fpath, stop_before_pixels=True)
                dicom_files.append(fpath)
            except:
                continue
    
    dicom_files.sort()
    
    for i, dcm_path in enumerate(dicom_files[:max_images]):
        try:
            ds = pydicom.dcmread(dcm_path)
            pixel_array = ds.pixel_array
            
            if pixel_array.ndim == 3:
                frame_idx = pixel_array.shape[0] // 2
                pixel_array = pixel_array[frame_idx]
            
            adjusted = auto_windowing(pixel_array)
            
            img = Image.fromarray(adjusted)
            png_path = os.path.join(tempfile.gettempdir(), f"prepost_{i}.png")
            img.save(png_path)
            
            images.append({
                'path': png_path,
                'base64': encode_image(png_path)
            })
            
        except Exception as e:
            logger.warning(f"处理失败: {e}")
            continue
    
    return images


def compare_with_gpt4o(pre_images, post_images, client):
    """使用GPT-4o进行术前术后对比"""
    
    system_prompt = """你是一位专业的心血管影像分析专家，负责对比分析术前和术后的冠脉造影影像。

请对比分析以下两组影像（术前 vs 术后），给出专业的对比报告，包括：

1. **手术前后血管通畅程度对比**
2. **狭窄部位的变化** - 术前狭窄位置和程度 vs 术后改善情况
3. **血流改善评估** - TIMI血流分级变化
4. **手术效果评价** - 支架置入效果、血流恢复情况
5. **术后建议** - 后续治疗和随访建议

请用通俗易懂的中文表述。
"""

    user_prompt = f"""请对比分析以下术前和术后的冠脉造影影像：

术前影像（术前半数）：
{chr(10).join([f"[术前图像{i+1}]" for i in range(len(pre_images))])}

术后影像（术中/术后）：
{chr(10).join([f"[术后图像{i+1}]" for i in range(len(post_images))])}
"""

    try:
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 添加术前图像
        for img in pre_images:
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img['base64']}"}
                    }
                ]
            })
        
        # 添加术后图像
        for img in post_images:
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img['base64']}"}
                    }
                ]
            })
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ] + [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img['base64']}"}}
                    ]
                }
                for img in pre_images + post_images
            ],
            max_tokens=2500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"GPT-4o API调用失败: {e}")
        return None


def generate_comparison_report(pre_folder, post_folder, api_key, output_file=None):
    """生成对比报告"""
    
    client = OpenAI(api_key=api_key)
    
    logger.info("正在加载术前图像...")
    pre_images = load_images_from_folder(pre_folder)
    logger.info(f"加载了 {len(pre_images)} 幅术前图像")
    
    logger.info("正在加载术后图像...")
    post_images = load_images_from_folder(post_folder)
    logger.info(f"加载了 {len(post_images)} 幅术后图像")
    
    if not pre_images or not post_images:
        logger.error("图像加载失败")
        return None
    
    logger.info("正在调用GPT-4o进行对比分析...")
    
    report = compare_with_gpt4o(pre_images, post_images, client)
    
    if report:
        print("\n" + "="*60)
        print("冠脉造影 术前术后对比分析报告")
        print("="*60)
        print(f"\n术前检查: {pre_folder}")
        print(f"术后检查: {post_folder}")
        print("\n" + "-"*60)
        print(report)
        print("="*60)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# 冠脉造影术前术后对比分析报告\n\n")
                f.write(f"**术前检查**: {pre_folder}\n\n")
                f.write(f"**术后检查**: {post_folder}\n\n")
                f.write("---\n\n")
                f.write(report)
            logger.info(f"报告已保存到: {output_file}")
        
        return report
    else:
        logger.error("对比分析失败")
        return None


def main():
    parser = argparse.ArgumentParser(description='术前术后对比分析')
    parser.add_argument('pre_op', help='术前DICOM文件夹路径')
    parser.add_argument('post_op', help='术后DICOM文件夹路径')
    parser.add_argument('--api-key', '-k', required=True, help='OpenAI API Key')
    parser.add_argument('--output', '-o', default='comparison_report.md', help='输出报告文件')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pre_op) or not os.path.exists(args.post_op):
        logger.error("路径不存在")
        return
    
    generate_comparison_report(args.pre_op, args.post_op, args.api_key, args.output)


if __name__ == '__main__':
    main()
