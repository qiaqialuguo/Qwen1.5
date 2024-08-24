from rag_classification.api_tools.tool_vehicle_issues import tool_wrapper_for_qwen_vehicle_issues

TOOL_VEHICLE_ISSUES_FINAL = [
    {
        'name_for_human':
            'vehicle_issues',
        'name_for_model':
            'vehicle_issues',
        'description_for_model': "回答用户汽车功能，汽车故障等任何汽车相关的问题时，用这个工具，"
                                 "用户说车辆信息时也提取车辆信息.",
        'parameters': [{
            "name": "has_vehicle_information",
            "type": "string",
            "description": "True or False",
            'required': True
        },{
            "name": "vehicle_brand_name",
            "type": "string",
            "description": "品牌名称，只能有一个值",
            'required': False
        }, {
            "name": "vehicle_series",
            "type": "string",
            "description": "车系名称可以是X3，i3,X5等任何车系，只能有一个值",
            'required': False
        }, {
            "name": "vehicle_model_year",
            "type": "string",
            "description": "车辆年款可以是2023款，2019款，2008款等，只能有一个值",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_vehicle_issues()
    }

]
TOOL_DESC_VEHICLE_ISSUES_FINAL = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_VEHICLE_ISSUES_FINAL = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

User: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action with json formatted
Monitoring: the result of the action
... (this Thought/Action/Action Input/Monitoring can be repeated only once)
Thought: 我需要将Monitoring的内容返回给用户
FeedbackToUsers: the final answer to the original input question,一定要有这个字段

Begin!

User: {query}
Thought:我将调用vehicle_issues工具来获取问题答案
Action: vehicle_issues
Action Input:{Extracted_Json}
Monitoring:{api_output}
"""