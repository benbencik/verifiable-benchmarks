import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from toploc import build_proofs_base64, verify_proofs_base64

# --- 1. Define the Neural Network ---
# 4 → 16 → 12 → 8 (hidden) → 3 (output)
class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(4, 16),
            nn.ReLU(),
            nn.Linear(16, 12),
            nn.ReLU(),
            nn.Linear(12, 8),    # ← last hidden layer
            nn.ReLU(),
            nn.Linear(8, 3),
        )
    def forward(self, x):
        # run through all but final Linear to grab last hidden state
        for layer in self.net[:-1]:
            x = layer(x)
        hidden = x.clone()   # <-- last hidden activation
        output = self.net[-1](x)       # final linear layer
        return output, hidden

# --- 2. Load and Prepare the Dataset ---
print("Loading and preparing the Iris dataset...")
iris = load_iris()
X, y = iris.data, iris.target

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Scale data and convert to PyTorch Tensors
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train_tensor = torch.tensor(X_train, dtype=torch.bfloat16)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
X_test_tensor = torch.tensor(X_test, dtype=torch.bfloat16)
y_test_tensor = torch.tensor(y_test, dtype=torch.long)

# --- 3. Train the Model ---
print("Training the SimpleNet model...")
torch.manual_seed(42)
model = SimpleNet()
model.to(torch.bfloat16) # Convert model parameters to bfloat16

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# Training loop
for epoch in range(200):
    optimizer.zero_grad()
    outputs, _ = model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 50 == 0:
        print(f"Epoch [{epoch+1}/200], Loss: {loss.item():.4f}")

# --- 4. Extract Activations for Verification ---
print("Extracting hidden layer activations from test samples...")
model.eval() # Set model to evaluation mode

SAMPLES_TO_PROVE = 5
samples = X_test_tensor[:SAMPLES_TO_PROVE]
true_results = y_test_tensor[:SAMPLES_TO_PROVE]

# Get the real activations from the model's hidden layer
with torch.no_grad():
    output, original_activations_list = model(samples)


output_np = output.to(dtype=torch.float32).numpy()
res = np.argmax(output_np, axis=1)


# The `toploc` library expects a list of tensors
original_activations = [act for act in original_activations_list]
print(f"Extracted {len(original_activations)} activation tensors.\n")
print("Model result: {} \nTrue result: {}".format(res, true_results))

# --- 5. Build Verifiable Proofs using toploc ---
# topk=4 means we prove the computation based on the 4 most active neurons
TOPK_VAL = 4
BATCH_SIZE = 2

print(f"Step 4: Building proofs with topk={TOPK_VAL} and decode_batching_size={BATCH_SIZE}...")
proofs = build_proofs_base64(
    original_activations,
    decode_batching_size=BATCH_SIZE,
    topk=TOPK_VAL,
    skip_prefill=False
)
print("Proofs generated successfully.")
print(f"Proofs: {proofs}") # Uncomment to see the base64 encoded proofs
print("\n")


# --- 6. Verify the Proofs ---
print("Step 5: Running verification scenarios...")

# Scenario A: Verify with the EXACT SAME activations (This should pass)
print("--> Verifying with original activations (expecting SUCCESS)...")
results_success = verify_proofs_base64(
    original_activations,
    proofs,
    decode_batching_size=BATCH_SIZE,
    topk=TOPK_VAL,
    skip_prefill=False
)
print("Verification Results (Success Scenario):")
print(*results_success, sep="\n")
print("-" * 20)


# Scenario B: Verify with MODIFIED activations (This should fail)
# Let's simulate a situation where the prover tries to cheat or there's a computational error
# by slightly altering the activations before verification.
altered_activations = [act * 1.5 for act in original_activations]

print("\n--> Verifying with altered activations (expecting FAILURE)...")
results_fail = verify_proofs_base64(
    altered_activations,
    proofs,
    decode_batching_size=BATCH_SIZE,
    topk=TOPK_VAL,
    skip_prefill=False
)
print("Verification Results (Failure Scenario):")
print(*results_fail, sep="\n")
print("-" * 20)