import time, datetime
from .bid import Bid

class Participant:
    def __init__(self, api_key):
        self.this = self.__class__.__name__
        self.api_key = api_key
        print(f'{int(time.mktime(datetime.datetime.now().timetuple()))} {self.this}: object for new user created with key {api_key}')
        self.bundles = []
        self.last_seen = None
        self.most_recent_winning_data = None

    def bid(self, auction, amount):
        if amount <= 0:
            Bid(self, auction, amount)
            self.bundles = list(filter(lambda a: a != auction.bundle_id, self.bundles))
            self.last_seen = auction.auction_start
            return True

        if self.bundles.count(auction.bundle_id) > 2:  # you can only bid twice per bundle
            return False

        self.bundles.append(auction.bundle_id)
        Bid(self, auction, amount)
        self.last_seen = auction.auction_start
        return True

    def update_latest_won(self, data):
        self.most_recent_winning_data = data



