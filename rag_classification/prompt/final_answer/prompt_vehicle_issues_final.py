from rag_classification.api_tools.tool_vehicle_issues import tool_wrapper_for_qwen_vehicle_issues

TOOL_VEHICLE_ISSUES_FINAL = [
    {
        'name_for_human':
            'vehicle_issues',
        'name_for_model':
            'vehicle_issues',
        'description_for_model': "这个工具来提取用户问题中的车辆信息，如果问题中没有提到车辆信息，"
                                 "has_vehicle_information为False，提到了车辆信息则为True，"
                                 "并在JSON中记录用户说的车辆信息.",
        'parameters': [{
            "name": "has_vehicle_information",
            "type": "boolean",
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

REACT_PROMPT_VEHICLE_ISSUES_FINAL = """Extracting information as best you can. You have access to the following tool:

{tool_descs}

Use the following format:

Question: the input question you must extract
Thought: you should always think about what to do
Extracted_Json: the extracting information with json formatted

Begin!

Question: {query}"""