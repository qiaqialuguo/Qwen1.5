import json
import re

import requests
from logging_xianyi.logging_xianyi import logging_xianyi


def tool_wrapper_for_qwen_used_car_valuation():
    def tool_(query, already_known_user, user_id, session_id, original_question=None):
        # try:
        #     query = json.loads(re.search(r'\{.*?}', query, re.DOTALL).group(0))
        # except:
        #     query = {}
        if query == '':
            query = {}
        field_dict = {}
        field_dict['brand'] = 'vehicle_brand_name'
        field_dict['series'] = 'vehicle_series'
        field_dict['modelYear'] = 'vehicle_model_year'
        field_dict['licensingYear'] = 'vehicle_licensing_year'
        field_dict['licensingMonth'] = 'vehicle_licensing_month'
        field_dict['city'] = 'vehicle_licensing_city'
        field_dict['mileage'] = 'vehicle_mileage'
        field_dict['condition'] = 'vehicle_condition'
        field_dict['color'] = 'vehicle_exterior_color'
        query = {field_dict.get(k, k): v for k, v in query.items()}
        # 换车的话清空之前的条件
        if ('vehicle_brand_name' in query or 'vehicle_series' in query):
            already_known_user['used_car_valuation'] = {}
        for key, value in query.items():
            if (isinstance(value, (str, int, float)) and
                    (str(value) != '') and
                    (str(value) and not any(substring in str(value) for substring in ('未指定', '未知')))):
                already_known_user['used_car_valuation'][key] = value
        query = already_known_user['used_car_valuation']
        print('调用工具时的query:' + str(query))
        logging_xianyi.debug(query, user_id)
        mapping_dict = {}
        if ('vehicle_brand_name' not in query or 'vehicle_series' not in query):
            missing_keys = [key for key in ['vehicle_brand_name', 'vehicle_series', ] if key not in query]
            already_list = [(key, value) for key, value in already_known_user['used_car_valuation'].items()]
            mapping_dict['vehicle_brand_name'] = '车辆品牌名称'
            mapping_dict['vehicle_series'] = '车系'
            mapping_dict['vehicle_model_year'] = '车辆年款'
            mapping_dict['vehicle_licensing_year'] = '车辆上牌时年份'
            mapping_dict['vehicle_licensing_month'] = '车辆上牌时月份'
            mapping_dict['vehicle_licensing_city'] = '车辆上牌地所在城市'
            mapping_dict['vehicle_mileage'] = '车辆里程数'
            mapping_dict['vehicle_condition'] = '车况'
            mapping_dict['vehicle_exterior_color'] = '车身颜色'
            missing_keys = [mapping_dict[item] if item in mapping_dict else item for item in missing_keys]
            # already_list = [mapping_dict[item] if item in mapping_dict else item for item in already_list]
            return f"正在给车辆估值，需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user
        # already_known_user['used_car_valuation'] = {}

        query['userId'] = user_id
        query['sessionId'] = session_id
        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/usedCarSuggest/usedCarValuation',
                                 json=query, timeout=60)
        # already_known_user['scene'] = ''
        # 处理响应
        if response.status_code == 200:
            # # 请求成功
            data = response.json()  # 获取响应数据，如果是 JSON 格式
            if 'success' == data['status']:
                return '_[DONE]_', already_known_user
            else:
                # 请求失败
                data = response.json()  # 获取响应数据，如果是 JSON 格式
                del already_known_user['used_car_valuation'][data['message']]
                missing_keys = [key for key in ['vehicle_brand_name', 'vehicle_series', ] if key not in already_known_user['used_car_valuation']]
                missing_keys = [mapping_dict[item] if item in mapping_dict else item for item in missing_keys]
                return f"正在给车辆估值，用户说的{' 和 '.join(missing_keys)}识别错误，让用户重新描述", already_known_user

        else:
            return '返回错误', already_known_user

    return tool_
