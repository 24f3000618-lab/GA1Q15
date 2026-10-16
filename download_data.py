import requests, json

EXPORT_URL =  "https://exam.sanand.workers.dev/questionData?email=24f3000618%40ds.study.iitm.ac.in&quizSign=g24sXsIPrKDxPFNGSN9%2BaMnpgi6UBAYhkAc2SAtA9EQW4G6axYzfqUyAfS1Rt3Y3iIp3IDdo5%2Fds%2B%2FxyX99nhoJUqvJwof1iODLB2HnVC0ZFy7GVRFJxQm41OG1CzCAz6y4SjqH44WTNKhO6MyvGaZtbpAnFOwGJCyg%2FWbT421i7tYNe3ZCYfHTARikYMw5EdDmwmKtfEYsSWwgxPai0hh7yebcY%2FPId6NiGh65RQpByHguTerEjfRh5F8HuGy9P7ZPxqrECeX8tBbnV%2FMqPKBEWeUI9lyCqoZUyjkaSDuJSRdhRQXing89NWmJGpn3TIFHkqokd6iqg%2BHpkmCXr%2Bg%3D%3D&questionId=q-ledger-agent-server&path=%2Fexport"
RATES_URL  =  "https://exam.sanand.workers.dev/questionData?email=24f3000618%40ds.study.iitm.ac.in&quizSign=g24sXsIPrKDxPFNGSN9%2BaMnpgi6UBAYhkAc2SAtA9EQW4G6axYzfqUyAfS1Rt3Y3iIp3IDdo5%2Fds%2B%2FxyX99nhoJUqvJwof1iODLB2HnVC0ZFy7GVRFJxQm41OG1CzCAz6y4SjqH44WTNKhO6MyvGaZtbpAnFOwGJCyg%2FWbT421i7tYNe3ZCYfHTARikYMw5EdDmwmKtfEYsSWwgxPai0hh7yebcY%2FPId6NiGh65RQpByHguTerEjfRh5F8HuGy9P7ZPxqrECeX8tBbnV%2FMqPKBEWeUI9lyCqoZUyjkaSDuJSRdhRQXing89NWmJGpn3TIFHkqokd6iqg%2BHpkmCXr%2Bg%3D%3D&questionId=q-ledger-agent-server&path=%2Frates"
ORDERS_URL = "https://exam.sanand.workers.dev/questionData?email=24f3000618%40ds.study.iitm.ac.in&quizSign=g24sXsIPrKDxPFNGSN9%2BaMnpgi6UBAYhkAc2SAtA9EQW4G6axYzfqUyAfS1Rt3Y3iIp3IDdo5%2Fds%2B%2FxyX99nhoJUqvJwof1iODLB2HnVC0ZFy7GVRFJxQm41OG1CzCAz6y4SjqH44WTNKhO6MyvGaZtbpAnFOwGJCyg%2FWbT421i7tYNe3ZCYfHTARikYMw5EdDmwmKtfEYsSWwgxPai0hh7yebcY%2FPId6NiGh65RQpByHguTerEjfRh5F8HuGy9P7ZPxqrECeX8tBbnV%2FMqPKBEWeUI9lyCqoZUyjkaSDuJSRdhRQXing89NWmJGpn3TIFHkqokd6iqg%2BHpkmCXr%2Bg%3D%3D&questionId=q-ledger-agent-server&path=%2Forders&page=1"


# 1. the export (fast: everything in one request)
export_rows = [json.loads(l) for l in requests.get(EXPORT_URL, timeout=120).text.splitlines() if l.strip()]
print("export rows:", len(export_rows))

# 2. the paged API (slow: 85 requests), to compare
paged_rows, url = [], ORDERS_URL
while url:
    d = requests.get(url, timeout=60).json()
    paged_rows += d["orders"]
    url = d.get("next")
print("paged rows:", len(paged_rows))

# 3. do they match?
print("same ids in both:", {r["id"] for r in export_rows} == {r["id"] for r in paged_rows})

# 4. save the paged version (the official one) + rates
with open("orders.json", "w") as f:
    json.dump(paged_rows, f)
with open("rates.json", "w") as f:
    json.dump(requests.get(RATES_URL, timeout=30).json(), f)
print("saved orders.json and rates.json")