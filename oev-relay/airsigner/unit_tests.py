import requests, json, random, secrets, warnings, time, datetime
from web3 import Web3
warnings.filterwarnings("ignore", category=DeprecationWarning)

URL = "http://192.168.1.93:33667/" # put yur own IP here m8
# URL = "http://192.168.1.84:33667/" # put yur own IP here m8

open_auctions = []
JACOB = "0x9dD2e5271c3F53B21876b579571d5Eb865650Fe9"
MIDHAV = "0x2218a813a7E587640132E633A8cce7DBc80B8eB8"
BURAK = "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6"
users = {'jacob': JACOB, 'burak': BURAK, 'midhav': MIDHAV}

longer_zeroes = "0x000000000000000000000000000000000000000000000000000000000000000"

def get_random_bytes32():
    return "0x" + secrets.token_hex(32)

def get_random_user():
    return random.sample(users.items(), 1)[0]

def sign(relay_key, endpoint_id, timestamp, searcher, beacon_id):
    endpoint = URL + "sign"
    payload = {"key": relay_key, "endpoint": endpoint_id, "auction_time": timestamp, "searcher": searcher, "beacon": beacon_id}
    encoded_parameters = '{"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000657468657265756d000000000000000000000000000000000000000000000000"}'
    data = json.loads(encoded_parameters)
    r = requests.post(endpoint, params=payload, data=data)
    if r.status_code == 200:
        print(r.text)
        return json.loads(r.text)
    else:
        print(r.text)
        return False

def run_once():
    key = "relay_key"
    endpoint_id = "0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe"
    timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
    searcher = get_random_user()
    beacon_id = get_random_bytes32()
    sign(key, endpoint_id, timestamp, searcher, beacon_id)


if __name__ == "__main__":
    run_once()

