// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.27;

import {OperatorSet} from "@eigenlayer-contracts/src/contracts/libraries/OperatorSetLib.sol";

import {IAVSTaskHook} from "@hourglass-monorepo/src/interfaces/avs/l2/IAVSTaskHook.sol";
import {IBN254CertificateVerifier} from "@hourglass-monorepo/src/interfaces/avs/l2/IBN254CertificateVerifier.sol";

contract AVSTaskHook is IAVSTaskHook {

    // Data needed for the benchmark task
    struct BenchmarkTaskPayload {
        string modelId;
        string datasetId;
    }

    // Store the result of a completed benchmark, mapping task hash to accuracy
    mapping(bytes32 => uint8) public benchmarkResults;

    // Track which tasks have been verified to prevent double verification
    mapping(bytes32 => bool) public verifiedTasks;

    event BenchmarkTaskCreated(bytes32 taskHash, string modelId, string datasetId);
    event BenchmarkVerified(bytes32 taskHash, uint8 accuracy);


    // --- Hook Implementations ---
    function validatePreTaskCreation(
        address, /*caller*/
        OperatorSet memory, /*operatorSet*/
        bytes memory payload
    ) external pure {
        BenchmarkTaskPayload memory task = abi.decode(payload, (BenchmarkTaskPayload));
        require(bytes(task.modelId).length > 0, "Model ID cannot be empty");
        require(bytes(task.datasetId).length > 0, "Dataset ID cannot be empty");
    }

    function validatePostTaskCreation(
        bytes32 taskHash
    ) external {
        // We can't easily access payload data here, so we emit a generic event.
        // The off-chain operator knows the task details.
        emit BenchmarkTaskCreated(taskHash, "unknown", "unknown");
    }

    function validateTaskResultSubmission(
        bytes32 taskHash,
        IBN254CertificateVerifier.BN254Certificate memory cert
    ) external {
        // Ensure task hasn't been verified before
        require(!verifiedTasks[taskHash], "Task already verified");

        // Decode the benchmark accuracy from the messageHash field
        // We'll use the first byte of the messageHash to store our accuracy
        uint8 accuracy = uint8(cert.messageHash[0]);

        // Perform validation check
        require(accuracy <= 100, "Accuracy cannot be > 100");

        // Store the result on-chain
        benchmarkResults[taskHash] = accuracy;
        verifiedTasks[taskHash] = true;

        // Emit an event to confirm verification
        emit BenchmarkVerified(taskHash, accuracy);
    }
}
