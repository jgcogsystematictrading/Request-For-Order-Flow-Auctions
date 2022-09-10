# the Item class creates an object to represent what is being bid on

class Item:
    def __init__(self, template_id, encoded_parameters, chain_id, endpoint_id, subscription_id, searcher, beacon):
        self.this = self.__class__.__name__
        self.template_id = template_id
        self.encoded_parameters = encoded_parameters
        self.chain_id = chain_id
        self.endpoint_id = endpoint_id
        self.subscription_id = subscription_id
        self.searcher = searcher
        self.beacon = beacon
