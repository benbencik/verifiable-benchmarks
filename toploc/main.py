import os
import shutil
import argparse

from model_utils import load_dataset_from_hf, load_model_from_hf
from prover import ModelProver, PROOFS_DIR, TRAINED_MODELS_DIR
from verifier import Verifier

def cleanup():
    if os.path.exists(PROOFS_DIR):
        shutil.rmtree(PROOFS_DIR)
        print(f"Cleaned up {PROOFS_DIR}")
    if os.path.exists(TRAINED_MODELS_DIR):
        shutil.rmtree(TRAINED_MODELS_DIR)
        print(f"Cleaned up {TRAINED_MODELS_DIR}")
    os.makedirs(PROOFS_DIR, exist_ok=True)
    os.makedirs(TRAINED_MODELS_DIR, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Run proof generation or verification")
    parser.add_argument("--dataset_url", required=True, help="Hugging Face URL to CSV dataset with last columns as labels")
    parser.add_argument("--model_url", required=True, help="Hugging Face URL to .pt model file")
    parser.add_argument("--task", choices=["predict", "verify"], required=True, help="Task to run: predict or verify")
    parser.add_argument("--accuracy", help="Promissed int accuracy 0 to 1")
    parser.add_argument("--proof", help="Provided proof in single string deleimited by ~")

    args = parser.parse_args()
    dataset_url = args.dataset_url
    model_url = args.model_url
    task = args.task

    # Load dataset and model
    X, y = load_dataset_from_hf(dataset_url)
    model = load_model_from_hf(model_url)

    prover_params = {
        "decode_batching_size": 1,
        "topk": 4,
        "skip_prefill": False
    }

    if task == "verify":
        proof = args.proof
        
        verifier = Verifier()
        results_success = verifier.verify_proof(model, proof, prover_params, X, y)
        print("Verification success:", results_success)
    elif task == "predict":
        prover = ModelProver(model)
        proof_data = prover.generate_proof(X, prover_params)
        prover.store_proof(proof_data, model_url, dataset_url, y)

if __name__ == "__main__":
    main()
