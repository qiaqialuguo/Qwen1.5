from collections import defaultdict

import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM

# 初始化一个 defaultdict 用于存储不同类型层的计数
layer_counts = defaultdict(int)

dir = '/opt/large-model/qwen/qwen1.5/Qwen1.5-1.8B-Chat'
# dir = "/opt/large-model/llama/llama3/Meta-Llama-3-8B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    dir,
    device_map='cuda',
    torch_dtype=torch.bfloat16
    # , bnb_4bit_compute_dtype=torch.float16
    # , load_in_4bit=True
).eval()


# 获取模型中的所有层数及每层的固定参数量和可训练参数量
def count_parameters(module):
    fixed_params = sum(p.numel() for p in module.parameters() if not p.requires_grad)
    trainable_params = sum(p.numel() for p in module.parameters() if p.requires_grad)
    return fixed_params, trainable_params


fixed_layer_params = {}
trainable_layer_params = {}
layer_instances = {}

# 遍历模型的所有层并记录固定参数量和可训练参数量以及实例数
for name, module in model.named_modules():
    # print(name,module.__class__.__name__,sum(p.numel() for p in module.parameters()))
    layer_type = module.__class__.__name__
    fixed_params, trainable_params = count_parameters(module)

    if layer_type not in fixed_layer_params:
        fixed_layer_params[layer_type] = 0
        trainable_layer_params[layer_type] = 0
        layer_instances[layer_type] = 0

    fixed_layer_params[layer_type] += fixed_params
    trainable_layer_params[layer_type] += trainable_params
    layer_instances[layer_type] += 1


# 打印每种层的固定参数总量、可训练参数总量和实例总数
for layer_type in fixed_layer_params:
    print(
        f"{layer_type}: {layer_instances[layer_type]} 层, {fixed_layer_params[layer_type]} "
        f"固定参数, {trainable_layer_params[layer_type]} 可训练参数")

