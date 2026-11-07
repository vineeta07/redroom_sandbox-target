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
<title>Support Assistant</title>
<style>
  :root {
    --bg: #0f172a; --panel: #ffffff; --ink: #1e293b; --muted: #64748b;
    --brand: #4f46e5; --brand2: #7c3aed; --line: #e2e8f0; --bot: #f1f5f9;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont,
    "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: linear-gradient(135deg, #1e1b4b, #0f172a); color: var(--ink);
    display: flex; align-items: center; justify-content: center; padding: 16px;
  }
  .card {
    width: 100%; max-width: 460px; background: var(--panel); border-radius: 18px;
    box-shadow: 0 24px 60px rgba(0,0,0,.35); overflow: hidden; display: flex;
    flex-direction: column; height: min(680px, 92vh);
  }
  .top {
    background: linear-gradient(135deg, var(--brand), var(--brand2));
    color: #fff; padding: 18px 20px;
  }
  .top h1 { margin: 0; font-size: 17px; font-weight: 650; letter-spacing: .2px; }
  .top p { margin: 4px 0 0; font-size: 12.5px; opacity: .85; }
  .meta {
    display: flex; align-items: center; gap: 8px; padding: 12px 16px;
    border-bottom: 1px solid var(--line); background: #fafafa;
  }
  .meta label { font-size: 12px; color: var(--muted); font-weight: 600; }
  .meta input {
    flex: 1; padding: 7px 10px; border: 1px solid var(--line); border-radius: 9px;
    font-size: 13px; outline: none;
  }
  .meta input:focus { border-color: var(--brand); }
  .thread {
    flex: 1; overflow-y: auto; padding: 18px 16px; display: flex;
    flex-direction: column; gap: 12px; background:
    radial-gradient(circle at 20% 0%, #f8fafc, #eef2ff);
  }
  .row { display: flex; }
  .row.me { justify-content: flex-end; }
  .bubble {
    max-width: 78%; padding: 10px 13px; border-radius: 14px; font-size: 13.5px;
    line-height: 1.45; white-space: pre-wrap; word-wrap: break-word;
  }
  .me .bubble { background: var(--brand); color: #fff; border-bottom-right-radius: 4px; }
  .bot .bubble {
    background: var(--bot); color: var(--ink); border: 1px solid var(--line);
    border-bottom-left-radius: 4px;
  }
  .who { font-size: 10.5px; color: var(--muted); margin: 0 4px 3px; }
  .compose { display: flex; gap: 8px; padding: 12px; border-top: 1px solid var(--line); }
  .compose input {
    flex: 1; padding: 11px 13px; border: 1px solid var(--line); border-radius: 11px;
    font-size: 14px; outline: none;
  }
  .compose input:focus { border-color: var(--brand); }
  .compose button {
    border: 0; background: var(--brand); color: #fff; padding: 0 18px;
    border-radius: 11px; font-size: 14px; font-weight: 600; cursor: pointer;
  }
  .compose button:hover { background: #4338ca; }
  .compose button:disabled { opacity: .5; cursor: default; }
</style>
</head>
<body>
  <div class="card">
    <div class="top">
      <h1>Support Assistant</h1>
      <p>Ask about your order status or account.</p>
    </div>
    <div class="meta">
      <label for="cid">Customer ID</label>
      <input id="cid" value="cust_101" autocomplete="off">
    </div>
    <div class="thread" id="thread">
      <div class="row bot">
        <div>
          <div class="who">Assistant</div>
          <div class="bubble">Hi! How can I help you with your order today?</div>
        </div>
      </div>
    </div>
    <form class="compose" id="form">
      <input id="msg" placeholder="Type a message…" autocomplete="off">
      <button type="submit" id="send">Send</button>
    </form>
  </div>
<script>
  const thread = document.getElementById('thread');
  const form = document.getElementById('form');
  const msg = document.getElementById('msg');
  const cid = document.getElementById('cid');
  const send = document.getElementById('send');

  function add(who, text, mine) {
    const row = document.createElement('div');
    row.className = 'row ' + (mine ? 'me' : 'bot');
    row.innerHTML = '<div><div class="who">' + who +
      '</div><div class="bubble"></div></div>';
    row.querySelector('.bubble').textContent = text;
    thread.appendChild(row);
    thread.scrollTop = thread.scrollHeight;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = msg.value.trim();
    if (!text) return;
    add('You', text, true);
    msg.value = '';
    send.disabled = true;
    try {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_id: cid.value.trim(), message: text })
      });
      const data = await res.json();
      add('Assistant', data.reply, false);
    } catch (err) {
      add('Assistant', 'Something went wrong. Please try again.', false);
    } finally {
      send.disabled = false;
      msg.focus();
    }
  });
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE


class AskRequest(BaseModel):
    customer_id: str
    message: str


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
