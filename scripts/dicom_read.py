#!/usr/bin/env python3
import sys,os,json,argparse
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from lib.dicom_utils import get_tag,format_date,format_time,get_modality_name,get_sex_name,anonymize_value,SENSITIVE_TAGS,find_dicom_files

def analyze_dicom(file_path, anonymize=False):
    import pydicom
    try: ds=pydicom.dcmread(file_path,force=True,stop_before_pixels=True)
    except Exception as e: return {'error':str(e),'file':file_path}
    def val(tag):
        raw=get_tag(ds,tag)
        if anonymize and tag in SENSITIVE_TAGS: return anonymize_value(tag,raw)
        return raw
    return {'file':file_path,
        'patient':{'name':val('PatientName'),'id':val('PatientID'),'birth_date':format_date(val('PatientBirthDate')),'sex':get_sex_name(val('PatientSex'))},
        'study':{'date':format_date(val('StudyDate')),'time':format_time(val('StudyTime')),'description':val('StudyDescription')},
        'series':{'description':val('SeriesDescription'),'modality':get_modality_name(val('Modality')),'modality_code':val('Modality')},
        'equipment':{'manufacturer':val('Manufacturer'),'model':val('ManufacturerModelName'),'station':val('StationName')},
        'image':{'rows':val('Rows'),'columns':val('Columns'),'bits_allocated':val('BitsAllocated'),'bits_stored':val('BitsStored'),'samples_per_pixel':val('SamplesPerPixel'),'photometric':val('PhotometricInterpretation'),'frame_count':val('NumberOfFrames')}}

def format_report(data):
    if 'error' in data: return f"❌ 读取失败: {data['error']}\n   文件: {data['file']}"
    p,s,se,eq,im=data['patient'],data['study'],data['series'],data['equipment'],data['image']
    return f"""
╔══════════════════════════════════════════════════════════════╗
║                    DICOM 医学影像分析报告                      ║
╚══════════════════════════════════════════════════════════════╝

【患者信息】
  姓名: {p['name']}
  患者ID: {p['id']}
  出生日期: {p['birth_date']}
  性别: {p['sex']}

【检查信息】
  检查日期: {s['date']}
  检查时间: {s['time']}
  检查描述: {s['description']}

【系列信息】
  模态: {se['modality']} ({se['modality_code']})
  系列描述: {se['description']}

【设备信息】
  制造商: {eq['manufacturer']}
  设备型号: {eq['model']}
  工作站: {eq['station']}

【影像参数】
  图像尺寸: {im['rows']} × {im['columns']} 像素
  位深: {im['bits_allocated']}-bit ({im['bits_stored']} bit存储)
  采样数: {im['samples_per_pixel']}
  色彩空间: {im['photometric']}
  帧数: {im['frame_count']}

【文件路径】
  {data['file']}
"""

def main():
    parser=argparse.ArgumentParser(description='DICOM 元数据分析')
    parser.add_argument('input'); parser.add_argument('--anonymize','-a',action='store_true')
    parser.add_argument('--json','-j',action='store_true')
    args=parser.parse_args()
    if not os.path.exists(args.input): print(f"❌ 路径不存在: {args.input}"); sys.exit(1)
    if os.path.isfile(args.input): results=[analyze_dicom(args.input,args.anonymize)]
    else:
        files=find_dicom_files(args.input)
        if not files: print(f"❌ 未找到 DICOM 文件"); sys.exit(1)
        results=[analyze_dicom(f,args.anonymize) for f in files]
    if args.json: print(json.dumps(results,ensure_ascii=False,indent=2))
    else:
        for r in results: print(format_report(r))

if __name__=='__main__': main()
