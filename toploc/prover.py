import torch
import json
import os
import numpy as np
from toploc import build_proofs_base64
from model_utils import save_model_with_metadata, load_model_with_metadata, TRAINED_MODELS_DIR

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
        print(f"Generating proof for model {self.model.__class__.__name__}...")
        
        # Ensure model is in evaluation mode
        # self.model.eval() 

        # Get the real activations from the model's hidden layer
        with torch.no_grad():
            output, original_activations_list = self.model(samples_tensor)

        # Convert output to numpy for result interpretation (optional for proof)
        output_np = output.to(dtype=torch.float32).numpy()
        predicted_classes = np.argmax(output_np, axis=1).tolist()

        # The `toploc` library expects a list of tensors
        original_activations = [act for act in original_activations_list]
        print(f"Extracted {len(original_activations)} activation tensors.")

        # Build verifiable proofs
        proofs_base64 = build_proofs_base64(
            original_activations,
            decode_batching_size=prover_params["decode_batching_size"],
            topk=prover_params["topk"],
            skip_prefill=prover_params["skip_prefill"]
        )
        print("Proofs generated successfully.")
        
        # Prepare data for proof JSON
        # Convert samples_tensor to a list of lists (numpy arrays) for JSON serialization
        samples_list = samples_tensor.tolist()

        return {
            "proofs_base64": proofs_base64,
            "samples_input": samples_list,
            "predicted_classes": predicted_classes,
            "prover_params_used": prover_params
        }
    
    def store_proof(self, model_id, proof_data):
        proof_filename = os.path.join(PROOFS_DIR, f"proof_{model_id}.json")
        
        # Add the model_id to the proof data for easy linkage during verification
        proof_data["model_id"] = model_id

        with open(proof_filename, 'w') as f:
            json.dump(proof_data, f, indent=4)
        print(f"Proof stored to {proof_filename}")
        return proof_filename