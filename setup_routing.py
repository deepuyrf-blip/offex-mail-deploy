import os, json, urllib.request, urllib.error
TOK=os.environ["CF_TOKEN"]; ACC=os.environ["ACCOUNT_ID"]
ZONE_NAME=os.environ.get("ZONE_NAME","offexmail.online")
API="https://api.cloudflare.com/client/v4"
def api(m,p,b=None):
    d=json.dumps(b).encode() if b is not None else None
    r=urllib.request.Request(API+p,data=d,method=m,headers={"Authorization":"Bearer "+TOK,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(r,timeout=30) as x: return x.status, json.loads(x.read().decode())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except Exception: return e.code, {}
    except Exception as e: return 0, {"errors":[str(e)]}
st,d=api("GET","/zones?name="+ZONE_NAME); zid=((d.get("result") or [{}])[0] or {}).get("id")
st,d=api("GET",f"/zones/{zid}/email/routing"); print("routing:", json.dumps(d.get("result"))[:200])
st,d=api("GET",f"/zones/{zid}/email/routing/rules/catch_all"); print("catch_all:", json.dumps(d.get("result"))[:500])
st,d=api("GET",f"/zones/{zid}/dns_records?type=MX"); print("mx:", [(x["content"],x.get("priority")) for x in ((d.get("result") or []) if isinstance(d,dict) else [])])
