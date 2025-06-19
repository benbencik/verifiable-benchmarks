import torch
import json
import os
import time
import numpy as np
import sklearn
from toploc import build_proofs_base64
from model_utils import save_model_with_metadata, load_model_with_metadata, TRAINED_MODELS_DIR
import torch.nn.functional as F


# Ensure the proofs directory exists
PROOFS_DIR = "proofs"
if not os.path.exists(PROOFS_DIR):
    os.makedirs(PROOFS_DIR)

class ModelProver:
    def __init__(self, model):
        self.model = model

    def save_trained_model(self, prover_params, model_data_type=torch.bfloat16):
        return save_model_with_metadata(self.model, prover_params, model_data_type)

    def generate_proof(self, samples_tensor, prover_params):        
        # Get the real activations from the model's hidden layer
        with torch.no_grad():
            output, original_activations_list = self.model(samples_tensor)

        # Convert output to numpy for result interpretation (optional for proof)
        # output_np = output.to(dtype=torch.float32).numpy()
        predicted_classes = torch.argmax(output, dim=1).tolist()
        # predicted_classes = np.argmax(output_np, axis=1).tolist()

        # The `toploc` library expects a list of tensors
        original_activations = [act for act in original_activations_list]
        # print(f"Extracted {len(original_activations)} activation tensors.")

        # Build verifiable proofs
        proofs_base64 = build_proofs_base64(
            original_activations,
            decode_batching_size=prover_params["decode_batching_size"],
            topk=prover_params["topk"],
            skip_prefill=prover_params["skip_prefill"]
        )
        
        concatenated_proof = '~'.join(proofs_base64)  # Join proofs into a single string for storage
        
        # print("Proofs generated successfully.")
        
        # Prepare data for proof JSON
        # Convert samples_tensor to a list of lists (numpy arrays) for JSON serialization
        samples_list = samples_tensor.tolist()

        return {
            "proofs_base64": concatenated_proof,
            "samples_input": samples_list,
            "predicted_classes": predicted_classes,
            "prover_params_used": prover_params
        }
    
    def store_proof(self, proof_data, model_url, dataset_url ,y):
        
        time_now = time.time_ns()
        proof_filename = os.path.join(PROOFS_DIR, f"proof_{time_now}.json")
        accuracy = round(sklearn.metrics.accuracy_score(proof_data["predicted_classes"], y), 3)
        
        print(y)
              
        print(f"Calculated accuracy: {accuracy}")
        
        data = {
            "model_url": model_url,
            "datset_url": dataset_url,
            "proof": proof_data["proofs_base64"],
        }

        with open(proof_filename, 'w') as f:
            json.dump(data, f)
        print(f"Proof stored to {proof_filename}")
        return proof_filename