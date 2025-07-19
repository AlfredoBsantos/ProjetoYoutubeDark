import torch

if torch.cuda.is_available():
    print("\n✅ SUCESSO! A GPU está pronta para ser usada pelo PyTorch.")
    print(f"Nome da GPU detectada: {torch.cuda.get_device_name(0)}\n")
else:
    print("\n❌ FALHA! O PyTorch não conseguiu detectar a GPU.")
    print("Verifique a instalação do CUDA Toolkit e dos drivers da NVIDIA.\n")