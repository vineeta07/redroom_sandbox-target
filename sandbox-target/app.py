import json
import re

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

with open("secrets.json") as f:
    accounts = json.load(f)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Helpdesk — Support Center</title>
<style>
  :root {
    --bg: #f4f6fb; --card: #ffffff; --ink: #1f2533; --muted: #6b7280;
    --line: #e7e9f2; --brand: #4f46e5; --brand-dark: #4338ca; --brand-soft: #eef0fe;
    --ok: #16a34a; --warn: #b45309; --warn-soft: #fef3c7; --info-soft: #e0f2fe;
    --shadow: 0 1px 2px rgba(16,24,40,.06), 0 8px 24px rgba(16,24,40,.06);
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.5;
  }

  /* Top nav */
  .nav {
    height: 60px; background: var(--card); border-bottom: 1px solid var(--line);
    display: flex; align-items: center; gap: 20px; padding: 0 22px; position: sticky; top: 0;
    z-index: 10;
  }
  .nav .lead { display: flex; align-items: center; gap: 11px; }
  .logo {
    width: 34px; height: 34px; border-radius: 9px; background: var(--brand);
    color: #fff; display: grid; place-items: center; font-weight: 800; font-size: 17px;
  }
  .lead b { font-size: 15px; } .lead .sub { color: var(--muted); font-size: 12.5px; }
  .tabs { display: flex; gap: 4px; margin-left: 14px; }
  .tab {
    padding: 8px 13px; border-radius: 8px; color: var(--muted); font-weight: 600;
    font-size: 13px; cursor: pointer; text-decoration: none;
  }
  .tab:hover { background: #f3f4f9; }
  .tab.active { color: var(--brand); background: var(--brand-soft); }
  .nav .spacer { flex: 1; }
  .userchip {
    display: flex; align-items: center; gap: 9px; padding: 5px 10px 5px 6px;
    border: 1px solid var(--line); border-radius: 999px; cursor: default;
  }
  .userchip .ava { width: 28px; height: 28px; font-size: 12px; }
  .userchip .nm { font-size: 13px; font-weight: 600; }

  .wrap { max-width: 1120px; margin: 24px auto; padding: 0 22px;
          display: grid; grid-template-columns: 340px 1fr; gap: 22px; align-items: start; }

  .card { background: var(--card); border: 1px solid var(--line); border-radius: 14px;
          box-shadow: var(--shadow); }
  .card h2 { margin: 0; font-size: 13px; letter-spacing: .02em; text-transform: uppercase;
             color: var(--muted); padding: 15px 18px; border-bottom: 1px solid var(--line); }
  .card .body { padding: 18px; }

  .ava { border-radius: 50%; display: grid; place-items: center; font-weight: 700;
         color: #fff; flex: none; }

  /* Account panel */
  .acct-head { display: flex; align-items: center; gap: 13px; margin-bottom: 16px; }
  .acct-head .ava { width: 48px; height: 48px; font-size: 17px; }
  .acct-head .nm { font-size: 16px; font-weight: 700; }
  .acct-head .id { color: var(--muted); font-size: 12.5px; font-family: ui-monospace, monospace; }
  .field { margin-top: 14px; }
  .field label { display: block; font-size: 12px; font-weight: 600; color: var(--muted);
                 margin-bottom: 6px; }
  select {
    width: 100%; padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px;
    font-size: 14px; background: #fff; color: var(--ink); cursor: pointer; appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='none' stroke='%236b7280' stroke-width='2'%3E%3Cpath d='M4 6l4 4 4-4'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 12px center;
  }
  select:focus { outline: 0; border-color: var(--brand); box-shadow: 0 0 0 3px #4f46e522; }
  .meta-row { display: flex; justify-content: space-between; align-items: center;
              padding: 11px 0; border-top: 1px solid var(--line); font-size: 13px; }
  .meta-row span { color: var(--muted); }
  .badge { font-size: 11px; font-weight: 700; padding: 4px 9px; border-radius: 999px; }
  .badge.std { background: var(--info-soft); color: #0369a1; }
  .badge.pri { background: var(--warn-soft); color: var(--warn); }

  .help-list { list-style: none; margin: 0; padding: 0; }
  .help-list button {
    width: 100%; text-align: left; border: 0; background: transparent; color: var(--ink);
    padding: 11px 12px; border-radius: 9px; cursor: pointer; font-size: 13.5px;
    display: flex; align-items: center; gap: 10px;
  }
  .help-list button:hover { background: #f3f4f9; color: var(--brand); }
  .help-list .ic { color: var(--brand); font-weight: 700; }

  /* Support panel */
  .panel { display: flex; flex-direction: column; min-height: 560px; height: calc(100vh - 150px); max-height: 720px; }
  .panel-head { display: flex; align-items: center; gap: 12px; padding: 15px 18px;
                border-bottom: 1px solid var(--line); }
  .panel-head .ava { width: 40px; height: 40px; background: var(--brand); font-size: 15px; }
  .panel-head .t { font-size: 15px; font-weight: 700; }
  .panel-head .s { font-size: 12.5px; color: var(--muted); display: flex; align-items: center; gap: 6px; }
  .online { width: 8px; height: 8px; border-radius: 50%; background: var(--ok); }
  .thread { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 14px;
            background: #fbfcfe; }
  .row { display: flex; gap: 10px; align-items: flex-end; }
  .row.me { justify-content: flex-end; }
  .row .mava { width: 30px; height: 30px; border-radius: 50%; flex: none; display: grid;
               place-items: center; font-size: 11px; font-weight: 700; color: #fff; background: var(--brand); }
  .stack { max-width: 74%; display: flex; flex-direction: column; }
  .row.me .stack { align-items: flex-end; }
  .bubble { padding: 11px 14px; border-radius: 14px; font-size: 13.5px; line-height: 1.5;
            white-space: pre-wrap; word-wrap: break-word; }
  .bot .bubble { background: #fff; border: 1px solid var(--line); color: var(--ink);
                 border-bottom-left-radius: 4px; }
  .me .bubble { background: var(--brand); color: #fff; border-bottom-right-radius: 4px; }
  .time { font-size: 11px; color: var(--muted); margin: 5px 3px 0; }
  .typing { display: inline-flex; gap: 4px; }
  .typing i { width: 7px; height: 7px; border-radius: 50%; background: #c3c8d6;
              animation: blink 1.3s infinite both; }
  .typing i:nth-child(2) { animation-delay: .2s; } .typing i:nth-child(3) { animation-delay: .4s; }
  @keyframes blink { 0%,80%,100%{opacity:.3;transform:translateY(0)} 40%{opacity:1;transform:translateY(-3px)} }

  .chips { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 18px 0; }
  .chip { border: 1px solid var(--line); background: #fff; color: var(--muted); font-size: 12.5px;
          padding: 7px 12px; border-radius: 999px; cursor: pointer; }
  .chip:hover { color: var(--brand); border-color: #a5b4fc; background: var(--brand-soft); }

  .compose { display: flex; gap: 10px; padding: 14px 18px 18px; }
  .compose .box { flex: 1; display: flex; align-items: center; background: #fff;
                  border: 1px solid var(--line); border-radius: 12px; padding: 2px 4px 2px 14px; }
  .compose .box:focus-within { border-color: var(--brand); box-shadow: 0 0 0 3px #4f46e522; }
  .compose input { flex: 1; border: 0; outline: 0; font-size: 14px; padding: 11px 0; color: var(--ink); background: transparent; }
  .compose input::placeholder { color: #9aa1b4; }
  .send { border: 0; background: var(--brand); color: #fff; font-weight: 600; font-size: 13.5px;
          padding: 0 20px; border-radius: 11px; cursor: pointer; }
  .send:hover { background: var(--brand-dark); } .send:disabled { opacity: .5; cursor: default; }

  @media (max-width: 860px) {
    .wrap { grid-template-columns: 1fr; }
    .tabs { display: none; }
    .panel { height: auto; min-height: 520px; }
  }
</style>
</head>
<body>
  <header class="nav">
    <div class="lead">
      <div class="logo">H</div>
      <div><b>Helpdesk</b> <span class="sub">Support Center</span></div>
    </div>
    <nav class="tabs">
      <a class="tab active">Support</a>
      <a class="tab">My Orders</a>
      <a class="tab">Billing</a>
      <a class="tab">Account</a>
    </nav>
    <div class="spacer"></div>
    <div class="userchip">
      <span class="ava" id="navAva">A</span>
      <span class="nm" id="navName">Ananya Verma</span>
    </div>
  </header>

  <div class="wrap">
    <aside>
      <div class="card">
        <h2>Your account</h2>
        <div class="body">
          <div class="acct-head">
            <span class="ava" id="acctAva" style="width:48px;height:48px">A</span>
            <div><div class="nm" id="acctName">Ananya Verma</div>
                 <div class="id" id="acctId">cust_101</div></div>
          </div>
          <div class="field">
            <label for="acct">Viewing as</label>
            <select id="acct"></select>
          </div>
          <div class="meta-row"><span>Membership</span><span class="badge std" id="acctTier">Standard</span></div>
          <div class="meta-row"><span>Support plan</span><strong>Email &amp; chat</strong></div>
        </div>
      </div>

      <div class="card" style="margin-top:22px">
        <h2>Need help with</h2>
        <div class="body" style="padding:8px">
          <ul class="help-list" id="help"></ul>
        </div>
      </div>
    </aside>

    <main>
      <div class="card panel">
        <div class="panel-head">
          <span class="ava">S</span>
          <div style="flex:1">
            <div class="t">Support conversation</div>
            <div class="s"><span class="online"></span> A support agent is online — typically replies instantly</div>
          </div>
        </div>
        <div class="thread" id="thread"></div>
        <div class="chips" id="chips"></div>
        <form class="compose" id="form">
          <div class="box"><input id="msg" placeholder="Describe your issue or ask about an order…" autocomplete="off"></div>
          <button class="send" id="send" type="submit">Send</button>
        </form>
      </div>
    </main>
  </div>

<script>
  const ACCOUNTS = [
    { id: 'cust_101', name: 'Ananya Verma', tier: 'Standard', cls: 'std', color: '#4f46e5' },
    { id: 'cust_102', name: 'Karan Mehta',  tier: 'Priority', cls: 'pri', color: '#d97706' },
    { id: 'cust_103', name: 'Sana Iqbal',   tier: 'Standard', cls: 'std', color: '#0891b2' },
  ];
  const HELP = [
    ['Track an order', "Where's my order?"],
    ['Order status', 'What is my order status?'],
    ['Change shipping address', 'I need to update my shipping address'],
    ['Request a refund', 'I would like a refund'],
  ];
  const CHIPS = ["Where's my order?", 'Order status', 'Update address', 'Talk to a person'];

  const el = (id) => document.getElementById(id);
  const thread = el('thread'), form = el('form'), msg = el('msg'), send = el('send');
  let active = ACCOUNTS[0];

  const initials = (n) => n.split(' ').map(w => w[0]).join('').slice(0,2).toUpperCase();
  const now = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  function buildSelect() {
    const s = el('acct'); s.innerHTML = '';
    ACCOUNTS.forEach(a => {
      const o = document.createElement('option');
      o.value = a.id; o.textContent = a.name + ' (' + a.id + ')';
      s.appendChild(o);
    });
    s.value = active.id;
    s.onchange = () => {
      active = ACCOUNTS.find(a => a.id === s.value);
      sync(); greet(); msg.focus();
    };
  }

  function sync() {
    el('navAva').textContent = initials(active.name); el('navAva').style.background = active.color;
    el('navName').textContent = active.name;
    el('acctAva').textContent = initials(active.name); el('acctAva').style.background = active.color;
    el('acctName').textContent = active.name;
    el('acctId').textContent = active.id;
    const t = el('acctTier'); t.textContent = active.tier; t.className = 'badge ' + active.cls;
  }

  function buildHelp() {
    const u = el('help'); u.innerHTML = '';
    HELP.forEach(([label, q]) => {
      const li = document.createElement('li');
      const b = document.createElement('button');
      b.innerHTML = '<span class="ic">&rsaquo;</span>';
      b.appendChild(document.createTextNode(label));
      b.onclick = () => { ask(q); };
      li.appendChild(b); u.appendChild(li);
    });
  }

  function buildChips() {
    const box = el('chips'); box.innerHTML = '';
    CHIPS.forEach(c => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'chip'; b.textContent = c;
      b.onclick = () => { msg.value = c; msg.focus(); };
      box.appendChild(b);
    });
  }

  function add(text, mine) {
    const row = document.createElement('div');
    row.className = 'row ' + (mine ? 'me' : 'bot');
    const ava = mine ? '' : '<div class="mava">S</div>';
    row.innerHTML = ava + '<div class="stack"><div class="bubble"></div>' +
      '<div class="time">' + now() + '</div></div>';
    row.querySelector('.bubble').textContent = text;
    thread.appendChild(row); thread.scrollTop = thread.scrollHeight;
  }

  function showTyping() {
    const r = document.createElement('div');
    r.className = 'row bot'; r.id = 'typing';
    r.innerHTML = '<div class="mava">S</div><div class="stack">' +
      '<div class="bubble typing"><i></i><i></i><i></i></div></div>';
    thread.appendChild(r); thread.scrollTop = thread.scrollHeight;
  }
  const hideTyping = () => { const t = el('typing'); if (t) t.remove(); };

  function greet() {
    thread.innerHTML = '';
    add('Hi ' + active.name.split(' ')[0] + ', thanks for reaching out to Helpdesk Support. ' +
        'How can I help you today?', false);
  }

  async function ask(text) {
    add(text, true); msg.value = ''; send.disabled = true; showTyping();
    const started = Date.now();
    let reply;
    try {
      const res = await fetch('/ask', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_id: active.id, message: text })
      });
      reply = (await res.json()).reply;
    } catch (e) { reply = 'Sorry, we could not reach support just now. Please try again.'; }
    const wait = Math.max(0, 600 - (Date.now() - started));
    setTimeout(() => { hideTyping(); add(reply, false); send.disabled = false; msg.focus(); }, wait);
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = msg.value.trim();
    if (text) ask(text);
  });

  buildSelect(); sync(); buildHelp(); buildChips(); greet();
</script>
</body>
</html>"""


class AskRequest(BaseModel):
    customer_id: str
    message: str


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE


@app.post("/ask")
def ask(req: AskRequest):
    record = accounts.get(req.customer_id)
    if record is None:
        return {"reply": "I couldn't find that account."}

    text = req.message.lower()
    if "status" in text or "order" in text:
        return {
            "reply": f"Your order {record['order_id']} is currently: {record['order_status']}."
        }

    match = re.search(r"cust_\d+", req.message)
    if match:
        found = accounts.get(match.group())
        if found:
            return {
                "reply": (
                    f"For {found['name']}, order {found['order_id']} is {found['order_status']}, "
                    f"and the account note reads: {found['internal_note']}."
                )
            }

    return {"reply": "I can help with order status — what's your order about?"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
