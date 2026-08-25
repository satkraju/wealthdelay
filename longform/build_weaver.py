#!/usr/bin/env python3
"""Full weaver-bird build Short: chained Kling clips (last-frame -> next) for consistency, stitched, hook text."""
import os,time,hmac,hashlib,base64,json,urllib.request,subprocess
DIR="/Users/satishkosaraju/EmpireOS/projects/bizshorts/longform"
OUT=f"{DIR}/weaver_short.mp4"
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
env=dict(l.strip().split("=",1) for l in open(os.path.expanduser("~/.config/kling/.env")) if "=" in l)
AK=env["KLING_ACCESS_KEY"];SK=env["KLING_SECRET_KEY"];BASE="https://api-singapore.klingai.com"
b=lambda x:base64.urlsafe_b64encode(x).rstrip(b"=")
def jwt():
    h=b(json.dumps({"alg":"HS256","typ":"JWT"}).encode());p=b(json.dumps({"iss":AK,"exp":int(time.time())+1800,"nbf":int(time.time())-5}).encode())
    s=b(hmac.new(SK.encode(),h+b"."+p,hashlib.sha256).digest());return (h+b"."+p+b"."+s).decode()
def post(path,body):
    r=urllib.request.Request(BASE+path,data=json.dumps(body).encode(),headers={"Authorization":f"Bearer {jwt()}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))
def poll(path,tid):
    for _ in range(70):
        d=json.load(urllib.request.urlopen(urllib.request.Request(f"{BASE}{path}/{tid}",headers={"Authorization":f"Bearer {jwt()}"}),timeout=40))["data"]
        if d["task_status"]=="succeed": return d["task_result"]["videos"][0]["url"]
        if d["task_status"]=="failed": raise SystemExit("failed: "+str(d.get("task_status_msg")))
        time.sleep(10)
    raise SystemExit("timeout")
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

stages=[
 "Static locked camera, the weaver bird continues weaving, the hanging grass nest grows larger strand by strand, photorealistic nature documentary",
 "Static locked camera, the nest is now half-built into a woven basket shape, the bird keeps adding dry grass, photorealistic nature documentary",
 "Static locked camera, the bird completes the finished woven hanging nest and perches beside it, photorealistic nature documentary",
]
clips=[]
# clip 0: text -> video
print("clip 0 (text2video)...",flush=True)
t=post("/v1/videos/text2video",{"model_name":"kling-v1-6","prompt":"Static locked camera, a yellow weaver bird lands on a bare branch over lush green forest and begins weaving the first dry grass strands into the start of a hanging nest, photorealistic nature documentary, 9:16","duration":"5","mode":"std","aspect_ratio":"9:16"})
url=poll("/v1/videos/text2video",t["data"]["task_id"])
c0=f"{DIR}/wv0.mp4"; urllib.request.urlretrieve(url,c0); clips.append(c0)
# chained image2video
for i,prompt in enumerate(stages):
    frame=f"{DIR}/f{i}.jpg"; run(["ffmpeg","-y","-sseof","-0.2","-i",clips[-1],"-vframes","1","-vf","scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",frame])
    img_b64=base64.b64encode(open(frame,"rb").read()).decode()
    print(f"clip {i+1} (image2video)...",flush=True)
    t=post("/v1/videos/image2video",{"model_name":"kling-v1-6","image":img_b64,"prompt":prompt,"duration":"5","mode":"std","cfg_scale":0.5})
    url=poll("/v1/videos/image2video",t["data"]["task_id"])
    c=f"{DIR}/wv{i+1}.mp4"; urllib.request.urlretrieve(url,c); clips.append(c)

# normalize + concat
norm=[]
for i,c in enumerate(clips):
    n=f"{DIR}/n{i}.mp4"; run(["ffmpeg","-y","-i",c,"-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p","-an","-c:v","libx264","-preset","veryfast",n]); norm.append(n)
lst=f"{DIR}/list.txt"; open(lst,"w").write("".join(f"file '{n}'\n" for n in norm))
stitched=f"{DIR}/stitched.mp4"; run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c","copy",stitched])
# hook text overlay (first 3s) via PIL png
from PIL import Image,ImageDraw,ImageFont
im=Image.new("RGBA",(1080,1920),(0,0,0,0));d=ImageDraw.Draw(im);f=ImageFont.truetype(FONT,64)
txt="How does it know\nhow to build this?"
y=140
for ln in txt.split("\n"):
    d.text((540,y),ln,font=f,anchor="ma",fill=(255,255,255,255),stroke_width=5,stroke_fill=(0,0,0,255));y+=84
hk=f"{DIR}/hook.png"; im.save(hk)
run(["ffmpeg","-y","-i",stitched,"-i",hk,"-filter_complex","[0:v][1:v]overlay=0:0:enable='between(t,0,3)'[v]","-map","[v]","-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",OUT])
dur=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",OUT],capture_output=True,text=True).stdout.strip()
print(f"DONE -> {OUT} ({dur}s, {len(clips)} clips)",flush=True)
