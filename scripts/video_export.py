#!/usr/bin/env python3
import os,sys,argparse,logging
import cv2,numpy as np,pydicom
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from lib.dicom_utils import auto_windowing,find_dicom_files
logging.basicConfig(level=logging.INFO,format='%(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

def dicom_to_video(input_path,output_path,fps=15,max_size=1280):
    dicom_files=find_dicom_files(input_path) if os.path.isdir(input_path) else [input_path]
    if not dicom_files: return None
    dicom_files.sort(); logger.info(f'{len(dicom_files)} 个文件')
    ds=pydicom.dcmread(dicom_files[0],force=True); arr=ds.pixel_array
    h,w=(arr.shape[1],arr.shape[2]) if arr.ndim==3 else arr.shape
    if max(h,w)>max_size:
        s=max_size/max(h,w); w,h=int(w*s),int(h*s)
    fourcc=cv2.VideoWriter_fourcc(*'mp4v'); out=cv2.VideoWriter(output_path,fourcc,fps,(w,h))
    count=0
    for fp in dicom_files:
        try:
            ds=pydicom.dcmread(fp,force=True); frames=ds.pixel_array if ds.pixel_array.ndim==3 else [ds.pixel_array]
            for frame in frames:
                adj=auto_windowing(frame); resized=cv2.resize(adj,(w,h))
                out.write(cv2.cvtColor(resized,cv2.COLOR_GRAY2BGR)); count+=1
        except: continue
    out.release()
    logger.info(f'{count}帧 → {output_path} ({os.path.getsize(output_path)/(1024*1024):.1f}MB)')
    return output_path

def compress_video(input_path,output_path,target_mb=50):
    cap=cv2.VideoCapture(input_path)
    if not cap.isOpened(): return None
    fps=cap.get(cv2.CAP_PROP_FPS); w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); dur=total/max(fps,1)
    if w>1280: s=1280/w; w,h=1280,int(h*s)
    fourcc=cv2.VideoWriter_fourcc(*'mp4v'); out=cv2.VideoWriter(output_path,fourcc,fps,(w,h))
    while True:
        ret,frame=cap.read()
        if not ret: break
        out.write(cv2.resize(frame,(w,h)))
    cap.release(); out.release()
    logger.info(f'压缩完成: {os.path.getsize(output_path)/(1024*1024):.1f}MB')
    return output_path

def convert_format(input_path,output_path):
    cap=cv2.VideoCapture(input_path)
    if not cap.isOpened(): return None
    fps=cap.get(cv2.CAP_PROP_FPS); w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ext=os.path.splitext(output_path)[1].lower(); codec={'avi':'XVID'}.get(ext.lstrip('.'),'mp4v')
    fourcc=cv2.VideoWriter_fourcc(*codec); out=cv2.VideoWriter(output_path,fourcc,fps,(w,h))
    while True:
        ret,frame=cap.read()
        if not ret: break
        out.write(frame)
    cap.release(); out.release()
    logger.info(f'转换完成: {os.path.getsize(output_path)/(1024*1024):.1f}MB')
    return output_path

def main():
    parser=argparse.ArgumentParser(description='视频导出')
    parser.add_argument('input'); parser.add_argument('output')
    parser.add_argument('--fps',type=int,default=15); parser.add_argument('--compress',action='store_true')
    parser.add_argument('--target-size',type=int,default=50)
    args=parser.parse_args()
    if not os.path.exists(args.input): sys.exit(1)
    if os.path.isdir(args.input) or args.input.endswith('.dcm'): dicom_to_video(args.input,args.output,args.fps)
    elif args.compress: compress_video(args.input,args.output,args.target_size)
    else: convert_format(args.input,args.output)

if __name__=='__main__': main()
