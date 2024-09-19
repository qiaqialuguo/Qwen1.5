from rag_classification.api_tools.tool_search_web import tool_wrapper_for_qwen_search_web

TOOL_SEARCH_WEB = [
    {
        'name_for_human':
            'search_web',
        'name_for_model':
            'search_web',
        'description_for_model': "这个工具用来查询搜索引擎，你需要对搜索引擎返回的结果进行整理.",
        'parameters': [{
            "name": "query",
            "type": "string",
            "description": "name",
            'required': False
        }],
        'tool_api': tool_wrapper_for_qwen_search_web()
    }

]
TOOL_DESC_SEARCH_WEB = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model}. Parameters: {parameters} Format the arguments as a JSON object."""

REACT_PROMPT_SEARCH_WEB = """Answer the following questions as best you can. You have access to the following tool:

{tool_descs}

Use the following format:

User: the input question you must answer
FeedbackToUsers: the final answer to the original input question,一定要有这个字段
Thought: you should always think about what to do，尽可能简短

Begin!

api返回的结果是:_api_output_

User: {query}"""