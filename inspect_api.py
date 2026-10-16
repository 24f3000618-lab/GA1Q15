import requests, json

URLS = {
    "orders": "https://exam.sanand.workers.dev/questionData?email=24f3000618%40ds.study.iitm.ac.in&quizSign=g24sXsIPrKDxPFNGSN9%2BaMnpgi6UBAYhkAc2SAtA9EQW4G6axYzfqUyAfS1Rt3Y3iIp3IDdo5%2Fds%2B%2FxyX99nhoJUqvJwof1iODLB2HnVC0ZFy7GVRFJxQm41OG1CzCAz6y4SjqH44WTNKhO6MyvGaZtbpAnFOwGJCyg%2FWbT421i7tYNe3ZCYfHTARikYMw5EdDmwmKtfEYsSWwgxPai0hh7yebcY%2FPId6NiGh65RQpByHguTerEjfRh5F8HuGy9P7ZPxqrECeX8tBbnV%2FMqPKBEWeUI9lyCqoZUyjkaSDuJSRdhRQXing89NWmJGpn3TIFHkqokd6iqg%2BHpkmCXr%2Bg%3D%3D&questionId=q-ledger-agent-server&path=%2Forders&page=1",
    "rates":  "https://exam.sanand.workers.dev/questionData?email=24f3000618%40ds.study.iitm.ac.in&quizSign=g24sXsIPrKDxPFNGSN9%2BaMnpgi6UBAYhkAc2SAtA9EQW4G6axYzfqUyAfS1Rt3Y3iIp3IDdo5%2Fds%2B%2FxyX99nhoJUqvJwof1iODLB2HnVC0ZFy7GVRFJxQm41OG1CzCAz6y4SjqH44WTNKhO6MyvGaZtbpAnFOwGJCyg%2FWbT421i7tYNe3ZCYfHTARikYMw5EdDmwmKtfEYsSWwgxPai0hh7yebcY%2FPId6NiGh65RQpByHguTerEjfRh5F8HuGy9P7ZPxqrECeX8tBbnV%2FMqPKBEWeUI9lyCqoZUyjkaSDuJSRdhRQXing89NWmJGpn3TIFHkqokd6iqg%2BHpkmCXr%2Bg%3D%3D&questionId=q-ledger-agent-server&path=%2Frates",
    "export": "https://exam.sanand.workers.dev/questionData?email=24f3000618%40ds.study.iitm.ac.in&quizSign=g24sXsIPrKDxPFNGSN9%2BaMnpgi6UBAYhkAc2SAtA9EQW4G6axYzfqUyAfS1Rt3Y3iIp3IDdo5%2Fds%2B%2FxyX99nhoJUqvJwof1iODLB2HnVC0ZFy7GVRFJxQm41OG1CzCAz6y4SjqH44WTNKhO6MyvGaZtbpAnFOwGJCyg%2FWbT421i7tYNe3ZCYfHTARikYMw5EdDmwmKtfEYsSWwgxPai0hh7yebcY%2FPId6NiGh65RQpByHguTerEjfRh5F8HuGy9P7ZPxqrECeX8tBbnV%2FMqPKBEWeUI9lyCqoZUyjkaSDuJSRdhRQXing89NWmJGpn3TIFHkqokd6iqg%2BHpkmCXr%2Bg%3D%3D&questionId=q-ledger-agent-server&path=%2Fexport",
}

for name, url in URLS.items():
    r = requests.get(url, timeout=30)
    print("=====", name, r.status_code, r.headers.get("content-type"))
    print(r.text[:1500])   # first 1500 characters
    print()