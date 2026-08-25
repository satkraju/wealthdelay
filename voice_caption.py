#!/usr/bin/env python3
"""Generate ElevenLabs voiceover + burn captions onto the silent montage."""
import urllib.request, os, subprocess, tempfile, sys, json

KEY = open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
VOICE = "pNInz6obpgDQGcFmaJgB"   # Adam — deep male
MODEL = "eleven_multilingual_v2"
SILENT = "/Users/satishkosaraju/EmpireOS/projects/bizshorts/temple_restore_silent.mp4"
OUT = "/Users/satishkosaraju/EmpireOS/projects/bizshorts/temple_restore_final.mp4"
GAP = 0.30

LINES = [
    "This temple has been dead for five hundred years.",
    "But it didn't always look like this.",
    "Watch... as time runs backwards.",
    "The stone heals. The pillars rise. The cracks close.",
    "Color floods back across carvings no one has seen in centuries.",
    "The lamps light. The smoke returns. The people come home.",
    "This is what it may have looked like when it was alive.",
    "And almost no one alive today remembers it stood like this.",
]


def tts(text, path):
    body = json.dumps({"text": text, "model_id": MODEL,
                       "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",
                                 data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        f.write(r.read())


def dur(path):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=nw=1:nk=1",path],capture_output=True,text=True).stdout.strip())


def ass_time(t):
    h=int(t//3600); m=int((t%3600)//60); s=t%60
    return f"{h}:{m:02d}:{s:05.2f}"


def main():
    tmp = tempfile.mkdtemp(prefix="voice_")
    # silence clip for gaps
    sil = os.path.join(tmp,"sil.wav")
    subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=44100:cl=mono","-t",str(GAP),sil],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    concat=[]; events=[]; cursor=0.0
    for i,line in enumerate(LINES):
        mp3=os.path.join(tmp,f"l{i}.mp3"); wav=os.path.join(tmp,f"l{i}.wav")
        tts(line,mp3)
        subprocess.run(["ffmpeg","-y","-i",mp3,"-ar","44100","-ac","1",wav],
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
        d=dur(wav)
        events.append((cursor,cursor+d,line))
        concat.append(wav); cursor+=d
        if i<len(LINES)-1:
            concat.append(sil); cursor+=GAP
        print(f"  voiced line {i+1}/{len(LINES)}  ({d:.1f}s)",file=sys.stderr)
    # concat audio
    listf=os.path.join(tmp,"a.txt")
    open(listf,"w").write("".join(f"file '{w}'\n" for w in concat))
    full=os.path.join(tmp,"full.wav")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",listf,"-c","copy",full],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    audio_dur=dur(full); video_dur=dur(SILENT)
    final_dur=max(audio_dur,video_dur)+0.3
    # ASS captions
    ass=os.path.join(tmp,"cap.ass")
    with open(ass,"w") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n")
        f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV\n")
        f.write("Style: Def, Arial, 58, &H00FFFFFF, &H00000000, &H64000000, 1, 1, 4, 2, 2, 80, 80, 300\n\n")
        f.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for a,b,txt in events:
            f.write(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Def,,0,0,0,,{txt}\n")
    pad=final_dur-video_dur
    vf=f"tpad=stop_mode=clone:stop_duration={pad:.2f},subtitles={ass}" if pad>0.05 else f"subtitles={ass}"
    subprocess.run(["ffmpeg","-y","-i",SILENT,"-i",full,
        "-filter_complex",f"[0:v]{vf}[v];[1:a]apad[a]",
        "-map","[v]","-map","[a]","-t",f"{final_dur:.2f}",
        "-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
        "-movflags","+faststart",OUT],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    print(f"DONE -> {OUT}  ({dur(OUT):.1f}s, narration {audio_dur:.1f}s)")


if __name__=="__main__":
    main()
