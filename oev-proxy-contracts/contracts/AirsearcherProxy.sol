// SPDX-License-Identifier: MIT
pragma solidity 0.8.14;
import "@api3/airnode-protocol-v1/contracts/dapis/interfaces/IDapiServer.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./utils/ExtendedMulticall.sol";

/// @title Contract that serves as a proxy for Searchers to update
/// DapiServer datafeeds with signed data.
/// @notice A Searcher can update the beacon (i.e a single source datafeed)
/// using signed data that it won from the auction. Searchers can
/// also update multiple beacons simultaneously to update a beacon set i.e
/// a multisource aggregated datafeed.
/// @dev The AirSearcher contract acts as a proxy between the searchers contract and
/// the DapiServer, only searchers with the correct signatures can interact
/// with the proxy and subsequently update the DapiServer

contract AirsearcherProxy is Ownable, ExtendedMulticall {
    using ECDSA for bytes32;

    /// @notice Address of the DapiServer
    address public dapiServer;

    /// @param _dapiServer Address of the DapiServer
    constructor(address _dapiServer) {
        require(_dapiServer != address(0), "dAPI server address zero");
        dapiServer = _dapiServer;
    }

    /// @notice Used to withdraw all the bids collected in the contract.
    /// @dev This is a temporary solution until we have a more versatile
    /// system to distribute the bids collected in the contract.
    function withdraw() public onlyOwner {
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "Forward failed");
    }

    /// @notice Registers the Beacon update subscription
    /// @dev A convience function to quickly register subscriptions
    /// that specify Airsearcher as the relayer and sponsor
    /// @param airnode Airnode address
    /// @param templateId Template ID
    /// @return subscriptionId Subscription ID
    function registerSearcherBeaconUpdateSubscription(
        address airnode,
        bytes32 templateId
    ) external returns (bytes32 subscriptionId) {
        subscriptionId = IDapiServer(dapiServer)
            .registerBeaconUpdateSubscription(
                airnode,
                templateId,
                "0x",
                address(this),
                address(this)
            );
    }

    /// @notice Called by the Searcher to fulfill the Beacon update subscription
    /// and update the beacon value.
    /// @dev This function can be used to call `fulfillPspBeaconUpdate` in DapiServer
    /// if the 'msg.sender' has the appropriate signatures.
    /// @param subscriptionId Subscription ID
    /// @param beaconId The Id of the beacon that will be updated
    /// @param airnode Airnode address
    /// @param bidAmount The bid amount that needs to be transfered to the contract
    /// @param timestamp Timestamp used in the signature that is passed to DapiServer
    /// @param expireTimestamp Timestamp used in signature to verify searcher
    /// @param data Fulfillment data (a single `int256` encoded in contract ABI)
    /// @param dapiSignature Subscription ID, timestamp, sponsor wallet address
    /// and fulfillment data signed by the Airnode wallet
    /// @param searcherSignature beacon ID, expireTimestamp, msg.sender address
    /// and bid amount signed by the Airnode wallet
    function fulfillSearcherPspBeaconUpdate(
        bytes32 subscriptionId,
        bytes32 beaconId,
        address airnode,
        uint256 bidAmount,
        uint256 timestamp,
        uint256 expireTimestamp,
        bytes calldata data,
        bytes calldata dapiSignature,
        bytes calldata searcherSignature
    ) external payable {
        require(
            beaconId ==
                IDapiServer(dapiServer).subscriptionIdToBeaconId(
                    subscriptionId
                ),
            "Subscription not registered"
        );
        require(
            (
                keccak256(
                    abi.encodePacked(
                        beaconId,
                        expireTimestamp,
                        msg.sender,
                        bidAmount
                    )
                ).toEthSignedMessageHash()
            ).recover(searcherSignature) == airnode,
            "Signature Mismatch"
        );
        require(block.timestamp < expireTimestamp, "Signature has expired");
        require(msg.value >= bidAmount, "Insufficient Bid amount");
        IDapiServer(dapiServer).fulfillPspBeaconUpdate(
            subscriptionId,
            airnode,
            address(this),
            address(this),
            timestamp,
            data,
            dapiSignature
        );
    }

    /// @notice Called by the Searcher to fulfill the Beacon update subscription
    /// for multiple beacons and update the beacon set value.
    /// @dev This function can be used to call `fulfillPspBeaconUpdate` in DapiServer
    /// for multiple beacons and update the beacon set if the 'msg.sender' has
    /// the appropriate signatures.
    /// @param subscriptionIds Array of Subscription ID
    /// @param beaconIds Array beacon IDs that will be updated
    /// @param airnodes Array of Airnode address
    /// @param bidAmounts Array of bid amounts for each beacon to be updated
    /// @param timestamps Array of Timestamps that is passed to DapiServer
    /// @param expireTimestamps Array of Timestamps used in signature to verify searcher
    /// @param data Fulfillment data (a single `int256` encoded in contract ABI)
    /// @param dapiSignatures Array of Signatures of Subscription ID, timestamp, sponsor
    /// wallet address and fulfillment data signed by the respective Airnode wallets
    /// @param searcherSignatures beacon ID, expireTimestamp, msg.sender address
    /// and bid amount signed by the respective Airnode wallets
    function fulfillSearcherPspBeaconSetUpdate(
        bytes32[] memory subscriptionIds,
        bytes32[] memory beaconIds,
        address[] memory airnodes,
        uint256[] memory bidAmounts,
        uint256[] memory timestamps,
        uint256[] memory expireTimestamps,
        bytes[] memory data,
        bytes[] memory dapiSignatures,
        bytes[] memory searcherSignatures
    ) external payable {
        uint256 beaconCount = airnodes.length;
        uint256 totalBid = 0;
        require(
            beaconCount == subscriptionIds.length &&
                beaconCount == beaconIds.length &&
                beaconCount == bidAmounts.length &&
                beaconCount == timestamps.length &&
                beaconCount == expireTimestamps.length &&
                beaconCount == data.length &&
                beaconCount == dapiSignatures.length &&
                beaconCount == searcherSignatures.length,
            "Parameter length mismatch"
        );
        require(beaconCount > 1, "Specified less than two Beacons");
        for (uint256 ind = 0; ind < beaconCount; ind++) {
            if (dapiSignatures[ind].length != 0) {
                require(
                    beaconIds[ind] ==
                        IDapiServer(dapiServer).subscriptionIdToBeaconId(
                            subscriptionIds[ind]
                        ),
                    "Subscription not registered"
                );
                require(
                    (
                        keccak256(
                            abi.encodePacked(
                                beaconIds[ind],
                                expireTimestamps[ind],
                                msg.sender,
                                bidAmounts[ind]
                            )
                        ).toEthSignedMessageHash()
                    ).recover(searcherSignatures[ind]) == airnodes[ind],
                    "Signature Mismatch"
                );
                require(
                    block.timestamp < expireTimestamps[ind],
                    "Signature has expired"
                );
                totalBid += bidAmounts[ind];
                IDapiServer(dapiServer).fulfillPspBeaconUpdate(
                    subscriptionIds[ind],
                    airnodes[ind],
                    address(this),
                    address(this),
                    timestamps[ind],
                    data[ind],
                    dapiSignatures[ind]
                );
            }
        }
        require(msg.value >= totalBid, "Insufficient Bid amount");
        IDapiServer(dapiServer).updateBeaconSetWithBeacons(beaconIds);
    }
}
