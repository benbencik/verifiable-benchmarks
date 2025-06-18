# Verifiable Benchmarks

**Verifiable Benchmarks** is an open-source framework for trustless verification of machine learning inference, inspired by the [TOPLOC](https://arxiv.org/pdf/2501.16007) approach. This project addresses the critical challenge of establishing trust in third-party ML inference providers, ensuring that users can independently verify the integrity and faithfulness of off-chain model execution.

## Why Verifiable Inference?

In decentralized ML inference marketplaces and cloud-based AI services, there's an inherent risk:  
Providers might surreptitiously modify models, reduce precision, inject biases, or otherwise deviate from their advertised service. Users need cryptographic assurance that the inference results are genuine, reproducible, and uncompromised.

## Approach: TOPLOC-Inspired Inference Verification

Our system leverages the core ideas of the TOPLOC protocol:

- **Locality-Sensitive Hashing of Activations:**  
  During model inference, we hash the top-k values and indices of intermediate activations, encoding them as a polynomial congruence. This efficiently compresses the representation, reducing proof storage by over 1000x while retaining security guarantees.

- **Proof Robustness:**  
  The approach is robust to typical sources of nondeterminism (e.g., GPU computation ordering) and algebraic rewrites, ensuring that honest recomputation by a verifier matches the submitted proof.

- **Merkle Tree Aggregation:**  
  For each data point, an inference proof is generated (encoded in base64), and the collection of these proofs is aggregated into a Merkle tree. This further reduces on-chain storage and enables batch verification.

## System Architecture

### Off-chain Verification with EigenLayer AVS

We integrate [EigenLayer AVS (Actively Validated Services)](https://docs.eigenlayer.xyz/) to perform scalable, decentralized off-chain verification of submitted inference proofs. Here’s how it works:

- **Proof Generation:**  
  Each inference request produces a compact, base64-encoded proof of correct execution.

- **Merkle Aggregation:**  
  Proofs for multiple inputs are bundled via a Merkle tree. Only the root (and necessary branches for disputes) need be stored or verified on-chain, minimizing data footprint.

- **AVS Verification:**  
  Validators in the EigenLayer AVS network independently recompute the inference and check the submitted proof against their own recomputation, using the TOPLOC encoding. Discrepancies can trigger slashing or dispute resolution.

### Repository Components

## Getting Started

## References

- [TOPLOC: Polynomial Congruence Locality-Sensitive Hashing for Verifiable Neural Network Inference](https://arxiv.org/pdf/2501.16007)
- [EigenLayer Documentation](https://docs.eigenlayer.xyz/)
