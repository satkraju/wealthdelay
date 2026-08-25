#!/usr/bin/env python3
"""Vimana HINDI v2 — consistent craft (same image, diff framing) scenes 1&3, voice-only."""
import urllib.request, os, subprocess, tempfile, json, glob
KEY=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
VOICE="JBFqnCBsd6RMkjVDRZzb"
DL="/Users/satishkosaraju/Downloads"
OUT="/Users/satishkosaraju/EmpireOS/projects/bizshorts/vimana_hindi.mp4"
W,H,FPS,TAIL=1080,1920,30,0.45
# (image stub, zoom, yfrac, hindi line)
SCENES=[
 ("nano-banana-2_silhouetted",1.30,0.30,
  "कहते हैं, प्राचीन भारत में उड़ने वाली मशीनें थीं। और पुराने ग्रंथ इन्हें विस्तार से बताते हैं।"),
 ("Close-up_of_an_ancient_palm-leaf",1.0,0.5,
  "इन्हें कहा जाता है — विमान। उड़ने वाले रथ, जिनका वर्णन हज़ारों साल पहले महाभारत और रामायण में मिलता है।"),
 ("nano-banana-2_silhouetted",1.05,0.58,
  "और ये कोई धुंधली कथाएँ नहीं हैं। ग्रंथ बताते हैं ऐसे यान, जो आकाश में, नगरों के बीच, और कुछ कहते हैं, लोकों के बीच भी चलते थे।"),
 ("A_blinding_white_explosion",1.0,0.5,
  "एक श्लोक में एक ऐसे अस्त्र का वर्णन है — हज़ार सूरज से भी तेज़ एक चमक, जिसने पूरे नगर को राख कर दिया।"),
 ("Modern_hands_turning_pages",1.0,0.5,
  "जो लोग इसका अध्ययन करते हैं, वे आज भी एकमत नहीं हैं। प्राचीन कल्पना, या किसी भूली हुई सच्चाई की याद?"),
 ("An_ornate_vimana_craft_rising",1.0,0.5,
  "किसी ने यह हज़ारों साल पहले लिखा था। सवाल यह है... उन्होंने आख़िर देखा क्या था?"),
]
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
def find(s):
    h=glob.glob(os.path.join(DL,f"*{s}*"));
    if not h: raise SystemExit("missing "+s)
    return h[0]
tmp=tempfile.mkdtemp(prefix="vh2_")
clips=[];auds=[]
for i,(stub,z,yf,line) in enumerate(SCENES):
    mp3=os.path.join(tmp,f"v{i}.mp3");wav=os.path.join(tmp,f"v{i}.wav")
    body=json.dumps({"text":line,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.55,"similarity_boost":0.75,"use_speaker_boost":True}}).encode()
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",data=body,headers={"xi-api-key":KEY,"Content-Type":"application/json"})
    open(mp3,"wb").write(urllib.request.urlopen(req,timeout=120).read())
    run(["ffmpeg","-y","-i",mp3,"-ar","44100","-ac","1",wav])
    d=dur(wav);clen=d+TAIL
    img=find(stub)
    sw,sh=int(W*z),int(H*z)
    vf=f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={W}:{H}:(iw-{W})/2:(ih-{H})*{yf},setsar=1,fps={FPS},format=yuv420p"
    clip=os.path.join(tmp,f"c{i}.mp4")
    run(["ffmpeg","-y","-loop","1","-t",f"{clen:.2f}","-i",img,"-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p","-r",str(FPS),clip]);clips.append(clip)
    apad=os.path.join(tmp,f"a{i}.wav")
    run(["ffmpeg","-y","-i",wav,"-af",f"apad=pad_dur={TAIL}","-t",f"{clen:.2f}",apad]);auds.append(apad)
    print(f"  scene {i+1}/6 {d:.1f}s")
vl=os.path.join(tmp,"v.txt");open(vl,"w").write("".join(f"file '{c}'\n" for c in clips))
al=os.path.join(tmp,"a.txt");open(al,"w").write("".join(f"file '{a}'\n" for a in auds))
vid=os.path.join(tmp,"vid.mp4");aud=os.path.join(tmp,"aud.wav")
run(["ffmpeg","-y","-f","concat","-safe","0","-i",vl,"-c","copy",vid])
run(["ffmpeg","-y","-f","concat","-safe","0","-i",al,"-c","copy",aud])
run(["ffmpeg","-y","-i",vid,"-i",aud,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",OUT])
print(f"DONE -> {OUT} ({dur(OUT):.1f}s)")
