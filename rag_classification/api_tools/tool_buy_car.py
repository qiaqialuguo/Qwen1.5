import json
import re

import requests
from logging_xianyi.logging_xianyi import logging_xianyi


def tool_wrapper_for_qwen_buy_car():
    def tool_(query, already_known_user, user_id, session_id, original_question=None):
        # try:
        #     query = json.loads(re.search(r'\{.*?}', query, re.DOTALL).group(0))
        # except:
        #     query = {}
        if query == '':
            query = {}
        for key, value in query.items():
            # 模型抽取校验
            if (isinstance(value, (str, int, float)) and
                    (str(value) != '') and
                    (str(value) and not any(substring in str(value) for substring in ('未指定', '未知', '无具体说明')))):
                already_known_user['buy_car'][key] = value
        query = already_known_user['buy_car']
        print('调用工具时的query:' + str(query))
        logging_xianyi.debug(query, user_id)
        if not query:
            return "没有提取出有效信息，继续跟用户聊聊问一下其他信息", already_known_user
        if 'vehicle_labels' in query:
            # 原始字符串
            source_str = query['vehicle_labels']
            reference_str = '内饰好,外观好,性价比高,空间大,驾驶感受好'
            # 将字符串分割为列表
            source_list = source_str.split(',')
            reference_list = reference_str.split(',')
            # 保留在参考列表中的内容
            filtered_list = [item for item in source_list if item in reference_list]
            # 将保留的内容拼接回字符串
            query['vehicle_labels'] = ','.join(filtered_list)
        # if 'price' not in query or 'vehicle_classification' not in query or 'energy_type' not in query:
        #     missing_keys = [key for key in ['price', 'vehicle_classification', 'energy_type'] if key not in query]
        #     already_list = [(key, value) for key, value in already_known_user['buy_car'].items()]
        #     mapping_dict = {}
        #     mapping_dict['price'] = '价位'
        #     mapping_dict['vehicle_classification'] = '车型分类'
        #     mapping_dict['energy_type'] = '能源形式'
        #     mapping_dict['brand_type'] = '品牌类型'
        #     mapping_dict['vehicle_size'] = '车型级别'
        #     mapping_dict['number_of_seats'] = '座位数'
        #     mapping_dict['number_of_doors'] = '车门数'
        #     mapping_dict['number_of_compartments'] = '车辆厢数'
        #     missing_keys = [mapping_dict[item] if item in mapping_dict else item for item in missing_keys]
        #     return f"正在给用户推荐车，需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user
        already_known_user['buy_car'] = {}
        query['userId'] = user_id
        query['sessionId'] = session_id
        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/newCarSuggest/newCarRecommendation',
                                 json=query, timeout=60)
        already_known_user['scene'] = ''
        # 处理响应
        if response.status_code == 200:
            # 请求成功
            # data = response.json()  # 获取响应数据，如果是 JSON 格式
            # return str(data), already_known_user
            return '_[DONE]_', already_known_user
        else:
            # 请求失败
            return '查询失败，请检查', already_known_user

    return tool_
