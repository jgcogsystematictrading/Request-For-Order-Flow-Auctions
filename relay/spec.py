from dotenv import load_dotenv
import json, os
from web3 import Web3
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params


class RelaySpec:
    def __init__(self):
        self.this = self.__class__.__name__
        load_dotenv("config/secrets.env")

        self.config = self.read_config()
        self.web3s = self.read_web3s() # commented out to save time on startup during dev

        self.valid_api_keys = self.read_api_keys()
        self.valid_beacons_and_endpoints, self.subscription_ids = self.read_beacons_and_subscriptions()

        self.dapi_server_address = "0xd7CA5BD7a45985D271F216Cb1CAD82348464f6d5"
        self.dapi_server_abi = json.load(open('/home/ice/Projects/defi_infrastructure/api3/relay_airsigner/relay/contracts/DapiServer.json', 'r'))

        self.http_port = self.config["port"]
        self.auction_runtime_seconds = self.config["timers"]["auctionTimer"]

        self.admin_key = os.getenv("ADMIN_API_KEY")
        self.signer_url = os.getenv("SIGNER_URL")
        self.zeroes = "0x0000000000000000000000000000000000000000"
        self.longer_zeroes = "0x000000000000000000000000000000000000000000000000000000000000000"
        self.relayer = self.config["contracts"]["RelayerAddress"]
        self.relayer_abi = json.load(open('/home/ice/Projects/defi_infrastructure/api3/relay_airsigner/relay/contracts/AirsignerRelay.json', 'r'))
        self.fulfillPspBeaconUpdate = "0x4a00c629"


    def read_config(self):
        ifile = open("config/config.json", "r")
        config = ifile.read()
        ifile.close()
        return json.loads(config)["config"]

    def read_api_keys(self):
        ifile = open("config/api_keys.json", "r")
        config = ifile.read()
        ifile.close()
        data = json.loads(config)["api_keys"]
        valid_keys = []
        for user in data:
            valid_keys.append(user["key"])
        return valid_keys

    def read_beacons_and_subscriptions(self):
        ifile = open("config/beacons_subscriptions.json", "r")
        config = ifile.read()
        ifile.close()
        endpoints = json.loads(config)["endpoints"]
        subscription_ids = json.loads(config)["subscription_ids"]
        beacons_and_endpoints = {}
        for endpoint in endpoints:
            beacons = {"0x000000000000000000000000000000000000000000000000000000000000000": "rrp-default"}
            for asset, beacon in endpoint["beacon_ids"].items():
                beacons[beacon] = asset
            beacons_and_endpoints[endpoint["endpoint_id"]] = beacons
        return beacons_and_endpoints, subscription_ids

    def read_web3s(self):
        from web3 import Web3, HTTPProvider
        ifile = open("config/web3s.json", "r")
        config = ifile.read()
        ifile.close()
        data = json.loads(config)["providers"]
        providers = {}
        for provider in data:
            http_obj = Web3(HTTPProvider(provider["http_provider"]))
            try:
                providers[http_obj.eth.chain_id] = (provider["chain"], http_obj)
            except Exception as e:
                print(f'{e}: {provider["http_provider"]}')
        return providers

    def _asset_from_encoded_parameters(self, encoded_parameters):
        asset_hex = encoded_parameters.replace('0x', '')[128:]
        asset = str(Web3.toText(hexstr=asset_hex)).strip()
        return asset.rstrip('\x00')

    def load_contract(self, address, abi, web3):
        address = Web3.toChecksumAddress(address)
        return web3.eth.contract(address=address, abi=abi)

    def fetch_events(self, event, from_block=None, address=None, topics=None):
        abi = event._get_event_abi()
        abi_codec = event.web3.codec
        argument_filters = dict()
        _filters = dict(**argument_filters)
        data_filter_set, event_filter_params = construct_event_filter_params(abi, abi_codec, contract_address=event.address, argument_filters=_filters, fromBlock=from_block, toBlock="latest", address=address, topics=topics)
        logs = event.web3.eth.getLogs(event_filter_params)
        for entry in logs:
            data = get_event_data(abi_codec, abi, entry)
            yield data