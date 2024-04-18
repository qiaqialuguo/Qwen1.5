import requests

query = {'price': '20万左右', 'energy_type': '混合动力', 'vehicle_classification': '轿车'}

response = requests.post(f'http://192.168.110.29:12581/auto-ai-agent/business/newCarRecommendation',json=query)
if response.status_code == 200:
    # 请求成功
    data = response.json()  # 获取响应数据，如果是 JSON 格式
    print(str(data))
else:
    # 请求失败
    print('查询失败，请检查')