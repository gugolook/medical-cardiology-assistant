#!/usr/bin/env python3
"""
DICOM 工具库 - 医学影像处理辅助函数
提供 DICOM 文件读取、转换、分析等常用功能
"""

import os
import re
from datetime import datetime
from typing import List, Optional, Any
import numpy as np
from PIL import Image
import pydicom


# 敏感标签列表 - 需要脱敏的 DICOM 字段
SENSITIVE_TAGS = {
    'PatientName',           # 患者姓名
    'PatientID',             # 患者ID
    'PatientBirthDate',       # 出生日期
    'PatientAddress',         # 地址
    'PatientSex',             # 性别
    'PatientAge',             # 年龄
    'PatientWeight',          # 体重
    'PatientHeight',          # 身高
    'ReferringPhysicianName', # 转诊医生姓名
    'PerformingPhysicianName',# 执行医生姓名
    'InstitutionName',        # 机构名称
    'StudyDescription',       # 检查描述（可能包含患者信息）
    'SeriesDescription',     # 系列描述
}


def get_tag(ds: pydicom.dataset.FileDataset, tag: str, default: Any = None) -> Any:
    """
    安全获取 DICOM 标签值
    
    Args:
        ds: DICOM 数据集
        tag: 标签名称
        default: 默认值
    
    Returns:
        标签值或默认值
    """
    try:
        if tag in ds:
            value = ds[tag].value
            # 处理 PersonName 对象
            if hasattr(value, 'components'):
                return str(value)
            # 处理多值标签
            if isinstance(value, (list, tuple)):
                return str(value[0]) if value else default
            return str(value) if value is not None else default
    except Exception:
        pass
    return default


def format_date(date_str: Optional[str]) -> str:
    """
    格式化 DICOM 日期字符串
    
    Args:
        date_str: DICOM 日期格式 (YYYYMMDD)
    
    Returns:
        格式化的日期字符串 (YYYY年MM月DD日)
    """
    if not date_str or len(date_str) < 8:
        return "未知"
    try:
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        return f"{year}年{month}月{day}日"
    except Exception:
        return "未知"


def format_time(time_str: Optional[str]) -> str:
    """
    格式化 DICOM 时间字符串
    
    Args:
        time_str: DICOM 时间格式 (HHMMSS或HHMMSS.SSS)
    
    Returns:
        格式化的时间字符串 (HH:MM:SS)
    """
    if not time_str or len(time_str) < 6:
        return "未知"
    try:
        hour = time_str[:2]
        minute = time_str[2:4]
        second = time_str[4:6]
        return f"{hour}:{minute}:{second}"
    except Exception:
        return "未知"


def get_modality_name(code: Optional[str]) -> str:
    """
    获取模态名称
    
    Args:
        code: DICOM 模态代码 (如 'XA', 'CT', 'MR')
    
    Returns:
        模态中文名称
    """
    modality_map = {
        'XA': 'X射线血管造影',
        'CT': '计算机断层扫描',
        'MR': '磁共振成像',
        'CR': '计算机放射摄影',
        'DR': '数字放射摄影',
        'DX': '数字X射线',
        'US': '超声检查',
        'PT': '正电子发射断层',
        'NM': '核医学',
        'RF': '射频影像',
        'SC': '次要捕获',
        'IO': '内窥镜检查',
        'MG': '乳腺X线摄影',
    }
    return modality_map.get(code, code if code else '未知')


def get_sex_name(code: Optional[str]) -> str:
    """
    获取性别名称
    
    Args:
        code: DICOM 性别代码 (M/F/O)
    
    Returns:
        性别中文名称
    """
    sex_map = {
        'M': '男',
        'F': '女',
        'O': '其他',
    }
    return sex_map.get(code, '未知')


def anonymize_value(tag: str, value: Any) -> str:
    """
    脱敏处理敏感标签值
    
    Args:
        tag: 标签名称
        value: 标签值
    
    Returns:
        脱敏后的值
    """
    if value is None or value == '未知':
        return value
    
    value_str = str(value)
    
    # 患者姓名、ID、地址 - 完全脱敏
    if tag in ['PatientName', 'PatientID', 'PatientAddress']:
        return '***'
    
    # 出生日期 - 仅保留年份
    if tag == 'PatientBirthDate':
        if len(value_str) >= 8:
            return value_str[:4] + '年**月**日'
        return value_str[:4] + '****'
    
    # 医生姓名、机构名称 - 保留首字 + 脱敏
    if tag in ['ReferringPhysicianName', 'PerformingPhysicianName', 'InstitutionName']:
        if len(value_str) > 0:
            return value_str[0] + '***'
        return '***'
    
    # 其他敏感标签
    if tag in SENSITIVE_TAGS:
        return '***'
    
    return value_str


def auto_windowing(pixel_array: np.ndarray, 
                   window_center: Optional[float] = None,
                   window_width: Optional[float] = None) -> np.ndarray:
    """
    自动窗宽窗位调整
    
    Args:
        pixel_array: 原始像素数组
        window_center: 窗位 (默认自动计算)
        window_width: 窗宽 (默认自动计算)
    
    Returns:
        调整后的 8 位图像数组
    """
    # 自动计算窗宽窗位（如果未提供）
    if window_center is None or window_width is None:
        min_val = np.min(pixel_array)
        max_val = np.max(pixel_array)
        window_center = (min_val + max_val) / 2
        window_width = (max_val - min_val) / 2
    
    # 应用窗宽窗位
    return apply_windowing(pixel_array, window_center, window_width)


def apply_windowing(pixel_array: np.ndarray,
                   window_center: float,
                   window_width: float) -> np.ndarray:
    """
    应用窗宽窗位调整
    
    Args:
        pixel_array: 原始像素数组
        window_center: 窗位
        window_width: 窗宽
    
    Returns:
        调整后的 8 位图像数组
    """
    min_val = window_center - window_width / 2
    max_val = window_center + window_width / 2
    
    # 裁剪到窗口范围
    clipped = np.clip(pixel_array, min_val, max_val)
    
    # 归一化到 0-255
    normalized = ((clipped - min_val) / (max_val - min_val) * 255).astype(np.uint8)
    
    return normalized


def load_pixel_frame(file_path: str, frame_index: int = 0) -> tuple:
    """
    加载 DICOM 文件的像素帧
    
    Args:
        file_path: DICOM 文件路径
        frame_index: 帧索引（多帧图像）
    
    Returns:
        (ds, pixel_array) DICOM 数据集和像素数组
    """
    ds = pydicom.dcmread(file_path, force=True)
    pixel_array = ds.pixel_array
    
    # 处理多帧图像
    if pixel_array.ndim == 3:
        pixel_array = pixel_array[frame_index]
    
    return ds, pixel_array


def save_frame_as_png(pixel_array: np.ndarray,
                      output_path: str,
                      window_center: Optional[float] = None,
                      window_width: Optional[float] = None) -> None:
    """
    将像素帧保存为 PNG 图像
    
    Args:
        pixel_array: 像素数组
        output_path: 输出路径
        window_center: 窗位（可选）
        window_width: 窗宽（可选）
    """
    # 应用窗宽窗位
    adjusted = apply_windowing(pixel_array, window_center, window_width) if (
        window_center is not None and window_width is not None
    ) else auto_windowing(pixel_array)
    
    # 转换为 PIL Image
    img = Image.fromarray(adjusted)
    
    # 保存
    img.save(output_path)


def find_dicom_files(folder_path: str, recursive: bool = True) -> List[str]:
    """
    在文件夹中查找 DICOM 文件
    
    Args:
        folder_path: 文件夹路径
        recursive: 是否递归搜索子文件夹
    
    Returns:
        DICOM 文件路径列表
    """
    dicom_files = []
    
    if not os.path.exists(folder_path):
        return dicom_files
    
    # 如果是文件，检查是否为 DICOM
    if os.path.isfile(folder_path):
        try:
            pydicom.dcmread(folder_path, stop_before_pixels=True)
            return [folder_path]
        except:
            return []
    
    # 遍历文件夹
    if recursive:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # 尝试读取 DICOM 文件
                    pydicom.dcmread(file_path, stop_before_pixels=True)
                    dicom_files.append(file_path)
                except:
                    # 尝试通过扩展名判断
                    if file.lower().endswith('.dcm'):
                        dicom_files.append(file_path)
                    continue
    else:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                try:
                    pydicom.dcmread(file_path, stop_before_pixels=True)
                    dicom_files.append(file_path)
                except:
                    if file.lower().endswith('.dcm'):
                        dicom_files.append(file_path)
                    continue
    
    return sorted(dicom_files)


def get_dicom_metadata(file_path: str) -> dict:
    """
    获取 DICOM 文件的元数据
    
    Args:
        file_path: DICOM 文件路径
    
    Returns:
        元数据字典
    """
    try:
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        
        metadata = {
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'patient_name': get_tag(ds, 'PatientName'),
            'patient_id': get_tag(ds, 'PatientID'),
            'patient_birth_date': format_date(get_tag(ds, 'PatientBirthDate')),
            'patient_sex': get_sex_name(get_tag(ds, 'PatientSex')),
            'study_date': format_date(get_tag(ds, 'StudyDate')),
            'study_time': format_time(get_tag(ds, 'StudyTime')),
            'study_description': get_tag(ds, 'StudyDescription'),
            'series_description': get_tag(ds, 'SeriesDescription'),
            'modality': get_modality_name(get_tag(ds, 'Modality')),
            'modality_code': get_tag(ds, 'Modality'),
            'manufacturer': get_tag(ds, 'Manufacturer'),
            'model': get_tag(ds, 'ManufacturerModelName'),
            'station_name': get_tag(ds, 'StationName'),
            'rows': get_tag(ds, 'Rows'),
            'columns': get_tag(ds, 'Columns'),
            'bits_allocated': get_tag(ds, 'BitsAllocated'),
            'bits_stored': get_tag(ds, 'BitsStored'),
            'samples_per_pixel': get_tag(ds, 'SamplesPerPixel'),
            'photometric': get_tag(ds, 'PhotometricInterpretation'),
            'number_of_frames': get_tag(ds, 'NumberOfFrames'),
        }
        
        return metadata
    
    except Exception as e:
        return {
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'error': str(e)
        }


def anonymize_dicom_file(input_path: str, output_path: str) -> bool:
    """
    脱敏 DICOM 文件
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
    
    Returns:
        是否成功
    """
    try:
        ds = pydicom.dcmread(input_path)
        
        # 遍历所有标签并脱敏
        for elem in ds:
            if elem.keyword in SENSITIVE_TAGS:
                ds[elem.keyword].value = anonymize_value(elem.keyword, elem.value)
        
        # 保存脱敏后的文件
        ds.save_as(output_path)
        
        return True
    
    except Exception:
        return False


if __name__ == '__main__':
    # 测试代码
    print("DICOM 工具库已加载")
    print(f"敏感标签数量: {len(SENSITIVE_TAGS)}")
