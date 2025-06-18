import os
import shutil
from models.iris_nn import SimpleNet 
from model_utils import load_and_prepare_dataset, train_model, save_model_with_metadata
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
    
    
    X_train, y_train, X_test, y_test = load_and_prepare_dataset()
    print("Training the model...")
    model = SimpleNet()
    train_model(model, X_train, y_train, epochs=200, lr=0.01)
    print("Model training completed.")
    print("\n" + "="*50 + "\n")
    
    # Save the trained model with its metadata
    _, _, _ = save_model_with_metadata(model, prover_params)
    

    