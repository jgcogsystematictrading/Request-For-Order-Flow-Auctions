from abc import ABC
from typing import Dict
import tornado.web
import socket, json

class AirsignerHttp:
    def __init__(self, port, callback) -> None:
        self.this = self.__class__.__name__
        self.callback = callback
        global http_server
        http_server = self
        global ports
        ports = port
        print(f'{self.this}: Starting Airsigner webserver at {(socket.gethostbyname(socket.gethostname()))}:{port}')

        self.app = tornado.web.Application(
            [
                (r"/", Splash),
                (r"/sign", Sign)
            ]
        )
        self.app.listen(port)

class Splash(tornado.web.RequestHandler, ABC):
    async def get(self):
        try:
            greeting = f'Welcome to the Airsigner splash page!'

            html = f"""<html> 
                <head><title> Airsigner: Protocol Owned MEV </title></head> 
                <body> 
                <p>{greeting}</p> 
                </body> 
                </html>"""
            self.write(html)
        except Exception as e:
            self.send_error(400, reason=e)

class Sign(tornado.web.RequestHandler):
    async def post(self):
        try:
            relay_key = self.get_query_argument("key")
            endpoint_id = self.get_query_argument("endpoint")
            auction_time = int(self.get_query_argument("auction_time"))
            # airnode_time = int(self.get_query_argument("airnode_time"))
            searcher = self.get_query_argument("searcher")
            beacon_id = self.get_query_argument("beacon", default="0x000000000000000000000000000000000000000000000000000000000000000")
            encoded_parameters = json.loads(self.request.body)
            response: Dict = http_server.callback.signed_oracle_update(relay_key, auction_time, beacon_id, endpoint_id, searcher, encoded_parameters)
            self.write(response)
        except Exception as e:
            print(e)
            self.send_error(400, reason=e)
