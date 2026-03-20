#!/usr/bin/env python3
import os,sys,argparse,logging
import cv2,numpy as np
from PIL import Image
logging.basicConfig(level=logging.INFO,format='%(levelname)s - %(message)s')
logger=logging.getLogger(__name__)
VIDEO_EXTS={'.mp4','.avi','.mov','.mkv','.wmv'}

def extract_keyframes_video(video_path,num_frames=5,output_dir='keyframes'):
    os.makedirs(output_dir,exist_ok=True)
    cap=cv2.VideoCapture(video_path)
    if not cap.isOpened(): logger.error(f'无法打开'); return []
    total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    logger.info(f'视频: {total}帧 {fps:.1f}FPS')
    scored=[]; idx=0
    while idx<min(total,1000):
        ret,frame=cap.read()
        if not ret: break
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        score=np.var(gray)*0.5+np.std(gray)*0.3+(255-np.mean(gray))*0.2
        scored.append((idx,score,frame.copy())); idx+=1
    cap.release()
    scored.sort(key=lambda x:x[1],reverse=True)
    top=sorted(scored[:num_frames],key=lambda x:x[0])
    saved=[]
    for i,(fidx,_,frame) in enumerate(top):
        out=os.path.join(output_dir,f'keyframe_{i+1:03d}.png')
        cv2.imwrite(out,frame); saved.append(out)
    return saved

def detect_vessels(frame):
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    blur=cv2.GaussianBlur(gray,(5,5),0); edges=cv2.Canny(blur,50,150)
    edges=cv2.dilate(edges,np.ones((3,3),np.uint8),iterations=2)
    contours,_=cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    vessels=[]
    for c in contours:
        area=cv2.contourArea(c)
        if 100<area<5000:
            x,y,w,h=cv2.boundingRect(c); ar=float(w)/h if h>0 else 1
            if ar>2 or ar<0.5: vessels.append(c)
    result=frame.copy(); cv2.drawContours(result,vessels,-1,(0,255,0),2)
    return result,len(vessels)

def detect_stenosis(frame):
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    blur=cv2.GaussianBlur(gray,(5,5),0); edges=cv2.Canny(blur,50,150)
    contours,_=cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    points=[]
    for c in contours:
        area=cv2.contourArea(c)
        if area>50:
            peri=cv2.arcLength(c,True)
            if peri>0 and 4*np.pi*area/(peri**2)<0.3:
                M=cv2.moments(c)
                if M['m00']>0: points.append((int(M['m10']/M['m00']),int(M['m01']/M['m00'])))
    result=frame.copy()
    for i,(cx,cy) in enumerate(points):
        cv2.circle(result,(cx,cy),8,(0,0,255),-1); cv2.circle(result,(cx,cy),12,(255,255,255),2)
        cv2.putText(result,f'#{i+1}',(cx+15,cy+5),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
    return result,points

def generate_gif(video_path,output_gif,num_frames=30,duration=100):
    cap=cv2.VideoCapture(video_path)
    if not cap.isOpened(): return None
    total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices=np.linspace(0,total-1,num_frames,dtype=int)
    frames=[]
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES,idx); ret,frame=cap.read()
        if ret:
            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB); rgb=cv2.resize(rgb,(512,512))
            frames.append(Image.fromarray(rgb))
    cap.release()
    if frames: frames[0].save(output_gif,save_all=True,append_images=frames[1:],duration=duration,loop=0); return output_gif
    return None

def main():
    parser=argparse.ArgumentParser(description='视频分析')
    parser.add_argument('input'); parser.add_argument('--output','-o',default='analysis')
    parser.add_argument('--num-frames','-n',type=int,default=5)
    parser.add_argument('--gif',action='store_true'); parser.add_argument('--track',action='store_true')
    parser.add_argument('--stenosis',action='store_true')
    args=parser.parse_args()
    if not os.path.exists(args.input): sys.exit(1)
    ext=os.path.splitext(args.input)[1].lower()
    if ext not in VIDEO_EXTS: sys.exit(1)
    os.makedirs(args.output,exist_ok=True)
    kf=extract_keyframes_video(args.input,args.num_frames,args.output)
    if args.gif: generate_gif(args.input,os.path.join(args.output,'angiography.gif'))
    if args.track:
        cap=cv2.VideoCapture(args.input); ret,frame=cap.read(); cap.release()
        if ret:
            r,c=detect_vessels(frame); cv2.imwrite(os.path.join(args.output,'vessel_analysis.png'),r)
            logger.info(f'血管: {c}个区域')
    if args.stenosis:
        cap=cv2.VideoCapture(args.input); ret,frame=cap.read(); cap.release()
        if ret:
            r,p=detect_stenosis(frame); cv2.imwrite(os.path.join(args.output,'stenosis_marked.png'),r)
            logger.info(f'狭窄: {len(p)}个点')
    print(f'\n✅ 完成 → {args.output}')

if __name__=='__main__': main()
