#!/usr/bin/env python3
import sys,os,json,argparse
from collections import Counter
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from lib.dicom_utils import get_tag,format_date,get_modality_name,find_dicom_files,anonymize_value,SENSITIVE_TAGS

def analyze_folder(folder_path,anonymize=False):
    files=find_dicom_files(folder_path)
    if not files: return {'error':'未找到 DICOM 文件','folder':folder_path}
    import pydicom
    records=[]
    for fp in files:
        try:
            ds=pydicom.dcmread(fp,force=True,stop_before_pixels=True)
            patient=get_tag(ds,'PatientName')
            if anonymize: patient=anonymize_value('PatientName',patient)
            records.append({'path':fp,'modality':get_tag(ds,'Modality'),'series':get_tag(ds,'SeriesDescription'),'patient':patient,'date':format_date(get_tag(ds,'StudyDate'))})
        except: continue
    return {'folder':folder_path,'total_files':len(records),
        'modalities':dict(Counter(r['modality'] for r in records)),
        'series':{k:v for k,v in Counter(r['series'] for r in records).most_common(10)},
        'patients':dict(Counter(r['patient'] for r in records)),
        'files':records[:30],'truncated':len(records)>30}

def format_report(data):
    if 'error' in data: return f"❌ {data['error']}: {data['folder']}"
    lines=[f"\n╔══════════════════════════════════════════════════════════════╗\n║                    DICOM 批量分析报告                         ║\n╚══════════════════════════════════════════════════════════════╝\n\n文件夹: {data['folder']}\n文件总数: {data['total_files']}\n"]
    lines.append('【按模态统计】')
    for mod,count in sorted(data['modalities'].items()): lines.append(f'  {get_modality_name(mod)} ({mod}): {count} 个')
    lines.append('\n【按系列统计】')
    for ser,count in sorted(data['series'].items(),key=lambda x:-x[1])[:10]:
        if ser!='N/A': lines.append(f'  {ser}: {count} 个')
    return '\n'.join(lines)

def main():
    parser=argparse.ArgumentParser(description='DICOM 批量分析')
    parser.add_argument('input'); parser.add_argument('--anonymize','-a',action='store_true')
    parser.add_argument('--json','-j',action='store_true')
    args=parser.parse_args()
    if not os.path.isdir(args.input): print(f'❌ 不是文件夹'); sys.exit(1)
    result=analyze_folder(args.input,args.anonymize)
    if args.json: print(json.dumps(result,ensure_ascii=False,indent=2))
    else: print(format_report(result))

if __name__=='__main__': main()
