import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union, Iterable

class ChatMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: Optional[str]

dir = '/opt/large-model/qwen/qwen1.5/Qwen1.5-1.8B-Chat'
# dir = "/opt/large-model/llama/llama3/Meta-Llama-3-8B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    dir,
    device_map='cuda',
    torch_dtype=torch.bfloat16
    , bnb_4bit_compute_dtype=torch.float16
    , load_in_4bit=True
).eval()

tokenizer = AutoTokenizer.from_pretrained(dir)
print(tokenizer.vocab_size)
print(tokenizer.model_max_length)
start_time = time.time()
inputs = tokenizer.apply_chat_template(
    [ChatMessage(role='user', content='你')],
    tokenize=False,
    add_generation_prompt=True
)

# Print the inputs to see the tokenized format
print(inputs)

# 利用tokenizer将输入文本转换为模型需要的格式，并指定放置到cuda上
model_inputs = tokenizer([inputs], return_tensors="pt").to('cuda')
print(model_inputs)

# 查看输入向量化后的向量（嵌入层的输出）
with torch.no_grad():
    # 获取嵌入层的输出
    embeddings = model.get_input_embeddings()(model_inputs.input_ids)

# Print the embeddings for inspection
print("嵌入向量（Embeddings）：")
print(embeddings)
print("嵌入向量长度：", len(embeddings[0][0]))
print("嵌入向量维度：", embeddings.size())

# 获取位置嵌入向量
with torch.no_grad():
    outputs = model(
        input_ids=model_inputs.input_ids,
        attention_mask=model_inputs.attention_mask,
        output_hidden_states=True,
        output_attentions=True,
        return_dict=True
    )

# 获取注意力权重和隐藏状态
print("注意力权重（Attention weights）：")
print(outputs.attentions[0].size())
print("隐藏状态（Hidden states）：")
print(len(outputs.hidden_states))

generated_ids = model.generate(
    model_inputs.input_ids,
    max_new_tokens=1024,
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]
response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
end_time = time.time()

# Print the response and token counts
print(response)
number_of_tokens = tokenizer([response], return_tensors="pt").to('cuda').input_ids.shape[1]
print(f'Number of output tokens: {number_of_tokens}')
print('每秒token数：'+ str(number_of_tokens / (end_time - start_time)))