# Request-For-Order-Flow-Auctions

Initial grant source: https://forum.api3.org/t/secondary-proposal-airsigner-mev-airnode-development/1557

Contract Reference for DapiServer.sol (main API3 data feed contract that we built on top of): https://polygonscan.com/address/0xd7CA5BD7a45985D271F216Cb1CAD82348464f6d5#code

# Overview
A sealed bid request for order flow auction designed to internalise MEV and increase granularity of oracle services. MEV is internalised by allowing searchers to participate in auctions for the first right to update an oracle instead of for blockspace.  The auction process will maintain low barriers for entry to prevent the risks arising from vertical integration/centralisation of order flow, and to maximise profits for stakeholders of the oracle. 
 
This mechanism will operate as a sidecar to the deviation threshold based order flow of the oracle, and instead auction off new order flow driven by requests, creating a more granular data feed on top of the underlying service. In the case of oracles, regular payment for order flow of already generated transactions introduces latency that would decrease their quality of service, while generating transactions upon request is both possible and desirable. Searchers know when to request oracle order flow because there are designated API endpoints for each node operator they can query off chain https://docs.api3.org/airnode/v0.7/introduction/why-use-airnode.html. 
 
# Three main components:
AirSigner- A proxy API to Airnode (oracle node operator software) that data providers can run to make agreements with searchers paying for signed data points to be used within a specified time frame and by certain public keys.
 
OEV Proxy Contract - This contract acts as a proxy for DapiServer.sol and verifies payment amounts, msg.sender, and the expiry signature of the auction before it relays the data. Only this contract can update DapiServer.sol with the signatures provided so it cannot be front-ran. The profits from bids will collect in this contract, and be distributed later by a multi-sig based on off-chain calculations and profit splits.
 
OEV Relay - A third party API that implements DOS prevention and profit maximisation of the auction for all the respective AirSigners. The main method of discouraging and punishing DOS is by watching for on-chain events and rate limiting/lowering reputation scores for API keys of searchers who fail to execute on the agreements. Another benefit of the relay is that it’s much easier to maximise profit for one actor instead of coordination between all the first party data providers. The runner of this relay is unable to tamper with any of the price data, the worst exploit they can perform is to censor searcher bids and extract the MEV themselves. Running the relay can be incentivised with a share of profits to combat this risk, or done by large stakeholders such as the API3 technical team that operates similar services. 
 
# Searcher Integration:
Searchers will transition from watching the mempool for oracle transactions to backrun, to creating their own “mempools” of potential oracle transactions that can be generated. This is done by subscribing to and aggregating the respective API endpoints from each of the different data providers that make up the data feeds. 
 
Once they find a possible MEV opportunity they make a POST request to the relay containing a list of the different API calls to the respective AirSigners, along with the offered bid amount in the form of the native token. This list of API requests will function like a flashbots bundle, so if one datapoint from your list has been outbid then the whole list is ineligible to win the auction round. The relay will return an auction Id and timestamp of when the auction ends when you place a bid. Searchers should continue to monitor the APIs and the state of the blockchain to qualify that the opportunity is still present up until the auction ends, and if it is not they need to remove their bid before the end timestamp with another POST request. 
 
Once the auction ends only the winning bidder can view the signed data. They have to land this data and the MEV transaction on-chain as quickly as possible as they are now entered into an agreement to do so and may have their relay access affected if not. The signature will expire after a certain amount of time to allow new auctions to take place for those data points. 

 ![Screenshot (57)](https://user-images.githubusercontent.com/69164627/189503514-5b16cea0-47ec-4fe4-956e-8d3630beabc5.png)
 
# Frequently Asked Questions:
Will oracles now be incentivized to trigger more MEV when they run this software?
If you consume an oracle you already believe that the data providers are long term incentivized. Triggering more MEV increases user fees and over the long term they will move to another dapp/oracle to avoid this. So you can expect that data providers will not do this, and increasing their revenue through MEV should only incentivize them more to play the long game.
