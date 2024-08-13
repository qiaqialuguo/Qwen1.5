from rag_classification.api_tools.tool_buy_car import tool_wrapper_for_qwen_buy_car

TOOL_BUY_CAR = [
    {
        'name_for_human':
            'buy_car',
        'name_for_model':
            'buy_car',
        'description_for_model': "这是一个记录用户对车辆预期的工具，请你尝试从最新的用户说的话中推测出适合用户的车辆特征，"
                                 "不需要用户说具体的数值，"
                                 "基于猜测的信息构建JSON，请尽量推测，发散思维，尽量不要给空json，"
                                 "然后调用这个工具，你的回答中只能有一次Extracted_Json，不要重复说，"
                                 "对车的预期包括但不限于价位/预算（price），车型分类（body_type），"
                                 "能源形式（energy_type），品牌类型（brand_type），车型级别（vehicle_size）"
                                 "，座位数（number_of_seats）等。",
        'parameters': [{
            "name": "price",
            "type": "string",
            "description": "价位(预算)的形式可以是X万，X万左右，X万到Y万，X万以内，X万以上.其中X和Y为价格，请用阿拉伯数字表示，如果价格很模糊要把它规整成一个具体价格，比如10万，7万等",
            'required': False
        }, {
            "name": "body_type",
            "type": "string",
            "description": "车型分类可以是轿车、MPV、SUV，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "energy_type",
            "type": "string",
            "description": "能源类型可以是新能源车，燃油车，混合动力车，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "brand_type",
            "type": "string",
            "description": "品牌类型可以是豪华，合资，国产，新势力，可以多选，多选的话用英文逗号分隔，没说品牌类型需要追问",
            'required': False
        }, {
            "name": "vehicle_size",
            "type": "string",
            "description": "车型级别可以是微型车/A00级，小型车/A0级，紧凑型车/A级，中型车/B级，中大型车/C级，"
                           "大型车/D级，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "number_of_seats",
            "type": "string",
            "description": "座位数可以是2座，4座，5座，6座，7座，7座以上，可以多选，多选的话用英文逗号分隔",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_buy_car()
    }

]
TOOL_DESC_BUY_CAR = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_BUY_CAR = """Extracting information as best you can,提取即可，不需要解释太多.. You have access to the following tool:

{tool_descs}

Use the following format,每种key(Question,Thought,Extracted_Json)最多只出现一次，不要重复输出，不要编例子:

User: the input information you must extract
Thought: you should always think about what to do，尽可能简短
Extracted_Json: the extracting information with json formatted，只回复本次提取的信息即可，不要重复回复这个字段

Begin!

User: {query}"""