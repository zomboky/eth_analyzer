import json
from datetime import datetime
from get_daily_prices import get_daily_prices

today = datetime.now().strftime("%Y-%m-%d")
HISTORIC_JSON_FILE = f"prices_history/{today}.json"

def load_data_from_json(filename=HISTORIC_JSON_FILE):   
    get_daily_prices(symbol="ETHUSDC", interval="1m", limit=1440)
    with open(filename, "r") as f:
        return json.load(f)

""" def load_data_from_json(filename=HISTORIC_JSON_FILE):
    with open(filename, "r") as f:
        return json.load(f) """

def process_klines_data(klines):
    times = []
    prices = []
    for k in klines:
        dt = datetime.fromtimestamp(k[0] / 1000)
        price = float(k[4])
        times.append(dt)
        prices.append(price)
    return times, prices
