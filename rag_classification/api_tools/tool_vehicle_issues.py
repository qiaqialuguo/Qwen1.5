import json


def tool_wrapper_for_qwen_vehicle_issues():
    def tool_(query, already_known_user, user_id):
        query = json.loads(query)["query"]
        return '请咨询优必爱客服', already_known_user

    return tool_