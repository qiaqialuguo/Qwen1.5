import torch
from transformers import AutoModelForCausalLM

dir = '/opt/large-model/qwen/qwen1.5/Qwen1.5-1.8B-Chat'

model = AutoModelForCausalLM.from_pretrained(
    dir,
    device_map='cuda',
    torch_dtype=torch.bfloat16
    # , bnb_4bit_compute_dtype=torch.float16
    # , load_in_4bit=True
).eval()


def count_parameters(model):
    total_params = 0
    layer_params = []

    for name, param in model.named_parameters():
        print(name,param.numel(),param.requires_grad)
        if 'layer' in name:
            layer_num = int(name.split('.')[2])  # 假设层数的位置是名称中的第三个，例如 "model.encoder.layerX...."
            if len(layer_params) == layer_num:
                layer_params.append(0)
            layer_params[layer_num] += param.numel()
        total_params += param.numel()

    return total_params, layer_params


total_params, layer_params = count_parameters(model)
print(f"Total parameters: {total_params:,}")
print(f"Parameters per layer: {layer_params}")