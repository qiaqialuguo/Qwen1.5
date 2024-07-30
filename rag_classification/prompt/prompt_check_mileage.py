from rag_classification.api_tools.tool_check_mileage import tool_wrapper_for_qwen_check_mileage

TOOL_CHECK_MILEAGE = [
    {
        'name_for_human':
            'check_mileage',
        'name_for_model':
            'check_mileage',
        'description_for_model': "用这个工具查询用户的里程数，并把工具查询到的那段话直接输出给用户,是问句的话也直接问用户.",
        'parameters': [{
            "name": "query",
            "type": "string",
            "description": "用户说的话",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_check_mileage()
    }

]
TOOL_DESC_CHECK_MILEAGE = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_CHECK_MILEAGE = """Answer the following questions as best you can. You have access to the following tool:

{tool_descs}

Use the following format:

User: the input question you must answer
Thought: you should always think about what to do，尽可能简短
Action: check_mileage
Action Input: the input to the action with json formatted
Monitoring: the result of the action
... (this Thought/Action/Action Input/Monitoring must repeat only once)
Thought: I now know the final answer
FeedbackToUser: the final answer to the original input question

Begin!

api返回的结果是:_api_output_

User: {query}"""