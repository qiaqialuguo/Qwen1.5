import json

import requests

url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'  # 替换为你的实际URL
header = {'Authorization': 'Bearer sk-777003151b354aa6889b598f9ff666b4', 'Content-Type': 'application/json',
          'X-DashScope-SSE': 'enable'}
response = requests.post(url, json=json.loads("""{
  "model": "qwen2-72b-instruct",
  "input":{
        "messages":[      
            {
                "role": "user",
                "content": "你是谁"
            }
        ]
    }
}"""), headers=header)
buffer = ""
for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        if decoded_line.startswith("data:"):
            buffer += decoded_line[5:]  # 移除 "data: " 前缀
            print(decoded_line[5:])
