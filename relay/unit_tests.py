import requests, json, random, secrets, warnings, time, datetime, os
from web3 import Web3, HTTPProvider
from typing import List
from defi_infrastructure.contract.deploy_contract import deploy_returns_address_abi

warnings.filterwarnings("ignore", category=DeprecationWarning)

URL = "http://192.168.1.93:33666/"  # put yur own IP here m8
# URL = "http://192.168.1.84:33666/" # put yur own IP here m8


JACOB = "0x9dD2e5271c3F53B21876b579571d5Eb865650Fe9"
MIDHAV = "0x2218a813a7E587640132E633A8cce7DBc80B8eB8"
BURAK = "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6"
AIRNODE_ADDRESS = "0xf84BeF38e561f21F67581cD2283c79C979724CEd"  # random
DAPI_SERVER = "0xd7CA5BD7a45985D271F216Cb1CAD82348464f6d5"

DEPLOYED_CONTRACTS = {}

users = {'jacob': JACOB, 'burak': BURAK, 'midhav': MIDHAV}
open_auctions = []


def deploy_airsigner_contract(web3, account):
    address_to_check = "0x1f7326763936E651D8c23B239FBe7e2368592904"
    if web3.eth.getCode(address_to_check) != b'':
        print(f"AirsignerRelay already deployed at {address_to_check}")
        return retreive_airsigner_contract_obj(web3, address_to_check)
    else:
        absolute_path = "/home/ice/Projects/defi_infrastructure/api3/relay_airsigner/relay/contracts/AirsignerRelay.sol"
        address, abi = deploy_returns_address_abi(absolute_path, web3, account.privateKey, args=[DAPI_SERVER])
        DEPLOYED_CONTRACTS["AirsignerRelay"] = {address: abi}
        print(f"DEPLOYED AirsignerRelay {address}")
        ofile1 = open("/home/ice/Projects/defi_infrastructure/api3/relay_airsigner/relay/contracts/AirsignerRelay.json", "w")
        json.dump(abi, ofile1)
        ofile1.close()
        return load_contract(web3, address, abi)

def load_contract(web3, address, abi):
    address = Web3.toChecksumAddress(address)
    return web3.eth.contract(address=address, abi=abi)

def retreive_airsigner_contract_obj(web3, address):
    abi = json.load(open('/home/ice/Projects/defi_infrastructure/api3/relay_airsigner/relay/contracts/AirsignerRelay.json', 'r'))
    return load_contract(web3, address, abi)

def get_random_bytes32():
    return "0x" + secrets.token_hex(32)

def get_endpoints_from_web():
    try:
        endpoint = URL + "ids"
        r = requests.get(endpoint)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            return False
    except Exception as e:
        print(f'{e}')

def get_subs_from_web():
    try:
        endpoint = URL + "subs"
        r = requests.get(endpoint)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            return False
    except Exception as e:
        print(f'{e}')

def get_random_user():
    return random.sample(users.items(), 1)[0]

def get_random_bid():
    return random.randrange(10000, 10000000000, 10)


def get_user_by_hostname():
    import socket
    hostname = socket.gethostname()
    options = {
        'bot-host': 'jacob',
        'node': 'burak',
        'laptop': 'midhav'
    }
    return options[hostname], users[options[hostname]]

def place_bid(key, airnodes: List, searchers: List, amounts: List, endpoint_ids: List, assets: List, chain_ids: List, subscription_ids: List, beacons: List):
    try:
        endpoint = URL + "bids"
        payload = {"key": key}
        encoded_parameters = []
        for asset in assets:
            parameter = str(Web3.toHex(text=asset)).replace("0x", "").ljust(64, "0")
            encoded_parameter = {"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000" + parameter}
            encoded_parameters.append(encoded_parameter)
        bid_parameters = {"bid_parameters": {"airnodes": airnodes, "beacons": beacons, "searchers": searchers, "amounts": amounts, "endpoint_ids": endpoint_ids, "chain_ids": chain_ids, "subscription_ids": subscription_ids, "encoded_parameters": encoded_parameters}}
        header = {"Content-Type": "application/json"}
        r = requests.post(endpoint, headers=header, params=payload, json=json.dumps(bid_parameters))
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            print(r.text)
            return False
    except Exception as e:
        print(f'{e}')


def run_once():
    chain_id = 1
    beacons_and_endpoints = get_endpoints_from_web()
    airnodes, addresses, amounts, endpoint_ids, assets, chain_ids, subscription_ids, beacon_ids = [], [], [], [], [], [], [], []
    key = None

    for i in range((int(time.mktime(datetime.datetime.now().timetuple())) % 2), 3):
        if beacons_and_endpoints in [None, False]:
            return False

        endpoint_id = None
        beacon_ids = None
        for endpoint, beacons in beacons_and_endpoints["endpoints"].items():
            endpoint_id = endpoint
            beacon_ids = beacons

        beacon_id, asset = random.choice(list(beacon_ids.items()))
        subscription_id = random.choice(list(get_subs_from_web()["subscription_ids"]))

        key, address = get_user_by_hostname()
        amount = get_random_bid()

        airnodes.append(AIRNODE_ADDRESS)
        addresses.append(address)
        amounts.append(amount)
        endpoint_ids.append(endpoint_id)
        assets.append(asset)
        chain_ids.append(chain_id)
        subscription_ids.append(subscription_id)
    beacon_ids = list(beacon_ids.keys())[0:len(airnodes)]

    auction_details = place_bid(key, airnodes, addresses, amounts, endpoint_ids, assets, chain_ids, subscription_ids, beacon_ids)
    print(auction_details)
    if (int(time.mktime(datetime.datetime.now().timetuple())) % 7) == 0:  # send the occaisonal bid retraction
        auction_details = place_bid(key, airnodes, addresses, [0 for amount in amounts], endpoint_ids, assets, chain_ids, subscription_ids, beacon_ids)
        print(auction_details)


if __name__ == "__main__":
    # web3 = Web3(HTTPProvider(endpoint_uri=os.getenv("ganache"), request_kwargs={'timeout': 100}))
    # account = web3.eth.account.from_key(os.getenv("flashbots"))
    # deploy_airsigner_contract(web3, account)

    while True:
        run_once()
        time.sleep(1)
