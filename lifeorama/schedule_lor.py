#!/usr/bin/env python3
"""Life-O-Rama YouTube scheduler — uploads all rendered explainers to the LOR channel.

First-time setup (one time only):
  python3 schedule_lor.py --auth        # opens browser → sign in with LOR channel account

Dry run (see what will be scheduled, nothing uploaded):
  python3 schedule_lor.py --plan

Schedule everything in out/ at 3 videos/week:
  python3 schedule_lor.py --go

Options:
  --start YYYY-MM-DD    first publish date (default: tomorrow)
  --per-week N          videos per week (default: 3, Mon/Wed/Fri at 15:00 UTC)
  --hour-utc H          publish hour UTC (default: 15)
"""
import os, sys, json, subprocess, argparse, datetime

DIR   = os.path.dirname(os.path.abspath(__file__))
OUT   = f"{DIR}/out"
UP    = os.path.join(os.path.dirname(DIR), "youtube_upload.py")
TOKEN = os.path.expanduser("~/.config/empireos/yt_token_lor.json")

# Mon=0 Wed=2 Fri=4 — the 3x/week publishing days
WEEKDAYS_3X = [0, 2, 4]

def auth():
    subprocess.run(["python3", UP, "--auth", "--token-file", TOKEN], check=True)

def plan_dates(start: datetime.date, per_week: int, count: int, hour_utc: int):
    """Return a list of `count` UTC datetimes spread across weekdays."""
    if per_week == 3:
        days = WEEKDAYS_3X
    elif per_week == 7:
        days = list(range(7))
    else:
        # spread evenly across the week
        step = max(1, 7 // per_week)
        days = [i * step for i in range(per_week)]

    dates = []
    d = start
    while len(dates) < count:
        if d.weekday() in days:
            dates.append(datetime.datetime(d.year, d.month, d.day, hour_utc, 0, 0,
                                           tzinfo=datetime.timezone.utc))
        d += datetime.timedelta(days=1)
    return dates

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--auth",     action="store_true", help="connect Life-O-Rama YouTube channel")
    p.add_argument("--who",      action="store_true", help="print which channel is connected")
    p.add_argument("--plan",     action="store_true", help="dry run — show schedule, upload nothing")
    p.add_argument("--go",       action="store_true", help="upload + schedule everything in out/")
    p.add_argument("--start",    help="first publish date YYYY-MM-DD (default: tomorrow)")
    p.add_argument("--per-week", type=int, default=3)
    p.add_argument("--hour-utc", type=int, default=15)
    a = p.parse_args()

    if a.auth:
        auth(); sys.exit()
    if a.who:
        subprocess.run(["python3", UP, "--who", "--token-file", TOKEN], check=True); sys.exit()
    if not (a.plan or a.go):
        sys.exit("Pass --auth (first time), --plan (dry run), or --go (schedule).")

    # Find rendered videos (mp4 + matching txt description)
    vids = sorted(f[:-4] for f in os.listdir(OUT) if f.endswith(".mp4")
                  and os.path.exists(f"{OUT}/{f[:-4]}.txt"))
    if not vids:
        sys.exit(f"No rendered videos found in {OUT}/ (need <id>.mp4 + <id>.txt pairs).")

    start = (datetime.date.fromisoformat(a.start) if a.start
             else datetime.date.today() + datetime.timedelta(days=1))
    schedule = plan_dates(start, a.per_week, len(vids), a.hour_utc)

    print(f"Life-O-Rama schedule — {len(vids)} video(s), {a.per_week}x/week, starting {start}\n")
    for vid_id, when in zip(vids, schedule):
        desc = open(f"{OUT}/{vid_id}.txt").read().split("\n")[0][:60]
        print(f"  {when.strftime('%Y-%m-%d %a %H:%M UTC')}  {vid_id}  —  {desc}")

    if a.plan:
        print("\n(dry run — nothing uploaded. Re-run with --go to schedule.)")
        return

    print()
    for vid_id, when in zip(vids, schedule):
        txt_path  = f"{OUT}/{vid_id}.txt"
        txt       = open(txt_path).read()
        lines     = txt.split("\n")
        title     = lines[0].strip() or vid_id
        # last non-empty line is the hashtags
        tags_line = next((l for l in reversed(lines) if l.strip().startswith("#")), "")
        tags      = " ".join(tags_line.split())
        iso       = when.strftime("%Y-%m-%dT%H:%M:%SZ")

        cmd = ["python3", UP,
               "--video",      f"{OUT}/{vid_id}.mp4",
               "--title",      title,
               "--desc-file",  txt_path,
               "--tags",       tags,
               "--publish-at", iso,
               "--token-file", TOKEN]
        print(f"→ scheduling {vid_id} for {iso} …", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip().splitlines()
        print("   " + (out[-1] if out else "(no output)"))

if __name__ == "__main__":
    main()
