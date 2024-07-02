from rag_classification.api_tools.tool_used_car_valuation import tool_wrapper_for_qwen_used_car_valuation

TOOL_USED_CAR_VALUATION_FINAL = [
    {
        'name_for_human':
            'used_car_valuation',
        'name_for_model':
            'used_car_valuation',
        'description_for_model': "这是一个给二手车估值的工具。当用户想对车辆进行估值或卖车的时候调用这个工具，"
                                 "返回的是评估出的车辆的价格，"
                                 "对车的描述包含 车辆品牌名称（vehicle_brand_name），车系（vehicle_series），车型（vehicle_model），"
                                 "车辆上牌时年份（vehicle_licensing_year），车辆上牌时月份（vehicle_licensing_month），"
                                 "车辆上牌地所在城市（vehicle_licensing_city），车辆里程数（vehicle_mileage），"
                                 "车身颜色（vehicle_exterior_color）。",
        'parameters': [{
            "name": "vehicle_brand_name",
            "type": "string",
            "description": "品牌名称，只能有一个值",
            'required': False
        }, {
            "name": "vehicle_series",
            "type": "string",
            "description": "车系名称可以是X3，i3,X5，A6等任何车系，只能有一个值",
            'required': False
        }, {
            "name": "vehicle_model",
            "type": "string",
            "description": "车型，车型比较具体，如2017款 118i 时尚型，2021款 Sportback 35 TFSI 进取致雅型等",
            'required': False
        },{
            "name": "vehicle_licensing_year",
            "type": "string",
            "description": "车辆上牌年份是一个具体年份，比如2016年,2020年,2021年,2023年等，只能有一个值",
            'required': False
        }, {
            "name": "vehicle_licensing_month",
            "type": "string",
            "description": "车辆上牌月份是一个具体月份，比如1月,2月,11月等，只能有一个值",
            'required': False
        }, {
            "name": "vehicle_licensing_city",
            "type": "string",
            "description": "车辆上牌地所在城市是一个城市名，问清楚用户是在哪个城市，只能有一个值",
            'required': False
        }, {
            "name": "vehicle_mileage",
            "type": "string",
            "description": "车辆里程数是车辆行驶了多少公里，比如10000公里，40000公里，单位是公里，只能有一个值",
            'required': False
        }, {
            "name": "vehicle_exterior_color",
            "type": "string",
            "description": "车身颜色是车辆的颜色，只能有一个值",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_used_car_valuation()
    }

]
TOOL_DESC_USED_CAR_VALUATION_FINAL = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_USED_CAR_VALUATION_FINAL = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action with json formatted
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question,在结果中不说是工具调用的，就当是你自己估值的，请你同时给出估值使用的参数值（valuationUsageParameters里的具体value）

Begin!

Question: {query}
Thought:我将调用used_car_valuation工具来对车辆进行估值,在结果中不说是工具调用的，就当是你自己估值的，请你同时给出估值使用的参数值（valuationUsageParameters里的具体value）
Action: used_car_valuation
Action Input:{Extracted_Json}
Observation:{api_output}
"""