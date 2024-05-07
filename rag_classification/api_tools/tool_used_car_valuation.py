import json

import requests


def tool_wrapper_for_qwen_used_car_valuation():
    def tool_(query, already_known_user, user_id, original_question=None):
        try:
            query = json.loads(query)
        except:
            query = {}
        for key, value in query.items():
            if '' != value:
                already_known_user['used_car_valuation'][key] = value
        query = already_known_user['used_car_valuation']
        print(query)
        if ('vehicle_brand_name' not in query or 'vehicle_series' not in query
                or 'vehicle_model_year' not in query or 'vehicle_mileage' not in query
                or 'vehicle_licensing_year' not in query):
            missing_keys = [key for key in ['vehicle_brand_name', 'vehicle_series', 'vehicle_model_year','vehicle_mileage','vehicle_licensing_year'] if key not in query]
            already_list = [(key, value) for key, value in already_known_user['used_car_valuation'].items()]
            mapping_dict = {}
            mapping_dict['vehicle_brand_name'] = '车辆品牌名称'
            mapping_dict['vehicle_series'] = '车系'
            mapping_dict['vehicle_model_year'] = '车辆年款'
            mapping_dict['vehicle_licensing_year'] = '车辆上牌时年份'
            mapping_dict['vehicle_licensing_month'] = '车辆上牌时月份'
            mapping_dict['vehicle_licensing_city'] = '车辆上牌地所在城市'
            mapping_dict['vehicle_mileage'] = '车辆里程数'
            mapping_dict['vehicle_exterior_color'] = '车身颜色'
            missing_keys = [mapping_dict[item] if item in mapping_dict else item for item in missing_keys]
            # already_list = [mapping_dict[item] if item in mapping_dict else item for item in already_list]
            return f"正在给车辆估值，需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user
        already_known_user['used_car_valuation'] = {}

        query['userId'] = user_id
        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/business/usedCarValuation',json=query)
        already_known_user['scene'] = ''
        # 处理响应
        if response.status_code == 200:
            # 请求成功
            data = response.json()  # 获取响应数据，如果是 JSON 格式
            return str(data), already_known_user
        else:
            # 请求失败
            return '查询失败，请检查', already_known_user
    return tool_