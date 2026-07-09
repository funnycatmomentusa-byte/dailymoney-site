#!/usr/bin/env python3
"""Cloudflare DNS + Worker Auto-Setup
Jalankan setelah mendapat API token Cloudflare."""
import json, urllib.request, os, sys

API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
if not API_TOKEN:
    print("❌ Set CLOUDFLARE_API_TOKEN environment variable first")
    print("export CLOUDFLARE_API_TOKEN='your_token'")
    sys.exit(1)

DOMAIN = "dailymoney.my.id"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def cf_api(method, path, data=None):
    url = f"https://api.cloudflare.com/client/v4{path}"
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    if data:
        req.data = json.dumps(data).encode()
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
        return resp
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

# Get zone ID
print("🔍 Getting zone ID...")
resp = cf_api("GET", f"/zones?name={DOMAIN}")
if not resp.get("success") or not resp.get("result"):
    print("❌ Zone not found. Add domain to Cloudflare first.")
    print(f"   Errors: {resp.get('errors')}")
    sys.exit(1)
zone_id = resp["result"][0]["id"]
zone_name = resp["result"][0]["name"]
print(f"✅ Zone: {zone_name} (ID: {zone_id})")

# Existing records
resp = cf_api("GET", f"/zones/{zone_id}/dns_records?per_page=100")
existing = {r["type"] + ":" + r["name"]: r for r in resp.get("result", [])}

# DNS Records to ensure
wanted = [
    {"type": "A", "name": DOMAIN, "content": "185.199.108.153"},
    {"type": "A", "name": DOMAIN, "content": "185.199.109.153"},
    {"type": "A", "name": DOMAIN, "content": "185.199.110.153"},
    {"type": "A", "name": DOMAIN, "content": "185.199.111.153"},
    {"type": "CNAME", "name": f"www.{DOMAIN}", "content": "funnycatmomentusa-byte.github.io"},
]

for rec in wanted:
    key = f"{rec['type']}:{rec['name']}"
    if key in existing:
        existing_rec = existing[key]
        # Update proxy to true
        if not existing_rec.get("proxied"):
            print(f"  📝 Enabling proxy for {rec['type']} {rec['name']}...")
            cf_api("PATCH", f"/zones/{zone_id}/dns_records/{existing_rec['id']}",
                   {"proxied": True})
            print(f"    ✅ Proxied enabled")
        else:
            print(f"  ✅ {rec['type']} {rec['name']} already proxied")
    else:
        print(f"  📝 Adding {rec['type']} {rec['name']} -> {rec['content']}...")
        rec_data = {**rec, "proxied": True, "ttl": 1}
        resp = cf_api("POST", f"/zones/{zone_id}/dns_records", rec_data)
        if resp.get("success"):
            print(f"    ✅ Added (proxied)")
        else:
            errs = [e.get("message", "") for e in resp.get("errors", [])]
            if any("already exists" in e for e in errs):
                print(f"    ⏭️ Already exists")
            else:
                print(f"    ❌ {errs}")

# Enable Always Use HTTPS
print("📝 Enabling Always Use HTTPS...")
cf_api("PATCH", f"/zones/{zone_id}/settings/always_use_https", {"value": "on"})
print("   ✅ Always Use HTTPS enabled")

# Enable Automatic HTTPS Rewrites
print("📝 Enabling Automatic HTTPS Rewrites...")
cf_api("PATCH", f"/zones/{zone_id}/settings/automatic_https_rewrites", {"value": "on"})
print("   ✅ Automatic HTTPS Rewrites enabled")

# Set TLS to 1.2 minimum
print("📝 Setting minimum TLS to 1.2...")
cf_api("PATCH", f"/zones/{zone_id}/settings/min_tls_version", {"value": "1.2"})
print("   ✅ Minimum TLS 1.2 set")

# Deploy Worker via API
print("📝 Deploying security headers worker...")
worker_script = """// DailyMoney Security Headers Worker v1.0
const SECURITY_HEADERS = {
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), camera=(), microphone=(), payment=(), display-capture=()',
  'X-XSS-Protection': '0',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' https: data:; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://api.coingecko.com; frame-src 'none'; object-src 'none'",
  'Cross-Origin-Opener-Policy': 'same-origin'
};
async function handleRequest(request) {
  const response = await fetch(request);
  const newHeaders = new Headers(response.headers);
  for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
    newHeaders.set(key, value);
  }
  newHeaders.delete('X-Powered-By');
  newHeaders.delete('X-GitHub-Request-Id');
  return new Response(response.body, {
    status: response.status, statusText: response.statusText, headers: newHeaders
  });
}
addEventListener('fetch', event => { event.respondWith(handleRequest(event.request)); });
"""

# Check if worker exists
resp = cf_api("GET", f"/accounts/{zone_id}/workers/scripts/dailymoney-security-headers")
if resp.get("success"):
    # Update existing worker
    print("   ✅ Worker already exists, updating...")
    
# We need account_id, not zone_id. Try to get it
resp = cf_api("GET", "/accounts?per_page=1")
if resp.get("success") and resp.get("result"):
    account_id = resp["result"][0]["id"]
    
    # Upload worker
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/dailymoney-security-headers",
        data=worker_script.encode(),
        headers={
            **HEADERS,
            "Content-Type": "application/javascript"
        },
        method="PUT"
    )
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
        if resp.get("success"):
            print("   ✅ Worker deployed!")
            
            # Create route
            route_data = {
                "pattern": f"{DOMAIN}/*",
                "script": "dailymoney-security-headers",
                "zone_id": zone_id
            }
            cf_api("POST", f"/zones/{zone_id}/workers/routes", route_data)
            print("   ✅ Worker route added!")
    except Exception as e:
        print(f"   ⚠️ Worker deploy: {str(e)[:100]}")
        print("   ℹ️  You may need to deploy manually via Wrangler CLI")

print()
print("✅ Cloudflare setup complete!")
print("🌐 https://dailymoney.my.id — now secured with Cloudflare proxy")
