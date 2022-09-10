pragma solidity 0.8.14;
import "IDapiServer.sol";
import "ECDSA.sol";
import "Ownable.sol";
import "ExtendedMulticall.sol";

contract AirsignerRelay is Ownable, ExtendedMulticall {
    using ECDSA for bytes32;

    /// @notice Address of the DapiServer
    address public dapiServer;

    /// @param _dapiServer Address of the DapiServer
    constructor(address _dapiServer) {
        require(_dapiServer != address(0), "dAPI server address cannot be zero");
        dapiServer = _dapiServer;
    }

    function withdraw() public onlyOwner {
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "Forward failed");
    }

    function registerSearcherBeaconUpdateSubscription(address airnode, bytes32 templateId) external returns (bytes32 subscriptionId) {
        subscriptionId = IDapiServer(dapiServer).registerBeaconUpdateSubscription(airnode, templateId, "0x", address(this), address(this));
    }

    function fulfillSearcherPspBeaconUpdate(bytes32 subscriptionId, bytes32 beaconId, address airnode, uint256 bidAmount, uint256 timestamp, uint256 expireTimestamp, bytes calldata data, bytes calldata dapiSignature, bytes calldata searcherSignature) external payable {
        require(beaconId == IDapiServer(dapiServer).subscriptionIdToBeaconId(subscriptionId), "Subscription not registered");
        require((keccak256(abi.encodePacked(beaconId, expireTimestamp, msg.sender, bidAmount)).toEthSignedMessageHash()).recover(searcherSignature) == airnode, "Signature Mismatch");
        require(block.timestamp < expireTimestamp, "Signature has expired");
        require(msg.value >= bidAmount, "Insufficient Bid amount");
        IDapiServer(dapiServer).fulfillPspBeaconUpdate(subscriptionId, airnode, address(this), address(this), timestamp, data, dapiSignature);
    }

    function fulfillSearcherPspBeaconSetUpdate(bytes32[] memory subscriptionIds, bytes32[] memory beaconIds, address[] memory airnodes, uint256[] memory bidAmounts, uint256[] memory timestamps, uint256[] memory expireTimestamps, bytes[] memory data, bytes[] memory dapiSignatures, bytes[] memory searcherSignatures) external payable {
        uint256 beaconCount = airnodes.length;
        uint256 totalBid = 0;
        require(beaconCount == subscriptionIds.length && beaconCount == beaconIds.length && beaconCount == bidAmounts.length && beaconCount == timestamps.length && beaconCount == expireTimestamps.length && beaconCount == data.length && beaconCount == dapiSignatures.length && beaconCount == searcherSignatures.length, "Parameter length mismatch");
        require(beaconCount > 1, "Specified less than two Beacons");
        for (uint256 ind = 0; ind < beaconCount; ind++) {
            if (dapiSignatures[ind].length != 0) {
                require(beaconIds[ind] == IDapiServer(dapiServer).subscriptionIdToBeaconId(subscriptionIds[ind]), "Subscription not registered");
                require((keccak256(abi.encodePacked(beaconIds[ind], expireTimestamps[ind], msg.sender, bidAmounts[ind])).toEthSignedMessageHash()).recover(searcherSignatures[ind]) == airnodes[ind], "Signature Mismatch");
                require(block.timestamp < expireTimestamps[ind], "Signature has expired");
                totalBid += bidAmounts[ind];
                IDapiServer(dapiServer).fulfillPspBeaconUpdate(subscriptionIds[ind], airnodes[ind], address(this), address(this), timestamps[ind], data[ind], dapiSignatures[ind]);
            }
        }
        require(msg.value >= totalBid, "Insufficient Bid amount");
        IDapiServer(dapiServer).updateBeaconSetWithBeacons(beaconIds);
    }
}