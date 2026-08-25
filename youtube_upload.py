#!/usr/bin/env python3
"""WealthDelay YouTube uploader. One-time OAuth, then upload/schedule any Short from the command line.

Setup (one time):
  1. Put your OAuth client file at ~/.config/empireos/yt_client_secret.json
  2. Run once: python3 youtube_upload.py --auth      (opens browser, sign in, approve)
     -> saves token to ~/.config/empireos/yt_token.json

Upload:
  python3 youtube_upload.py --video finance/compound_gap.mp4 \
      --title "They invested the SAME amount..." \
      --desc-file finance/compound_gap.txt \
      --tags "compound interest,investing,401k,personal finance" \
      [--publish-at 2026-06-16T14:00:00Z]   # omit = publish now (public)

Notes:
  - Shorts are auto-detected by YouTube from vertical aspect + <=3min; we also append #Shorts to the description.
  - --publish-at schedules a PRIVATE->PUBLIC release at that UTC time (ISO-8601, must be future).
"""
import os,sys,argparse,json
CFG=os.path.expanduser("~/.config/empireos")
CLIENT=f"{CFG}/yt_client_secret.json"
_DEFAULT_TOKEN=f"{CFG}/yt_token.json"
SCOPES=["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube.readonly","https://www.googleapis.com/auth/youtube.force-ssl"]

def creds(token_file=None):
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    tok=token_file or _DEFAULT_TOKEN
    c=None
    if os.path.exists(tok):
        c=Credentials.from_authorized_user_file(tok,SCOPES)
    if not c or not c.valid:
        if c and c.expired and c.refresh_token:
            c.refresh(Request())
        else:
            if not os.path.exists(CLIENT):
                sys.exit(f"Missing OAuth client file: {CLIENT}\nSee setup steps in this file's docstring.")
            flow=InstalledAppFlow.from_client_secrets_file(CLIENT,SCOPES)
            c=flow.run_local_server(port=0)
        open(tok,"w").write(c.to_json()); os.chmod(tok,0o600)
    return c

def service(token_file=None):
    from googleapiclient.discovery import build
    return build("youtube","v3",credentials=creds(token_file))

def whoami(token_file=None):
    yt=service(token_file)
    r=yt.channels().list(part="snippet,statistics",mine=True).execute()
    ch=r["items"][0]
    print(f"Authed channel: {ch['snippet']['title']}  (subs: {ch['statistics'].get('subscriberCount','?')})")

def upload(args):
    from googleapiclient.http import MediaFileUpload
    yt=service(getattr(args,"token_file",None))
    desc=open(args.desc_file).read() if args.desc_file else (args.desc or "")
    if not getattr(args,"no_shorts_tag",False) and "#Shorts" not in desc:
        desc=desc.rstrip()+"\n\n#Shorts"
    tags=[t.strip() for t in (args.tags or "").split(",") if t.strip()]
    status={"selfDeclaredMadeForKids":False}
    if args.publish_at:
        status["privacyStatus"]="private"; status["publishAt"]=args.publish_at
    else:
        status["privacyStatus"]=args.privacy
    body={"snippet":{"title":args.title,"description":desc,"tags":tags,"categoryId":"27"},  # 27 = Education
          "status":status}
    media=MediaFileUpload(args.video,chunksize=-1,resumable=True,mimetype="video/*")
    req=yt.videos().insert(part="snippet,status",body=body,media_body=media)
    resp=None
    while resp is None:
        st,resp=req.next_chunk()
        if st: print(f"  uploading… {int(st.progress()*100)}%",flush=True)
    vid=resp["id"]
    when=f"scheduled for {args.publish_at}" if args.publish_at else f"published ({args.privacy})"
    print(f"DONE -> https://youtu.be/{vid}  [{when}]")
    return vid

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--auth",action="store_true",help="run one-time OAuth and exit")
    p.add_argument("--who",action="store_true",help="print the authed channel and exit")
    p.add_argument("--video"); p.add_argument("--title")
    p.add_argument("--desc"); p.add_argument("--desc-file")
    p.add_argument("--tags")
    p.add_argument("--privacy",default="public",choices=["public","unlisted","private"])
    p.add_argument("--publish-at",help="ISO-8601 UTC, e.g. 2026-06-16T14:00:00Z (schedules a future public release)")
    p.add_argument("--token-file",help="path to OAuth token JSON (default: ~/.config/empireos/yt_token.json)")
    p.add_argument("--no-shorts-tag",action="store_true",help="do NOT append #Shorts to description (for long-form videos)")
    a=p.parse_args()
    if a.auth: creds(a.token_file); whoami(a.token_file); sys.exit()
    if a.who: whoami(a.token_file); sys.exit()
    if not (a.video and a.title): sys.exit("Need --video and --title (or --auth / --who).")
    upload(a)
