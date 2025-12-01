import requests
syms = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA"]
r = requests.get("https://query1.finance.yahoo.com/v7/finance/quote", params={"symbols": ",".join(syms)}, timeout=10)
print(r.status_code)
print(len(r.json().get('quoteResponse',{}).get('result',[])))
print([i.get('symbol') for i in r.json().get('quoteResponse',{}).get('result',[])])
