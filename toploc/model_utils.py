import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from huggingface_hub import hf_hub_download
import pandas as pd
import json
import os
import sys
from datetime import datetime
import importlib
from urllib.parse import urlparse

#  Add the directory containing the `models` folder to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ensure the models directory exists
MODELS_DIR = "models"
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# Ensure the trained_models directory exists for saving instances
TRAINED_MODELS_DIR = "trained_models"
if not os.path.exists(TRAINED_MODELS_DIR):
    os.makedirs(TRAINED_MODELS_DIR)

def load_and_prepare_dataset():
    print("Loading and preparing the Iris dataset...")
    iris = load_iris()
    X, y = iris.data, iris.target

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    X_train_tensor = torch.tensor(X_train, dtype=torch.bfloat16)
    y_train_tensor = torch.tensor(y_train, dtype=torch.long)
    X_test_tensor = torch.tensor(X_test, dtype=torch.bfloat16)
    y_test_tensor = torch.tensor(y_test, dtype=torch.long)

    return X_train_tensor, y_train_tensor, X_test_tensor, y_test_tensor

def train_model(model, X_train_tensor, y_train_tensor, epochs=200, lr=0.01):
    print(f"Training the {model.__class__.__name__} model...")
    torch.manual_seed(42)
    model.to(torch.bfloat16)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs, _ = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 50 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
    print(f"Model {model.__class__.__name__} training complete.")


def save_model_with_metadata(model, prover_params, model_data_type=torch.bfloat16):
    model_class_name = model.__class__.__name__
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    model_id = f"{model_class_name}_{timestamp}"
    
    model_filename = os.path.join(TRAINED_MODELS_DIR, f"{model_id}.pt")
    metadata_filename = os.path.join(TRAINED_MODELS_DIR, f"{model_id}.json")

    model = model.to(dtype=model_data_type)
    model.eval()

    # Save model state dictionary
    torch.save(model, model_filename)

    # Prepare metadata
    metadata = {
        "model_id": model_id,
        "model_class_name": model_class_name,
        "data_type": str(model_data_type).split('.')[-1], # e.g., 'bfloat16'
        "prover_params": prover_params,
        "model_path": os.path.abspath(model_filename) # Store absolute path for clarity
    }

    # Save metadata to JSON
    with open(metadata_filename, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Model metadata saved to {metadata_filename}")

    return model_id, model_filename, metadata_filename

def load_model_with_metadata(model_id):
    metadata_filename = os.path.join(TRAINED_MODELS_DIR, f"{model_id}.json")

    if not os.path.exists(metadata_filename):
        raise FileNotFoundError(f"Metadata file not found for model ID: {model_id}")

    with open(metadata_filename, 'r') as f:
        metadata = json.load(f)

    model_class_name = metadata["model_class_name"]
    model_path = metadata["model_path"]
    data_type_str = metadata["data_type"]
    prover_params = metadata["prover_params"]

    # Dynamically import the model class
    try:
        # Assuming model classes are in model_prover.models module
        # ! fix this do not want to be hardcoded
        model_module = importlib.import_module("models.iris_nn")
        model_class = getattr(model_module, model_class_name)
    except (ImportError, AttributeError):
        raise ValueError(f"Could not find model class '{model_class_name}' in model_prover.models.")

    # Instantiate the model
    model = model_class()

    # Determine the torch.dtype from the string
    if data_type_str == 'bfloat16':
        model_dtype = torch.bfloat16
    elif data_type_str == 'float32':
        model_dtype = torch.float32
    else:
        raise ValueError(f"Unsupported data type: {data_type_str}")

    model.to(model_dtype)
    model.load_state_dict(torch.load(model_path))
    model.eval() # Set to evaluation mode after loading
    print(f"Model {model_id} loaded successfully from {model_path}")
    
    return model, metadata

def load_model_from_hf(url: str):
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")
    
    if "blob" in path_parts:
        repo_id = "/".join(path_parts[:2])
        filename = path_parts[-1]
    elif "resolve" in path_parts:
        repo_id = "/".join(path_parts[:2])
        filename = path_parts[-1]
    else:
        raise ValueError("Unexpected Hugging Face URL format. Expecting /blob/ or /resolve/ in the path.")

    model_path = hf_hub_download(repo_id=repo_id, filename=filename)
    model = torch.load(model_path, map_location="cpu", weights_only=False)
    return model

def load_dataset_from_hf(url):
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")
    
    if "blob" in path_parts:
        repo_id = "/".join(path_parts[1:3])
        filename = path_parts[-1]
    elif "resolve" in path_parts:
        repo_id = "/".join(path_parts[:2])
        filename = path_parts[-1]
    else:
        raise ValueError("Unexpected Hugging Face URL format. Expecting /blob/ or /resolve/ in the path.")

    csv_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    df = pd.read_csv(csv_path)

    # ! Assuming last column is the target
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values

    X = torch.tensor(X, dtype=torch.bfloat16)
    y = torch.tensor(y, dtype=torch.long)
    
    return X, y
