from rag_classification.api_tools.tool_buy_car import tool_wrapper_for_qwen_buy_car

TOOL_BUY_CAR = [
    {
        'name_for_human':
            'buy_car',
        'name_for_model':
            'buy_car',
        'description_for_model': "这是一个记录用户对车辆预期的工具，请你尝试从用户说的话中抽取出如下预期，基于已知信息构建JSON，用户没说信息就给空json，然后调用这个工具，"
                                 "对车的预期包含价位/预算（price），车型分类（vehicle_classification），"
                                 "能源形式（energy_type），品牌类型（brand_type），车型级别（vehicle_size），座位数（number_of_seats），"
                                 "车门数（number_of_doors），车辆厢数（number_of_compartments），车辆品牌名称（vehicle_brand_name）。",
        'parameters': [{
            "name": "price",
            "type": "string",
            "description": "价位(预算)的形式可以是X万，X万左右，X万到Y万，X万以内，X万以上或不限.其中X和Y为价格，用户没说价格的话需要追问",
            'required': False
        }, {
            "name": "vehicle_classification",
            "type": "string",
            "description": "车型分类可以是轿车、MPV、SUV或不限，可以多选，多选的话用英文逗号分隔，用户没说车型分类的话需要追问",
            'required': False
        }, {
            "name": "energy_type",
            "type": "string",
            "description": "能源类型可以是新能源车，燃油车，混合动力车或不限，可以多选，多选的话用英文逗号分隔，用户没说能源类型的话需要追问,用户说新能源时需要调用这个工具",
            'required': False
        }, {
            "name": "brand_type",
            "type": "string",
            "description": "品牌类型可以是豪华，合资，国产，新势力或不限，可以多选，多选的话用英文逗号分隔，没说品牌类型需要追问",
            'required': False
        }, {
            "name": "vehicle_size",
            "type": "string",
            "description": "车型级别可以是微型车/A00级，小型车/A0级，紧凑型车/A级，中型车/B级，中大型车/C级，"
                           "大型车/D级或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "number_of_seats",
            "type": "string",
            "description": "座位数可以是2座，4座，5座，6座，7座，7座以上或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "number_of_doors",
            "type": "string",
            "description": "车门数可以是两门，三门，四门，五门或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "number_of_compartments",
            "type": "string",
            "description": "车辆厢数可以是两厢，三厢或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }, {
            "name": "vehicle_brand_name",
            "type": "string",
            "description": "品牌名称可以是奔驰，宝马，奥迪，日产，丰田，本田，福特，凯迪拉克，别克，标志，"
                           "雪铁龙或不限，可以多选，多选的话用英文逗号分隔",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_buy_car()
    }

]
TOOL_DESC_BUY_CAR = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_BUY_CAR = """Extracting information as best you can,提取即可，不需要解释太多.. You have access to the following tool:

{tool_descs}

Use the following format,每种key(Question,Thought,Extracted_Json)最多只出现一次，不要重复输出，不要编例子:

Question: the input information you must extract
Thought: you should always think about what to do，尽可能简短
Extracted_Json: the extracting information with json formatted，只回复本次提取的信息即可，不用把历史说的消息也加上

Begin!

Question: {query}"""