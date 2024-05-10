response = """切换判断耗时: 0.9105315208435059 结果长度: 89 每秒字数: 97.74510597672823 输入长度: 1994 显存增加: -0.0009765625 G 
切换判断结果：Thought: 用户在询问关于"优必爱AI智能体-BAVA"所属公司的信息，这与当前场景buy_car无关。
Probability: 100%
New_Scene: name"""

i = response.rfind('\nNew_Scene:')
j = response.rfind('\nProbability:')
# 如果正确分类
if 0 <= i and 0 <= j:
    probability = response[i + len('\nProbability:'):].strip().split('\n')[0].split('%')[0]
    plugin_name = response[i + len('\nNew_Scene:'):].strip().split('\n')[0]
    print(response[i + len('\nProbability:'):].strip().split('\n')[0])
    print(plugin_name)
