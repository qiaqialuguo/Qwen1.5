import json

import requests
from logging_xianyi.logging_xianyi import logging_xianyi

def tool_wrapper_for_qwen_vehicle_issues():
    def tool_(query, already_known_user, user_id, original_question=None):
        try:
            query = json.loads(query)
        except:
            query = {}
            # raise Exception("vehicle_issues模型抽取后不是JSON：" + query)
        query_tmp = {}
        for key, value in query.items():
            # 模型抽取校验
            if '' != value:
                query_tmp[key] = value
        # if not query_tmp:
        query_tmp['question'] = original_question
        query_tmp['userId'] = user_id
        # 如果用户说了车型信息，需要补充全
        # else:
        #     if ('vehicle_brand_name' not in query_tmp or 'vehicle_series' not in query_tmp
        #             or 'vehicle_model_year' not in query_tmp):
        #         missing_keys = [key for key in
        #                         ['vehicle_brand_name', 'vehicle_series', 'vehicle_model_year'] if key not in query_tmp]
        #         already_list = [(key, value) for key, value in already_known_user['used_car_valuation'].items()]
        #         mapping_dict = {}
        #         mapping_dict['vehicle_brand_name'] = '车辆品牌名称'
        #         mapping_dict['vehicle_series'] = '车系'
        #         mapping_dict['vehicle_model_year'] = '车辆年款'
        #         missing_keys = [mapping_dict[item] if item in mapping_dict else item for item in missing_keys]
        #         # already_list = [mapping_dict[item] if item in mapping_dict else item for item in already_list]
        #         return f"需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user

        query = query_tmp
        print(query)
        logging_xianyi.debug(query, user_id)
        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/knowledge/question',
                                 json=query, timeout=30)
        # 处理响应
        if response.status_code == 200:
            # 请求成功
            data = response.json()  # 获取响应数据，如果是 JSON 格式
            if 'success' == data['status']:
                already_known_user['scene'] = ''
                return str(data['data']), already_known_user
            # 需要继续问用户缺少什么
            else:
                return f"需要继续询问用户{' 和 '.join(['车辆品牌名称', '车系', '车辆年款'])}", already_known_user
        else:
            # 请求失败
            return '查询失败，请检查', already_known_user

    return tool_
