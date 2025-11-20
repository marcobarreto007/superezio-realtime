import torch

print("=" * 60)
print("VERIFICACAO CUDA")
print("=" * 60)
print(f"CUDA disponivel: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Numero de GPUs: {torch.cuda.device_count()}")
    print(f"VRAM total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print(f"VRAM usada: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    print(f"VRAM reservada: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
else:
    print("CUDA NAO DISPONIVEL!")
print(f"PyTorch version: {torch.__version__}")
print("=" * 60)
