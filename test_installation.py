#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装测试脚本
验证所有依赖和功能是否正常工作
"""

import sys
import os
import io

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_imports():
    """测试所有必要的库导入"""
    print("[OK] 测试库导入...")
    tests = []

    # 基础依赖
    try:
        import pydicom
        print(f"  [OK] pydicom {pydicom.__version__}")
        tests.append(True)
    except ImportError as e:
        print(f"  [FAIL] pydicom 导入失败: {e}")
        tests.append(False)

    try:
        from PIL import Image
        print(f"  [OK] PIL (Pillow) {Image.__version__}")
        tests.append(True)
    except ImportError as e:
        print(f"  [FAIL] PIL 导入失败: {e}")
        tests.append(False)

    try:
        import numpy as np
        print(f"  [OK] numpy {np.__version__}")
        tests.append(True)
    except ImportError as e:
        print(f"  [FAIL] numpy 导入失败: {e}")
        tests.append(False)

    # 可选依赖
    optional = []

    try:
        import cv2
        print(f"  [OK] opencv-python {cv2.__version__} (可选)")
        optional.append(True)
    except ImportError:
        print(f"  [WARN] opencv-python 未安装 (视频分析功能不可用)")
        optional.append(False)

    try:
        import scipy
        print(f"  [OK] scipy {scipy.__version__} (可选)")
        optional.append(True)
    except ImportError:
        print(f"  [WARN] scipy 未安装 (图像增强功能不可用)")
        optional.append(False)

    try:
        import openai
        print(f"  [OK] openai {openai.__version__} (可选)")
        optional.append(True)
    except ImportError:
        print(f"  [WARN] openai 未安装 (AI 分析功能不可用)")
        optional.append(False)

    try:
        import reportlab
        print(f"  [OK] reportlab {reportlab.Version} (可选)")
        optional.append(True)
    except ImportError:
        print(f"  [WARN] reportlab 未安装 (PDF 生成功能不可用)")
        optional.append(False)

    return all(tests), all(optional)

def test_utils_module():
    """测试工具库"""
    print("\n[OK] 测试工具库...")
    try:
        from lib.dicom_utils import (
            SENSITIVE_TAGS, get_tag, format_date, format_time,
            get_modality_name, get_sex_name, anonymize_value,
            auto_windowing, find_dicom_files
        )
        print(f"  [OK] 成功导入工具库")
        print(f"  [OK] 敏感标签数量: {len(SENSITIVE_TAGS)}")
        print(f"  [OK] 模态映射测试: XA -> {get_modality_name('XA')}")
        print(f"  [OK] 性别映射测试: M -> {get_sex_name('M')}")
        print(f"  [OK] 日期格式化测试: 20260320 -> {format_date('20260320')}")
        print(f"  [OK] 时间格式化测试: 143055 -> {format_time('143055')}")
        print(f"  [OK] 脱敏测试: PatientName -> {anonymize_value('PatientName', '张三')}")
        return True
    except Exception as e:
        print(f"  [FAIL] 工具库导入失败: {e}")
        return False

def test_scripts():
    """测试脚本文件"""
    print("\n[OK] 测试脚本文件...")
    scripts_dir = "scripts"
    required_scripts = [
        "dicom_read.py",
        "dicom_convert.py",
        "dicom_batch.py",
        "keyframe_extract.py",
        "video_export.py",
        "video_analyze.py",
        "generate_report.py",
        "ai_report.py",
        "patient_report.py",
        "compare_prepost.py",
        "generate_pdf.py",
    ]

    missing = []
    for script in required_scripts:
        script_path = os.path.join(scripts_dir, script)
        if os.path.exists(script_path):
            print(f"  [OK] {script}")
        else:
            print(f"  [FAIL] {script} 缺失")
            missing.append(script)

    return len(missing) == 0

def test_structure():
    """测试项目结构"""
    print("\n[OK] 测试项目结构...")
    required_items = [
        "lib/dicom_utils.py",
        "lib/__init__.py",
        "SKILL.md",
        "README.md",
        "requirements.txt",
        "INSTALL.md",
        "USAGE.md",
    ]

    all_exist = True
    for item in required_items:
        if os.path.exists(item):
            print(f"  [OK] {item}")
        else:
            print(f"  [FAIL] {item} 缺失")
            all_exist = False

    return all_exist

def main():
    """主测试函数"""
    print("="*60)
    print("[TEST] Cardiology Assistant 安装测试")
    print("="*60)

    results = {}

    # 测试导入
    basic_ok, optional_ok = test_imports()
    results["基础依赖"] = basic_ok
    results["可选依赖"] = optional_ok

    # 测试工具库
    results["工具库"] = test_utils_module()

    # 测试脚本
    results["脚本文件"] = test_scripts()

    # 测试结构
    results["项目结构"] = test_structure()

    # 总结
    print("\n" + "="*60)
    print("[SUMMARY] 测试总结")
    print("="*60)

    for key, value in results.items():
        status = "[PASS]" if value else "[FAIL]"
        print(f"  {key}: {status}")

    print("\n" + "="*60)

    if all(results.values()):
        print("[SUCCESS] 所有测试通过！Cardiology Assistant 已成功安装")
        print("\n你可以开始使用了：")
        print("  python scripts/dicom_read.py --help")
        print("  python scripts/dicom_convert.py --help")
        print("  更多使用方法请参阅 USAGE.md")
        return 0
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"[WARN] 以下测试失败: {', '.join(failed)}")
        print("\n建议：")
        if not results["基础依赖"]:
            print("  1. 运行: pip install -r requirements.txt")
        if not results["工具库"]:
            print("  2. 确保从项目根目录运行测试")
        if not results["项目结构"]:
            print("  3. 检查项目文件是否完整")
        return 1

if __name__ == "__main__":
    sys.exit(main())
