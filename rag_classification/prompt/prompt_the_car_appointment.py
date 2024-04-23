from rag.rag_handler import tool_wrapper_for_qwen_appointment

TOOL_THE_CAR_APPOINTMENT = [
    {
        'name_for_human':
            'the_car_appointment',
        'name_for_model':
            'the_car_appointment',
        'description_for_model':
            "从用户说的话中抽取用户的预约信息，预约信息包括预约时间（appointment_time），车辆维护类型"
            "（vehicle_maintenance_type），车辆品牌名称（vehicle_brand_name），"
            "4s店名称（automobile_sales_service_shop_name），"
            "4s店地址（automobile_sales_service_shop_address），用户想要预约时调用这个工具。",
        'parameters': [{
            "name": "appointment_time",
            "type": "string",
            "description": "time（What day and what time）",
            'required': True
        }, {
            "name": "vehicle_maintenance_type",
            "type": "string",
            "description": "保养或维修二选一",
            'required': True
        }, {
            "name": "vehicle_brand_name",
            "type": "string",
            "description": "车辆品牌名称",
            'required': True
        }, {
            "name": "automobile_sales_service_shop_name",
            "type": "string",
            "description": "4s店名称",
            'required': True
        }, {
            "name": "automobile_sales_service_shop_address",
            "type": "string",
            "description": "4s店地址",
            'required': True
        }, ],
        'tool_api': tool_wrapper_for_qwen_appointment()
    }

]
TOOL_DESC_THE_CAR_APPOINTMENT = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} 目前已知用户的描述是:{already_known}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_THE_CAR_APPOINTMENT = """Answer the following questions as best you can. You have access to the following tool:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: buy_car
Action Input: the input to the action with json formatted
Observation: the result of the action
... (this Thought/Action/Action Input/Observation must repeat only once)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {query}"""