"""Web admin panel — lightweight dashboard served alongside the bot."""

import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from . import database as db
from .config import ADMIN_ID

# Simple auth token (admin_id based)
ADMIN_TOKEN = os.environ.get("ADMIN_WEB_TOKEN", str(ADMIN_ID))


def _auth_ok(path: str) -> bool:
    parsed = urlparse(path)
    params = parse_qs(parsed.query)
    token = params.get("token", [""])[0]
    return token == ADMIN_TOKEN


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Asmo Admin Panel</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #0f0f0f; color: #e0e0e0; padding: 16px;
}
.header {
  text-align: center; padding: 20px 0; margin-bottom: 20px;
  border-bottom: 1px solid #222;
}
.header h1 { font-size: 22px; color: #fff; }
.header p { font-size: 13px; color: #888; margin-top: 4px; }

.stats-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px; margin-bottom: 24px;
}
.stat-card {
  background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px;
  padding: 16px; text-align: center;
}
.stat-value { font-size: 28px; font-weight: 700; color: #fff; }
.stat-label { font-size: 12px; color: #888; margin-top: 4px; }
.stat-card.green .stat-value { color: #4ade80; }
.stat-card.blue .stat-value { color: #60a5fa; }
.stat-card.yellow .stat-value { color: #facc15; }
.stat-card.red .stat-value { color: #f87171; }

.tabs {
  display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;
}
.tab {
  padding: 8px 16px; border-radius: 8px; cursor: pointer;
  background: #1a1a1a; border: 1px solid #2a2a2a;
  color: #888; font-size: 13px; font-weight: 500;
}
.tab.active { background: #2563eb; color: #fff; border-color: #2563eb; }

.section { display: none; }
.section.active { display: block; }

table {
  width: 100%; border-collapse: collapse;
  background: #1a1a1a; border-radius: 12px; overflow: hidden;
}
th {
  background: #222; color: #888; font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.05em; padding: 10px 12px; text-align: left;
}
td { padding: 10px 12px; border-top: 1px solid #222; font-size: 13px; }
tr:hover td { background: #1f1f1f; }

.badge {
  padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500;
}
.badge-new { background: #1e3a5f; color: #60a5fa; }
.badge-active { background: #1a3d1a; color: #4ade80; }
.badge-done { background: #1a3d1a; color: #4ade80; }
.badge-rejected { background: #3d1a1a; color: #f87171; }

.refresh-btn {
  position: fixed; bottom: 20px; right: 20px;
  width: 48px; height: 48px; border-radius: 50%;
  background: #2563eb; color: #fff; border: none;
  font-size: 20px; cursor: pointer; box-shadow: 0 4px 12px rgba(37,99,235,0.3);
}
.empty { text-align: center; color: #666; padding: 40px; font-size: 14px; }
.search {
  width: 100%; padding: 10px 14px; border-radius: 8px;
  background: #1a1a1a; border: 1px solid #2a2a2a; color: #e0e0e0;
  margin-bottom: 12px; font-size: 14px;
}
.search:focus { outline: none; border-color: #2563eb; }
</style>
</head>
<body>

<div class="header">
  <h1>🎯 Asmo Creative AI</h1>
  <p>Admin Panel — Realtime Dashboard</p>
</div>

<div class="stats-grid" id="statsGrid"></div>

<div class="tabs">
  <div class="tab active" onclick="showTab('orders')">📦 Buyurtmalar</div>
  <div class="tab" onclick="showTab('clients')">👥 Mijozlar</div>
  <div class="tab" onclick="showTab('revenue')">💰 Daromad</div>
</div>

<input class="search" id="searchInput" placeholder="Qidirish..." oninput="filterTable()">

<div class="section active" id="sec-orders">
  <table id="ordersTable">
    <thead><tr><th>#</th><th>Mijoz</th><th>Xizmat</th><th>Sana</th><th>Holat</th></tr></thead>
    <tbody></tbody>
  </table>
</div>

<div class="section" id="sec-clients">
  <table id="clientsTable">
    <thead><tr><th>Ism</th><th>Username</th><th>Buyurtmalar</th><th>Oxirgi</th></tr></thead>
    <tbody></tbody>
  </table>
</div>

<div class="section" id="sec-revenue">
  <div id="revenueContent"></div>
</div>

<button class="refresh-btn" onclick="loadData()">↻</button>

<script>
const TOKEN = new URLSearchParams(window.location.search).get('token');
let currentTab = 'orders';
let allData = {};

async function loadData() {
  try {
    const r = await fetch('/api/dashboard?token=' + TOKEN);
    allData = await r.json();
    renderStats();
    renderOrders();
    renderClients();
    renderRevenue();
  } catch(e) {
    document.body.innerHTML = '<div class="empty">Yuklanmadi. Sahifani yangilang.</div>';
  }
}

function renderStats() {
  const s = allData.stats;
  document.getElementById('statsGrid').innerHTML = `
    <div class="stat-card blue">
      <div class="stat-value">${s.total_users}</div>
      <div class="stat-label">Jami mijozlar</div>
    </div>
    <div class="stat-card green">
      <div class="stat-value">${s.today_orders}</div>
      <div class="stat-label">Bugungi buyurtma</div>
    </div>
    <div class="stat-card yellow">
      <div class="stat-value">${s.month_orders}</div>
      <div class="stat-label">Bu oy</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${s.total_orders}</div>
      <div class="stat-label">Jami buyurtma</div>
    </div>
    <div class="stat-card green">
      <div class="stat-value">${Number(s.confirmed_sum).toLocaleString()}</div>
      <div class="stat-label">Daromad (so'm)</div>
    </div>
    <div class="stat-card red">
      <div class="stat-value">${s.new_orders}</div>
      <div class="stat-label">Yangi (kutmoqda)</div>
    </div>
  `;
}

function statusBadge(status) {
  const map = {
    'new': ['Yangi', 'badge-new'],
    'confirmed': ['Tasdiqlangan', 'badge-active'],
    'in_progress': ['Jarayonda', 'badge-active'],
    'done': ['Tayyor', 'badge-done'],
    'rejected': ['Rad etilgan', 'badge-rejected'],
  };
  const [text, cls] = map[status] || [status, 'badge-new'];
  return `<span class="badge ${cls}">${text}</span>`;
}

function renderOrders() {
  const tbody = document.querySelector('#ordersTable tbody');
  const orders = allData.orders || [];
  if (!orders.length) { tbody.innerHTML = '<tr><td colspan="5" class="empty">Buyurtmalar yo\\'q</td></tr>'; return; }
  tbody.innerHTML = orders.map(o => `
    <tr>
      <td>#${o.id}</td>
      <td>${o.name || o.user_fullname || '—'}</td>
      <td>${o.svc_name || '—'}</td>
      <td>${(o.created_at || '').slice(0,16)}</td>
      <td>${statusBadge(o.status)}</td>
    </tr>
  `).join('');
}

function renderClients() {
  const tbody = document.querySelector('#clientsTable tbody');
  const clients = allData.clients || [];
  if (!clients.length) { tbody.innerHTML = '<tr><td colspan="4" class="empty">Mijozlar yo\\'q</td></tr>'; return; }
  tbody.innerHTML = clients.map(c => `
    <tr>
      <td>${c.full_name || '—'}</td>
      <td>${c.username ? '@'+c.username : '—'}</td>
      <td>${c.orders_count || 0}</td>
      <td>${(c.last_order || '').slice(0,10)}</td>
    </tr>
  `).join('');
}

function renderRevenue() {
  const s = allData.stats;
  document.getElementById('revenueContent').innerHTML = `
    <div class="stats-grid">
      <div class="stat-card green">
        <div class="stat-value">${s.confirmed_count}</div>
        <div class="stat-label">Tasdiqlangan to'lov</div>
      </div>
      <div class="stat-card yellow">
        <div class="stat-value">${s.pending_payments}</div>
        <div class="stat-label">Kutilmoqda</div>
      </div>
      <div class="stat-card green">
        <div class="stat-value">${Number(s.confirmed_sum).toLocaleString()}</div>
        <div class="stat-label">Umumiy daromad (so'm)</div>
      </div>
      <div class="stat-card blue">
        <div class="stat-value">${s.top_service}</div>
        <div class="stat-label">Top xizmat (${s.top_service_count} ta)</div>
      </div>
    </div>
  `;
}

function showTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('sec-' + tab).classList.add('active');
}

function filterTable() {
  const q = document.getElementById('searchInput').value.toLowerCase();
  const tableId = currentTab === 'orders' ? 'ordersTable' : 'clientsTable';
  document.querySelectorAll('#' + tableId + ' tbody tr').forEach(row => {
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

loadData();
setInterval(loadData, 30000); // Har 30 sekundda yangilanadi
</script>

</body>
</html>"""


class AdminWebHandler:
    """Mixin methods for the HTTP handler to serve admin dashboard."""

    @staticmethod
    def handle_admin_request(handler, path: str) -> bool:
        """Returns True if the request was handled."""
        parsed = urlparse(path)

        if parsed.path == "/admin":
            if not _auth_ok(path):
                handler.send_response(403)
                handler.end_headers()
                handler.wfile.write(b"Access denied. Token required.")
                return True
            handler.send_response(200)
            handler.send_header("Content-Type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(DASHBOARD_HTML.encode())
            return True

        if parsed.path == "/api/dashboard":
            if not _auth_ok(path):
                handler.send_response(403)
                handler.end_headers()
                handler.wfile.write(b'{"error":"forbidden"}')
                return True
            try:
                rs = db.revenue_stats()
                orders = db.all_orders_data()
                clients = db.all_clients_data()
                data = {"stats": rs, "orders": orders, "clients": clients}
                handler.send_response(200)
                handler.send_header("Content-Type", "application/json")
                handler.end_headers()
                handler.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode())
            except Exception as e:
                handler.send_response(500)
                handler.end_headers()
                handler.wfile.write(json.dumps({"error": str(e)}).encode())
            return True

        return False
