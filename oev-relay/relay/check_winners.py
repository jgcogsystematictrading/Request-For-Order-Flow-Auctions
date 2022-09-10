import requests

for api_key in ['jacob', 'midhav', 'burak']:
    response = requests.get("http://192.168.1.93:33666/claim?key="+api_key)
    print(f'{api_key}: {response.text}')
