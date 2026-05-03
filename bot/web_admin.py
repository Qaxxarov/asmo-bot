"""Web admin panel — dashboard API."""

import json, os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from . import database as db
from .config import ADMIN_ID

ADMIN_TOKEN = os.environ.get("ADMIN_WEB_TOKEN", str(ADMIN_ID))

def _auth_ok(path: str) -> bool:
    return parse_qs(urlparse(path).query).get("token", [""])[0] == ADMIN_TOKEN

DASHBOARD_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Asmo Admin</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,sans-serif;background:#0f0f0f;color:#e0e0e0;padding:16px}
.header{text-align:center;padding:20px 0;border-bottom:1px solid #222;margin-bottom:20px}
.header h1{font-size:22px;color:#fff}.header p{font-size:13px;color:#888;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:24px}
.card{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:16px;text-align:center}
.val{font-size:28px;font-weight:700;color:#fff}.lbl{font-size:12px;color:#888;margin-top:4px}
.green .val{color:#4ade80}.blue .val{color:#60a5fa}.yellow .val{color:#facc15}.red .val{color:#f87171}
.tabs{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}
.tab{padding:8px 16px;border-radius:8px;cursor:pointer;background:#1a1a1a;border:1px solid #2a2a2a;color:#888;font-size:13px}
.tab.active{background:#2563eb;color:#fff;border-color:#2563eb}
.sec{display:none}.sec.active{display:block}
table{width:100%;border-collapse:collapse;background:#1a1a1a;border-radius:12px;overflow:hidden}
th{background:#222;color:#888;font-size:11px;text-transform:uppercase;padding:10px 12px;text-align:left}
td{padding:10px 12px;border-top:1px solid #222;font-size:13px}
tr:hover td{background:#1f1f1f}
.badge{padding:2px 8px;border-radius:6px;font-size:11px;font-weight:500}
.b-new{background:#1e3a5f;color:#60a5fa}.b-ok{background:#1a3d1a;color:#4ade80}.b-no{background:#3d1a1a;color:#f87171}
.search{width:100%;padding:10px 14px;border-radius:8px;background:#1a1a1a;border:1px solid #2a2a2a;color:#e0e0e0;margin-bottom:12px;font-size:14px}
.search:focus{outline:none;border-color:#2563eb}
.empty{text-align:center;color:#666;padding:40px}
.refresh{position:fixed;bottom:20px;right:20px;width:48px;height:48px;border-radius:50%;background:#2563eb;color:#fff;border:none;font-size:20px;cursor:pointer}
</style></head><body>
<div class="header"><h1>🎯 Asmo Creative AI</h1><p>Admin Panel</p></div>
<div class="grid" id="g"></div>
<div class="tabs">
<div class="tab active" onclick="show('orders',this)">📦 Buyurtmalar</div>
<div class="tab" onclick="show('clients',this)">👥 Mijozlar</div>
</div>
<input class="search" placeholder="Qidirish..." oninput="filt(this.value)">
<div class="sec active" id="s-orders"><table id="t1"><thead><tr><th>#</th><th>Mijoz</th><th>Xizmat</th><th>Narx</th><th>Muddat</th><th>Holat</th></tr></thead><tbody></tbody></table></div>
<div class="sec" id="s-clients"><table id="t2"><thead><tr><th>Ism</th><th>Username</th><th>Buyurtmalar</th></tr></thead><tbody></tbody></table></div>
<button class="refresh" onclick="load()">↻</button>
<script>
const T=new URLSearchParams(location.search).get('token');let D={},cur='orders';
async function load(){try{const r=await fetch('/api/dashboard?token='+T);D=await r.json();render()}catch(e){}}
function render(){const s=D.stats||{};
document.getElementById('g').innerHTML=`
<div class="card blue"><div class="val">${s.total_users||0}</div><div class="lbl">Mijozlar</div></div>
<div class="card green"><div class="val">${s.today_orders||0}</div><div class="lbl">Bugun</div></div>
<div class="card yellow"><div class="val">${s.month_orders||0}</div><div class="lbl">Bu oy</div></div>
<div class="card"><div class="val">${s.total_orders||0}</div><div class="lbl">Jami</div></div>
<div class="card red"><div class="val">${s.new_orders||0}</div><div class="lbl">Yangi</div></div>
<div class="card green"><div class="val">${s.confirmed_payments||0}</div><div class="lbl">To'langan</div></div>`;
const sm={"new":["Yangi","b-new"],"confirmed":["Tasdiqlangan","b-ok"],"in_progress":["Jarayonda","b-new"],"done":["Tayyor","b-ok"],"rejected":["Rad","b-no"],"paid":["To'langan","b-ok"]};
const tb1=document.querySelector('#t1 tbody');const o=D.orders||[];
tb1.innerHTML=o.length?o.map(x=>{const[t,c]=sm[x.status]||[x.status,"b-new"];
return`<tr><td>#${x.id}</td><td>${x.name||x.user_fullname||'—'}</td><td>${x.svc_name||'—'}</td><td>${x.agreed_price||'—'}</td><td>${x.deadline||'—'}</td><td><span class="badge ${c}">${t}</span></td></tr>`}).join(''):'<tr><td colspan="6" class="empty">Yo\\'q</td></tr>';
const tb2=document.querySelector('#t2 tbody');const cl=D.clients||[];
tb2.innerHTML=cl.length?cl.map(x=>`<tr><td>${x.full_name||'—'}</td><td>${x.username?'@'+x.username:'—'}</td><td>${x.orders_count||0}</td></tr>`).join(''):'<tr><td colspan="3" class="empty">Yo\\'q</td></tr>'}
function show(id,el){cur=id;document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));el.classList.add('active');
document.querySelectorAll('.sec').forEach(s=>s.classList.remove('active'));document.getElementById('s-'+id).classList.add('active')}
function filt(q){const tid=cur==='orders'?'t1':'t2';document.querySelectorAll('#'+tid+' tbody tr').forEach(r=>{r.style.display=r.textContent.toLowerCase().includes(q.toLowerCase())?'':'none'})}
load();setInterval(load,30000);
</script></body></html>"""


class AdminWebHandler:
    @staticmethod
    def handle(handler, path: str) -> bool:
        parsed = urlparse(path)
        if parsed.path == "/admin":
            if not _auth_ok(path):
                handler.send_response(403); handler.end_headers(); handler.wfile.write(b"Forbidden"); return True
            handler.send_response(200); handler.send_header("Content-Type","text/html; charset=utf-8"); handler.end_headers()
            handler.wfile.write(DASHBOARD_HTML.encode()); return True
        if parsed.path == "/api/dashboard":
            if not _auth_ok(path):
                handler.send_response(403); handler.end_headers(); return True
            try:
                data = {"stats": db.stats(), "orders": db.all_orders_data(), "clients": db.all_clients_data()}
                handler.send_response(200); handler.send_header("Content-Type","application/json"); handler.end_headers()
                handler.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode())
            except Exception as e:
                handler.send_response(500); handler.end_headers(); handler.wfile.write(str(e).encode())
            return True
        return False
