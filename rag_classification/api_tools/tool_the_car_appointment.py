import json

import requests


def tool_wrapper_for_qwen_appointment():
    def tool_(query, already_known_user, user_id):
        try:
            query = json.loads(query)
        except:
            query = {}
        for key, value in query.items():
            if '' != value:
                already_known_user['the_car_appointment'][key] = value
        query = already_known_user['the_car_appointment']
        print(query)
        if 'appointment_time' not in query:
            missing_keys = [key for key in ['appointment_time'] if key not in query]
            already_list = [(key, value) for key, value in already_known_user['the_car_appointment'].items()]
            return f"已知{already_list}，需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user

        query['userId'] = user_id
        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/appointment/toStore', json=query)
        # 处理响应
        if response.status_code == 200:
            #     请求成功
            data = response.json()  # 获取响应数据，如果是 JSON 格式
            column = data['column']
            if '' == column:
                already_known_user['the_car_appointment'] = {}
                return data['result'], already_known_user
            else:
                already_known_user['the_car_appointment'].pop(column)
                return data['result'], already_known_user

        else:
            # 请求失败
            already_known_user['the_car_appointment'] = {}
            return '抱歉，记录失败', already_known_user

    return tool_