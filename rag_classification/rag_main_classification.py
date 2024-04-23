import datetime
import time
from contextlib import asynccontextmanager

import GPUtil
import torch
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from transformers import AutoTokenizer, AutoModelForCausalLM

from transformers.generation.logits_process import LogitsProcessorList

from rag_classification import rag_args_classification
from rag_classification.rag_handler_classification import ChatCompletionRequest, ChatCompletionResponse, \
    StopWordsLogitsProcessor, parse_messages, _gc, ChatCompletionResponseChoice, ChatMessage, trim_stop_words
from rag_classification.rag_tools_classification import build_planning_prompt


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
    global model, tokenizer

    stop_words = []
    if 'Observation:' not in stop_words:
        stop_words.append('Observation:')
    if 'Observation:\n' not in stop_words:
        stop_words.append('Observation:\n')
    stop_words_ids = [tokenizer.encode(_) for _ in stop_words]

    stop_words_logits_processor = StopWordsLogitsProcessor(
        stop_words_ids=stop_words_ids,
        eos_token_id=model.generation_config.eos_token_id,
    )
    logits_processor = LogitsProcessorList([stop_words_logits_processor])

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
            model.generation_config.temperature = None
            model.generation_config.top_k = None
            model.generation_config.top_p = None
            model.generation_config.do_sample = False  # greedy 禁用采样，贪婪
            print("\033[1;42m用户【" + request.user_id + "】开始提问，生成答案中...  \033[0m\033[1;45m" + str(
                datetime.datetime.now()) +
                  "  \033[0m\033[1;44m模式：非流式，使用rag\033[0m")
            start_time = time.time()
            start_mem = GPUtil.getGPUs()[0].memoryUsed
            if already_known_user['scene'] == 'no_scene':
                print('组织分类prompt')
                prompt = build_planning_prompt(query, already_known_user)  # 组织prompt
                conversation.append({'role': 'user', 'content': prompt})
                # 模型进行分类
                inputs = tokenizer.apply_chat_template(
                    conversation,
                    tokenize=False,
                    add_generation_prompt=True
                )
                model_inputs = tokenizer([inputs], return_tensors="pt").to('cuda')
                generated_ids = model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=1024,
                )
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]
                response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                i = response.rfind('\nScene:')
                classify_time = time.time()
                classify_mem = GPUtil.getGPUs()[0].memoryUsed
                print('\033[1;37m分类耗时：', classify_time - start_time, '结果长度：', len(response), '每秒字数：',
                      '时间没变' if classify_time == start_time else len(response) / (classify_time - start_time), '输入长度:',
                      len(str(conversation)), '显存增加:',
                      (classify_mem - start_mem) / 1024, 'G\033[0m')
                print('\033[1;37m分类结果：'+response+'\033[0m')
                # 删掉分类的prompt
                conversation.pop(len(conversation)-1)
                # 如果正确分类
                if 0 <= i:
                    plugin_name = response[i + len('\nScene:'):].strip()
                    already_known_user['scene'] = plugin_name
                # 如果没正确分类
                else:
                    response = '目前没有处理分类异常，请将问题反馈给宪一处理。异常分类情况：'+response
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
            prompt = build_planning_prompt(query, already_known_user)  # 组织prompt
            conversation.append({'role': 'user', 'content': prompt})
            inputs = tokenizer.apply_chat_template(
                conversation,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = tokenizer([inputs], return_tensors="pt").to('cuda')
            generated_ids = model.generate(
                model_inputs.input_ids,
                max_new_tokens=1024,
                logits_processor=logits_processor
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            # todo 有问题
            end_time = time.time()
            end_mem = GPUtil.getGPUs()[0].memoryUsed
            print("\033[0;37m历史:\n[" + str(
                ''.join([str(item) + "\n" for item in history])[:-1]) + "]\033[0m\n"
                                                                        "\033[0;33m问题：【" + query + "】\033[0m\n"
                                                                                                     "\033[0;36m回答：【" + response + "】\033[0m")
            print(already_known_user)
            print('\033[1;44m回答完毕，耗时：', end_time - start_time, '答案长度：', len(response), '每秒字数：',
                  '时间没变' if end_time == start_time else len(response) / (end_time - start_time), '输入长度:',
                  len(str(conversation)), '显存增加:',
                  (end_mem - start_mem) / 1024, 'G\033[0m')
            _gc(args=args)
            response = response.split('Final Answer:')[-1]
            history.append((query, response))
            # history.append((query, api_output))  # api返回的放在后面，很重要
            history_global[request.user_id] = history

            response = trim_stop_words(response, stop_words)
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
    tokenizer = AutoTokenizer.from_pretrained(args.checkpoint_path)

    model = AutoModelForCausalLM.from_pretrained(
        args.checkpoint_path,
        device_map='cuda'
        , bnb_4bit_compute_dtype=torch.float16
        , load_in_4bit=True
    ).eval()

    # * 3.运行web框架
    uvicorn.run(app, host=args.server_name, port=args.server_port, workers=1)