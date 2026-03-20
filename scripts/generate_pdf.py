#!/usr/bin/env python3
"""
PDF报告生成器
生成专业的冠脉造影PDF报告
"""

import os
import sys
import argparse
import tempfile
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
    from reportlab.lib.units import inch, mm
except ImportError:
    print("请安装 reportlab: pip install reportlab")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CoronaryReportPDF:
    """冠脉造影PDF报告生成器"""
    
    def __init__(self, output_path):
        self.output_path = output_path
        self.story = []
        self.styles = getSampleStyleSheet()
        
        # 自定义样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=20,
            alignment=1,  # 居中
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0d47a1'),
            spaceBefore=15,
            spaceAfter=10,
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=18,
            spaceAfter=8,
        )
        
    def add_title(self, title):
        """添加标题"""
        self.story.append(Paragraph(title, self.title_style))
        self.story.append(Spacer(1, 10*mm))
        
    def add_info_row(self, label, value):
        """添加信息行"""
        text = f"<b>{label}:</b> {value}"
        self.story.append(Paragraph(text, self.normal_style))
        
    def add_patient_info(self, patient_info):
        """添加患者信息"""
        self.story.append(Paragraph("患者信息", self.heading_style))
        
        info_map = {
            '姓名': patient_info.get('patient_name', '未知'),
            'ID': patient_info.get('patient_id', '未知'),
            '检查日期': patient_info.get('study_date', '未知'),
            '检查类型': patient_info.get('study_description', '冠脉造影'),
            '设备': patient_info.get('modality', 'DSA'),
        }
        
        for label, value in info_map.items():
            self.add_info_row(label, value)
        
        self.story.append(Spacer(1, 8*mm))
        
    def add_image(self, image_path, width=150*mm, height=None):
        """添加图像"""
        if os.path.exists(image_path):
            if height:
                self.story.append(Image(image_path, width=width, height=height))
            else:
                self.story.append(Image(image_path, width=width))
            self.story.append(Spacer(1, 5*mm))
            logger.info(f"添加图像: {image_path}")
        
    def add_content(self, content):
        """添加正文内容"""
        # 处理换行
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                self.story.append(Paragraph(line, self.normal_style))
        self.story.append(Spacer(1, 5*mm))
        
    def add_section(self, title, content):
        """添加章节"""
        self.story.append(Paragraph(title, self.heading_style))
        self.add_content(content)
        
    def add_report_content(self, ai_report):
        """添加AI报告内容"""
        self.story.append(Paragraph("影像分析报告", self.heading_style))
        
        # 分段添加
        lines = ai_report.split('\n')
        for line in lines:
            if line.strip():
                if line.startswith('【') and line.endswith('】'):
                    # 章节标题
                    self.story.append(Paragraph(f"<b>{line}</b>", self.normal_style))
                else:
                    self.story.append(Paragraph(line, self.normal_style))
        
    def add_disclaimer(self):
        """添加免责声明"""
        self.story.append(Spacer(1, 10*mm))
        
        disclaimer = """
        <b>免责声明：</b>
        本报告由AI辅助生成，仅供参考，不能替代专业医生的诊断。
        如有疑问，请咨询您的主治医生。
        """
        self.story.append(Paragraph(disclaimer, self.normal_style))
        
    def add_footer(self):
        """添加页脚"""
        pass
        
    def build(self):
        """生成PDF"""
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm,
        )
        
        doc.build(self.story)
        logger.info(f"PDF报告已生成: {self.output_path}")


def create_pdf_report(output_path, patient_info=None, images=None, 
                     ai_report=None, report_title="冠脉造影报告"):
    """创建完整的PDF报告"""
    
    pdf = CoronaryReportPDF(output_path)
    
    # 标题
    pdf.add_title(report_title)
    
    # 报告时间
    pdf.add_info_row("报告生成时间", datetime.now().strftime('%Y年%m月%d日 %H:%M'))
    
    # 患者信息
    if patient_info:
        pdf.add_patient_info(patient_info)
    
    # 图像
    if images:
        pdf.add_section("关键影像", "")
        for img in images[:3]:  # 最多3张
            pdf.add_image(img, width=120*mm)
    
    # AI报告
    if ai_report:
        pdf.add_report_content(ai_report)
    
    # 免责声明
    pdf.add_disclaimer()
    
    # 生成
    pdf.build()
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='生成PDF报告')
    parser.add_argument('--output', '-o', default='coronary_report.pdf', help='输出PDF文件')
    parser.add_argument('--patient-name', default='患者', help='患者姓名')
    parser.add_argument('--patient-id', help='患者ID')
    parser.add_argument('--date', help='检查日期')
    parser.add_argument('--images', nargs='*', help='图像文件列表')
    parser.add_argument('--report', help='AI报告文本文件')
    
    args = parser.parse_args()
    
    # 患者信息
    patient_info = {
        'patient_name': args.patient_name,
        'patient_id': args.patient_id or '未知',
        'study_date': args.date or datetime.now().strftime('%Y年%m月%d日'),
        'study_description': '冠脉造影',
        'modality': 'DSA',
    }
    
    # AI报告
    ai_report = None
    if args.report and os.path.exists(args.report):
        with open(args.report, 'r', encoding='utf-8') as f:
            ai_report = f.read()
    
    # 生成PDF
    create_pdf_report(
        args.output,
        patient_info=patient_info,
        images=args.images,
        ai_report=ai_report
    )
    
    print(f"PDF报告已生成: {args.output}")


if __name__ == '__main__':
    main()
