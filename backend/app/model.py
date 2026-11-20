"""Fine-tuned CLIP (E4): a leaf photo -> 768 numbers.

The normal CLIP ViT-L/14 image part with our fine-tuned last 4 blocks + final norm + projection on top
(`clip_ft_delta.safetensors`, made by the Day 2 Colab notebook). The steps are the same as the notebook's
`app_embed`, so the laptop gives the same numbers as `database.npz` (checked by tests/test_model.py).
"""

import os

import numpy as np
import torch
import torch.nn.functional as F
import transformers
from safetensors.torch import load_file
from transformers import CLIPConfig, CLIPVisionModelWithProjection

BASE_MODEL = "openai/clip-vit-large-patch14"
SIZE = 224
# CLIP's own colour averages and spreads: every photo is scaled with these before the model sees it
MEAN = torch.tensor([0.48145466, 0.4578275, 0.40821073]).view(1, 3, 1, 1)
STD = torch.tensor([0.26862954, 0.26130258, 0.27577711]).view(1, 3, 1, 1)


def set_threads():
    """How many CPU threads PyTorch may use: TORCH_THREADS from the environment, else every CPU thread."""
    n = int(os.getenv("TORCH_THREADS") or os.cpu_count() or 1)
    torch.set_num_threads(n)
    return n


def from_hub(cls, **kwargs):
    """Load from the local Hugging Face cache without asking the internet; download only if it isn't there yet."""
    try:
        return cls.from_pretrained(BASE_MODEL, local_files_only=True, **kwargs)
    except OSError:
        return cls.from_pretrained(BASE_MODEL, **kwargs)


def load_model(delta_file):
    """CLIP's image part + our fine-tuned weights, in float32 and eval mode.
    The base model comes from the Hugging Face cache (downloaded once, about 1.7 GB)."""
    transformers.logging.set_verbosity_error()  # hide the long, harmless "LOAD REPORT" about unused text weights
    transformers.logging.disable_progress_bar()  # and the "Loading weights" bar
    full = from_hub(CLIPConfig)
    vision_config = full.vision_config
    vision_config.projection_dim = full.projection_dim  # 768 for ViT-L/14
    model = from_hub(CLIPVisionModelWithProjection, config=vision_config)
    ours = load_file(str(delta_file))
    _, unexpected = model.load_state_dict(ours, strict=False)  # "missing" = the untouched base weights: fine
    if unexpected or not ours:
        raise ValueError(f"{delta_file} does not fit CLIP ViT-L/14 (unknown weights: {unexpected[:3]})")
    for p in model.parameters():
        p.requires_grad_(False)
    return model.float().eval()


@torch.inference_mode()
def embed(model, photo):
    """photo: 224 x 224 x 3 RGB uint8 (from photo_check.prepare_photo) -> 768 float32 numbers of length 1."""
    if photo.shape != (SIZE, SIZE, 3) or photo.dtype != np.uint8:
        raise ValueError(f"expected a {SIZE} x {SIZE} RGB uint8 photo, got {photo.shape} {photo.dtype}")
    x = torch.from_numpy(np.array(photo)).permute(2, 0, 1)[None].float() / 255.0  # np.array: a writable copy
    x = (x - MEAN) / STD
    v = model.visual_projection(model.vision_model(pixel_values=x).pooler_output)
    return F.normalize(v.float(), dim=-1)[0].numpy()
