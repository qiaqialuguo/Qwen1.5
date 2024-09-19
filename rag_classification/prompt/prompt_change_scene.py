TOOLS_CHANGE_SCENE = [
    {
        'name_for_human':
            'name',
        'name_for_model':
            'name',
        'description_for_model': "返回AI助手的名字. 当用户问到你是谁或者你是谁开发的，或者你是不是谁时，进入这个场景，只问名字时不用说是谁开发的，根据用户是问的中英文来选择是中文还是英文回答，你是优必爱AI智能体-BAVA",
    },
    {
        'name_for_human':
            'buy_car',
        'name_for_model':
            'buy_car',
        'description_for_model': "这是一个给用户推荐车的场景。当用户想买车或者想要被推荐车的时候进入这个场景。"
    },
    {
        'name_for_human':
            'used_car_valuation',
        'name_for_model':
            'used_car_valuation',
        'description_for_model': "这是一个给二手车估值的场景。当用户想对车辆进行估值或卖车的时候进入这个场景。"
    },
    {
        'name_for_human':
            'the_car_appointment',
        'name_for_model':
            'the_car_appointment',
        'description_for_model':
            "用户想要预约车辆服务时进入这个场景，特别是在用户查询完自己车的公里数后，会引导用户是否预约，可以结合上下文判断用户是否要预约。",
    },
    {
        'name_for_human':
            'vehicle_issues',
        'name_for_model':
            'vehicle_issues',
        'description_for_model': "当用户问汽车功能，汽车故障等任何汽车相关的问题时，包括车辆对比时，进入这个场景",
    },{
        'name_for_human':
            'check_mileage',
        'name_for_model':
            'check_mileage',
        'description_for_model': "当用户问自己的车的里程数时，比如：'我的车行驶了多少公里'，进入这个场景",
    },{
        'name_for_human':
            'what_scenes',
        'name_for_model':
            'what_scenes',
        'description_for_model': "这个工具用来返回你能做什么.",
    },
    {
        'name_for_human':
            'search_web',
        'name_for_model':
            'search_web',
        'description_for_model': "当不是其他的场景或问题，并且你不知道答案时，进入这个场景,比如天气问题，时间问题，生活问题等等",
    },
    {
        'name_for_human':
            'no_scene',
        'name_for_model':
            'no_scene',
        'description_for_model': "当没有其他合适的场景,并且你知道答案时，进入这个场景,问候也属于这个场景，当用户问 你好 时需要切换到这个场景",
    }

]
TOOL_DESC_CHANGE_SCENE = """{name_for_model}: Entering this scene with the {name_for_human} API. What is the {name_for_human} scene useful for? {description_for_model}."""

REACT_PROMPT_CHANGE_SCENE = """你现在要根据上下文对用户的问题进行判断，判断用户是否想切换场景，现在处于的场景是{now_scene}，可供切换的场景类别有:

{tool_descs}

Use the following format，不用解释太多，输出切换到了什么场景即可:

User: the input question you must determine whether to switch scenes or not
Now_Scene:{now_scene}
New_Scene: the new scene to switch, should be one of [{tool_names}]
Thought: you should always think about what to do，尽可能简短

Begin!

User: {query}
Now_Scene:{now_scene}"""