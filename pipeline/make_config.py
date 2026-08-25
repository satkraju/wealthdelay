#!/usr/bin/env python3
"""
Topic-bank -> pipeline config generator (the scaling engine).

For each topic in topics.json, asks Gemini to write a full short (scene prompts +
voiceover lines) in that bucket's format, assigns a rotated voice (never Adam),
and writes config_<slug>.json that pipeline.py can run.

    python3 make_config.py                 # generate configs for all unmade topics
    python3 make_config.py --n 5           # only the next 5 unmade topics
    python3 make_config.py --topic "X" --bucket lost_temple   # one ad-hoc topic

Needs GEMINI_API_KEY (~/.config/gemini/.env). Run pipeline.py on the output configs.
"""
import os, sys, json, re, argparse, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = json.load(open(os.path.join(HERE, "topics.json")))
POOL = list(BANK["voice_pool"].items())   # [(name, id), ...]  -- Adam excluded by design

def load_key(path, name):
    p = os.path.expanduser(path)
    if not os.path.exists(p): return None
    for line in open(p):
        if line.strip().startswith(name+"="): return line.split("=",1)[1].strip()

GEMINI_KEY = load_key("~/.config/gemini/.env", "GEMINI_API_KEY")

def slug(s):
    return re.sub(r"[^a-z0-9]+","_", s.lower()).strip("_")[:40]

def pick_voice(title):
    # deterministic rotation by title -> stable, spreads across the pool, never Adam
    idx = int(hashlib.md5(title.encode()).hexdigest(), 16) % len(POOL)
    return POOL[idx][1]

PROMPT = """You are scripting a faceless, vertical (9:16) AI short for a history/mythology channel.
Bucket: {bucket} — {bucket_desc}
Topic: {topic}

Rules:
- 7 to 9 scenes. For lost_temple use the SAME camera framing every scene (ruin -> restored morph).
- Each scene: a vivid hyper-realistic cinematic IMAGE prompt (end with ", cinematic, 9:16") and a short ANIM prompt (motion only).
- 6 to 8 VOICEOVER lines: English, strong hook first line, emotional, one knowledge-gap, a share-worthy ending. Frame myth honestly ("legends say"/"the texts describe").
- No on-screen text instructions; captions are added later.

Return ONLY valid JSON, no prose:
{{"title":"<short title>","scenes":[{{"image_prompt":"...","anim_prompt":"..."}}],"voiceover_lines":["...","..."]}}"""

def gen_one(client, bucket, topic):
    from google.genai import types
    p = PROMPT.format(bucket=bucket, bucket_desc=BANK["buckets"][bucket], topic=topic)
    r = client.models.generate_content(model="gemini-2.5-flash", contents=p,
        config=types.GenerateContentConfig(response_mime_type="application/json"))
    data = json.loads(r.text)
    title = data["title"]
    cfg = {
        "title": slug(title),
        "aspect": "9:16",
        "veo_model": "veo-3.0-fast-generate-001",
        "image_model": "imagen-4.0-generate-001",
        "voice_id": pick_voice(title),
        "morph": bucket == "lost_temple",
        "scenes": [{"image_prompt": s["image_prompt"], "anim_prompt": s.get("anim_prompt","slow cinematic push")}
                   for s in data["scenes"]],
        "voiceover_lines": data["voiceover_lines"],
    }
    out = os.path.join(HERE, f"config_{cfg['title']}.json")
    json.dump(cfg, open(out,"w"), indent=2, ensure_ascii=False)
    print("  wrote", os.path.basename(out), "| voice", cfg["voice_id"][:6], "| scenes", len(cfg["scenes"]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=0, help="limit number of topics")
    ap.add_argument("--topic"); ap.add_argument("--bucket")
    a = ap.parse_args()
    if not GEMINI_KEY: sys.exit("Missing GEMINI_API_KEY (~/.config/gemini/.env)")
    from google import genai
    client = genai.Client(api_key=GEMINI_KEY)
    if a.topic:
        gen_one(client, a.bucket or "mythic_mystery", a.topic); return
    todo = [t for t in BANK["topics"]
            if not os.path.exists(os.path.join(HERE, f"config_{slug(t['topic'])}.json"))]
    if a.n: todo = todo[:a.n]
    print(f"generating {len(todo)} configs...")
    for t in todo:
        try: gen_one(client, t["bucket"], t["topic"])
        except Exception as e: print("  FAIL", t["topic"], e)

if __name__ == "__main__":
    main()
