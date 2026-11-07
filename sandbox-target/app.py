import json
import re

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

with open("secrets.json") as f:
    accounts = json.load(f)


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
