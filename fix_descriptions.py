#!/usr/bin/env python3
"""Patch descriptions of already-scheduled WealthDelay videos to use the corrected calculator links from ideas.json.
Matches each scheduled video by its title. Also rewrites the local out/<id>.txt files. Run after re-auth (force-ssl scope)."""
import os,json,warnings; warnings.filterwarnings("ignore")
import sys; sys.argv=["x"]
DIR=os.path.dirname(os.path.abspath(__file__)); FIN=f"{DIR}/finance"; OUT=f"{FIN}/out"
exec(open(f"{DIR}/youtube_upload.py").read().split("if __name__")[0])  # service(), creds()

def build_desc(e):
    S=e["scenes"]
    return (f"{S['hook']['big']} {S['hook']['accent']}\n\n👉 Run your own numbers (free): {e['tool_url']}\n\n{e['disclaimer']}\n\n"
            +" ".join(f"#{t.replace(' ','')}" for t in e["tags"])+" #Shorts")

ideas=json.load(open(f"{FIN}/ideas.json")); byTitle={e["title"]:e for e in ideas}
yt=service()
ch=yt.channels().list(part="contentDetails",mine=True).execute()
up=ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
items=yt.playlistItems().list(part="snippet",playlistId=up,maxResults=25).execute()["items"]
for it in items:
    title=it["snippet"]["title"]; vid=it["snippet"]["resourceId"]["videoId"]
    e=byTitle.get(title)
    if not e: continue
    desc=build_desc(e); open(f"{OUT}/{e['id']}.txt","w").write(desc)
    yt.videos().update(part="snippet",body={"id":vid,"snippet":{
        "title":e["title"],"description":desc,"tags":e["tags"],"categoryId":"27"}}).execute()
    print(f"patched {e['id']}  ->  {e['tool_url']}")
print("done")
