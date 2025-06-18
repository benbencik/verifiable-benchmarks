import os
import shutil
from model_utils import load_dataset_from_hf, load_model_from_hf
from prover import ModelProver, PROOFS_DIR, TRAINED_MODELS_DIR
from verifier import Verifier


# Clean up previous runs for a fresh start
def cleanup():
    if os.path.exists(PROOFS_DIR):
        shutil.rmtree(PROOFS_DIR)
        print(f"Cleaned up {PROOFS_DIR}")
    if os.path.exists(TRAINED_MODELS_DIR):
        shutil.rmtree(TRAINED_MODELS_DIR)
        print(f"Cleaned up {TRAINED_MODELS_DIR}")
    os.makedirs(PROOFS_DIR, exist_ok=True)
    os.makedirs(TRAINED_MODELS_DIR, exist_ok=True)


if __name__ == "__main__":
    # cleanup()
   
    prover_params = {
        "decode_batching_size": 1,
        "topk": 4,
        "skip_prefill": False
    }
    
    # X_train, y_train, X_test, y_test = load_and_prepare_dataset()
    
    # # --- Training Phase ---
    # print("Training the model...")
    # model = SimpleNet()
    # train_model(model, X_train, y_train, epochs=200, lr=0.01)
    # print("Model training completed.")
    # print("\n" + "="*50 + "\n")
    
    # # Save the trained model with its metadata
    # _, _, _ = save_model_with_metadata(model, prover_params)
    
    # exit(0)
    
    X, y = load_dataset_from_hf("https://huggingface.co/datasets/benbencik/eigen-datasets/blob/main/iris.csv")
    model = load_model_from_hf("https://huggingface.co/benbencik/eigen-models/blob/main/SimpleNet_20250618162512.pt")
    
    
    # Instantiate the Prover
    prover = ModelProver(model)

    # Save the trained model with its metadata
    # model_id, model_path, metadata_path = prover.save_trained_model(prover_params)
    # print(f"Model ID for this run: {model_id}")

    # Select samples for proving
    # print(f"True labels for samples: {y.numpy()}")

    # Generate the proof
    proof_data = prover.generate_proof(X, prover_params)
    proof_filename = prover.store_proof(proof_data)

    print("\n" + "="*50 + "\n")

    # --- Verification Phase ---
    verifier = Verifier()

    # Scenario 1: Successful verification
    results_success, prover_preds, verifier_preds = verifier.verify_proof(model, proof_filename, X, y)
    # print("Scenario 1: Verifying with the original proof (expecting SUCCESS)")
    # print(f"Verification Success Status: {results_success}")
    # # You can further check if prover_preds == verifier_preds for classification tasks
    # print(f"Prover's predictions: {prover_preds}, Verifier's recomputed predictions: {verifier_preds}")
    # print(f"Do predicted classes match after recomputation? {prover_preds == verifier_preds}")


    # Scenario 2: Simulate a challenge/tampering (e.g., altered proof data)
    
    