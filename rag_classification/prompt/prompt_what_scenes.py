from rag_classification.api_tools.tool_name import tool_wrapper_for_qwen_name
from rag_classification.api_tools.tool_what_scenes import tool_wrapper_for_qwen_what_scenes

TOOL_WHAT_SCENES = [
    {
        'name_for_human':
            'what_scenes',
        'name_for_model':
            'what_scenes',
        'description_for_model': "这个工具用来返回你能做什么.",
        'parameters': [{
            "name": "query",
            "type": "string",
            "description": "what_scenes",
            'required': True
        }],
        'tool_api': tool_wrapper_for_qwen_what_scenes()
    }

]
TOOL_DESC_WHAT_SCENES = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_WHAT_SCENES = """Answer the following questions as best you can. You have access to the following tool:

{tool_descs}

Use the following format:

User: the input question you must answer
FeedbackToUsers: the final answer to the original input question,一定要有这个字段
Thought: you should always think about what to do，尽可能简短

Begin!

api返回的结果是:_api_output_

User: {query}"""