REACT_PROMPT_NO_SCENE = """Answer the following questions as best you can.

Use the following format:

User: the input question you must answer
FeedbackToUsers: the final answer to the original input question，回答简短一些,一定要有这个字段
Thought: I now know the final answer，尽可能简短

Begin!

User: {query}"""