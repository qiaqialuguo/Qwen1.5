from rag_classification.api_tools.tool_vehicle_issues import tool_wrapper_for_qwen_vehicle_issues

TOOL_VEHICLE_ISSUES = [
    {
        'name_for_human':
            'vehicle_issues',
        'name_for_model':
            'vehicle_issues',
        'description_for_model': "这个工具来提取问题中的品牌名称,车系名称,车辆年款，如果问题中没有提到品牌名称,车系名称,车辆年款，"
                                 "has_vehicle_information为No，提到了品牌名称,车系名称,车辆年款中任何一个则为Yes，"
                                 "并在JSON中记录用户说的车辆信息.",
        'parameters': [{
            "name": "has_vehicle_information",
            "type": "string",
            "description": "Yes or No",
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
TOOL_DESC_VEHICLE_ISSUES = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_VEHICLE_ISSUES = """Extracting information as best you can,提取即可，不需要解释太多.. You have access to the following tool:

{tool_descs}

Use the following format:

Question: the input question you must extract
Thought: you should always think about what to do，尽可能简短
Extracted_Json: the extracting information with json formatted

Begin!

Question: {query}"""