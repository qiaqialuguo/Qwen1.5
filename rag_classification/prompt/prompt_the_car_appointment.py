from rag_classification.api_tools.tool_the_car_appointment import tool_wrapper_for_qwen_appointment

TOOL_THE_CAR_APPOINTMENT = [
    {
        'name_for_human':
            'the_car_appointment',
        'name_for_model':
            'the_car_appointment',
        'description_for_model':
            "从用户说的话中抽取用户的预约信息，基于已知信息构建JSON，用户没说信息就给空json，现在时间是{time}，预约信息包括预约时间（appointment_time），车辆维护类型"
            "（vehicle_maintenance_type），"
            "4s店名称（automobile_sales_service_shop_name），"
            "4s店地址（automobile_sales_service_shop_address），用户想要预约时调用这个工具。",
        'parameters': [{
            "name": "appointment_time",
            "type": "string",
            "description": "预约时间，请返回用户说的原样的时间，比如明天，下周三等",
            'required': True
        }, {
            "name": "vehicle_maintenance_type",
            "type": "string",
            "description": "保养或维修二选一",
            'required': False
        }, {
            "name": "automobile_sales_service_shop_name",
            "type": "string",
            "description": "4s店名称",
            'required': False
        }, {
            "name": "automobile_sales_service_shop_address",
            "type": "string",
            "description": "4s店地址,地址包括最近的、附近的等等",
            'required': False
        }, ],
        'tool_api': tool_wrapper_for_qwen_appointment()
    }

]
TOOL_DESC_THE_CAR_APPOINTMENT = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_THE_CAR_APPOINTMENT = """Extracting information as best you can,提取即可，不需要解释太多. You have access to the following tool:

{tool_descs}

Use the following format,每种key(Question,Thought,Extracted_Json)最多只出现一次，不要重复输出，不要编例子:

User: the input information you must extract
Thought: you should always think about what to do，尽可能简短
Extracted_Json: the extracting information with json formatted，只回复本次提取的信息即可，不用把历史说的消息也加上

Begin!

User: {query}"""