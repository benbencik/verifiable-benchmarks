import torch
from toploc import build_proofs_base64
from toploc import verify_proofs_base64

torch.manual_seed(42)

prefill = [torch.randn(5, 16, dtype=torch.bfloat16)]
generate = [torch.randn(16, dtype=torch.bfloat16) for _ in range(10)]
activations = prefill + generate

proofs = build_proofs_base64(activations, decode_batching_size=3, topk=4, skip_prefill=False)
print(f"Activation shapes: {[i.shape for i in activations]}")
print(f"Proofs: {proofs}")

activations = [i * 1.01 for i in activations]
results = verify_proofs_base64(activations, proofs, decode_batching_size=3, topk=4, skip_prefill=False)

print("Results:")
print(*results, sep="\n")