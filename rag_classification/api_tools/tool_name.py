import json


def tool_wrapper_for_qwen_name():
    def tool_(query, already_known_user, user_id):
        # query = json.loads(query)["query"]
        #  场景复原
        already_known_user['scene'] = ''
        return '你是优必爱的AI智能体BAVA，你是ubiai开发的', already_known_user

    return tool_