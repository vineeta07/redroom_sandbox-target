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
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Harbor — Customer Support</title>
<style>
  :root {
    --bg: #f6f4fb; --bg2: #efecf8; --card: #ffffff; --ink: #3b3a52; --muted: #8b8aa6;
    --line: #ece8f6; --accent: #8a7fd6; --accent-ink: #6b5fc4; --accent-soft: #efecfb;
    --mint: #bfe6d6; --mint-ink: #3f8f74; --peach: #f8d3bf; --peach-ink: #c07a52;
    --sky: #c9def3; --sky-ink: #5083b0; --lilac: #e2d4f2; --lilac-ink: #8a62b8;
    --bubble-bot: #f4f2fb; --shadow: 0 1px 2px rgba(60,50,90,.05), 0 10px 30px rgba(60,50,90,.07);
    --radius: 16px;
  }
  html[data-theme="dark"] {
    --bg: #1b1a26; --bg2: #201f2e; --card: #26253655; --card: #272636; --ink: #e9e7f5;
    --muted: #b9b7d6; --line: #35334a; --accent: #a99ef0; --accent-ink: #bcb2ff;
    --accent-soft: #332f52; --bubble-bot: #2e2d41;
    --mint: #2f5c4e; --mint-ink: #9fe0c9; --peach: #6b4332; --peach-ink: #f6c3a6;
    --sky: #2d4a66; --sky-ink: #add4f4; --lilac: #4a3a63; --lilac-ink: #d8c3f2;
    --shadow: 0 1px 2px rgba(0,0,0,.25), 0 14px 36px rgba(0,0,0,.35);
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0; background: var(--bg); color: var(--ink); transition: background .3s, color .3s;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 14.5px; line-height: 1.55;
  }

  /* Nav */
  .nav { height: 62px; background: var(--card); border-bottom: 1px solid var(--line);
         display: flex; align-items: center; gap: 18px; padding: 0 22px; position: sticky; top: 0; z-index: 20; }
  .brand { display: flex; align-items: center; gap: 11px; cursor: pointer; }
  .logo { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg,#a99ef0,#8a7fd6);
          color: #fff; display: grid; place-items: center; font-size: 18px; }
  .brand b { font-size: 15.5px; font-weight: 700; }
  .tabs { display: flex; gap: 4px; margin-left: 10px; }
  .tab { padding: 8px 14px; border-radius: 10px; color: var(--muted); font-weight: 600; font-size: 13.5px;
         cursor: pointer; border: 0; background: transparent; }
  .tab:hover { background: var(--bg2); color: var(--ink); }
  .tab.active { color: var(--accent-ink); background: var(--accent-soft); }
  .spacer { flex: 1; }
  .icon-btn { width: 40px; height: 40px; border-radius: 11px; border: 1px solid var(--line); background: var(--card);
              cursor: pointer; font-size: 17px; display: grid; place-items: center; color: var(--ink); }
  .icon-btn:hover { background: var(--bg2); }
  .userchip { display: flex; align-items: center; gap: 9px; padding: 5px 12px 5px 6px; border: 1px solid var(--line);
              border-radius: 999px; }
  .ava { border-radius: 50%; display: grid; place-items: center; font-weight: 700; color: #fff; flex: none;
         background: linear-gradient(135deg,#f0a8c4,#d98ab0); }
  .userchip .ava { width: 28px; height: 28px; font-size: 12px; }
  .userchip .nm { font-size: 13.5px; font-weight: 600; }

  .wrap { max-width: 980px; margin: 30px auto; padding: 0 22px; }
  .view { display: none; }
  .view.active { display: block; animation: fade .25s ease; }
  @keyframes fade { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

  /* Home */
  .hero { display: flex; align-items: center; gap: 16px; margin-bottom: 22px; }
  .hero .ava { width: 56px; height: 56px; font-size: 20px; }
  .hero h1 { margin: 0; font-size: 24px; font-weight: 750; }
  .hero p { margin: 3px 0 0; color: var(--muted); }
  .askbar { display: flex; gap: 10px; background: var(--card); border: 1px solid var(--line);
            border-radius: 14px; padding: 7px 8px 7px 16px; box-shadow: var(--shadow); margin-bottom: 26px; }
  .askbar input { flex: 1; border: 0; outline: 0; background: transparent; color: var(--ink); font-size: 15px; }
  .askbar input::placeholder { color: var(--muted); }
  .btn { border: 0; cursor: pointer; background: var(--accent); color: #fff; font-weight: 650; font-size: 14px;
         padding: 11px 20px; border-radius: 11px; }
  .btn:hover { background: var(--accent-ink); }
  .cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
  .ac { text-align: left; background: var(--card); border: 1px solid var(--line); border-radius: var(--radius);
        padding: 20px; cursor: pointer; box-shadow: var(--shadow); transition: transform .15s, box-shadow .15s;
        color: var(--ink); font-family: inherit; }
  .ac:hover { transform: translateY(-2px); box-shadow: 0 14px 34px rgba(60,50,90,.12); }
  .ac .ci { width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center; font-size: 21px;
            margin-bottom: 13px; }
  .ac h3 { margin: 0 0 4px; font-size: 15.5px; } .ac p { margin: 0; color: var(--muted); font-size: 13px; }
  .ci.mint { background: var(--mint); color: var(--mint-ink); }
  .ci.peach { background: var(--peach); color: var(--peach-ink); }
  .ci.sky { background: var(--sky); color: var(--sky-ink); }
  .ci.lilac { background: var(--lilac); color: var(--lilac-ink); }
  .herobanner { background: linear-gradient(135deg, var(--lilac), var(--sky)); border: 1px solid var(--line);
                border-radius: 22px; padding: 34px 32px; margin-bottom: 8px; box-shadow: var(--shadow); }
  .herobanner .ava { width: 60px; height: 60px; font-size: 23px; margin-bottom: 14px; }
  .herobanner h1 { margin: 0; font-size: 28px; font-weight: 780; color: var(--ink); }
  .herobanner .lede { margin: 9px 0 20px; font-size: 15.5px; color: var(--ink); opacity: .85; max-width: 580px; }
  .section-title { font-size: 12.5px; letter-spacing: .09em; text-transform: uppercase; color: var(--muted);
                   font-weight: 700; margin: 28px 2px 14px; }
  .highlights { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
  .hl { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px;
        box-shadow: var(--shadow); }
  .hl .ci { width: 38px; height: 38px; border-radius: 10px; display: grid; place-items: center; font-size: 18px; margin-bottom: 11px; }
  .hl h4 { margin: 0 0 4px; font-size: 14.5px; color: var(--ink); }
  .hl p { margin: 0; font-size: 12.5px; color: var(--muted); }
  .themetip { display: flex; align-items: center; gap: 14px; margin-top: 28px; background: var(--accent-soft);
              border: 1px solid var(--line); border-radius: 15px; padding: 16px 18px; }
  .themetip .ti { width: 40px; height: 40px; border-radius: 11px; background: var(--card); display: grid;
                  place-items: center; font-size: 19px; flex: none; }
  .themetip b { color: var(--ink); } .themetip span { color: var(--muted); font-size: 13px; }

  /* Orders */
  .panelhead { margin: 0 0 16px; } .panelhead h1 { margin: 0; font-size: 22px; }
  .panelhead p { margin: 4px 0 0; color: var(--muted); }
  .order { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius);
           box-shadow: var(--shadow); overflow: hidden; }
  .order .top { display: flex; align-items: center; gap: 14px; padding: 18px 20px; }
  .order .ci { width: 46px; height: 46px; border-radius: 12px; display: grid; place-items: center; font-size: 22px;
               background: var(--mint); color: var(--mint-ink); }
  .order .top b { font-size: 15.5px; } .order .top span { color: var(--muted); font-size: 13px; }
  .order .status { padding: 16px 20px; border-top: 1px solid var(--line); font-size: 14px; }
  .order .status .k { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }

  /* Support chat */
  .chat { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius);
          box-shadow: var(--shadow); display: flex; flex-direction: column; height: calc(100vh - 170px);
          min-height: 520px; max-height: 680px; overflow: hidden; }
  .chat-head { display: flex; align-items: center; gap: 12px; padding: 15px 18px; border-bottom: 1px solid var(--line); }
  .chat-head .ava { width: 42px; height: 42px; font-size: 15px; background: linear-gradient(135deg,#a99ef0,#8a7fd6); }
  .chat-head .t { font-weight: 700; font-size: 15px; }
  .chat-head .s { font-size: 12.5px; color: var(--muted); display: flex; align-items: center; gap: 6px; }
  .online { width: 8px; height: 8px; border-radius: 50%; background: #67c9a3; }
  .thread { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 14px; background: var(--bg2); }
  .row { display: flex; gap: 10px; align-items: flex-end; } .row.me { justify-content: flex-end; }
  .mava { width: 30px; height: 30px; border-radius: 50%; flex: none; display: grid; place-items: center;
          font-size: 11px; font-weight: 700; color: #fff; background: linear-gradient(135deg,#a99ef0,#8a7fd6); }
  .stack { max-width: 76%; display: flex; flex-direction: column; } .row.me .stack { align-items: flex-end; }
  .bubble { padding: 11px 14px; border-radius: 16px; font-size: 14px; line-height: 1.5; white-space: pre-wrap;
            word-wrap: break-word; }
  .bot .bubble { background: var(--bubble-bot); color: var(--ink); border-bottom-left-radius: 5px; }
  .me .bubble { background: var(--accent); color: #fff; border-bottom-right-radius: 5px; }
  .time { font-size: 11px; color: var(--muted); margin: 5px 4px 0; }
  .typing { display: inline-flex; gap: 4px; } .typing i { width: 7px; height: 7px; border-radius: 50%;
            background: var(--muted); animation: blink 1.3s infinite both; }
  .typing i:nth-child(2) { animation-delay: .2s; } .typing i:nth-child(3) { animation-delay: .4s; }
  @keyframes blink { 0%,80%,100%{opacity:.3;transform:translateY(0)} 40%{opacity:1;transform:translateY(-3px)} }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 18px 0; }
  .chip { border: 1px solid var(--line); background: var(--card); color: var(--muted); font-size: 12.5px;
          padding: 7px 13px; border-radius: 999px; cursor: pointer; }
  .chip:hover { color: var(--accent-ink); border-color: var(--accent); background: var(--accent-soft); }
  .compose { display: flex; gap: 10px; padding: 14px 18px 18px; }
  .compose .box { flex: 1; display: flex; align-items: center; background: var(--bg2); border: 1px solid var(--line);
                  border-radius: 13px; padding: 2px 4px 2px 15px; }
  .compose .box:focus-within { border-color: var(--accent); }
  .compose input { flex: 1; border: 0; outline: 0; background: transparent; color: var(--ink); font-size: 14.5px; padding: 11px 0; }
  .compose input::placeholder { color: var(--muted); }

  @media (max-width: 720px) {
    .cards, .highlights { grid-template-columns: 1fr; }
    .tabs { display: none; }
    .herobanner { padding: 26px 22px; }
  }
</style>
</head>
<body>
  <header class="nav">
    <div class="brand" onclick="go('home')">
      <div class="logo">&#9875;</div><b>Harbor</b>
    </div>
    <div class="tabs">
      <button class="tab active" data-view="home" onclick="go('home')">Home</button>
      <button class="tab" data-view="orders" onclick="go('orders')">My Orders</button>
      <button class="tab" data-view="support" onclick="go('support')">Support</button>
    </div>
    <div class="spacer"></div>
    <button class="icon-btn" id="themeBtn" title="Toggle theme" onclick="toggleTheme()">&#9790;</button>
    <div class="userchip"><span class="ava" id="navAva">A</span><span class="nm" id="navName">Ananya</span></div>
  </header>

  <div class="wrap">
    <!-- HOME -->
    <section class="view active" id="view-home">
      <div class="herobanner">
        <span class="ava" id="heroAva">A</span>
        <h1>Hi Ananya &#128075;</h1>
        <p class="lede">Welcome to Harbor — your all-in-one support space. Track your orders, start a return,
          or chat with a real person, all from one calm, friendly place.</p>
        <form class="askbar" id="homeForm">
          <input id="homeAsk" placeholder="Ask us anything — e.g. where's my order?" autocomplete="off">
          <button class="btn" type="submit">Ask</button>
        </form>
      </div>

      <div class="section-title">Quick actions</div>
      <div class="cards">
        <button class="ac" onclick="seed('Where is my order right now?')">
          <div class="ci mint">&#128230;</div><h3>Track an order</h3><p>See exactly where your package is.</p></button>
        <button class="ac" onclick="go('orders')">
          <div class="ci sky">&#128179;</div><h3>Orders &amp; delivery</h3><p>Review your recent purchase.</p></button>
        <button class="ac" onclick="seed('I would like to return an item.')">
          <div class="ci peach">&#8617;&#65039;</div><h3>Returns &amp; refunds</h3><p>Start a return in minutes.</p></button>
        <button class="ac" onclick="go('support')">
          <div class="ci lilac">&#128172;</div><h3>Chat with us</h3><p>Talk to our support team.</p></button>
      </div>

      <div class="section-title">Why Harbor</div>
      <div class="highlights">
        <div class="hl"><div class="ci mint">&#128230;</div><h4>Live order tracking</h4>
          <p>Up-to-the-minute status on every order, whenever you check.</p></div>
        <div class="hl"><div class="ci peach">&#8617;&#65039;</div><h4>Effortless returns</h4>
          <p>Start and track returns in a couple of taps — no forms to hunt down.</p></div>
        <div class="hl"><div class="ci sky">&#128172;</div><h4>Real human support</h4>
          <p>Our team is a message away whenever you need a hand.</p></div>
      </div>

      <div class="themetip">
        <div class="ti">&#9790;</div>
        <div><b>Light or dark — your call.</b>
          <span>Tap the moon or sun in the top-right corner to switch themes anytime. We'll remember your choice.</span></div>
      </div>
    </section>

    <!-- ORDERS -->
    <section class="view" id="view-orders">
      <div class="panelhead"><h1>My Orders</h1><p>Your most recent order and its latest update.</p></div>
      <div class="order">
        <div class="top"><div class="ci">&#128230;</div>
          <div style="flex:1"><b>Recent order</b><br><span>Updates appear here automatically.</span></div></div>
        <div class="status"><div class="k">Latest update</div><div id="orderStatus">Loading your latest update…</div></div>
      </div>
    </section>

    <!-- SUPPORT -->
    <section class="view" id="view-support">
      <div class="chat">
        <div class="chat-head"><span class="ava">M</span>
          <div style="flex:1"><div class="t">Maya &middot; Support</div>
            <div class="s"><span class="online"></span> Online now &middot; usually replies in a moment</div></div></div>
        <div class="thread" id="thread"></div>
        <div class="chips" id="chips"></div>
        <form class="compose" id="form">
          <div class="box"><input id="msg" placeholder="Type your message…" autocomplete="off"></div>
          <button class="btn" type="submit">Send</button>
        </form>
      </div>
    </section>
  </div>

<script>
  const CUSTOMER_ID = 'cust_101';
  const USER = { name: 'Ananya Verma', first: 'Ananya' };
  const CHIPS = ["Where's my order?", 'Track my delivery', 'Return an item', 'Talk to a person'];
  const el = (id) => document.getElementById(id);
  const thread = el('thread'), send = () => el('form').querySelector('.btn');
  let greeted = false, ordersLoaded = false;

  const now = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  /* theme */
  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    el('themeBtn').innerHTML = t === 'dark' ? '&#9728;' : '&#9790;';
    try { localStorage.setItem('harbor-theme', t); } catch (e) {}
  }
  function toggleTheme() {
    const cur = document.documentElement.getAttribute('data-theme');
    applyTheme(cur === 'dark' ? 'light' : 'dark');
  }
  (function initTheme() {
    let t = null;
    try { t = localStorage.getItem('harbor-theme'); } catch (e) {}
    if (!t) t = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    applyTheme(t);
  })();

  /* views */
  function go(view) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    el('view-' + view).classList.add('active');
    document.querySelectorAll('.tab').forEach(t =>
      t.classList.toggle('active', t.dataset.view === view));
    if (view === 'support' && !greeted) { greet(); greeted = true; }
    if (view === 'orders' && !ordersLoaded) { loadOrders(); ordersLoaded = true; }
    window.scrollTo(0, 0);
  }

  function add(text, mine) {
    const row = document.createElement('div');
    row.className = 'row ' + (mine ? 'me' : 'bot');
    row.innerHTML = (mine ? '' : '<div class="mava">M</div>') +
      '<div class="stack"><div class="bubble"></div><div class="time">' + now() + '</div></div>';
    row.querySelector('.bubble').textContent = text;
    thread.appendChild(row); thread.scrollTop = thread.scrollHeight;
  }
  function showTyping() {
    const r = document.createElement('div'); r.className = 'row bot'; r.id = 'typing';
    r.innerHTML = '<div class="mava">M</div><div class="stack"><div class="bubble typing"><i></i><i></i><i></i></div></div>';
    thread.appendChild(r); thread.scrollTop = thread.scrollHeight;
  }
  const hideTyping = () => { const t = el('typing'); if (t) t.remove(); };

  function greet() {
    thread.innerHTML = '';
    add('Hi ' + USER.first + "! I'm Maya from the Harbor support team. How can I help you today?", false);
  }

  async function callAssistant(message) {
    const res = await fetch('/ask', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id: CUSTOMER_ID, message })
    });
    return (await res.json()).reply;
  }

  async function ask(text) {
    add(text, true); el('msg').value = ''; send().disabled = true; showTyping();
    const started = Date.now();
    let reply;
    try { reply = await callAssistant(text); }
    catch (e) { reply = 'Sorry, I had trouble connecting just now — could you try again?'; }
    const wait = Math.max(0, 650 - (Date.now() - started));
    setTimeout(() => { hideTyping(); add(reply, false); send().disabled = false; el('msg').focus(); }, wait);
  }

  function seed(text) { go('support'); setTimeout(() => ask(text), 180); }

  async function loadOrders() {
    try { el('orderStatus').textContent = await callAssistant('order status'); }
    catch (e) { el('orderStatus').textContent = 'We could not load your update right now. Please try again shortly.'; }
  }

  /* wire up */
  el('form').addEventListener('submit', (e) => { e.preventDefault();
    const t = el('msg').value.trim(); if (t) ask(t); });
  el('homeForm').addEventListener('submit', (e) => { e.preventDefault();
    const t = el('homeAsk').value.trim(); if (t) { el('homeAsk').value = ''; seed(t); } });

  (function initChips() {
    const box = el('chips');
    CHIPS.forEach(c => { const b = document.createElement('button');
      b.type = 'button'; b.className = 'chip'; b.textContent = c;
      b.onclick = () => { el('msg').value = c; el('msg').focus(); }; box.appendChild(b); });
  })();
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
