// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.27;

import {OperatorSet} from "@eigenlayer-contracts/src/contracts/libraries/OperatorSetLib.sol";
import {IAVSTaskHook} from "@hourglass-monorepo/src/interfaces/avs/l2/IAVSTaskHook.sol";
import {IBN254CertificateVerifier} from "@hourglass-monorepo/src/interfaces/avs/l2/IBN254CertificateVerifier.sol";

/**
 * @notice This contract expects the IPFS CID to be generated and uploaded offchain.
 * Only the bytes32 representation of the CID is stored onchain for each benchmark result.
 */
contract AVSTaskHook is IAVSTaskHook {
    mapping(bytes32 => bytes32) public benchmarkResultCIDs;
    mapping(bytes32 => bool) public verifiedTasks;

    event BenchmarkTaskCreated(bytes32 taskHash);
    event BenchmarkResultSubmitted(bytes32 taskHash, bytes32 ipfsCID);

    function validatePreTaskCreation(
        address, /*caller*/
        OperatorSet memory, /*operatorSet*/
        bytes memory /*payload*/
    ) external view {
        // No validation needed since we're not using parameters
    }

    function validatePostTaskCreation(
        bytes32 taskHash
    ) external {
        emit BenchmarkTaskCreated(taskHash);
    }

    function validateTaskResultSubmission(
        bytes32 taskHash,
        IBN254CertificateVerifier.BN254Certificate memory cert
    ) external {
        require(!verifiedTasks[taskHash], "Task already verified");

        // Use the bytes32 directly, no need to decode
        bytes32 ipfsCID = cert.messageHash;

        benchmarkResultCIDs[taskHash] = ipfsCID;
        verifiedTasks[taskHash] = true;

        emit BenchmarkResultSubmitted(taskHash, ipfsCID);
    }
}
