#!/usr/bin/env python3
"""
患者通俗报告生成器
生成适合患者阅读的冠脉造影报告
"""

import os
import sys
import argparse
import base64
import tempfile
from datetime import datetime
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
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def auto_windowing(pixel_array):
    """自动窗宽窗位调整"""
    window_center = 128
    window_width = 256
    min_val = window_center - window_width // 2
    max_val = window_center + window_width // 2
    
    adjusted = np.clip(pixel_array, min_val, max_val)
    adjusted = ((adjusted - min_val) / (max_val - min_val) * 255).astype(np.uint8)
    return adjusted


def load_images(folder_path, max_images=3):
    """加载图像"""
    images = []
    dicom_files = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                fpath = os.path.join(root, file)
                pydicom.dcmread(fpath, stop_before_pixels=True)
                dicom_files.append(fpath)
            except:
                continue
    
    dicom_files.sort()
    
    for i, dcm_path in enumerate(dicom_files[:max_images]):
        try:
            ds = pydicom.dcmread(dcm_path)
            pixel_array = ds.pixel_array
            
            if pixel_array.ndim == 3:
                pixel_array = pixel_array[pixel_array.shape[0] // 2]
            
            adjusted = auto_windowing(pixel_array)
            
            img = Image.fromarray(adjusted)
            png_path = os.path.join(tempfile.gettempdir(), f"patient_img_{i}.png")
            img.save(png_path)
            
            images.append({
                'path': png_path,
                'base64': encode_image(png_path)
            })
        except Exception as e:
            logger.warning(f"处理失败: {e}")
            continue
    
    return images


def get_patient_info_from_dicom(folder_path):
    """从DICOM提取患者信息"""
    patient_info = {}
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                fpath = os.path.join(root, file)
                ds = pydicom.dcmread(fpath, stop_before_pixels=True)
                
                patient_info = {
                    'patient_name': getattr(ds, 'PatientName', '未知'),
                    'patient_id': getattr(ds, 'PatientID', '未知'),
                    'study_date': getattr(ds, 'StudyDate', '未知'),
                    'modality': getattr(ds, 'Modality', '未知'),
                    'study_description': getattr(ds, 'StudyDescription', '冠脉造影'),
                }
                
                # 格式化日期
                if patient_info['study_date'] != '未知':
                    try:
                        date_str = str(patient_info['study_date'])
                        patient_info['study_date'] = f"{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日"
                    except:
                        pass
                
                break
            except:
                continue
        break
    
    return patient_info


def generate_patient_report(images, api_key, patient_info=None):
    """生成患者通俗报告"""
    
    client = OpenAI(api_key=api_key)
    
    # 通俗易懂的系统提示
    system_prompt = """你是一位心血管影像科医生，正向患者解释他的冠脉造影检查结果。

请用患者能听懂的话来解释，不要用专业术语，或者解释清楚专业术语的意思。

报告应该这样写：

【您的检查结果】
用大白话告诉患者看到了什么

【血管情况】
- 心脏右边的血管（右冠状动脉）怎么样
- 心脏左边的血管（左前降支、左回旋支）怎么样
- 有没有堵？堵了多少？

【医生建议】
根据影像，给出通俗易懂的建议

注意事项：
- 用"您"称呼患者
- 避免"狭窄"、"闭塞"这样的词，或者立即解释是什么意思
- 比如说"血管堵了50%"而不是"狭窄50%"
- 保持积极但诚实的态度
- 适当安慰患者
"""

    user_prompt = """请分析以下冠脉造影影像，为患者生成一份通俗易懂的报告。

如果知道患者信息，请参考：
患者姓名：{patient_name}
检查日期：{study_date}
检查类型：{study_description}

请用通俗易懂的语言解释检查结果。"""

    # 填充患者信息
    p_name = patient_info.get('patient_name', '未知') if patient_info else '未知'
    p_date = patient_info.get('study_date', '未知') if patient_info else '未知'
    p_desc = patient_info.get('study_description', '冠脉造影') if patient_info else '冠脉造影'
    
    user_prompt = user_prompt.format(
        patient_name=p_name,
        study_date=p_date,
        study_description=p_desc
    )
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 添加图像
        for img in images:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img['base64']}"}}
                ]
            })
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1500,
            temperature=0.5
        )
        
        report = response.choices[0].message.content
        
        # 添加报告头部
        header = f"""
{'='*60}
冠脉造影患者通俗报告
{'='*60}

检查日期：{p_date}
检查类型：{p_desc}
报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}

{'='*60}

"""
        
        return header + report
        
    except Exception as e:
        logger.error(f"API调用失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='生成患者通俗报告')
    parser.add_argument('input', help='DICOM文件夹路径')
    parser.add_argument('--api-key', '-k', required=True, help='OpenAI API Key')
    parser.add_argument('--output', '-o', default='patient_report.txt', help='输出文件')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.error(f"路径不存在: {args.input}")
        return
    
    # 获取患者信息
    logger.info("正在读取患者信息...")
    patient_info = get_patient_info_from_dicom(args.input)
    logger.info(f"患者: {patient_info.get('patient_name', '未知')}")
    
    # 加载图像
    logger.info("正在加载图像...")
    images = load_images(args.input)
    logger.info(f"加载了 {len(images)} 幅图像")
    
    if not images:
        logger.error("无法加载图像")
        return
    
    # 生成报告
    logger.info("正在生成通俗报告...")
    report = generate_patient_report(images, args.api_key, patient_info)
    
    if report:
        print(report)
        
        # 保存
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"报告已保存到: {args.output}")
    else:
        logger.error("报告生成失败")


if __name__ == '__main__':
    main()
