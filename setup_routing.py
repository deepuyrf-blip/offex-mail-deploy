import os, json, sys, urllib.request, urllib.error
TOK = os.environ["CF_TOKEN"]; ACC = os.environ["ACCOUNT_ID"]
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
        except Exception: return e.code, {"raw": "unparsable"}
    except Exception as e:
        return 0, {"errors": [str(e)]}
def show(tag, st, d):
    print(f"[{tag}] http={st} success={d.get('success') if isinstance(d,dict) else None} errors={d.get('errors') if isinstance(d,dict) else None}")
st, d = api("GET", "/zones?name=" + ZONE_NAME); show("zones", st, d)
zones = (d.get("result") or []) if isinstance(d, dict) else []
if not zones:
    print("RESULT: ZONE_NOT_FOUND"); sys.exit(0)
zid = zones[0]["id"]; print("zone_id", zid, "status", zones[0].get("status"))
st, d = api("GET", f"/zones/{zid}/email/routing"); show("routing-get", st, d)
enabled = (d.get("result") or {}).get("enabled") if isinstance(d, dict) else None
print("routing_enabled:", enabled)
if enabled is not True:
    st, d = api("POST", f"/zones/{zid}/email/routing/enable", {}); show("routing-enable", st, d)
    st, d = api("POST", f"/zones/{zid}/email/routing/dns", {}); show("routing-dns", st, d)
st, d = api("GET", f"/accounts/{ACC}/email/routing/rules/catch_all"); show("catchall-get", st, d)
print("catchall_before:", json.dumps(d.get("result"))[:250] if isinstance(d, dict) else None)
body = {"enabled": True, "name": "Catch-all", "matchers": [{"type": "all"}],
        "actions": [{"type": "worker", "value": [WORKER]}]}
st, d = api("PUT", f"/accounts/{ACC}/email/routing/rules/catch_all", body); show("catchall-put", st, d)
if st >= 400:
    st, d = api("POST", f"/accounts/{ACC}/email/routing/rules/catch_all", body); show("catchall-post", st, d)
st, d = api("GET", f"/accounts/{ACC}/email/routing/rules/catch_all"); show("catchall-verify", st, d)
res = d.get("result") if isinstance(d, dict) else None
print("catchall_final:", json.dumps(res)[:400] if res else None)
print("RESULT:", "DONE" if (res and res.get("enabled")) else "FAILED")
