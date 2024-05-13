from transformers import AutoTokenizer
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union, Iterable
class ChatMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: Optional[str]

tokenizer = AutoTokenizer.from_pretrained('/opt/large-model/qwen/qwen1.5/Qwen1.5-32B-Chat')

inputs = tokenizer.apply_chat_template(
    [ChatMessage(role='user', content='我可以')],
    tokenize=False,
    add_generation_prompt=True
)
print(inputs)
# 利用tokenizer将输入文本转换为模型需要的格式，并指定放置到cuda上
model_inputs = tokenizer([inputs], return_tensors="pt").to('cuda')
print(model_inputs)
# 计算输入的token数
number_of_tokens = model_inputs.input_ids.shape[1]  # 对于每个批次中的项，获取token的数量
# 输出token数
print(f'Number of input tokens: {number_of_tokens}')

