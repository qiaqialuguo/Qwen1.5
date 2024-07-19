import json
import re

import requests
from logging_xianyi.logging_xianyi import logging_xianyi


def tool_wrapper_for_qwen_appointment():
    def tool_(query, already_known_user, user_id, session_id, original_question=None):
        try:
            query = json.loads(re.search(r'\{.*?}', query, re.DOTALL).group(0))
        except:
            query = {}
        for key, value in query.items():
            if '' != value and value and not any(substring in value for substring in ('未指定', '未知')):
                already_known_user['the_car_appointment'][key] = value
        query = already_known_user['the_car_appointment']
        print('调用工具时的query:'+str(query))
        logging_xianyi.debug(query, user_id)
        if 'appointment_time' not in query:
            missing_keys = [key for key in ['appointment_time'] if key not in query]
            already_list = [(key, value) for key, value in already_known_user['the_car_appointment'].items()]
            mapping_dict = {}
            mapping_dict['appointment_time'] = '预约时间'
            mapping_dict['vehicle_maintenance_type'] = '车辆维护类型'
            mapping_dict['automobile_sales_service_shop_name'] = '4s店名称'
            mapping_dict['automobile_sales_service_shop_address'] = '4s店地址'
            missing_keys = [mapping_dict[item] if item in mapping_dict else item for item in missing_keys]
            return f"用户正在预约，需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user
        query['userId'] = user_id
        query['sessionId'] = session_id
        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/appointment/toStore', json=query, timeout=60)
        already_known_user['scene'] = ''
        # 处理响应
        if response.status_code == 200:
            already_known_user['the_car_appointment'] = {}
            # #     请求成功
            # data = response.json()  # 获取响应数据，如果是 JSON 格式
            # column = data['column']
            # if '' == column:
            #     already_known_user['the_car_appointment'] = {}
            #     return data['result'], already_known_user
            # else:
            #     already_known_user['the_car_appointment'].pop(column)
            #     return data['result'], already_known_user
            return '_[DONE]_',already_known_user

        else:
            # 请求失败
            # already_known_user['the_car_appointment'] = {}
            return '抱歉，记录失败', already_known_user

    return tool_