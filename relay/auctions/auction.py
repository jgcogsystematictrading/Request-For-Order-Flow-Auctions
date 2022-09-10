# Auction class creates auctions and can start and stop them

class Auction:
    def __init__(self, items, bundle_id, auction_start):
        self.this = self.__class__.__name__
        self.bundle_id = bundle_id
        self.items = items
        self.auction_start = auction_start
        self.highest_bid = None

