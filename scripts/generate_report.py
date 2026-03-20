#!/usr/bin/env python3
import os,sys,json,argparse,logging
from datetime import datetime
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from lib.dicom_utils import find_dicom_files,auto_windowing,format_date,get_tag,SENSITIVE_TAGS
from scripts.dicom_read import analyze_dicom
from scripts.keyframe_extract import extract_from_multiframe,extract_from_folder,save_keyframes
logging.basicConfig(level=logging.INFO,format='%(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

def load_template(p=None):
    if p and os.path.exists(p): return open(p,encoding='utf-8').read()
    return """# 冠脉造影影像分析报告\n\n> 生成时间: {timestamp}\n> ⚠️ 仅供参考\n\n---\n\n## 一、影像元数据摘要\n\n{metadata}\n\n## 二、关键帧图像\n\n{keyframes}\n\n## 三、AI 分析请求\n\n{ai_prompt}\n\n---\n\n*本报告由 cardiology-assistant Skill 自动生成*\n"""

def build_metadata(analyses,anonymize=False):
    lines=[]
    for a in analyses:
        if 'error' in a: lines.append(f"- ❌ {a['file']}"); continue
        p,s,se,im=a['patient'],a['study'],a['series'],a['image']
        lines.append(f"### {os.path.basename(a['file'])}")
        lines.append(f"- 患者: {p['name']} | {p['sex']} | 出生 {p['birth_date']}")
        lines.append(f"- 检查: {s['date']} {s['time']} | {s['description']}")
        lines.append(f"- 模态: {se['modality']} ({se['modality_code']})")
        lines.append(f"- 图像: {im['rows']}×{im['columns']} | {im['bits_stored']}bit | {im['frame_count']}帧")
        lines.append('')
    return '\n'.join(lines)

def build_keyframes(kf_dir):
    if not kf_dir or not os.path.isdir(kf_dir): return '未提取'
    pngs=sorted([f for f in os.listdir(kf_dir) if f.endswith('.png')])
    if not pngs: return '无图像'
    lines=[f'共 {len(pngs)} 个关键帧:\n']
    for png in pngs: lines.append(f'![{png}]({os.path.join(kf_dir,png)})')
    return '\n'.join(lines)

def build_prompt(code):
    prompts={'XA':'请分析冠脉造影(CAG)影像:\n1. 影像质量\n2. 冠脉解剖(LAD/LCX/RCA/LM)\n3. 病变分析(位置/程度/形态)\n4. TIMI血流\n5. 诊疗建议(PCI/CABG/药物)\n\n请用专业术语，附通俗解释。',
        'CT':'请分析CT影像:\n1. 影像质量\n2. 解剖结构\n3. 异常发现\n4. 建议'}
    return prompts.get(code,'请分析影像:\n1. 质量\n2. 解剖\n3. 异常\n4. 建议')

def generate_report(input_path,output_path,anonymize=False,num_frames=5,template_path=None,keyframe_dir=None):
    if os.path.isfile(input_path):
        analyses=[analyze_dicom(input_path,anonymize)]; modality=analyses[0].get('series',{}).get('modality_code','UNKNOWN')
    else:
        files=find_dicom_files(input_path); analyses=[analyze_dicom(f,anonymize) for f in files[:10]]
        modality=analyses[0].get('series',{}).get('modality_code','UNKNOWN') if analyses else 'UNKNOWN'
    if keyframe_dir is None: keyframe_dir=os.path.join(os.path.dirname(output_path) or '.','keyframes')
    try:
        if os.path.isfile(input_path):
            indices,ds=extract_from_multiframe(input_path,num_frames); saved=save_keyframes(input_path,indices,keyframe_dir)
        else:
            indices,ds=extract_from_folder(input_path,num_frames)
            saved=save_keyframes(input_path if not isinstance(indices[0],str) else None,indices,keyframe_dir) if indices else []
    except Exception as e: logger.warning(f'关键帧失败: {e}'); saved=[]
    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report=load_template(template_path).format(timestamp=timestamp,metadata=build_metadata(analyses,anonymize),keyframes=build_keyframes(keyframe_dir),ai_prompt=build_prompt(modality))
    os.makedirs(os.path.dirname(output_path) or '.',exist_ok=True)
    with open(output_path,'w',encoding='utf-8') as f: f.write(report)
    summary={'report_path':output_path,'keyframe_dir':keyframe_dir,'keyframe_count':len(saved),'modality':modality,'file_count':len(analyses),'anonymized':anonymize}
    with open(output_path.replace('.md','.json'),'w',encoding='utf-8') as f: json.dump(summary,f,ensure_ascii=False,indent=2)
    return summary

def main():
    parser=argparse.ArgumentParser(description='报告生成')
    parser.add_argument('input'); parser.add_argument('--output','-o',default='report.md')
    parser.add_argument('--anonymize','-a',action='store_true'); parser.add_argument('--num-frames','-n',type=int,default=5)
    parser.add_argument('--template','-t'); parser.add_argument('--keyframes-dir','-k')
    args=parser.parse_args()
    if not os.path.exists(args.input): sys.exit(1)
    r=generate_report(args.input,args.output,anonymize=args.anonymize,num_frames=args.num_frames,template_path=args.template,keyframe_dir=args.keyframes_dir)
    print(f'\n✅ 报告: {r["report_path"]}\n   关键帧: {r["keyframe_count"]}个\n   模态: {r["modality"]}')

if __name__=='__main__': main()
