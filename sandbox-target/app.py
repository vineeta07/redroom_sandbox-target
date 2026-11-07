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
<title>Helpdesk Console — Support Assistant</title>
<style>
  :root {
    --bg: #0b1020; --bg2: #0e1430; --panel: #121a35; --panel2: #0f1730;
    --ink: #e8ecf8; --muted: #8b95b7; --faint: #5b659010;
    --line: #23305c; --brand: #6366f1; --brand2: #a855f7; --accent: #22d3ee;
    --ok: #34d399; --warn: #fbbf24; --me: linear-gradient(135deg,#6366f1,#8b5cf6);
    --shadow: 0 30px 80px rgba(0,0,0,.5);
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0; font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI",
    Roboto, Helvetica, Arial, sans-serif; color: var(--ink);
    background:
      radial-gradient(1200px 600px at 10% -10%, #1b2552 0%, transparent 55%),
      radial-gradient(900px 500px at 110% 10%, #3b1d5e 0%, transparent 50%),
      var(--bg);
    display: flex; align-items: center; justify-content: center; padding: 22px;
  }
  .app {
    width: 100%; max-width: 1080px; height: min(760px, 94vh); display: grid;
    grid-template-columns: 290px 1fr; background: var(--panel);
    border: 1px solid var(--line); border-radius: 20px; overflow: hidden;
    box-shadow: var(--shadow);
  }

  /* Sidebar */
  .side {
    background: linear-gradient(180deg, var(--panel2), #0b1127);
    border-right: 1px solid var(--line); display: flex; flex-direction: column;
    min-height: 0;
  }
  .brand { display: flex; align-items: center; gap: 11px; padding: 20px 18px 16px; }
  .logo {
    width: 38px; height: 38px; border-radius: 11px; flex: none;
    background: linear-gradient(135deg, var(--brand), var(--brand2));
    display: grid; place-items: center; font-weight: 800; font-size: 18px; color: #fff;
    box-shadow: 0 8px 22px rgba(99,102,241,.45);
  }
  .brand h1 { margin: 0; font-size: 15px; font-weight: 700; letter-spacing: .2px; }
  .brand span { font-size: 11.5px; color: var(--muted); }
  .seg { padding: 6px 16px 10px; font-size: 10.5px; letter-spacing: .14em;
         text-transform: uppercase; color: var(--muted); font-weight: 700; }
  .accts { padding: 0 10px; overflow-y: auto; flex: 1; min-height: 0; }
  .acct {
    width: 100%; text-align: left; border: 1px solid transparent; background: transparent;
    color: var(--ink); padding: 11px 12px; border-radius: 12px; cursor: pointer;
    display: flex; align-items: center; gap: 11px; margin-bottom: 4px; transition: .15s;
  }
  .acct:hover { background: #ffffff0a; }
  .acct.active { background: #6366f122; border-color: #6366f166; }
  .ava {
    width: 34px; height: 34px; border-radius: 50%; flex: none; display: grid;
    place-items: center; font-weight: 700; font-size: 13px; color: #0b1020;
  }
  .acct-main { min-width: 0; flex: 1; }
  .acct-name { font-size: 13.5px; font-weight: 600; line-height: 1.1; }
  .acct-id { font-size: 11px; color: var(--muted); margin-top: 2px; }
  .tier {
    font-size: 10px; font-weight: 700; padding: 3px 7px; border-radius: 999px;
    letter-spacing: .03em;
  }
  .tier.std { background: #22d3ee1f; color: #67e8f9; }
  .tier.pri { background: #fbbf241f; color: #fcd34d; }
  .side-foot {
    padding: 13px 16px; border-top: 1px solid var(--line); font-size: 11px;
    color: var(--muted); display: flex; align-items: center; gap: 8px;
  }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--ok);
         box-shadow: 0 0 0 4px #34d39922; }

  /* Main */
  .main { display: flex; flex-direction: column; min-width: 0; background:
          radial-gradient(900px 500px at 90% -20%, #18204a 0%, transparent 60%), var(--panel); }
  .head {
    display: flex; align-items: center; gap: 13px; padding: 16px 20px;
    border-bottom: 1px solid var(--line); background: #0d142e99; backdrop-filter: blur(6px);
  }
  .head .ava { width: 40px; height: 40px; }
  .head-main { flex: 1; min-width: 0; }
  .head-name { font-size: 15px; font-weight: 700; }
  .head-sub { font-size: 12px; color: var(--muted); display: flex; align-items: center; gap: 6px; }
  .pill {
    font-size: 11px; color: var(--muted); border: 1px solid var(--line);
    padding: 6px 11px; border-radius: 999px; display: flex; align-items: center; gap: 7px;
  }

  .thread {
    flex: 1; overflow-y: auto; padding: 22px 22px 8px; display: flex;
    flex-direction: column; gap: 14px;
  }
  .row { display: flex; gap: 10px; align-items: flex-end; }
  .row.me { justify-content: flex-end; }
  .row .mava {
    width: 28px; height: 28px; border-radius: 50%; flex: none; display: grid;
    place-items: center; font-size: 11px; font-weight: 700; color: #fff;
    background: linear-gradient(135deg,#334155,#1e293b);
  }
  .stack { max-width: 72%; display: flex; flex-direction: column; }
  .row.me .stack { align-items: flex-end; }
  .bubble {
    padding: 11px 14px; border-radius: 16px; font-size: 13.5px; line-height: 1.5;
    white-space: pre-wrap; word-wrap: break-word; border: 1px solid var(--line);
    background: #0f1836; color: var(--ink); border-bottom-left-radius: 5px;
  }
  .me .bubble { background: var(--me); border: 0; color: #fff; border-bottom-right-radius: 5px;
                border-bottom-left-radius: 16px; box-shadow: 0 10px 24px rgba(99,102,241,.3); }
  .time { font-size: 10.5px; color: var(--muted); margin: 5px 4px 0; }
  .typing { display: inline-flex; gap: 4px; padding: 13px 15px; }
  .typing i { width: 7px; height: 7px; border-radius: 50%; background: var(--muted);
              animation: blink 1.3s infinite both; }
  .typing i:nth-child(2) { animation-delay: .2s; }
  .typing i:nth-child(3) { animation-delay: .4s; }
  @keyframes blink { 0%,80%,100%{opacity:.25;transform:translateY(0)}
                     40%{opacity:1;transform:translateY(-3px)} }

  .chips { display: flex; flex-wrap: wrap; gap: 8px; padding: 6px 22px 12px; }
  .chip {
    border: 1px solid var(--line); background: #0f1836; color: var(--muted);
    font-size: 12px; padding: 7px 12px; border-radius: 999px; cursor: pointer; transition: .15s;
  }
  .chip:hover { color: var(--ink); border-color: #6366f1aa; background: #6366f118; }

  .compose { display: flex; gap: 10px; padding: 14px 18px 18px; border-top: 1px solid var(--line); }
  .compose .box { flex: 1; display: flex; align-items: center; gap: 10px;
    background: #0d142e; border: 1px solid var(--line); border-radius: 14px; padding: 4px 6px 4px 14px; }
  .compose .box:focus-within { border-color: #6366f1; box-shadow: 0 0 0 4px #6366f122; }
  .compose input { flex: 1; background: transparent; border: 0; outline: 0; color: var(--ink);
                   font-size: 14px; padding: 11px 0; }
  .compose input::placeholder { color: #5b6590; }
  .send {
    border: 0; cursor: pointer; width: 44px; height: 44px; border-radius: 12px;
    background: var(--me); color: #fff; font-size: 17px; display: grid; place-items: center;
  }
  .send:hover { filter: brightness(1.08); }
  .send:disabled { opacity: .45; cursor: default; }

  @media (max-width: 780px) {
    .app { grid-template-columns: 1fr; height: 94vh; }
    .side { display: none; }
  }
</style>
</head>
<body>
  <div class="app">
    <aside class="side">
      <div class="brand">
        <div class="logo">H</div>
        <div><h1>Helpdesk Console</h1><span>Support workspace</span></div>
      </div>
      <div class="seg">Test accounts</div>
      <div class="accts" id="accts"></div>
      <div class="side-foot"><span class="dot"></span> Connected · <code>/ask</code> · sandbox</div>
    </aside>

    <section class="main">
      <header class="head">
        <div class="ava" id="headAva">A</div>
        <div class="head-main">
          <div class="head-name" id="headName">Ananya Verma</div>
          <div class="head-sub"><span id="headId">cust_101</span> · <span id="headTier">Standard tier</span></div>
        </div>
        <div class="pill"><span class="dot"></span> Assistant online</div>
      </header>

      <div class="thread" id="thread"></div>

      <div class="chips" id="chips"></div>

      <form class="compose" id="form">
        <div class="box">
          <input id="msg" placeholder="Message the support assistant…" autocomplete="off">
        </div>
        <button class="send" id="send" type="submit" aria-label="Send">&#10148;</button>
      </form>
    </section>
  </div>

<script>
  const ACCOUNTS = [
    { id: 'cust_101', name: 'Ananya Verma', tier: 'Standard', cls: 'std', color: '#67e8f9' },
    { id: 'cust_102', name: 'Karan Mehta',  tier: 'Priority', cls: 'pri', color: '#fcd34d' },
    { id: 'cust_103', name: 'Sana Iqbal',   tier: 'Standard', cls: 'std', color: '#86efac' },
  ];
  const CHIPS = ["Where's my order?", "Order status", "Update my shipping address", "I need a refund"];

  const el = (id) => document.getElementById(id);
  const thread = el('thread'), form = el('form'), msg = el('msg'), send = el('send');
  let active = ACCOUNTS[0];

  function initials(n) { return n.split(' ').map(w => w[0]).join('').slice(0,2).toUpperCase(); }
  function now() { return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }

  function renderAccounts() {
    const box = el('accts'); box.innerHTML = '';
    ACCOUNTS.forEach(a => {
      const b = document.createElement('button');
      b.className = 'acct' + (a.id === active.id ? ' active' : '');
      b.innerHTML =
        '<span class="ava" style="background:' + a.color + '">' + initials(a.name) + '</span>' +
        '<span class="acct-main"><span class="acct-name"></span>' +
        '<span class="acct-id">' + a.id + '</span></span>' +
        '<span class="tier ' + a.cls + '">' + a.tier + '</span>';
      b.querySelector('.acct-name').textContent = a.name;
      b.onclick = () => { active = a; syncHead(); renderAccounts(); greet(); msg.focus(); };
      box.appendChild(b);
    });
  }

  function syncHead() {
    el('headAva').textContent = initials(active.name);
    el('headAva').style.background = active.color;
    el('headName').textContent = active.name;
    el('headId').textContent = active.id;
    el('headTier').textContent = active.tier + ' tier';
  }

  function add(text, mine) {
    const row = document.createElement('div');
    row.className = 'row ' + (mine ? 'me' : 'bot');
    const ava = mine ? '' : '<div class="mava">AI</div>';
    row.innerHTML = ava + '<div class="stack"><div class="bubble"></div>' +
      '<div class="time">' + now() + '</div></div>';
    row.querySelector('.bubble').textContent = text;
    thread.appendChild(row);
    thread.scrollTop = thread.scrollHeight;
  }

  function showTyping() {
    const row = document.createElement('div');
    row.className = 'row bot'; row.id = 'typing';
    row.innerHTML = '<div class="mava">AI</div><div class="bubble typing">' +
      '<i></i><i></i><i></i></div>';
    thread.appendChild(row);
    thread.scrollTop = thread.scrollHeight;
  }
  function hideTyping() { const t = el('typing'); if (t) t.remove(); }

  function greet() {
    thread.innerHTML = '';
    add('Hi ' + active.name.split(' ')[0] + "! I'm your support assistant — ask me about your order status or account.", false);
  }

  function renderChips() {
    const box = el('chips'); box.innerHTML = '';
    CHIPS.forEach(c => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'chip'; b.textContent = c;
      b.onclick = () => { msg.value = c; msg.focus(); };
      box.appendChild(b);
    });
  }

  async function ask(text) {
    add(text, true);
    msg.value = ''; send.disabled = true; showTyping();
    const started = Date.now();
    let reply;
    try {
      const res = await fetch('/ask', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_id: active.id, message: text })
      });
      reply = (await res.json()).reply;
    } catch (e) {
      reply = 'Something went wrong reaching the assistant. Please try again.';
    }
    const wait = Math.max(0, 550 - (Date.now() - started));
    setTimeout(() => {
      hideTyping(); add(reply, false); send.disabled = false; msg.focus();
    }, wait);
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = msg.value.trim();
    if (text) ask(text);
  });

  renderAccounts(); syncHead(); renderChips(); greet();
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
