import os, json, sys, urllib.request, urllib.error
TOK = os.environ["CF_TOKEN"]
ACC = os.environ["ACCOUNT_ID"]
ZONE_NAME = os.environ.get("ZONE_NAME", "offexmail.online")
WORKER = os.environ.get("WORKER", "offex-mail-ingest")
API = "https://api.cloudflare.com/client/v4"

def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
        headers={"Authorization": "Bearer " + TOK, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except Exception: return e.code, {}
    except Exception as e:
        return 0, {"errors": [str(e)]}

def show(tag, st, d):
    print(f"[{tag}] http={st} success={d.get('success') if isinstance(d,dict) else '?'} errors={d.get('errors') if isinstance(d,dict) else None}")

st, d = api("GET", "/zones?name=" + ZONE_NAME)
show("zones", st, d)
zones = (d.get("result") or []) if isinstance(d, dict) else []
if not zones:
    print("RESULT: ZONE_NOT_FOUND"); sys.exit(0)
zid = zones[0]["id"]; print("zone_id", zid, "status", zones[0].get("status"))

st, d = api("GET", f"/zones/{zid}/email/routing")
show("routing-get", st, d)
print("routing enabled:", (d.get("result") or {}).get("enabled") if isinstance(d, dict) else None)

st, d = api("POST", f"/zones/{zid}/email/routing/enable", {})
show("routing-enable", st, d)
st, d = api("POST", f"/zones/{zid}/email/routing/dns", {})
show("routing-dns", st, d)

body = {"enabled": True, "name": "Catch-all", "matchers": [{"type": "all"}],
        "actions": [{"type": "worker", "value": [WORKER]}]}
st, d = api("PUT", f"/accounts/{ACC}/email/routing/rules/catch_all", body)
show("catch-all-put", st, d)
print("RESULT:", "DONE" if st < 400 else "CATCHALL_FAILED")
