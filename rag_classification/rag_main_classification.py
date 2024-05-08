import datetime
import json
import time
from contextlib import asynccontextmanager
from copy import deepcopy

import GPUtil
import requests
import torch
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from transformers import AutoTokenizer, AutoModelForCausalLM

from transformers.generation.logits_process import LogitsProcessorList

from rag_classification import rag_args_classification
from rag_classification.api_tools.tool_name import tool_wrapper_for_qwen_name
from rag_classification.rag_handler_classification import ChatCompletionRequest, ChatCompletionResponse, \
    StopWordsLogitsProcessor, parse_messages, _gc, ChatCompletionResponseChoice, ChatMessage, trim_stop_words
from rag_classification.rag_tools_classification import build_planning_prompt, use_api, build_planning_prompt_final
from logging_xianyi.logging_xianyi import logging_xianyi


@asynccontextmanager
async def lifespan(app: FastAPI):  # collects GPU memory
    yield
    _gc(args=args, forced=True)


app = FastAPI(lifespan=lifespan)

# * 3.1.2 处理跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/v1/chat/completions', response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    logging_xianyi.debug('-----------new request--------------------------------', request.user_id)
    global model, tokenizer

    stop_words = []
    if 'Observation:' not in stop_words:
        stop_words.append('Observation:')
    if 'Observation:\n' not in stop_words:
        stop_words.append('Observation:\n')
    # stop_words_ids = [tokenizer.encode(_) for _ in stop_words]
    #
    # stop_words_logits_processor = StopWordsLogitsProcessor(
    #     stop_words_ids=stop_words_ids,
    #     eos_token_id=model.generation_config.eos_token_id,
    # )
    # logits_processor = LogitsProcessorList([stop_words_logits_processor])

    global history_global
    # 处理消息
    query, history, system, already_known_user = parse_messages(request.messages, request.user_id, history_global,
                                                                already_known_user_global)
    already_known_user_global[request.user_id] = already_known_user

    conversation = [
        {'role': 'system', 'content': system},
    ]
    for query_h, response_h in history:
        conversation.append({'role': 'user', 'content': query_h})
        conversation.append({'role': 'assistant', 'content': response_h})

    # 如果是流式
    if request.stream:
        pass
    # 如果是非流式
    else:
        # 如果不用rag
        if not request.use_rag:
            pass
        # 如果用rag
        else:
            print("\033[1;42m用户【" + request.user_id + "】开始提问，生成答案中...  \033[0m\033[1;45m" + str(
                datetime.datetime.now()) +
                  "  \033[0m\033[1;44m模式：非流式，使用rag\033[0m")
            logging_xianyi.debug('开始提问，生成答案中...模式：非流式，使用rag', request.user_id)
            start_time = time.time()
            start_mem = GPUtil.getGPUs()[0].memoryUsed
            prompt = ''
            response = ''
            if already_known_user['scene'] == '':
                print('组织分类prompt')
                logging_xianyi.debug('组织分类prompt', request.user_id)
                logging_xianyi.info('user:' + query, request.user_id)
                prompt = build_planning_prompt(query, already_known_user, request.user_id)  # 组织prompt
                conversation.append({'role': 'user', 'content': prompt})
                # 模型进行分类
                request_param = {'temperature': None, 'top_k': None, 'top_p': None, 'do_sample': False,
                                 'messages': conversation}
                response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
                if response.status_code == 200:
                    data = response.json()  # 获取响应数据，如果是 JSON 格式
                    response = data['choices'][0]['message']['content']
                else:
                    raise Exception("大模型返回错误")

                i = response.rfind('\nScene:')
                classify_time = time.time()
                classify_mem = GPUtil.getGPUs()[0].memoryUsed

                # 构建日志记录信息
                log_message = '分类耗时: {} 结果长度: {} 每秒字数: {} 输入长度: {} 显存增加: {} G'.format(
                    classify_time - start_time,
                    len(response),
                    '时间没变' if classify_time == start_time else len(response) / (classify_time - start_time),
                    len(str(conversation)),
                    (classify_mem - start_mem) / 1024
                )
                print('\033[1;37m', log_message, '\033[0m')
                logging_xianyi.debug(log_message, request.user_id)
                print('\033[1;37m分类结果：' + response + '\033[0m')
                logging_xianyi.debug('分类结果：' + response, request.user_id)
                # 删掉分类的prompt
                conversation.pop(len(conversation) - 1)
                # 如果正确分类
                if 0 <= i:
                    plugin_name = response[i + len('\nScene:'):].strip().split('\n')[0]
                    already_known_user['scene'] = plugin_name
                # 如果没正确分类
                else:
                    response = '目前没有处理分类异常，请将问题反馈给宪一处理。异常分类情况：' + response
                    logging_xianyi.info('assistant:' + response, request.user_id)
                    choice_data = ChatCompletionResponseChoice(
                        index=0,
                        message=ChatMessage(role='assistant', content=response),
                        finish_reason='stop',
                    )
                    return ChatCompletionResponse(model=request.model,
                                                  choices=[choice_data],
                                                  object='chat.completion')
            # 如果已有场景，也需要记录用户问题
            else:
                logging_xianyi.info('user:' + query, request.user_id)
            # 进入具体场景问答
            start_time = time.time()
            start_mem = GPUtil.getGPUs()[0].memoryUsed
            # prompt = build_planning_prompt(query, already_known_user)  # 组织prompt
            conversation_scene = deepcopy(conversation)  # 提取关键字时清空历史
            #  如果直接调用模型
            if 'no_scene' == already_known_user['scene']:
                conversation_scene.append({'role': 'user', 'content': query})
                #  请求模型
                request_param = {'temperature': 0.7, 'top_k': 20, 'top_p': 0.8, 'do_sample': True,
                                 'messages': conversation_scene}
                response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
                if response.status_code == 200:
                    data = response.json()  # 获取响应数据，如果是 JSON 格式
                    response = data['choices'][0]['message']['content']
                else:
                    raise Exception("大模型返回错误")

                end_time = time.time()
                end_mem = GPUtil.getGPUs()[0].memoryUsed
                #  场景复原
                already_known_user['scene'] = ''
                print("\033[0;37m历史:\n[" + str(
                    ''.join([str(item) + "\n" for item in history])[:-1]) + "]\033[0m\n"
                                                                            "\033[0;33m问题：【" + query + "】\033[0m\n"
                                                                                                         "\033[0;36m回答：【" + response + "】\033[0m")
                logging_xianyi.debug("历史:\n[" + str(
                    ''.join([str(item) + "\n" for item in history])[:-1]) + "]\n"
                                                                            "问题：【" + query + "】\n"
                                                                                               "回答：【" + response + "】",
                                     request.user_id)
                print(already_known_user)
                logging_xianyi.debug(already_known_user, request.user_id)

                # 构建日志记录信息
                log_message = '回答完毕，耗时： {} 答案长度： {} 每秒字数: {} 输入长度: {} 显存增加: {} G'.format(
                    end_time - start_time,
                    len(response),
                    '时间没变' if end_time == start_time else len(response) / (end_time - start_time),
                    len(str(conversation_scene)),
                    (end_mem - start_mem) / 1024
                )
                print('\033[1;44m', log_message, '\033[0m')
                logging_xianyi.debug(log_message, request.user_id)

                _gc(args=args)
                # response = response.split('Final Answer:')[-1]
                history.append((query, response))
                history_global[request.user_id] = history

                response = trim_stop_words(response, stop_words)
                logging_xianyi.info('assistant:' + response, request.user_id)
                choice_data = ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role='assistant', content=response),
                    finish_reason='stop',
                )
                already_known_user_global[request.user_id] = already_known_user
                return ChatCompletionResponse(model=request.model,
                                              choices=[choice_data],
                                              object='chat.completion')
            # 不需要提取直接调用API
            elif already_known_user['scene'] in ['name', 'what_scenes']:
                prompt = build_planning_prompt(query, already_known_user, request.user_id)  # 组织prompt,需要当前场景字段，所以要在use_api清空场景之前
                api_output, already_known_user = use_api(response, already_known_user, request.user_id,
                                                         query)  # 抽取入参并执行api
                already_known_user_global[request.user_id] = already_known_user
                prompt = prompt.replace('_api_output_', api_output)
                print(prompt)
                logging_xianyi.debug(prompt, request.user_id)
                conversation_scene.append({'role': 'user', 'content': prompt})
                #  请求模型
                request_param = {'temperature': 0.7, 'top_k': 20, 'top_p': 0.8, 'do_sample': True,
                                 'messages': conversation_scene}
                response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
                if response.status_code == 200:
                    data = response.json()  # 获取响应数据，如果是 JSON 格式
                    response = data['choices'][0]['message']['content']
                else:
                    raise Exception("大模型返回错误")

                end_time = time.time()
                end_mem = GPUtil.getGPUs()[0].memoryUsed
                print("\033[0;37m历史:\n[" + str(
                    ''.join([str(item) + "\n" for item in history])[:-1]) + "]\033[0m\n"
                                                                            "\033[0;33m问题：【" + query + "】\033[0m\n"
                                                                                                         "\033[0;36m回答：【" + response + "】\033[0m")
                logging_xianyi.debug("历史:\n[" + str(
                    ''.join([str(item) + "\n" for item in history])[:-1]) + "]\n"
                                                                            "问题：【" + query + "】\n"
                                                                                               "回答：【" + response + "】",
                                     request.user_id)
                print(already_known_user)
                logging_xianyi.debug(already_known_user, request.user_id)
                # 构建日志记录信息
                log_message = '回答完毕，耗时： {} 答案长度： {} 每秒字数: {} 输入长度: {} 显存增加: {} G'.format(
                    end_time - start_time,
                    len(response),
                    '时间没变' if end_time == start_time else len(response) / (end_time - start_time),
                    len(str(conversation_scene)),
                    (end_mem - start_mem) / 1024
                )
                print('\033[1;44m', log_message, '\033[0m')
                logging_xianyi.debug(log_message, request.user_id)
                _gc(args=args)
                response = response.split('Final Answer:')[-1]
                history.append((query, response))
                history_global[request.user_id] = history

                response = trim_stop_words(response, stop_words)
                logging_xianyi.info('assistant:' + response, request.user_id)
                choice_data = ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role='assistant', content=response),
                    finish_reason='stop',
                )
                return ChatCompletionResponse(model=request.model,
                                              choices=[choice_data],
                                              object='chat.completion')
            # 如果要抽取信息
            elif already_known_user['scene'] in ['buy_car', 'used_car_valuation',
                                                 'the_car_appointment', 'vehicle_issues']:
                prompt = build_planning_prompt(query, already_known_user, request.user_id)  # 组织prompt,需要当前场景字段，所以要在use_api清空场景之前
                conversation_scene.pop(0)  # 删掉之前的system
                conversation_scene.append({'role': 'system', 'content': '你要对用户话中的信息进行抽取并格式化成JSON'})
                conversation_scene.append({'role': 'user', 'content': prompt})
                print(conversation_scene)
                logging_xianyi.debug(conversation_scene, request.user_id)
                print(prompt)
                logging_xianyi.debug(prompt, request.user_id)
                # 模型进行抽取
                request_param = {'temperature': None, 'top_k': None, 'top_p': None, 'do_sample': False,
                                 'messages': conversation_scene}
                response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
                if response.status_code == 200:
                    data = response.json()  # 获取响应数据，如果是 JSON 格式
                    response = data['choices'][0]['message']['content']
                else:
                    raise Exception("大模型返回错误")

                j = response.rfind('\nExtracted_Json:')
                classify_time = time.time()
                classify_mem = GPUtil.getGPUs()[0].memoryUsed
                # 构建日志记录信息
                log_message = '抽取耗时: {} 结果长度: {} 每秒字数: {} 输入长度: {} 显存增加: {} G'.format(
                    classify_time - start_time,
                    len(response),
                    '时间没变' if classify_time == start_time else len(response) / (classify_time - start_time),
                    len(str(conversation_scene)),
                    (classify_mem - start_mem) / 1024
                )
                print('\033[1;37m', log_message, '\033[0m')
                logging_xianyi.debug(log_message, request.user_id)
                print('\033[1;37m抽取结果：' + response + '\033[0m')
                logging_xianyi.debug('抽取结果：' + response, request.user_id)
                # 如果正确抽取
                # if 0 <= j:
                Extracted_Json = response[j + len('\nExtracted_Json:'):].strip()
                scene = already_known_user['scene']  # 在清空前获取场景
                Extracted_Json_already = deepcopy(already_known_user[scene])
                Extracted_Json_already.pop('userId') if 'userId' in Extracted_Json_already else None
                api_output, already_known_user = use_api(response, already_known_user, request.user_id,
                                                         Extracted_Json, query)  # 抽取入参并执行api
                already_known_user_global[request.user_id] = already_known_user
                print('api返回结果：' + api_output)
                logging_xianyi.debug('api返回结果：' + api_output, request.user_id)
                # 对结果整理话术
                try:
                    json.loads(Extracted_Json)
                except:
                    Extracted_Json = '{}'
                print(Extracted_Json)
                logging_xianyi.debug(Extracted_Json,request.user_id)
                Extracted_Json = {**Extracted_Json_already, **json.loads(Extracted_Json)}
                prompt = build_planning_prompt_final(query, scene, Extracted_Json, api_output,request.user_id)
                print(prompt)
                logging_xianyi.debug(prompt,request.user_id)
                conversation_scene = [{'role': 'system', 'content': system}]
                conversation_scene.append({'role': 'user', 'content': prompt})
                request_param = {'temperature': 0.7, 'top_k': 20, 'top_p': 0.8, 'do_sample': True,
                                 'messages': conversation_scene}
                response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
                if response.status_code == 200:
                    data = response.json()  # 获取响应数据，如果是 JSON 格式
                    response = data['choices'][0]['message']['content']
                else:
                    raise Exception("大模型返回错误")

                response = response.split('Final Answer:')[-1]
                end_time = time.time()
                end_mem = GPUtil.getGPUs()[0].memoryUsed
                print("\033[0;37m历史:\n[" + str(
                    ''.join([str(item) + "\n" for item in history])[:-1]) + "]\033[0m\n"
                                                                            "\033[0;33m问题：【" + query + "】\033[0m\n"
                                                                                                         "\033[0;36m回答：【" + response + "】\033[0m")
                logging_xianyi.debug("历史:\n[" + str(
                    ''.join([str(item) + "\n" for item in history])[:-1]) + "]\n"
                                                                            "问题：【" + query + "】\n"
                                                                                               "回答：【" + response + "】",
                                     request.user_id)
                print(already_known_user)
                logging_xianyi.debug(already_known_user, request.user_id)
                # 构建日志记录信息
                log_message = '回答完毕，耗时： {} 答案长度： {} 每秒字数: {} 输入长度: {} 显存增加: {} G'.format(
                    end_time - start_time,
                    len(response),
                    '时间没变' if end_time == start_time else len(response) / (end_time - start_time),
                    len(str(conversation_scene)),
                    (end_mem - start_mem) / 1024
                )
                print('\033[1;44m', log_message, '\033[0m')
                logging_xianyi.debug(log_message, request.user_id)
                _gc(args=args)
                # response = response.split('Final Answer:')[-1]
                history.append((query, response))
                history_global[request.user_id] = history
                response = trim_stop_words(response, stop_words)
                logging_xianyi.info('assistant:' + response, request.user_id)
                choice_data = ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role='assistant', content=response),
                    finish_reason='stop',
                )
                return ChatCompletionResponse(model=request.model,
                                              choices=[choice_data],
                                              object='chat.completion')


if __name__ == '__main__':
    # * 1.获取参数
    args = rag_args_classification.get_args()
    # * 1.1 定义全局history
    history_global = dict()
    already_known_user_global = dict()
    # * 2.加载模型
    # tokenizer = AutoTokenizer.from_pretrained(args.checkpoint_path)
    #
    # model = AutoModelForCausalLM.from_pretrained(
    #     args.checkpoint_path,
    #     device_map='cuda'
    #     , bnb_4bit_compute_dtype=torch.float16
    #     , load_in_4bit=True
    # ).eval()

    # * 3.运行web框架
    uvicorn.run(app, host=args.server_name, port=args.server_port, workers=1)
