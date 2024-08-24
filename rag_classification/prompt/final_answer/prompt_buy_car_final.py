from rag_classification.api_tools.tool_buy_car import tool_wrapper_for_qwen_buy_car

TOOL_BUY_CAR_FINAL = [
    {
        'name_for_human':
            'buy_car',
        'name_for_model':
            'buy_car',
        'description_for_model': "这是一个给用户推荐车的工具，在用户想要买车或找车时使用这个工具，"
                                 "请注意Monitoring返回的内容，你是尝试从最新的用户说的话中推测出适合用户的车辆特征，"
                                 "不需要用户说具体的数值，"
                                 "如果说需要继续询问用户的时候就问用户信息，你的返回只能有一个FeedbackToUsers"
                                 "",
        'parameters': [],
        'tool_api': tool_wrapper_for_qwen_buy_car()
    }

]
TOOL_DESC_BUY_CAR_FINAL = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_BUY_CAR_FINAL = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

User: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action with json formatted
Monitoring: the result of the action
Thought: 我需要将Monitoring的内容返回给用户
FeedbackToUsers: 返回给用户Monitoring的内容，只返回一次,一定要有这个字段

Begin!

User: {query}
Thought:我将调用buy_car工具来获取车辆信息
Action: buy_car
Action Input:{Extracted_Json}
Monitoring:{api_output}
"""