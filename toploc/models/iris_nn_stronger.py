import torch.nn as nn

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