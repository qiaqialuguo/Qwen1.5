from rag_classification.api_tools.tool_used_car_valuation import tool_wrapper_for_qwen_used_car_valuation

# todo You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture. Knowledge cutoff: 2023-04 Current date: 2024-02-15
TOOL_USED_CAR_VALUATION = [
    {
        'name_for_human':
            'used_car_valuation',
        'name_for_model':
            'used_car_valuation',
        'description_for_model': "这是一个给二手车估值的工具。当用户想对车辆进行估值或卖车的时候调用这个工具，"
                                 "返回的是评估出的车辆的价格，从用户说的问题中提取车辆信息，基于已知信息构建JSON，"
                                 "用户没说信息就给空json，每次只提取User:中的信息，JSON里不要加注释，公里数用阿拉伯数字表示，你的回答中只能有一次Extracted_Json，不要重复说，"
                                 "对车的描述包含 车辆品牌名称（brand），车系（series），车辆年款（modelYear），"
                                 "车辆上牌时年份（licensingYear），车辆上牌时月份（licensingMonth），"
                                 "车辆上牌地所在城市（city），车辆里程数（mileage），"
                                 "车况（condition），车身颜色（color）。",
        'parameters': [{
            "name": "brand",
            "type": "string",
            "description": "品牌名称，只能有一个值,为空的话不输出",
            'required': False
        }, {
            "name": "series",
            "type": "string",
            "description": "车系名称可以是X3，i3,X5，A6等任何车系，车系比较简略，只能有一个值,为空的话不输出",
            'required': False
        }, {
            "name": "modelYear",
            "type": "string",
            "description": "车辆年款，如2023款，2019款，2008款等，只能有一个值,为空的话不输出",
            "required": False
        }, {
            "name": "licensingYear",
            "type": "string",
            "description": "车辆上牌年份是一个具体年份，比如2016年,2020年,2021年,2023年等，只能有一个值,为空的话不输出",
            'required': False
        }, {
            "name": "licensingMonth",
            "type": "string",
            "description": "车辆上牌月份是一个具体月份，比如1月,2月,11月等，只能有一个值,为空的话不输出",
            'required': False
        }, {
            "name": "city",
            "type": "string",
            "description": "车辆上牌地所在城市是一个城市名，问清楚用户是在哪个城市，只能有一个值,为空的话不输出",
            'required': False
        }, {
            "name": "mileage",
            "type": "string",
            "description": "车辆里程数是车辆行驶了多少公里，比如10000公里，40000公里，单位是公里，只能有一个值，公里数用阿拉伯数字表示,为空的话不输出",
            'required': False
        }, {
            "name": "condition",
            "type": "string",
            "description": "车况是优秀或良好，只能有一个值,为空的话不输出",
            'required': False
        }, {
            "name": "color",
            "type": "string",
            "description": "车身颜色是车辆的颜色，只能有一个值,为空的话不输出",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_used_car_valuation()
    }

]
TOOL_DESC_USED_CAR_VALUATION = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_USED_CAR_VALUATION = """Extracting information as best you can,提取即可，不需要解释太多.. You have access to the following tool:

{tool_descs}

Use the following format,每种key(User,Thought,Extracted_Json)最多只出现一次，不要重复输出，不要编例子:

User: the input information you must extract
Extracted_Json: the extracting information with json formatted，只回复本次提取的信息即可，不要重复回复这个字段
Thought: you should always think about what to do，尽可能简短

Begin!

User: {query}"""
