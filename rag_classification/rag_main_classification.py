import copy
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
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM

from transformers.generation.logits_process import LogitsProcessorList

from rag_classification import rag_args_classification
from rag_classification.api_tools.tool_name import tool_wrapper_for_qwen_name
from rag_classification.rag_handler_classification import ChatCompletionRequest, ChatCompletionResponse, \
    StopWordsLogitsProcessor, parse_messages, _gc, ChatCompletionResponseChoice, ChatMessage, trim_stop_words
from rag_classification.rag_tools_classification import build_planning_prompt, use_api, build_planning_prompt_final, \
    build_planning_prompt_change_scene
from logging_xianyi.logging_xianyi import logging_xianyi
from multiprocessing import Manager
import psycopg2
import json

manager = Manager()
history_global = manager.dict()
# already_known_user_global = manager.dict()
args = rag_args_classification.get_args()

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
    start_time = time.time()
    # 连接到 PostgreSQL 数据库
    conn = psycopg2.connect(
        dbname="ai_voyage",
        user="postgres",
        password="o%c%!ll$okopba8)",
        host="192.168.110.147"
    )
    cur = conn.cursor()

    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期天"]
    stop_words = ['Thought:']
    if 'Monitoring:' not in stop_words:
        stop_words.append('Monitoring:')
    if 'Monitoring:\n' not in stop_words:
        stop_words.append('Monitoring:\n')
    # stop_words_ids = [tokenizer.encode(_) for _ in stop_words]
    #
    # stop_words_logits_processor = StopWordsLogitsProcessor(
    #     stop_words_ids=stop_words_ids,
    #     eos_token_id=model.generation_config.eos_token_id,
    # )
    # logits_processor = LogitsProcessorList([stop_words_logits_processor])

    global history_global
    # 处理消息
    query, history, system, already_known_user = parse_messages(request.messages, request, history_global,
                                                                cur, request.history)

    # already_known_user_global[request.user_id] = already_known_user

    conversation = [
        {'role': 'system', 'content': system},
    ]
    for query_h, response_h in history:
        conversation.append({'role': 'user', 'content': query_h})
        conversation.append({'role': 'assistant', 'content': response_h})

    # 如果是流式
    # if request.stream:
    #     pass
    # 如果是非流式
    # else:
    # 如果不用rag
    if not request.use_rag:
        pass
    # 如果用rag
    else:
        print("\033[1;42m用户【" + request.user_id + "】开始提问，生成答案中...  \033[0m\033[1;45m" + str(
            datetime.now()) +
              "  \033[0m\033[1;44m模式：非流式，使用rag\033[0m")
        logging_xianyi.debug('开始提问，生成答案中...模式：非流式，使用rag', request.user_id)
        # start_time = time.time()
        start_mem = GPUtil.getGPUs()[0].memoryUsed
        prompt = ''
        response = ''
        # 判断场景是否过期
        if 'scene_time' in already_known_user:
            if already_known_user['scene_time'] == '':
                already_known_user['scene_time'] = 0  # 如果清理过scene_time，设为0，表示保留时长很长
            scene_period = time.time() - already_known_user['scene_time']
            print('场景已保留时长' + str(scene_period))
            if scene_period > 3600 * 24:  # 如果大于24小时
                already_known_user['scene'] = ''
        if already_known_user['scene'] == '':
            print('组织分类prompt')
            logging_xianyi.debug('组织分类prompt', request.user_id)
            logging_xianyi.info('user:' + query, request.user_id)
            prompt = ('你是 小优，一个由 优必爱 训练的大型语言模型。知识截止日期：{}。当前时间：{}，今天是{}。'
                      .format(datetime.now().strftime("%Y-%m")
                              , datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                              , weekdays[datetime.now().weekday()])
                      + build_planning_prompt(query, already_known_user, request.user_id))  # 组织prompt
            conversation.append({'role': 'user', 'content': prompt})
            print('分类conversation：'+str(conversation))
            # 模型进行分类
            request_param = {'temperature': None, 'top_k': None, 'top_p': None, 'do_sample': False,
                             'messages': conversation, 'stream': False}
            response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
            if response.status_code == 200:
                data = response.json()  # 获取响应数据，如果是 JSON 格式
                response = data['choices'][0]['message']['content']
            else:
                raise Exception("大模型返回错误")
            i = response.rfind('Scene:')
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
                plugin_name = response[i + len('Scene:'):].strip().split('\n')[0]
                already_known_user['scene'] = plugin_name
                already_known_user['scene_time'] = time.time()  # 场景时间
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
        # 如果已有场景，也需要记录用户问题,并判断是否切换场景
        else:
            logging_xianyi.info('user:' + query, request.user_id)
            print('组织切换场景prompt')
            logging_xianyi.debug('组织切换场景prompt', request.user_id)
            prompt = ('你是 小优，一个由 优必爱 训练的大型语言模型。知识截止日期：{}。当前时间：{},今天是{}。'
                      .format(datetime.now().strftime("%Y-%m")
                              , datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                              , weekdays[datetime.now().weekday()])
                      + build_planning_prompt_change_scene(query, already_known_user, request.user_id))  # 组织prompt
            conversation.append({'role': 'user', 'content': prompt})
            # 模型切换场景
            request_param = {'temperature': None, 'top_k': None, 'top_p': None, 'do_sample': False,
                             'messages': conversation}
            response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
            if response.status_code == 200:
                data = response.json()  # 获取响应数据，如果是 JSON 格式
                response = data['choices'][0]['message']['content']
            else:
                raise Exception("大模型返回错误")
            print(response)
            classify_time = time.time()
            classify_mem = GPUtil.getGPUs()[0].memoryUsed
            # 构建日志记录信息
            log_message = '切换判断耗时: {} 结果长度: {} 每秒字数: {} 输入长度: {} 显存增加: {} G'.format(
                classify_time - start_time,
                len(response),
                '时间没变' if classify_time == start_time else len(response) / (classify_time - start_time),
                len(str(conversation)),
                (classify_mem - start_mem) / 1024
            )
            print('\033[1;37m', log_message, '\033[0m')
            logging_xianyi.debug(log_message, request.user_id)
            print('\033[1;37m切换判断结果：' + response + '\033[0m')
            logging_xianyi.debug('切换判断结果：' + response, request.user_id)
            # 删掉分类的prompt
            conversation.pop(len(conversation) - 1)
            i = response.rfind('New_Scene:')
            j = response.rfind('Probability:')
            # 如果正确分类
            if 0 <= i:
                # probability = response[j + len('\nProbability:'):].strip().split('\n')[0].split('%')[0]
                plugin_name = response[i + len('New_Scene:'):].strip().split('\n')[0]
                if (
                        # int(probability) >= 80 and
                        plugin_name != already_known_user['scene']):
                    print('要切换新场景，新场景：' + plugin_name + ',旧场景：' + already_known_user['scene'])
                    logging_xianyi.debug(
                        '要切换新场景,新场景：' + plugin_name + ',旧场景：' + already_known_user['scene'],
                        request.user_id)
                    already_known_user[already_known_user['scene']] = {}  # 清空旧场景记录
                    already_known_user['scene'] = plugin_name
                    already_known_user['scene_time'] = time.time()  # 场景时间
                else:
                    already_known_user['scene_time'] = time.time()
            # 如果没正确分类
            else:
                response = '目前没有处理场景切换异常，请将问题反馈给宪一处理。异常分类情况：' + response
                logging_xianyi.info('assistant:' + response, request.user_id)
                choice_data = ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role='assistant', content=response),
                    finish_reason='stop',
                )
                return ChatCompletionResponse(model=request.model,
                                              choices=[choice_data],
                                              object='chat.completion')
        # 进入具体场景问答
        start_time = time.time()
        start_mem = GPUtil.getGPUs()[0].memoryUsed
        # prompt = build_planning_prompt(query, already_known_user)  # 组织prompt
        conversation_scene = deepcopy(conversation)  # 提取关键字时清空历史
        #  如果直接调用模型
        if 'no_scene' == already_known_user['scene']:
            # conversation_scene.append({'role': 'user', 'content': ('你是 小优，一个由 优必爱 训练的大型语言模型。知识截止日期：{}。当前时间：{}。'
            #                                                        .format(datetime.now().strftime("%Y-%m")
            #                                                                , datetime.now().strftime(
            #         "%Y-%m-%d %H:%M:%S")))})
            conversation_scene.append({'role': 'user', 'content': query})
            #  请求模型
            request_param = {'temperature': 0.7, 'top_k': 20, 'top_p': 0.8, 'do_sample': True,
                             'messages': conversation_scene, 'stream': request.stream}
            if request.stream:
                url = 'http://192.168.110.147:10029/v1/chat/completions'  # 替换为你的实际URL
                response = requests.post(url, json=request_param, stream=True)
                stream_yield = event_handler(already_known_user, conversation_scene, history, history_global, query,
                                             request, response, start_mem, start_time, stop_words, 'no_sence')
                return EventSourceResponse(stream_yield, media_type='text/event-stream')

            else:
                response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
                if response.status_code == 200:
                    data = response.json()  # 获取响应数据，如果是 JSON 格式
                    response = data['choices'][0]['message']['content']
                else:
                    raise Exception("大模型返回错误")
                response = await after_call_model(already_known_user, conversation_scene, history, history_global,
                                                  query,
                                                  request, response, start_mem, start_time, stop_words, 'no_sence')
                choice_data = ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role='assistant', content=response),
                    finish_reason='stop',
                )
                await update_already_known_user(request, already_known_user, conn, cur)
                # already_known_user_global[request.user_id] = already_known_user
                return ChatCompletionResponse(model=request.model,
                                              choices=[choice_data],
                                              object='chat.completion')
        # 不需要提取直接调用API
        elif already_known_user['scene'] in ['name', 'what_scenes', 'search_web', 'check_mileage']:
            prompt = ('你是 小优，一个由 优必爱 训练的大型语言模型。知识截止日期：{}。当前时间：{},今天是{}。'
                      .format(datetime.now().strftime("%Y-%m")
                              , datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                              , weekdays[datetime.now().weekday()])
                      + build_planning_prompt(query, already_known_user,
                                              request.user_id))  # 组织prompt,需要当前场景字段，所以要在use_api清空场景之前
            api_output, already_known_user = use_api(response, already_known_user, request.user_id,request.session_id,
                                                     query)  # 抽取入参并执行api
            await update_already_known_user(request, already_known_user, conn, cur)
            # already_known_user_global[request.user_id] = already_known_user
            prompt = prompt.replace('_api_output_', api_output)
            print(prompt)
            logging_xianyi.debug(prompt, request.user_id)
            conversation_scene.append({'role': 'user', 'content': prompt})
            #  请求模型
            request_param = {'temperature': 0.7, 'top_k': 20, 'top_p': 0.8, 'do_sample': True,
                             'messages': conversation_scene, 'stream': request.stream}
            if request.stream:
                url = 'http://192.168.110.147:10029/v1/chat/completions'  # 替换为你的实际URL
                response = requests.post(url, json=request_param, stream=True)
                stream_yield = event_handler(already_known_user, conversation_scene, history, history_global, query,
                                             request, response, start_mem, start_time, stop_words, 'direct_api')
                return EventSourceResponse(stream_yield, media_type='text/event-stream')
            else:
                response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
                if response.status_code == 200:
                    data = response.json()  # 获取响应数据，如果是 JSON 格式
                    response = data['choices'][0]['message']['content']
                else:
                    raise Exception("大模型返回错误")
                response = response.split('FeedbackToUsers:')[-1].strip()
                response = await after_call_model(already_known_user, conversation_scene, history, history_global,
                                                  query, request, response, start_mem, start_time, stop_words,
                                                  'direct_api')
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
            prompt = ('你是 小优，一个由 优必爱 训练的大型语言模型。知识截止日期：{}。当前时间：{},今天是{}。'
                      .format(datetime.now().strftime("%Y-%m")
                              , datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                              , weekdays[datetime.now().weekday()])
                      + build_planning_prompt(query, already_known_user,
                                              request.user_id))  # 组织prompt,需要当前场景字段，所以要在use_api清空场景之前
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
            i = response.find('Suspected_Reason:')  # 找最先出现的Suspected_Reason
            j = response.find('Extracted_Json:')  # 找最先出现的Extracted_Json
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
            Extracted_Json = Extracted_Json[:Extracted_Json.find('}') + 1]  # 不能嵌套json}
            Suspected_Reason = ''
            if i != -1:
                Suspected_Reason = response[i + len('\nSuspected_Reason:'):].strip()
                Suspected_Reason = Suspected_Reason[:Suspected_Reason.find('\nExtracted_Json:')]
                print('Suspected_Reason:' + Suspected_Reason)
            print('Extracted_Json:'+Extracted_Json)
            scene = already_known_user['scene']  # 在清空前获取场景
            Extracted_Json_already = deepcopy(already_known_user[scene])
            Extracted_Json_already.pop('userId') if 'userId' in Extracted_Json_already else None
            # 对结果整理话术
            try:
                json.loads(Extracted_Json)
            except:
                Extracted_Json = '{}'
            print('json.load后Extracted_Json：'+Extracted_Json)
            logging_xianyi.debug(Extracted_Json, request.user_id)
            Extracted_Json = {**Extracted_Json_already, **json.loads(Extracted_Json)}
            if i != -1:
                Extracted_Json['suspected_reason'] = Suspected_Reason  # 改成首字母小写的
            print('合并后json：'+str(Extracted_Json))
            api_output, already_known_user = use_api(response, already_known_user, request.user_id, request.session_id,
                                                     Extracted_Json, query)  # 抽取入参并执行api
            await update_already_known_user(request, already_known_user, conn, cur)
            # already_known_user_global[request.user_id] = already_known_user
            print('api返回结果：' + api_output)
            logging_xianyi.debug('api返回结果：' + api_output, request.user_id)
            # 清理value空值
            tmp_json = {}
            for key, value in Extracted_Json.items():
                # 模型抽取校验
                if '' != value and value:
                    tmp_json[key] = value
            Extracted_Json = tmp_json
            prompt = ('你是 小优，一个由 优必爱 训练的大型语言模型。知识截止日期：{}。当前时间：{}，今天是{}。'
                      .format(datetime.now().strftime("%Y-%m")
                              , datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                              , weekdays[datetime.now().weekday()])
                      + build_planning_prompt_final(query, scene, Extracted_Json, api_output, request.user_id))
            print(prompt)
            logging_xianyi.debug(prompt, request.user_id)
            conversation_scene = [{'role': 'system', 'content': system}]
            conversation_scene.append({'role': 'user', 'content': prompt})
            request_param = {'temperature': 0.7, 'top_k': 20, 'top_p': 0.8, 'do_sample': True,
                             'messages': conversation_scene, 'stream': request.stream}
            if request.stream:
                if api_output == '_[DONE]_':
                    response = '[DONE]'
                else:
                    url = 'http://192.168.110.147:10029/v1/chat/completions'  # 替换为你的实际URL
                    response = requests.post(url, json=request_param, stream=True)
                stream_yield = event_handler(already_known_user, conversation_scene, history, history_global, query,
                                             request, response, start_mem, start_time, stop_words, 'extract')
                return EventSourceResponse(stream_yield, media_type='text/event-stream')
            else:
                if scene in ['the_car_appointment', 'buy_car', 'used_car_valuation']:
                    if api_output == '_[DONE]_':
                        choice_data = ChatCompletionResponseChoice(
                            index=0,
                            message=ChatMessage(role='assistant', content='[DONE]'),
                            finish_reason='stop',
                        )
                        return ChatCompletionResponse(model=request.model,
                                                      choices=[choice_data],
                                                      object='chat.completion')
                response = requests.post(f'http://192.168.110.147:10029/v1/chat/completions', json=request_param)
                if response.status_code == 200:
                    data = response.json()  # 获取响应数据，如果是 JSON 格式
                    response = data['choices'][0]['message']['content']
                else:
                    raise Exception("大模型返回错误")
                response = response.split('FeedbackToUsers:')[-1].strip()
                response = await after_call_model(already_known_user, conversation_scene, history, history_global,
                                                  query, request, response, start_mem, start_time, stop_words,
                                                  'extract')
                choice_data = ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role='assistant', content=response),
                    finish_reason='stop',
                )
                return ChatCompletionResponse(model=request.model,
                                              choices=[choice_data],
                                              object='chat.completion')


async def update_already_known_user(request,already_known_user, conn, cur):
    cur.execute("INSERT INTO qwen_already_known_user_global (user_id,already_known_user,session_id) "
                "VALUES (%s,%s,%s) "
                "ON CONFLICT (user_id,session_id) DO UPDATE "
                "SET already_known_user = EXCLUDED.already_known_user", [request.user_id, json.dumps(already_known_user), request.session_id])
    conn.commit()
    cur.close()
    conn.close()


async def event_handler(already_known_user, conversation_scene, history, history_global, query, request,
                        response, start_mem, start_time, stop_words, call_model_type):
    buffer = ''
    final_answer = ''
    is_final_answer = False
    if '[DONE]' == response:
        final_answer = '结果已在卡片展示'
        if call_model_type == 'direct_api':
            await after_call_model(already_known_user, conversation_scene, history,
                                   history_global, query,
                                   request, final_answer, start_mem, start_time, stop_words,
                                   call_model_type)
        elif call_model_type == 'extract':
            await after_call_model(already_known_user, conversation_scene, history,
                                   history_global, query,
                                   request, final_answer, start_mem, start_time, stop_words,
                                   call_model_type)
        yield '[DONE]'
    else:
        for line in response.iter_lines():
            s = ''  # 因为最后一个[DONE]需要重新赋值，所以s不能放外面
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    if decoded_line[6:] == '[DONE]':
                        print('')
                        if call_model_type == 'no_sence':
                            await after_call_model(already_known_user, conversation_scene, history,
                                                   history_global, query,
                                                   request, buffer, start_mem, start_time, stop_words, call_model_type)
                        elif call_model_type == 'direct_api':
                            await after_call_model(already_known_user, conversation_scene, history,
                                                   history_global, query,
                                                   request, final_answer, start_mem, start_time, stop_words,
                                                   call_model_type)
                        elif call_model_type == 'extract':
                            await after_call_model(already_known_user, conversation_scene, history,
                                                   history_global, query,
                                                   request, final_answer, start_mem, start_time, stop_words,
                                                   call_model_type)
                    else:
                        try:
                            s = json.loads(decoded_line[6:])['choices'][0]['delta']['content']
                            print(s, end='', flush=True)
                            buffer += s
                        except KeyError:
                            # 如果任意一层的键不存在，则什么也不做
                            pass
                    if call_model_type == 'no_sence':
                        yield decoded_line[6:]
                    elif call_model_type in ['direct_api', 'extract']:
                        if is_final_answer:
                            final_answer = buffer.split('FeedbackToUsers:')[-1].strip()
                            yield decoded_line[6:]
                        else:
                            if 'FeedbackToUsers:' in buffer:
                                is_final_answer = True
                                if not buffer.endswith("FeedbackToUsers:"):
                                    # 输出同一返回里FeedbackToUsers:后的内容
                                    data = json.loads(decoded_line[6:])
                                    # 处理 content 字段
                                    for choice in data['choices']:
                                        content = choice['delta']['content']
                                        # 使用正则表达式去掉冒号前的内容,
                                        # [\s\S]*   匹配任何字符（包括换行符），零次或多次;
                                        # ?:   匹配第一个冒号 :
                                        # \s* 匹配零次或多次空白字符
                                        new_content = re.sub(r'^[\s\S]*?:\s*', '', content)
                                        choice['delta']['content'] = new_content
                                    new_json_string = json.dumps(data, ensure_ascii=False)
                                    yield new_json_string


import re
async def split_string(s):
    # 定义标点符号的正则表达式模式
    pattern = re.compile(r'([,.;!?:，。；！？：])')
    match = pattern.search(s)

    if match:
        delimiter = match.group(0)
        parts = s.split(delimiter, 1)  # 只拆分第一个出现的分隔符
        part1 = parts[0] + delimiter
        part2 = parts[1]
        yield part1
        yield part2
    else:
        yield s


async def after_call_model(already_known_user, conversation_scene, history, history_global, query, request, response,
                           start_mem, start_time, stop_words, call_model_type):
    end_time = time.time()
    end_mem = GPUtil.getGPUs()[0].memoryUsed
    if call_model_type == 'no_sence':
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
    log_message = '回答完毕，耗时： {} 答案长度： {} 每秒字数: {} 输入长度: {} 显存增加: {} G {}'.format(
        end_time - start_time,
        len(response),
        '时间没变' if end_time == start_time else len(response) / (end_time - start_time),
        len(str(conversation_scene)),
        (end_mem - start_mem) / 1024,
        str(datetime.now())
    )
    print('\033[1;44m', log_message, '\033[0m')
    logging_xianyi.debug(log_message, request.user_id)
    _gc(args=args, forced=True)
    # response = response.split('FeedbackToUsers:')[-1]
    history.append((query, response))
    history_global[request.user_id] = history
    response = trim_stop_words(response, stop_words)
    logging_xianyi.info('assistant:' + response, request.user_id)
    return response


if __name__ == '__main__':
    # * 1.获取参数
    args = rag_args_classification.get_args()
    # * 1.1 定义全局history
    history_global = dict()
    # already_known_user_global = dict()
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
