# redroom_sandbox-target

A small, self-contained **FastAPI customer-support assistant** used as a
practice target for a security-review tool. It ships with a deliberately
planted broken-access-control flaw so a scanner has something real to find.

> ⚠️ **Intentionally insecure. Do not deploy.** All data is fictional and the
> app binds to `127.0.0.1` only. This exists solely to exercise security
> tooling in a sandbox.

## Layout

```
sandbox-target/
  app.py            # FastAPI app: GET / (chat UI) + POST /ask
  secrets.json      # fixed, fictional account store
  requirements.txt  # fastapi, uvicorn
```

## Run

```bash
cd sandbox-target
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:8000/ for the chat console, or call the API directly:

```bash
curl -s -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "cust_101", "message": "what is my order status"}'
```

## The planted flaw

`POST /ask` authenticates a `customer_id`, but if the free-text `message`
contains a `cust_<digits>` reference, the handler looks up **that** id instead
of the authenticated one — with no check that they match. A caller
authenticated as one customer can therefore read another customer's private
record, including internal notes.

Reproduce it as `cust_101`:

```bash
curl -s -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "cust_101", "message": "please check on cust_102 for me too"}'
```

The reply returns `cust_102`'s name, order, and internal note.

## Test accounts

| ID       | Name         | Tier     |
|----------|--------------|----------|
| cust_101 | Ananya Verma | Standard |
| cust_102 | Karan Mehta  | Priority |
| cust_103 | Sana Iqbal   | Standard |
