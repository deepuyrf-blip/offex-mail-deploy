import os, json, sys, urllib.request, urllib.error
TOK=os.environ["CF_TOKEN"]; ACC=os.environ["ACCOUNT_ID"]
ZONE_NAME=os.environ.get("ZONE_NAME","offexmail.online"); WORKER=os.environ.get("WORKER","offex-mail-ingest")
API="https://api.cloudflare.com/client/v4"
def api(method, path, body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(API+path, data=data, method=method,
        headers={"Authorization":"Bearer "+TOK,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except Exception: return e.code, {}
    except Exception as e: return 0, {"errors":[str(e)]}
def show(t,s,d): print(f"[{t}] http={s} err={d.get('errors') if isinstance(d,dict) else None}")
st,d=api("GET","/zones?name="+ZONE_NAME)
zid=((d.get("result") or [{}])[0] or {}).get("id"); print("zone_id",zid)
st,d=api("GET",f"/accounts/{ACC}/email/routing/rules"); show("acct-rules-GET",st,d)
print("rules_now:", json.dumps(d.get("result"))[:250] if isinstance(d,dict) else None)
st,d=api("GET",f"/zones/{zid}/email/routing/rules"); show("zone-rules-GET",st,d)
st,d=api("PUT",f"/zones/{zid}/email/routing/rules/catch_all",{"enabled":True,"name":"Catch-all","matchers":[{"type":"all"}],"actions":[{"type":"worker","value":[WORKER]}]}); show("zone-catchall-PUT",st,d)
st,d=api("POST",f"/accounts/{ACC}/email/routing/rules",{"enabled":True,"name":"Catch-all","matchers":[{"type":"all"}],"actions":[{"type":"worker","value":[WORKER]}]}); show("acct-rules-POST",st,d)
st,d=api("PUT",f"/accounts/{ACC}/email/routing/rules/catch_all",{"enabled":True,"name":"Catch-all","matchers":[{"type":"all"}],"actions":[{"type":"worker","value":[WORKER]}]}); show("acct-catchall-PUT",st,d)
st,d=api("GET",f"/accounts/{ACC}/email/routing/rules/catch_all"); show("acct-catchall-GET",st,d)
res=d.get("result") if isinstance(d,dict) else None
print("final:", json.dumps(res)[:300] if res else None)
print("RESULT:", "DONE" if (res and res.get("enabled")) else "STILL_BLOCKED")
