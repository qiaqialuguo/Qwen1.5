REACT_PROMPT_NO_SCENE = """Answer the following questions as best you can.用户说问候你时，只回应问候就可以，不要回答之前的问题。

Use the following format:

User: the input question you must answer
FeedbackToUsers: the final answer to the original input question，回答简短一些,一定要有这个字段。用户说问候你时，只回应问候就可以，不要回答之前的问题。
Thought: I now know the final answer，尽可能简短

Begin!

User: {query}"""