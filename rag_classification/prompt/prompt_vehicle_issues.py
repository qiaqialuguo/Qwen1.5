from rag_classification.api_tools.tool_vehicle_issues import tool_wrapper_for_qwen_vehicle_issues

TOOL_VEHICLE_ISSUES = [
    {
        'name_for_human':
            'vehicle_issues',
        'name_for_model':
            'vehicle_issues',
        'description_for_model': "这个工具来获取汽车功能，汽车故障相关的问题的答案.",
        'parameters': [{
            "name": "question",
            "type": "string",
            "description": "user's question",
            'required': True
        }],
        'tool_api': tool_wrapper_for_qwen_vehicle_issues()
    }

]
TOOL_DESC_VEHICLE_ISSUES = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_VEHICLE_ISSUES = """Answer the following questions as best you can. You have access to the following tool:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: vehicle_issues
Action Input: the input to the action with json formatted

Begin!

调用了vehicle_issues API，api返回的结果是:_api_output_

Question: {query}"""