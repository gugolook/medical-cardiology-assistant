#!/usr/bin/env python3
import sys,os,argparse
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from lib.dicom_utils import auto_windowing,apply_windowing,save_frame_as_png,load_pixel_frame,find_dicom_files

def convert_single(dicom_path,output_path,wc=None,ww=None,frame_index=0):
    try:
        ds,pixel_array=load_pixel_frame(dicom_path,frame_index)
        save_frame_as_png(pixel_array,output_path,wc,ww)
        return True,output_path
    except Exception as e: return False,str(e)

def convert_batch(folder_path,output_dir,wc=None,ww=None):
    os.makedirs(output_dir,exist_ok=True)
    files=find_dicom_files(folder_path)
    if not files: return 0,"未找到 DICOM 文件"
    success=0
    for i,fpath in enumerate(files):
        base=os.path.splitext(os.path.basename(fpath))[0]
        out=os.path.join(output_dir,f'{base}_{i:04d}.png')
        ok,msg=convert_single(fpath,out,wc,ww)
        if ok: success+=1; print(f"  ✅ {os.path.relpath(fpath,folder_path)}")
        else: print(f"  ❌ {os.path.relpath(fpath,folder_path)}: {msg}")
    return success,f"{success}/{len(files)} 个文件转换成功"

def main():
    parser=argparse.ArgumentParser(description='DICOM → PNG')
    parser.add_argument('input'); parser.add_argument('output')
    parser.add_argument('--wc',type=float,default=None); parser.add_argument('--ww',type=float,default=None)
    parser.add_argument('--frame',type=int,default=0); parser.add_argument('--batch',action='store_true')
    args=parser.parse_args()
    if not os.path.exists(args.input): print(f"❌ 不存在: {args.input}"); sys.exit(1)
    if args.batch or os.path.isdir(args.input):
        ok,msg=convert_batch(args.input,args.output,args.wc,args.ww); print(f"\n{msg}")
    else:
        ok,msg=convert_single(args.input,args.output,args.wc,args.ww,args.frame)
        if ok: print(f"✅ 已保存: {msg}")
        else: print(f"❌ 失败: {msg}"); sys.exit(1)

if __name__=='__main__': main()
