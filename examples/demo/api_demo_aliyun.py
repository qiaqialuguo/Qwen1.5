import json
import time
from argparse import ArgumentParser
from contextlib import asynccontextmanager
from http import HTTPStatus
from dashscope import Generation
import random
import requests
import torch
import uvicorn
from fastapi import FastAPI
from threading import Thread
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union, Iterable

app = FastAPI()

# * 3.1.2 处理跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class ChatMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: Optional[str]


class DeltaMessage(BaseModel):
    role: Optional[Literal['user', 'assistant', 'system']] = None
    content: Optional[str] = None


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: Union[ChatMessage]
    finish_reason: Literal['stop', 'length']


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal['stop', 'length']]


class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal['chat.completion', 'chat.completion.chunk']
    choices: List[Union[ChatCompletionResponseChoice,
    ChatCompletionResponseStreamChoice]]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))


class ChatCompletionRequest(BaseModel):
    # model: Optional[str] = 'qwen2.5-72b-instruct'
    model: Optional[str] = 'qwen-plus-latest'
    # model: Optional[str] = 'qwen-max-latest'
    messages: List[dict]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    max_length: Optional[int] = None
    stream: Optional[bool] = False
    do_sample: Optional[bool] = False


@app.post('/v1/chat/completions', response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    global model, tokenizer
    conversation = request.messages
    is_stream = request.stream

    if is_stream:
        print(conversation)
        generate = predict(conversation,
                           request.model,
                           )
        s = handler(generate)
        return EventSourceResponse(s, media_type='text/event-stream')
    else:
        response = Generation.call(
            request.model,
            messages=conversation,
            # set the random seed, optional, default to 1234 if not set
            seed=random.randint(1, 10000),
            result_format='message',  # set the result to be "message" format.
            api_key='sk-dc5e9d4949394662a62a9cffbc2f63b4',
            stop=['User:', 'Action:', 'Action Input:', 'Think:','Thought:'],
        )
        print(response.code)
        response = response.output.choices[0]['message']['content']
        print('answer: ' + response)

        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role='assistant', content=response),
            finish_reason='stop',
        )
        return ChatCompletionResponse(model=request.model,
                                      choices=[choice_data],
                                      object='chat.completion')


async def handler(generate):
    s2 = ''
    print('stream_answer: ', end='')
    async for i in generate:
        if i == '[DONE]':
            # print('stream_answer: '+s2)
            print('')  # 换个行，好看
            pass
        else:
            try:
                # s2 += json.loads(i)['choices'][0]['delta']['content']
                # flush=True 会强制 print 函数立即将文本写入到标准输出（屏幕），而不是等到缓冲区满了或者发生换行时才写入。
                print(json.loads(i)['choices'][0]['delta']['content'], end='', flush=True)
            except KeyError:
                # 如果任意一层的键不存在，则什么也不做
                pass
        # time.sleep(0.2)
        yield i


async def predict(
        conversation,
        model_id,
):
    global model, tokenizer
    choice_data = ChatCompletionResponseStreamChoice(
        index=0, delta=DeltaMessage(role='assistant'), finish_reason=None)
    chunk = ChatCompletionResponse(model=model_id,
                                   choices=[choice_data],
                                   object='chat.completion.chunk')
    yield '{}'.format(_dump_json(chunk, exclude_unset=True))

    responses = Generation.call(
        model_id,
        messages=conversation,
        seed=random.randint(1, 10000),  # set the random seed, optional, default to 1234 if not set
        result_format='message',  # set the result to be "message"  format.
        stream=True,
        api_key='sk-dc5e9d4949394662a62a9cffbc2f63b4',
        output_in_full=True,  # get streaming output incrementally
        stop=['User:', 'Action:', 'Action Input:', 'Think:','Thought:'],
    )
    current_length = 0
    for response in responses:
        if response.status_code == HTTPStatus.OK:
            content = response.output.choices[0]['message']['content']
            if len(content) == current_length:
                continue
            new_text = content[current_length:]
            current_length = len(content)
            # print(new_text, end='', flush=True)
            choice_data = ChatCompletionResponseStreamChoice(
                index=0, delta=DeltaMessage(content=new_text), finish_reason=None)
            chunk = ChatCompletionResponse(model=model_id,
                                           choices=[choice_data],
                                           object='chat.completion.chunk')
            yield '{}'.format(_dump_json(chunk, exclude_unset=True))
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))

    choice_data = ChatCompletionResponseStreamChoice(index=0,
                                                     delta=DeltaMessage(),
                                                     finish_reason='stop')
    chunk = ChatCompletionResponse(model=model_id,
                                   choices=[choice_data],
                                   object='chat.completion.chunk')
    yield '{}'.format(_dump_json(chunk, exclude_unset=True))
    yield '[DONE]'


def _dump_json(data: BaseModel, *args, **kwargs) -> str:
    try:
        return data.model_dump_json(*args, **kwargs)
    except AttributeError:  # pydantic<2.0.0
        return data.json(*args, **kwargs)  # noqa


def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-c',
        '--checkpoint-path',
        type=str,
        default='/opt/large-model/qwen/qwen1.5/Qwen1.5-14B-Chat/',
        help='Checkpoint name or path, default to %(default)r',
    )
    parser.add_argument('--server-port',
                        type=int,
                        default=10029,
                        help='Demo server port.')
    parser.add_argument(
        '--server-name',
        type=str,
        default='0.0.0.0',
        help='Demo server name. Default: 0.0.0.0',
    )
    parser.add_argument(
        '--disable-gc',
        action='store_true',
        help='Disable GC after each response generated.',
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()

    # * 3.运行web框架
    uvicorn.run(app, host=args.server_name, port=args.server_port, workers=1)
