import time

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union, Iterable
class ChatMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: Optional[str]

dir = '/opt/large-model/qwen/qwen1.5/bit4'

model = AutoModelForCausalLM.from_pretrained(
        dir,
        device_map='cuda'
        ,torch_dtype=torch.bfloat16
        # , bnb_4bit_compute_dtype=torch.float16
        # , load_in_4bit=True
    ).eval()

tokenizer = AutoTokenizer.from_pretrained(dir)
start_time = time.time()
inputs = tokenizer.apply_chat_template(
    [ChatMessage(role='user', content='讲个故事')],
    tokenize=False,
    add_generation_prompt=True
)
# print(inputs)
# 利用tokenizer将输入文本转换为模型需要的格式，并指定放置到cuda上
model_inputs = tokenizer([inputs], return_tensors="pt").to('cuda')
generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=1024,
    )
generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
end_time = time.time()
# print(model_inputs)
# 计算输入的token数
print(response)
number_of_tokens = tokenizer([response], return_tensors="pt").to('cuda').input_ids.shape[1]  # 对于每个批次中的项，获取token的数量
# 输出token数
print(f'Number of input tokens: {number_of_tokens}')
print('每秒token数：'+ str(number_of_tokens / (end_time - start_time)))