from rag_classification.api_tools.tool_buy_car import tool_wrapper_for_qwen_buy_car

TOOL_BUY_CAR = [
    {
        'name_for_human':
            'buy_car',
        'name_for_model':
            'buy_car',
        'description_for_model': "这是一个记录用户对车辆预期的工具，请你尝试从最新的用户说的话中推测出适合用户的车辆特征，"
                                 "不需要用户说具体的数值，"
                                 "基于猜测的信息构建JSON，请尽量推测，发散思维，尽量不要给空json，不要跟用户说你构建了json"
                                 "然后调用这个工具，你的回答中只能有一次Extracted_Json，不要重复说，"
                                 "对车的预期包括但不限于价位/预算（price），车型分类（body_type），"
                                 "能源形式（energy_type），"
                                 "座位数（number_of_seats），车辆标签（vehicle_labels）等。",
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
            "description": "能源类型可以是新能源车，燃油车，混合动力车，可以多选，多选的话用英文逗号分隔；如果猜测用户想要长距离开的车，可以倾向于燃油车，新能源车在高速耗电快，也可以倾向于燃油，尽量不要单独推荐混动，可以带着新能源或燃油车",
            'required': False
        }, {
            "name": "number_of_seats",
            "type": "string",
            "description": "座位数可以是2座，4座，5座，6座，7座，7座以上，只能选一个",
            'required': False
        }, {
            "name": "vehicle_labels",
            "type": "string",
            "description": "车辆标签必须是以下的一种或几种 【内饰好,外观好,性价比高,空间大,驾驶感受好】，可以多选，多选的话用英文逗号分隔，油耗暂时不作为标签",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_buy_car()
    }

]
TOOL_DESC_BUY_CAR = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_BUY_CAR = """Extracting information as best you can,提取即可，不需要解释太多.
你的输出中不要出现【User:】，Suspected_Reason,Extracted_Json也只能出现一次. You have access to the following tool:

{tool_descs}

Use the following format,不要循环输出下面的格式，不要编例子，也就是说你的输出中不要出现【User:】，Suspected_Reason,Extracted_Json也只能出现一次:

User: the input information you must extract
Suspected_Reason:向用户解释为什么这样猜测,用 您 做称呼，客气一点，不要跟用户说参数和json相关的事情，不要说在json里构建
Extracted_Json: the extracting information with json formatted，只回复本次推理的信息即可，不要重复回复这个字段

Begin!

User: {query}"""