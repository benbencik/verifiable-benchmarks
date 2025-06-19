from flask import Flask, request
import os
import shutil

from model_utils import load_dataset_from_hf, load_model_from_hf
from prover import ModelProver
from verifier import Verifier

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run_task():
    dataset_url = request.form.get("dataset_url")
    model_url = request.form.get("model_url")
    task = request.form.get("task")
    proof = request.form.get("proof", None)

    if not all([dataset_url, model_url, task]):
        return "Missing required parameters", 400

    # Load data and model
    X, y = load_dataset_from_hf(dataset_url)
    model = load_model_from_hf(model_url)

    prover_params = {
        "decode_batching_size": 1,
        "topk": 4,
        "skip_prefill": False
    }

    if task == "verify":
        if not proof:
            return "Proof is required for verification task", 400
        verifier = Verifier()
        result = verifier.verify_proof(model, proof, prover_params, X, y)
        return f"Verification success: {result}"

    elif task == "predict":
        prover = ModelProver(model)
        proof_data = prover.generate_proof(X, prover_params)
        proof_file = prover.store_proof(proof_data, model_url, dataset_url, y)
        return f"Proof stored: {proof_file}"

    else:
        return "Invalid task. Must be either 'predict' or 'verify'.", 400

if __name__ == "__main__":
    app.run(debug=True)
