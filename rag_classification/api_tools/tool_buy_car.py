import json

import requests


def tool_wrapper_for_qwen_buy_car():
    def tool_(query, already_known_user, user_id):
        query = json.loads(query)
        for key, value in query.items():
            already_known_user['buy_car'][key] = value
        query = already_known_user['buy_car']
        print(query)
        if 'price' not in query or 'vehicle_classification' not in query or 'energy_type' not in query or (
                query['price'] == '不限'
                and query['vehicle_classification'] == '不限'
                and query['energy_type'] == '不限'):
            missing_keys = [key for key in ['price', 'vehicle_classification', 'energy_type'] if key not in query]
            already_list = [(key, value) for key, value in already_known_user['buy_car'].items()]
            return f"已知{already_list}，需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user
        already_known_user['buy_car'] = {}

        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/business/newCarRecommendation',json=query)
        # 处理响应
        if response.status_code == 200:
            # 请求成功
            data = response.json()  # 获取响应数据，如果是 JSON 格式
            return str(data), already_known_user
        else:
            # 请求失败
            return '查询失败，请检查', already_known_user
    return tool_