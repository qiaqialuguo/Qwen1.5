TOOLS = [
    {
        'name_for_human':
            'name',
        'name_for_model':
            'name',
        'description_for_model': "返回AI助手的名字. 当用户问到你是谁或者你是谁开发的，或者你是不是谁时，进入这个场景，只问名字时不用说是谁开发的，根据用户是问的中英文来选择是中文还是英文回答，你是优必爱AI智能体",
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
        'description_for_model': "这是一个给二手车估值的场景。当用户想对车辆进行估值或卖车或者问车辆价格的时候进入这个场景。"
    },
    {
        'name_for_human':
            'the_car_appointment',
        'name_for_model':
            'the_car_appointment',
        'description_for_model':
            "用户想要预约车辆服务时进入这个场景，特别是在用户查询完自己车的公里数后,会引导用户是否预约，引导格式是：截止目前，您的车辆累计行驶xxxxkm，根据官方推荐，建议完成xxxx项目，请问是否需要我为您预约到店保养？当用户Question是 需要 、 是 时，要进入到预约场景。",
    },
    {
        'name_for_human':
            'vehicle_issues',
        'name_for_model':
            'vehicle_issues',
        'description_for_model': "当用户问汽车功能，汽车故障等任何汽车相关的问题时，包括车辆对比，问汽车值不值得买时，进入这个场景",
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
        'description_for_model': "当没有其他合适的场景,并且你知道答案时，进入这个场景",
    }

]
TOOL_DESC = """{name_for_model}: Entering this scene with the {name_for_human} API. What is the {name_for_human} scene useful for? {description_for_model}."""

REACT_PROMPT = """你现在要对用户的问题进行分类，只分类即可，不用解释，不用回答问题，可供选择的场景类别有:

{tool_descs}

Use the following format:

User: the input question you must classify
Scene: the scene to enter, should be one of [{tool_names}]
Thought: you should always think about what to do，尽可能简短

Begin!

User: {query}"""