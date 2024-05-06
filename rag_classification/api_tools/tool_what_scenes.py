import json


def tool_wrapper_for_qwen_what_scenes():
    def tool_(query, already_known_user, user_id, original_question=None):
        # query = json.loads(query)["query"]
        #  场景复原
        already_known_user['scene'] = ''
        return '你可以给用户推荐车、评估二手车价格、预约到4s店维修或保养、解答汽车相关的问题等', already_known_user

    return tool_