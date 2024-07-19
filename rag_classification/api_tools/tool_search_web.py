import json

import requests


def tool_wrapper_for_qwen_search_web():
    def tool_(query, already_known_user, user_id, session_id, original_question=None):
        # query = json.loads(query)["query"]
        #  场景复原
        already_known_user['scene'] = ''
        response = requests.get(f'http://192.168.110.147:10005/searcher/api/search?keywords={query}',
                                 timeout=60)
        # 处理响应
        if response.status_code == 200:
            # 请求成功
            data = response.json()  # 获取响应数据，如果是 JSON 格式
            print(data)
            return str(data['data']), already_known_user
        else:
            # 请求失败
            return '查询失败，请检查', already_known_user

    return tool_