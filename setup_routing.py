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
def show(t,s,d): print(f"[{t}] http={s} success={d.get('success') if isinstance(d,dict) else None} errors={d.get('errors') if isinstance(d,dict) else None}")
st,d=api("GET","/zones?name="+ZONE_NAME); show("zones",st,d)
zones=(d.get("result") or []) if isinstance(d,dict) else []
if not zones: print("RESULT: ZONE_NOT_FOUND"); sys.exit(0)
zid=zones[0]["id"]; print("zone_id",zid)
st,d=api("GET",f"/zones/{zid}/dns_records?per_page=200"); show("dns-list",st,d)
recs=(d.get("result") or []) if isinstance(d,dict) else []
mx=[r for r in recs if r.get("type")=="MX"]
print("MX_before:", [(r["name"],r["content"],r.get("priority")) for r in mx])
for r in mx:
    if "mx.cloudflare.net" not in (r.get("content") or ""):
        st,d=api("DELETE",f"/zones/{zid}/dns_records/{r['id']}"); show("mx-del",st,d); print("deleted:",r["content"])
st,d=api("POST",f"/zones/{zid}/email/routing/enable",{}); show("enable",st,d)
st,d=api("POST",f"/zones/{zid}/email/routing/dns",{}); show("routing-dns",st,d)
st,d=api("GET",f"/zones/{zid}/dns_records?type=MX"); show("dns-mx-after",st,d)
print("MX_after:", [(r["name"],r["content"]) for r in ((d.get("result") or []) if isinstance(d,dict) else [])])
body={"enabled":True,"name":"Catch-all","matchers":[{"type":"all"}],"actions":[{"type":"worker","value":[WORKER]}]}
st,d=api("PUT",f"/accounts/{ACC}/email/routing/rules/catch_all",body); show("catchall",st,d)
st,d=api("GET",f"/accounts/{ACC}/email/routing/rules/catch_all"); show("catchall-verify",st,d)
res=d.get("result") if isinstance(d,dict) else None
print("catchall_final:", json.dumps(res)[:400] if res else None)
st,d=api("GET",f"/zones/{zid}/email/routing"); show("routing-final",st,d)
print("RESULT:", "DONE" if (res and res.get("enabled")) else "PARTIAL")
