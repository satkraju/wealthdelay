#!/usr/bin/env python3
"""Kling weaver-bird test: text->image (empty branch) -> image2video (bird builds nest). Reports cost."""
import os,time,hmac,hashlib,base64,json,urllib.request
BASE="https://api-singapore.klingai.com"
OUT="/Users/satishkosaraju/EmpireOS/projects/bizshorts/longform/weaver_test.mp4"
env=dict(l.strip().split("=",1) for l in open(os.path.expanduser("~/.config/kling/.env")) if "=" in l)
AK=env["KLING_ACCESS_KEY"]; SK=env["KLING_SECRET_KEY"]
def jwt():
    b=lambda x:base64.urlsafe_b64encode(x).rstrip(b"=")
    h=b(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
    p=b(json.dumps({"iss":AK,"exp":int(time.time())+1800,"nbf":int(time.time())-5}).encode())
    s=b(hmac.new(SK.encode(),h+b"."+p,hashlib.sha256).digest())
    return (h+b"."+p+b"."+s).decode()
def req(method,path,body=None):
    data=json.dumps(body).encode() if body else None
    r=urllib.request.Request(BASE+path,data=data,method=method,
        headers={"Authorization":f"Bearer {jwt()}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))
def poll(path,tid,label):
    for _ in range(80):
        d=req("GET",f"{path}/{tid}")["data"]
        st=d.get("task_status")
        if st=="succeed": return d["task_result"]
        if st=="failed": raise SystemExit(f"{label} failed: {d.get('task_status_msg')}")
        time.sleep(8)
    raise SystemExit(f"{label} timeout")

# 1) image
print("generating empty-branch image...",flush=True)
r=req("POST","/v1/images/generations",{"model_name":"kling-v1-5",
  "prompt":"a single bare acacia tree branch against a soft blurred green forest background, golden morning light, nature documentary, photorealistic, 9:16",
  "aspect_ratio":"9:16","n":1})
img=poll("/v1/images/generations",r["data"]["task_id"],"image")["images"][0]["url"]
print("image:",img,flush=True)

# 2) image2video
print("generating build video...",flush=True)
r=req("POST","/v1/videos/image2video",{"model_name":"kling-v1-6","image":img,
  "prompt":"time-lapse, a yellow weaver bird rapidly weaves dry grass strands into a hanging woven nest on the branch, the nest grows strand by strand, static locked camera, nature documentary",
  "duration":"5","mode":"std","cfg_scale":0.5})
vid=poll("/v1/videos/image2video",r["data"]["task_id"],"video")["videos"][0]["url"]
print("video:",vid,flush=True)
urllib.request.urlretrieve(vid,OUT)
print("DONE ->",OUT,flush=True)
