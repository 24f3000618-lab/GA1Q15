import json, os, re, time, requests
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- 1. LOAD + CLEAN (runs once at startup) ----------
raw = pd.DataFrame(json.load(open(os.path.join(HERE, "orders.json"))))
rates = json.load(open(os.path.join(HERE, "rates.json")))["usd_per_unit"]

# timestamps come as both "...Z" and "...+05:30": put them all on one UTC timeline
raw["updated_at"] = pd.to_datetime(raw["updated_at"], utc=True, format="ISO8601")
raw["created_at"] = pd.to_datetime(raw["created_at"], utc=True, format="ISO8601")

# an order can appear several times (versions): keep the NEWEST version of each id
latest = raw.sort_values("updated_at").drop_duplicates("id", keep="last").copy()

# business date = India time (the data runs exactly 1 Jan - 30 Jun 2026 in IST)
latest["day"] = latest["created_at"].dt.tz_convert("Asia/Kolkata").dt.strftime("%Y-%m-%d")

# every amount in USD
latest["usd"] = latest["amount"] * latest["currency"].map(rates)

def norm(s):
    """'Air-Fryers ' -> 'airfryer' so small spelling differences still match"""
    s = re.sub(r"[^a-z0-9]", "", str(s).lower())
    return s[:-1] if s.endswith("s") and len(s) > 3 else s

latest["status_l"] = latest["status"].str.strip().str.lower()
latest["region_n"] = latest["region"].map(norm)
latest["product_n"] = latest["product"].map(norm)
latest["customer_n"] = latest["customer"].str.strip().str.lower()

PAID = latest[latest.status_l == "paid"]
REFUNDED = latest[latest.status_l == "refunded"]   # 'void' orders are ignored everywhere

REGIONS = sorted(latest.region.unique())
PRODUCTS = sorted(latest["product"].unique())

# ---------- 2. QUESTION -> PLAN (the LLM part) ----------
LLM_URL = os.environ.get("LLM_URL", "https://aipipe.org/openai/v1/chat/completions")
LLM_KEY = os.environ["LLM_KEY"]
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

SYSTEM = f"""You convert a question about an order ledger into a JSON query plan.
Return ONLY a JSON object:
{{
 "measure": "revenue" | "refund_amount" | "refund_count" | "order_count" | "units" | "avg_order_value" | "customer_count",
 "filters": {{"region": null, "product": null, "customer": null, "date_from": null, "date_to": null}},
 "group_by": null | "product" | "region" | "customer" | "month",
 "rank": null | "top" | "bottom",
 "n": 1,
 "output": "number" | "name" | "list"
}}
Rules:
- All data is from 2026 (1 Jan - 30 Jun). If no year is given, assume 2026.
- Dates are YYYY-MM-DD and inclusive. 'March 2026' = 2026-03-01 to 2026-03-31. 'Q1' = 01-01 to 03-31. 'Q2' = 04-01 to 06-30. 'H1' = whole data.
- Use these exact spellings. Regions: {REGIONS}. Products: {PRODUCTS}. Customer ids look like C1030.
- "revenue", "sales", "turnover" = revenue. "refunds" = refund_amount (money) or refund_count (how many).
- "average order value", "average order size" = avg_order_value. "units sold", "quantity" = units.
- "how many customers" = customer_count. "how many orders" = order_count.
- "how much/total" = output number. "which product/who/which region" = output name with group_by + rank. "list/top 3" = output list with n=3.
- "highest/best/most" = rank top. "lowest/worst/least" = rank bottom.
Return only JSON, no explanation."""

def make_plan(question, deadline):
    last = None
    for _ in range(2):
        left = deadline - time.time()
        if left < 3:
            break
        try:
            r = requests.post(
                LLM_URL,
                headers={"Authorization": f"Bearer {LLM_KEY}"},
                json={"model": LLM_MODEL, "temperature": 0,
                      "response_format": {"type": "json_object"},
                      "messages": [{"role": "system", "content": SYSTEM},
                                   {"role": "user", "content": question}]},
                timeout=min(7, left - 1))
            return json.loads(r.json()["choices"][0]["message"]["content"])
        except Exception as e:
            last = e
    raise RuntimeError(f"LLM failed: {last}")

# ---------- 3. PLAN -> ANSWER (plain, exact maths) ----------
COUNT_MEASURES = ("order_count", "refund_count", "units", "customer_count")

def measure(g, m):
    if m in ("revenue", "refund_amount"): return g["usd"].sum()
    if m in ("order_count", "refund_count"): return len(g)
    if m == "units": return g["qty"].sum()
    if m == "avg_order_value": return g["usd"].mean() if len(g) else 0.0
    if m == "customer_count": return g["customer"].nunique()
    raise ValueError(f"unknown measure {m}")

def clean(x, m):
    x = float(x)
    return int(round(x)) if m in COUNT_MEASURES else round(x + 1e-9, 2)

def run_plan(plan):
    f = plan.get("filters") or {}
    m = plan["measure"]
    df = REFUNDED if m in ("refund_amount", "refund_count") else PAID

    if f.get("region"):    df = df[df.region_n   == norm(f["region"])]
    if f.get("product"):   df = df[df.product_n  == norm(f["product"])]
    if f.get("customer"):  df = df[df.customer_n == str(f["customer"]).strip().lower()]
    if f.get("date_from"): df = df[df.day >= f["date_from"]]
    if f.get("date_to"):   df = df[df.day <= f["date_to"]]

    gb = plan.get("group_by")
    if gb:
        df = df.assign(month=df.day.str[:7])
        results = {k: measure(g, m) for k, g in df.groupby(gb)}
        if not results:
            return [] if plan.get("output") == "list" else None
        bottom = plan.get("rank") == "bottom"
        # sort by value, ties broken alphabetically so answers are stable
        ordered = sorted(results.items(), key=lambda kv: ((kv[1] if bottom else -kv[1]), str(kv[0])))
        n = int(plan.get("n") or 1)
        if plan.get("output") == "list":
            return [k for k, _ in ordered[:n]]
        if plan.get("output") == "name":
            return ordered[0][0]
        return clean(ordered[0][1], m)

    return clean(measure(df, m), m) if len(df) else 0

# ---------- 4. THE WEB ENDPOINT ----------
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def hello():
    return {"status": "ok", "rows": len(latest)}

@app.post("/")
def answer(body: dict):
    deadline = time.time() + 13          # stay inside the 15-second limit
    plan = make_plan(body["question"], deadline)
    return {"answer": run_plan(plan)}