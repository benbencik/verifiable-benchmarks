// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.27;

import {OperatorSet} from "@eigenlayer-contracts/src/contracts/libraries/OperatorSetLib.sol";

import {IAVSTaskHook} from "@hourglass-monorepo/src/interfaces/avs/l2/IAVSTaskHook.sol";
import {IBN254CertificateVerifier} from "@hourglass-monorepo/src/interfaces/avs/l2/IBN254CertificateVerifier.sol";

contract AVSTaskHook is IAVSTaskHook {

    // Data needed for the benchmark task
    struct BenchmarkTaskPayload {
        string modelUrl;
        string datasetUrl;
    }

    // Store the result of a completed benchmark, mapping task hash to result struct
    struct BenchmarkResult {
        uint8 accuracy;
        string proof; // plain string
        string modelUrl;
    }
    mapping(bytes32 => BenchmarkResult) public benchmarkResults;

    // Track which tasks have been verified to prevent double verification
    mapping(bytes32 => bool) public verifiedTasks;

    event BenchmarkTaskCreated(bytes32 taskHash, string modelUrl, string datasetUrl);
    event BenchmarkVerified(bytes32 taskHash, uint8 accuracy, string proof, string modelUrl);


    // --- Hook Implementations ---
    function validatePreTaskCreation(
        address, /*caller*/
        OperatorSet memory, /*operatorSet*/
        bytes memory payload
    ) external pure {
        BenchmarkTaskPayload memory task = abi.decode(payload, (BenchmarkTaskPayload));
        require(bytes(task.modelUrl).length > 0, "Model URL cannot be empty");
        require(bytes(task.datasetUrl).length > 0, "Dataset URL cannot be empty");
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

        // Decode the ABI-encoded result from cert.messageHash (now used as bytes)
        (string memory modelUrl, string memory proof, uint8 accuracy) = abi.decode(abi.encodePacked(cert.messageHash), (string, string, uint8));

        // Perform validation check
        require(accuracy <= 100, "Accuracy cannot be > 100");

        // Store the result on-chain
        benchmarkResults[taskHash] = BenchmarkResult({accuracy: accuracy, proof: proof, modelUrl: modelUrl});
        verifiedTasks[taskHash] = true;

        // Emit an event to confirm verification
        emit BenchmarkVerified(taskHash, accuracy, proof, modelUrl);
    }
}
