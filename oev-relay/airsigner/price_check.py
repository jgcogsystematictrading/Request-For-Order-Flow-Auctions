import requests, json, time, datetime

def pricing(asset, url, endpoint_id, api_key):
    myobj = {'x-api-key': api_key}
    mydata = '{"parameters": {"coinId": "%s"}}' % asset
    response = requests.post(url + endpoint_id, headers=myobj, data=mydata)
    data = json.loads(response.text)
    try:
        return data["rawValue"]["market_data"]["current_price"]['usd'], int(time.mktime(datetime.datetime.now().timetuple()))
    except Exception as e:
        print(f'{e}: {data}')
        return False


if __name__ == "__main__":
    ifile = open("../relay/config/beacons_subscriptions.json", "r")
    config = ifile.read()
    ifile.close()
    data = json.loads(config)["endpoints"]
    beacons_and_endpoints = {}
    for endpoint in data:
        beacons = {}
        for asset, beacon in endpoint["beacon_ids"].items():
            beacons[beacon] = asset
        beacons_and_endpoints[endpoint["endpoint_id"]] = beacons
    for endpoint_id, beacons in beacons_and_endpoints.items():
        for beacon, asset in beacons.items():
            url = "https://vnci1lns59.execute-api.us-east-1.amazonaws.com/v1/"
            endpoint_id = "0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe"
            api_key = "_diarrhea_out_the_dick_diarrhea_out_the_dick_"
            print(f'{asset}: {pricing(asset, url, endpoint_id, api_key)}')






























def pricing_encoded(mydata):
    url = 'https://vnci1lns59.execute-api.us-east-1.amazonaws.com/v1/0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe'
    api_key = '_diarrhea_out_the_dick_diarrhea_out_the_dick_'
    myobj = {'x-api-key': api_key}
    # mydata = '{"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000657468657265756d000000000000000000000000000000000000000000000000"}'
    response = requests.post(url, headers=myobj, data=mydata)
    data = json.loads(response.text)
    return data#["rawValue"]["market_data"]["current_price"]['usd']



# if __name__ == "__main__":
#     mydata = '{"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000657468657265756d000000000000000000000000000000000000000000000000"}'
#     print(pricing_encoded(mydata))