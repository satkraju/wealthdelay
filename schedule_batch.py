#!/usr/bin/env python3
"""Schedule rendered WealthDelay shorts as future public releases (YouTube publishAt).

  python3 schedule_batch.py --plan                 # dry-run: show the drip schedule, upload nothing
  python3 schedule_batch.py --go                   # actually schedule every out/*.mp4
  options: --per-day N (default 1)  --start YYYY-MM-DD (default tomorrow)  --hour-utc H (default 16 = ~noon ET)

Reads out/<id>.mp4 + out/<id>.txt (description) and title/tags from finance/ideas.json.
Ramp guidance: keep --per-day 1 for the first 2 weeks, then raise it only if reach holds.
"""
import os,sys,json,subprocess,argparse,datetime
DIR=os.path.dirname(os.path.abspath(__file__)); FIN=f"{DIR}/finance"; OUT=f"{FIN}/out"
UP=f"{DIR}/youtube_upload.py"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plan",action="store_true"); p.add_argument("--go",action="store_true")
    p.add_argument("--per-day",type=int,default=1); p.add_argument("--start"); p.add_argument("--hour-utc",type=int,default=16)
    p.add_argument("--ideas-file",default="ideas.json")
    a=p.parse_args()
    if not (a.plan or a.go): sys.exit("pass --plan (dry run) or --go (schedule)")
    idea_list=json.load(open(f"{FIN}/{a.ideas_file}"))
    ideas={e["id"]:e for e in idea_list}
    have=set(f[:-4] for f in os.listdir(OUT) if f.endswith(".mp4"))
    # interleave by archetype (id prefix before _vN) round-robin, so the same
    # archetype never posts on consecutive days — keeps the feed from reading
    # as a visibly templated batch.
    import re,collections
    groups=collections.OrderedDict()
    for e in idea_list:
        vid=e["id"]
        if vid not in have: continue
        prefix=re.sub(r"_v\d+$","",vid)
        groups.setdefault(prefix,[]).append(vid)
    vids=[]
    while any(groups.values()):
        for k in list(groups.keys()):
            if groups[k]: vids.append(groups[k].pop(0))
    start=datetime.date.fromisoformat(a.start) if a.start else (datetime.date.today()+datetime.timedelta(days=1))
    # spread per_day slots: 16:00, then +Nh apart within the day
    slots_h=[a.hour_utc] if a.per_day==1 else [a.hour_utc+i*(8//max(1,a.per_day-1)) for i in range(a.per_day)]
    print(f"Scheduling {len(vids)} videos · {a.per_day}/day · starting {start} · slots(UTC)={slots_h}\n")
    plan=[]
    for i,vid_id in enumerate(vids):
        e=ideas.get(vid_id,{})
        day=start+datetime.timedelta(days=i//a.per_day); hh=slots_h[i%a.per_day]
        when=datetime.datetime(day.year,day.month,day.day,hh%24,0,0,tzinfo=datetime.timezone.utc)
        iso=when.strftime("%Y-%m-%dT%H:%M:%SZ")
        plan.append((vid_id,iso,e)); print(f"  {iso}  {vid_id}  — {e.get('title','?')}")
    if a.plan: print("\n(dry run — nothing scheduled. Re-run with --go to schedule.)"); return
    print()
    for vid_id,iso,e in plan:
        cmd=["python3",UP,"--video",f"{OUT}/{vid_id}.mp4","--title",e.get("title",vid_id),
             "--desc-file",f"{OUT}/{vid_id}.txt","--tags",",".join(e.get("tags",[])),"--publish-at",iso]
        print(f"-> scheduling {vid_id} for {iso}")
        r=subprocess.run(cmd,capture_output=True,text=True)
        out=(r.stdout+r.stderr).strip().splitlines()
        print("   "+(out[-1] if out else "(no output)"))
if __name__=="__main__": main()
