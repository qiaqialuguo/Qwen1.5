from collections import defaultdict
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM

# 初始化defaultdict用于存储不同类型层的计数
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
def traverse_layers(module, depth=0):
    for name, sub_module in module.named_children():
        layer_type = sub_module.__class__.__name__
        fixed_params, trainable_params = count_parameters(sub_module)

        if layer_type not in fixed_layer_params:
            fixed_layer_params[layer_type] = 0
            trainable_layer_params[layer_type] = 0
            layer_instances[layer_type] = 0

        fixed_layer_params[layer_type] += fixed_params
        trainable_layer_params[layer_type] += trainable_params
        layer_instances[layer_type] += 1

        # 打印当前层的参数信息和层级
        print(
            f"{' ' * 2 * depth}{layer_type}: 第 {layer_instances[layer_type]} 层, "
            f" {trainable_params} 个可训练参数"
        )

        # 递归遍历子层
        traverse_layers(sub_module, depth + 1)

# 递归遍历整个模型
traverse_layers(model)