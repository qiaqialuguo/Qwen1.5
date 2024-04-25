import json

import requests


def tool_wrapper_for_qwen_vehicle_issues():
    def tool_(query, already_known_user, user_id):
        # query = json.loads(query)
        query = {'question': query}
        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/knowledge/question',
                                 json=query)
        already_known_user['scene'] = ''
        # 处理响应
        if response.status_code == 200:
            # 请求成功
            # data = response.json()  # 获取响应数据，如果是 JSON 格式
            return str(response.text), already_known_user
        else:
            # 请求失败
            return '查询失败，请检查', already_known_user

    return tool_
