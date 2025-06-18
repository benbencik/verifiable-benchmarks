import sklearn.metrics
import torch
import json
import os
import numpy as np
import sklearn
from toploc import verify_proofs_base64
from model_utils import load_model_with_metadata, TRAINED_MODELS_DIR

# Ensure the proofs directory exists (same as in prover)
PROOFS_DIR = "proofs" 
if not os.path.exists(PROOFS_DIR):
    os.makedirs(PROOFS_DIR)

class Verifier:
    def __init__(self):
        pass

    def verify_proof(self, model, proof_filename, X, y):
        print(f"\n--- Starting Verification for {proof_filename} ---")
        
        if not os.path.exists(proof_filename):
            raise FileNotFoundError(f"Proof file not found: {proof_filename}")

        with open(proof_filename, 'r') as f:
            proof_data = json.load(f)

        model_id = proof_data["model_id"]
        proofs_base64 = proof_data["proofs_base64"]
        samples_input_list = proof_data["samples_input"]
        prover_params_used = proof_data["prover_params_used"]
        predicted_classes = proof_data["predicted_classes"]

        print(f"Loading model and metadata for Model ID: {model_id}")
        # model, metadata = load_model_with_metadata(model_id)

        # Reconstruct samples tensor from the list
        # Ensure the dtype matches what was used during proving (from metadata)
        # model_data_type_str = metadata["data_type"]
        # if model_data_type_str == 'bfloat16':
        #     samples_tensor_dtype = torch.bfloat16
        # elif model_data_type_str == 'float32':
        #     samples_tensor_dtype = torch.float32
        # else:
        #     raise ValueError(f"Unsupported data type for samples: {model_data_type_str}")

        # samples_tensor = torch.tensor(samples_input_list, dtype=torch.bfloat16)
        
        print("Recomputing activations using the loaded model and input samples...")
        # model.eval() # Ensure model is in evaluation mode?
        with torch.no_grad():
            recomputed_output, recomputed_activations_list = model(X)
        
        recomputed_activations = [act for act in recomputed_activations_list]
        recomputed_predicted_classes = np.argmax(recomputed_output.to(dtype=torch.float32).numpy(), axis=1).tolist()
        accuracy = sklearn.metrics.accuracy_score(recomputed_predicted_classes, y)
        print(accuracy)


        print("Running `toploc` verification...")
        verification_results = verify_proofs_base64(
            recomputed_activations,
            proofs_base64,
            decode_batching_size=prover_params_used["decode_batching_size"],
            topk=prover_params_used["topk"],
            skip_prefill=prover_params_used["skip_prefill"]
        )
        
        # print("\nVerification Results:")
        # print(f"Prover's Predicted Classes: {predicted_classes}")
        # print(f"Verifier's Recomputed Predicted Classes: {recomputed_predicted_classes}")
        # print(f"Toploc Proof Verification Status: {verification_results}")
        # print(f"--- Verification Complete for {proof_filename} ---\n")
        
        return verification_results, predicted_classes, recomputed_predicted_classes