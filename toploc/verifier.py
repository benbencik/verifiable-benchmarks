import sklearn.metrics
import torch
import os
import re
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

    def verify_proof(self, model, proof, prover_params, X, y):
        proofs_base64 = proof.split('~')
        
        prover_params_used = prover_params
        

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
        
        print("Recomputing activations using the loaded model and dataset...")
        # model.eval() # Ensure model is in evaluation mode?
        with torch.no_grad():
            recomputed_output, recomputed_activations_list = model(X)
        
        recomputed_activations = [act for act in recomputed_activations_list]
        
        # recomputed_predicted_classes = np.argmax(recomputed_output.to(dtype=torch.float32).numpy(), axis=1).tolist()
        # accuracy_recomputed = round(sklearn.metrics.accuracy_score(recomputed_predicted_classes, y),3)
        # print(f"Recomputed accuracy: {accuracy_recomputed}, Promised accuracy: {accuracy}")

        # if accuracy_recomputed != accuracy:
        #     return False

        print("Running `toploc` verification...")
        verification_results = verify_proofs_base64(
            recomputed_activations,
            proofs_base64,
            decode_batching_size=prover_params_used["decode_batching_size"],
            topk=prover_params_used["topk"],
            skip_prefill=prover_params_used["skip_prefill"]
        )

        # print(verification_results)
        # print(type(verification_results[0]))
        
        for i in verification_results:
            i = str(i)
            matches = re.findall(r'VerificationResult\[exp_mismatches=(\d+), mant_err_mean=([\d.]+), mant_err_median=([\d.]+)\]', i)
            parsed_results = [{'exp_mismatches': int(a), 'mant_err_mean': float(b), 'mant_err_median': float(c)} for a, b, c in matches]
            
            m = 0
            for result in parsed_results:
                m = max(m, result['exp_mismatches'])
            if m > 0:
                return False

        # print("\nVerification Results:")
        # print(f"Prover's Predicted Classes: {predicted_classes}")
        # print(f"Verifier's Recomputed Predicted Classes: {recomputed_predicted_classes}")
        # print(f"Toploc Proof Verification Status: {verification_results}")
        # print(f"--- Verification Complete for {proof_filename} ---\n")
        
        return True