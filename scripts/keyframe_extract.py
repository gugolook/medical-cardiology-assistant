#!/usr/bin/env python3
import os,sys,argparse,logging
import numpy as np,pydicom
from PIL import Image
from scipy import ndimage
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from lib.dicom_utils import auto_windowing,find_dicom_files
logging.basicConfig(level=logging.INFO,format='%(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

def calc_sharpness(f): return np.var(ndimage.laplace(f.astype(np.float64)))
def calc_contrast(f): return np.std(f)
def calc_brightness(f): return np.mean(f)
def score_frame(f):
    adj=auto_windowing(f)
    return calc_sharpness(adj)*0.4+calc_contrast(adj)*0.3+calc_brightness(adj)*0.3

def extract_from_multiframe(dicom_path,num_frames=5):
    ds=pydicom.dcmread(dicom_path,force=True); arr=ds.pixel_array
    if arr.ndim==2: return [0],ds
    n=arr.shape[0]; logger.info(f'检测到 {n} 帧')
    scores=sorted([(i,score_frame(arr[i])) for i in range(n)],key=lambda x:x[1],reverse=True)
    return sorted([s[0] for s in scores[:num_frames]]),ds

def extract_from_folder(folder_path,num_frames=5):
    files=find_dicom_files(folder_path)
    if not files: return [],None
    for fp in files:
        try:
            ds=pydicom.dcmread(fp,force=True)
            if ds.pixel_array.ndim==3: return extract_from_multiframe(fp,num_frames)
        except: continue
    scored=[]
    for fp in files[:200]:
        try: ds=pydicom.dcmread(fp,force=True); scored.append((fp,score_frame(ds.pixel_array)))
        except: continue
    scored.sort(key=lambda x:x[1],reverse=True)
    top=sorted([fp for fp,_ in scored[:num_frames]],key=lambda x:os.path.basename(x))
    return top,pydicom.dcmread(top[0],force=True) if top else None

def save_keyframes(source,indices,output_dir):
    os.makedirs(output_dir,exist_ok=True); saved=[]
    if isinstance(source,str) and os.path.isfile(source):
        ds=pydicom.dcmread(source,force=True); arr=ds.pixel_array
        for i,idx in enumerate(indices):
            frame=arr[idx] if arr.ndim==3 else arr
            out=os.path.join(output_dir,f'keyframe_{i+1:03d}.png')
            Image.fromarray(auto_windowing(frame)).save(out); saved.append(out)
    elif isinstance(indices,list) and all(isinstance(x,str) for x in indices):
        for i,fp in enumerate(indices):
            ds=pydicom.dcmread(fp,force=True)
            out=os.path.join(output_dir,f'keyframe_{i+1:03d}.png')
            Image.fromarray(auto_windowing(ds.pixel_array)).save(out); saved.append(out)
    return saved

def main():
    parser=argparse.ArgumentParser(description='关键帧提取')
    parser.add_argument('input'); parser.add_argument('--output','-o',default='keyframes')
    parser.add_argument('--num-frames','-n',type=int,default=5)
    args=parser.parse_args()
    if not os.path.exists(args.input): logger.error(f'不存在: {args.input}'); sys.exit(1)
    if os.path.isfile(args.input):
        indices,ds=extract_from_multiframe(args.input,args.num_frames)
        saved=save_keyframes(args.input,indices,args.output)
    else:
        indices,ds=extract_from_folder(args.input,args.num_frames)
        if not indices: logger.error('未找到帧'); sys.exit(1)
        saved=save_keyframes(args.input if not isinstance(indices[0],str) else None,indices,args.output)
    print(f'\n✅ 提取完成！共 {len(saved)} 个关键帧 → {args.output}')

if __name__=='__main__': main()
