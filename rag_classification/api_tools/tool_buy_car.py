import json

import requests


def tool_wrapper_for_qwen_buy_car():
    def tool_(query, already_known_user, user_id, original_question=None):
        try:
            query = json.loads(query)
        except :
            query = {}
        for key, value in query.items():
            # 模型抽取校验
            if '' != value:
                already_known_user['buy_car'][key] = value
        query = already_known_user['buy_car']
        print(query)
        if 'price' not in query or 'vehicle_classification' not in query or 'energy_type' not in query:
            missing_keys = [key for key in ['price', 'vehicle_classification', 'energy_type'] if key not in query]
            already_list = [(key, value) for key, value in already_known_user['buy_car'].items()]
            mapping_dict = {}
            mapping_dict['price'] = '价位'
            mapping_dict['vehicle_classification'] = '车型分类'
            mapping_dict['energy_type'] = '能源形式'
            mapping_dict['brand_type'] = '品牌类型'
            mapping_dict['vehicle_size'] = '车型级别'
            mapping_dict['number_of_seats'] = '座位数'
            mapping_dict['number_of_doors'] = '车门数'
            mapping_dict['number_of_compartments'] = '车辆厢数'
            mapping_dict['vehicle_brand_name'] = '车辆品牌名称'
            missing_keys = [mapping_dict[item] if item in mapping_dict else item for item in missing_keys]
            return f"正在给用户推荐车，需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user
        already_known_user['buy_car'] = {}

        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/business/newCarRecommendation',json=query)
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