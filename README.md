# Request-For-Order-Flow-Auctions

Initial grant source for context: https://forum.api3.org/t/secondary-proposal-airsigner-mev-airnode-development/1557

Contract Reference for DapiServer.sol (main API3 data feed contract that we built on top of): https://polygonscan.com/address/0xd7CA5BD7a45985D271F216Cb1CAD82348464f6d5#code

# Overview
A sealed bid request for order flow auction designed to internalise MEV and increase granularity of oracle services. Addressing profitability issues for liquidity providers on applications that rely on oracles such as GMX https://forum.rook.fi/t/kip-17-provide-a-coordination-facility-for-gmx/272 and Synthetix https://sips.synthetix.io/sips/sip-37/. MEV is internalised by allowing searchers to participate in auctions for the first right to update an oracle instead of for blockspace.  The auction process will maintain low barriers for entry to prevent the risks arising from vertical integration/centralisation of order flow, and to maximise profits for stakeholders of the oracle. 
 
This mechanism will operate as a sidecar to the deviation threshold based order flow of the oracle, and instead auction off new order flow driven by requests, creating a more granular data feed on top of the underlying service. In the case of oracles, regular payment for order flow of already generated transactions introduces latency that would decrease their quality of service, while generating transactions upon request is both possible and desirable. Searchers know when to request oracle order flow because there will be an API they can call managed by the oracle that displays constant aggregated off chain values for the respective data feeds. 

A solution to accurately distributing the MEV to the respective dapps that it was generated on trustlessly is to create specific data feeds for each application. This can be done efficiently without the oracle having to take on significantly higher costs. Application specific data feeds will still be mapped to data points that are updated by deviation threshold based rules called “beacon sets”. These data feeds all share data from the single beacon set they are mapped to, but will also each have their own separate datapoint that can be updated by searchers. This allows the oracle to host auctions for the application specific data points and forces searchers to bid for each one distinctly. This is done without forcing the oracle to take on higher operational costs or change its service significantly by maintaining the mapping to the beacon set, allowing it to still update every application-specific feed with one transaction. 
 
# Three main components:
AirSigner- A proxy API to Airnode (oracle node operator software) that data providers can run. This software allows the data provider to make agreements with actors to pay for signed data points that can be used to update a data feed within a specified time frame and by certain public keys.
 
OEV Proxy Contract - This contract acts as a proxy for DapiServer.sol and verifies payment amounts, msg.sender, and the expiry signature of the auction before it relays the data. Only this contract can update DapiServer.sol with the signatures provided so it cannot be front-ran. In the next iteration his contract will implement application specific data feeds mentioned above.
 
OEV Relay - A third party API that implements DOS prevention and profit maximisation of the auction for all the respective AirSigners. The main method of the OEV relay discouraging and punishing DOS can be to watch for on-chain events and punish API keys of searchers who fail to execute on the agreements they made with data providers. A popular method that can be used to help this function well is the use of reputation scoring for API keys, which was used by both Flashbots and Rook auction processes. Another benefit of the relay is that it’s much easier to maximise profit for one actor instead of coordination between all the first party data providers. The runner of this relay is unable to tamper with any of the price data, the worst exploit they can perform is to censor searcher bids and extract the MEV themselves. Running the relay can be incentivised with a share of profits to combat this risk, done by large stakeholders such as the API3 technical team. It should be noted that any oracle can already perform this exploit by sending their transactions to private mempools. 
 
# Searcher Integration:
Searchers will transition from watching the mempool for oracle transactions to backrun, to creating their own “mempools” of potential oracle transactions that can be generated. This is done by subscribing to an API managed by the oracle that can constantly return potential oracle order flow that could be triggered at any time. 
 
Once they find a possible MEV opportunity they make a POST request to the relay containing a list of the different API calls to the respective AirSigners, along with the offered bid amount in the form of the native token. This list of API requests will function like a flashbots bundle, so if one datapoint from your list has been outbid then the whole list is ineligible to win the auction round. The relay will return an auction Id and timestamp of when the auction ends when you place a bid. Searchers should continue to monitor the APIs and the state of the blockchain to qualify that the opportunity is still present up until the auction ends, and if it is not they need to remove their bid before the end timestamp with another POST request. 
 
Once the auction ends only the winning bidder can view the signed data. They have to land this data and the MEV transaction on-chain as quickly as possible as they are now entered into an agreement to do so and may have their relay access affected if not. The signature will expire after a certain amount of time to allow new auctions to take place for those data points. 

 ![Screenshot (63)](https://user-images.githubusercontent.com/69164627/192672101-9d50daf6-26bf-431e-8bdd-8b2b212b6531.png)
 
# Frequently Asked Questions:
Will oracles now be incentivized to trigger more MEV when they run this software?

If you consume an oracle you already believe that the data providers are long term incentivized. Triggering more MEV increases user fees and over the long term they will move to another dapp/oracle to avoid this. So you can expect that data providers will not do this, and increasing their revenue through MEV should only incentivize them more to play the long game.
