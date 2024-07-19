import json

import requests


def tool_wrapper_for_qwen_check_mileage():
    def tool_(query, already_known_user, user_id, session_id, original_question=None):
        # query = json.loads(query)["query"]
        #  场景复原
        already_known_user['scene'] = ''
        query = {'userId': user_id, 'sessionId': session_id}
        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/tesla/getMaintainInfo',
                                 timeout=60, json=query)
        # 处理响应
        if response.status_code == 200:
            # 请求成功
            data = response.json()  # 获取响应数据，如果是 JSON 格式
            print(data)
            if data['status'] == 'success':
                return str(data['data']), already_known_user
            else:
                return str(data['message']), already_known_user
        else:
            # 请求失败
            return '查询失败，请检查', already_known_user
        # return '行驶了10万公里，建议保养，请问您需要保养吗？', already_known_user

    return tool_
