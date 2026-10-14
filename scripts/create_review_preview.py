"""Render the README through GitHub's Markdown API for an offline visual review."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
headers = {"Content-Type": "application/json", "User-Agent": "profile-review"}
if os.environ.get("GITHUB_TOKEN"):
    headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
payload = json.dumps({"text": (ROOT/"README.md").read_text(encoding="utf-8"), "mode": "gfm"}).encode()
with urlopen(Request("https://api.github.com/markdown", data=payload, headers=headers), timeout=30) as response:
    rendered = response.read().decode()
assert "<picture>" in rendered and 'media="(max-width: 600px)"' in rendered
assert "prefers-reduced-motion" in rendered
html = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><base href="../">
<title>PedroYuri14 — revisão do perfil</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0D1117;color:#E6EDF3;font:16px/1.6 system-ui,sans-serif}
main{max-width:1000px;margin:30px auto;padding:32px;border:1px solid #30363D;border-radius:12px}
h1,h2{line-height:1.25;margin:30px 0 18px;padding-bottom:12px;border-bottom:1px solid #30363D}
h1{font-size:30px}h2{font-size:23px}p{margin:16px 0}a{color:#58A6FF;text-decoration:none}
img{max-width:100%;height:auto;vertical-align:middle}p img[width="48"]{height:48px;width:48px;margin-right:4px}
table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}td,th{border:1px solid #30363D;padding:10px 14px;text-align:left}
th{background:#161B22}sub{font-size:12px;color:#A7B3C2}li{margin:8px 0}code{background:#161B22;border-radius:4px;padding:2px 5px}
.octicon-link{display:none}@media(max-width:600px){main{margin:0;padding:18px 12px;border:0}h1{font-size:25px}h2{font-size:21px}table{font-size:11px}td,th{padding:7px}}
</style><main>''' + rendered + "</main></html>\n"
(ROOT/"docs/review.html").write_text(html, encoding="utf-8")
print("GitHub Markdown renderer preserved picture, mobile source and reduced-motion fallback.")
