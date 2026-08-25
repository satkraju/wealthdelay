#!/usr/bin/env python3
"""Re-voice the long-form with an ElevenLabs Hindi voice (overwrites cached mp3s)."""
import os, json, urllib.request, sys
KEY=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
HERE=os.path.dirname(os.path.abspath(__file__))
CFG=json.load(open(os.path.join(HERE,"ashwatthama.json")))
ASSETS=os.path.join(HERE,CFG["title"]+"_assets")
VOICE="vIdhHAZdn1bGjKe1dFw8"
def tts(text,out,speed=True):
    vs={"stability":0.5,"similarity_boost":0.75,"use_speaker_boost":True}
    if speed: vs["speed"]=1.15
    body=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":vs}).encode()
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",data=body,headers={"xi-api-key":KEY,"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as r:
        open(out,"wb").write(r.read())
segs=CFG["segments"]
# test seg 0 first
try:
    tts(segs[0]["hi"], os.path.join(ASSETS,"v0.mp3"))
    print("voice OK")
except urllib.error.HTTPError as e:
    print("VOICE FAIL",e.code,e.read()[:200]); sys.exit(1)
for i in range(1,len(segs)):
    try: tts(segs[i]["hi"], os.path.join(ASSETS,f"v{i}.mp3"))
    except urllib.error.HTTPError as e:
        if e.code==400:  # speed maybe unsupported -> retry without
            tts(segs[i]["hi"], os.path.join(ASSETS,f"v{i}.mp3"), speed=False)
        else: raise
    print(f"  voiced {i+1}/{len(segs)}",flush=True)
print("ALL REVOICED")
