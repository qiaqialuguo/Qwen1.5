from transformers import AutoTokenizer
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union, Iterable
class ChatMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: Optional[str]

tokenizer = AutoTokenizer.from_pretrained('/opt/large-model/qwen/qwen1.5/Qwen1.5-32B-Chat')

inputs = tokenizer.apply_chat_template(
    [ChatMessage(role='user', content="""

Answer the following questions as best you can. You have access to the following tools:

vehicle_issues: Call this tool to interact with the vehicle_issues API. What is the vehicle_issues API useful for? 回答用户汽车功能，汽车故障等任何汽车相关的问题时，用这个工具，用户说车辆信息时也提取车辆信息.. Parameters: [{"name": "has_vehicle_information", "type": "string", "description": "True or False", "required": true}, {"name": "vehicle_brand_name", "type": "string", "description": "品牌名称，只能有一个值", "required": false}, {"name": "vehicle_series", "type": "string", "description": "车系名称可以是X3，i3,X5等任何车系，只能有一个值", "required": false}, {"name": "vehicle_model_year", "type": "string", "description": "车辆年款可以是2023款，2019款，2008款等，只能有一个值", "required": false}] Format the arguments as a JSON object.

Use the following format:

User: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [vehicle_issues]
Action Input: the input to the action with json formatted
Monitoring: the result of the action
... (this Thought/Action/Action Input/Monitoring can be repeated zero or more times)
Thought: I now know the final answer
FeedbackToUser: the final answer to the original input question

Begin!

User: 路边停车需要注意什么
Thought:我将调用vehicle_issues工具来获取问题答案
Action: vehicle_issues
Action Input:{}
Monitoring:['路边停车需要注意的事项\n\n路边停车是一项需要谨慎对待的任务，不仅是为了避免不必要的罚款和扣分，更重要的是确保交通安全，防止发生意外事故。以下是路边停车需要注意的几个方面：\n\n1. 是否允许停车\n\n在路边停车之前，首先要确认该路段是否允许停车。不同的路段有不同的停车规定，有的路段禁止临时停车和长期停车，有的路段禁止长时间停车，还有的路段是禁止停车的。车主应该了解并遵守这些规定，以防因违章停车而被交警罚款扣分2。\n\n2. 注意前后车辆和障碍物\n\n在选择车位时，要仔细观察车位前后是否有障碍物。尤其是在车辆不断流动的路段停车时，驾驶员在开门下车前，应先从后视镜看后面是否有车（或有人骑自行车、摩托车），防止发生碰撞事故2。\n\n3. 遵循正确的停车规定\n\n除了上述的基本注意事项之外，还需要遵循一些具体的停车规定。例如，车辆停稳前不得开车门和上下人员，开关车门不得妨碍其他车辆和行人通行；路边停车应当紧靠道路右侧，驾驶人不得离车，上下人员或者装卸物品后，立即驶离；交叉路口、铁路道口、急弯路、宽度不足4米的窄路、桥梁、陡坡、隧道以及距离上述地点50米以内的路段，不得停车等4。\n\n4. 使用停车指引标志\n\n在一些停车需求相对集中的区域，可以试点开展停车指引标志设置，清晰告知驾驶人目的地周边停车设施分布情况，快速指引驾驶人寻找停车位，减少无效绕行路线，缓解因盲目寻找停车位而加重交通拥堵3。\n\n5. 注意停车收费和违停处罚\n\n在一些城市，路边停车是需要收费的，而且如果违法停车，还会受到罚款和扣分的处罚。因此，车主在路边停车时，不仅要遵守停车规定，还要注意查看停车收费标志，并且尽量避免违停567。\n\n总的来说，路边停车需要注意的事项非常多，但只要车主们都能够认真遵守相关规定，就能够有效地减少交通事故的发生，保障道路交通的安全和畅通。']

""")],
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

