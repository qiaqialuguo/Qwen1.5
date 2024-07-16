from rag_classification.api_tools.tool_the_car_appointment import tool_wrapper_for_qwen_appointment

TOOL_THE_CAR_APPOINTMENT_FINAL = [
    {
        'name_for_human':
            'the_car_appointment',
        'name_for_model':
            'the_car_appointment',
        'description_for_model':
            "用户预约车辆服务时使用这个工具，预约信息包括预约时间（appointment_time），车辆维护类型"
            "（vehicle_maintenance_type），"
            "4s店名称（automobile_sales_service_shop_name），"
            "4s店地址（automobile_sales_service_shop_address），用户想要预约时调用这个工具。其中预约时间是必填",
        'parameters': [{
            "name": "appointment_time",
            "type": "string",
            "description": "预约时间",
            'required': True
        }, {
            "name": "vehicle_maintenance_type",
            "type": "string",
            "description": "保养或维修二选一",
            'required': False
        },  {
            "name": "automobile_sales_service_shop_name",
            "type": "string",
            "description": "4s店名称",
            'required': False
        }, {
            "name": "automobile_sales_service_shop_address",
            "type": "string",
            "description": "4s店地址",
            'required': False
        }, ],
        'tool_api': tool_wrapper_for_qwen_appointment()
    }

]
TOOL_DESC_THE_CAR_APPOINTMENT_FINAL = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_THE_CAR_APPOINTMENT_FINAL = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action with json formatted
Monitoring: the result of the action
... (this Thought/Action/Action Input/Monitoring can be repeated only once)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {query}
Thought:我将调用the_car_appointment工具来尝试预约
Action: the_car_appointment
Action Input:{Extracted_Json}
Monitoring:{api_output}
"""