import uuid, datetime, time

class Bid:
    def __init__(self, bidder, auction, amount):
        self.this = self.__class__.__name__
        self.id = uuid.uuid1()
        self.bidder = bidder
        self.amount = None
        self.auction = auction

        if self.amount == None:  # highest bid gets added if it's a new bid
            self.amount = amount
            self.auction.highest_bid = self
            print(f'{int(time.mktime(datetime.datetime.now().timetuple()))} {self.this}: {bidder.api_key} bids {amount} for bundle ID: {auction.bundle_id} auction time: {auction.auction_start}')

        elif amount > self.amount:  # if higher bid is received it is updated
            self.amount = amount
            self.auction.highest_bid = self
            print(f'{int(time.mktime(datetime.datetime.now().timetuple()))} {self.this}: {bidder.api_key} increased bid to {amount} for bundle ID: {auction.bundle_id} auction time: {auction.auction_start}')