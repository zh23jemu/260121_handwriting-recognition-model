import torch

# 检查CUDA是否可用
if torch.cuda.is_available():
    print("CUDA可用！")
    print(f"CUDA设备数量: {torch.cuda.device_count()}")
    print(f"当前CUDA设备: {torch.cuda.current_device()}")
    print(f"CUDA设备名称: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA不可用，将使用CPU")
    print(f"当前设备: cpu")