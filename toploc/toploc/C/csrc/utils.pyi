from typing import Tuple, List
import torch

def get_fp_parts(
    tensor: torch.Tensor,
    num_threads: int = ...,
) -> Tuple[List[int], List[int]]: ...
