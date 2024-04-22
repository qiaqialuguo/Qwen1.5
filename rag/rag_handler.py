import copy
import json
import time

import requests
import torch
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union

from transformers import PreTrainedTokenizerFast

_TEXT_COMPLETION_CMD = object()


def _gc(args,forced: bool = False):
    if args.disable_gc and not forced:
        return

    import gc

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

class ChatMessage(BaseModel):
    role: Literal['user', 'assistant', 'system', 'function']
    content: Optional[str]
    function_call: Optional[Dict] = None


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = 'hi'
    messages: List[ChatMessage]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    max_length: Optional[int] = None
    stream: Optional[bool] = False
    user_id: Optional[str] = 'default'
    use_rag: Optional[bool] = True


def parse_messages(messages, user_id,history_global,already_known_user_global):
    if all(m.role != 'user' for m in messages):
        raise HTTPException(
            status_code=400,
            detail='Invalid request: Expecting at least one user message.',
        )

    messages = copy.deepcopy(messages)
    if messages[0].role == 'system':
        system = messages.pop(0).content.lstrip('\n').rstrip()
    else:
        system = 'You are a helpful assistant.'

    messages_with_fncall = messages
    messages = []
    for m_idx, m in enumerate(messages_with_fncall):
        role, content = m.role, m.content
        content = content or ''
        content = content.lstrip('\n').rstrip()

        if role == 'user':
            messages.append(
                ChatMessage(role='user',
                            content=content.lstrip('\n').rstrip()))
        else:
            raise HTTPException(
                status_code=400,
                detail=f'Invalid request: Incorrect role {role}.')

    query = _TEXT_COMPLETION_CMD
    if messages[-1].role == 'user':
        query = messages[-1].content
        messages = messages[:-1]

    if len(messages) % 2 != 0:
        raise HTTPException(status_code=400, detail='Invalid request')

    if user_id in history_global:
        history = history_global[user_id]
        if len(history) > 10:
            del history[:len(history) - 10]
    else:
        history = []

    already_known_user={}
    if user_id in already_known_user_global:
        already_known_user = already_known_user_global[user_id]
        print(already_known_user)
    already_known_user.setdefault('the_car_price', {})
    already_known_user.setdefault('the_car_configuration', {})
    already_known_user.setdefault('the_car_appointment', {})
    already_known_user.setdefault('name', {})
    already_known_user.setdefault('buy_car',{})
    already_known_user.setdefault('used_car_valuation',{})


    return query, history, system, already_known_user


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


def _dump_json(data: BaseModel, *args, **kwargs) -> str:
    try:
        return data.model_dump_json(*args, **kwargs)
    except AttributeError:  # pydantic<2.0.0
        return data.json(*args, **kwargs)  # noqa

def trim_stop_words(response, stop_words):
    if stop_words:
        for stop in stop_words:
            idx = response.find(stop)
            if idx != -1:
                response = response[:idx]
    return response

async def predict(
        query: str,
        history: List[List[str]],
        model_id: str,
        stop_words: List[str],
        gen_kwargs: Dict,
        system: str,
        model:PreTrainedTokenizerFast,
        tokenizer: PreTrainedTokenizerFast,
        args
):
    choice_data = ChatCompletionResponseStreamChoice(
        index=0, delta=DeltaMessage(role='assistant'), finish_reason=None)
    chunk = ChatCompletionResponse(model=model_id,
                                   choices=[choice_data],
                                   object='chat.completion.chunk')
    yield '{}'.format(_dump_json(chunk, exclude_unset=True))

    current_length = 0
    stop_words_ids = [tokenizer.encode(s)
                      for s in stop_words] if stop_words else None

    delay_token_num = max([len(x) for x in stop_words]) if stop_words_ids else 0
    response_generator = model.chat_stream(tokenizer,
                                           query,
                                           history=history,
                                           stop_words_ids=stop_words_ids,
                                           system=system,
                                           **gen_kwargs)
    for _new_response in response_generator:
        if len(_new_response) <= delay_token_num:
            continue
        new_response = _new_response[:-delay_token_num] if delay_token_num else _new_response

        if len(new_response) == current_length:
            continue

        new_text = new_response[current_length:]
        current_length = len(new_response)

        choice_data = ChatCompletionResponseStreamChoice(
            index=0, delta=DeltaMessage(content=new_text), finish_reason=None)
        chunk = ChatCompletionResponse(model=model_id,
                                       choices=[choice_data],
                                       object='chat.completion.chunk')
        yield '{}'.format(_dump_json(chunk, exclude_unset=True))

    if current_length != len(_new_response):
        # Determine whether to print the delay tokens
        delayed_text = _new_response[current_length:]
        new_text = trim_stop_words(delayed_text, stop_words)
        if len(new_text) > 0:
            choice_data = ChatCompletionResponseStreamChoice(
                index=0, delta=DeltaMessage(content=new_text), finish_reason=None)
            chunk = ChatCompletionResponse(model=model_id,
                                           choices=[choice_data],
                                           object='chat.completion.chunk')
            yield '{}'.format(_dump_json(chunk, exclude_unset=True))

    choice_data = ChatCompletionResponseStreamChoice(index=0,
                                                     delta=DeltaMessage(),
                                                     finish_reason='stop')
    chunk = ChatCompletionResponse(model=model_id,
                                   choices=[choice_data],
                                   object='chat.completion.chunk')
    yield '{}'.format(_dump_json(chunk, exclude_unset=True))
    yield '[DONE]'

    _gc(args=args)


def tool_wrapper_for_qwen_buy_car():
    def tool_(query, already_known_user, user_id):
        query = json.loads(query)
        for key, value in query.items():
            already_known_user['buy_car'][key] = value
        query = already_known_user['buy_car']
        print(query)
        if 'price' not in query or 'vehicle_classification' not in query or 'energy_type' not in query or (
                query['price'] == '不限'
                and query['vehicle_classification'] == '不限'
                and query['energy_type'] == '不限'):
            missing_keys = [key for key in ['price', 'vehicle_classification', 'energy_type'] if key not in query]
            already_list = [(key, value) for key, value in already_known_user['buy_car'].items()]
            return f"已知{already_list}，需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user
        already_known_user['buy_car'] = {}

        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/business/newCarRecommendation',json=query)
        # 处理响应
        if response.status_code == 200:
            # 请求成功
            data = response.json()  # 获取响应数据，如果是 JSON 格式
            return str(data), already_known_user
        else:
            # 请求失败
            return '查询失败，请检查', already_known_user
    return tool_


def tool_wrapper_for_qwen_used_car_valuation():
    def tool_(query, already_known_user, user_id):
        query = json.loads(query)
        for key, value in query.items():
            already_known_user['used_car_valuation'][key] = value
        query = already_known_user['used_car_valuation']
        print(query)
        if ('vehicle_brand_name' not in query or 'vehicle_series' not in query
                or 'vehicle_model_year' not in query or 'vehicle_mileage' not in query
                or 'vehicle_registration_year' not in query):
            missing_keys = [key for key in ['vehicle_brand_name', 'vehicle_series', 'vehicle_model_year','vehicle_mileage','vehicle_registration_year'] if key not in query]
            already_list = [(key, value) for key, value in already_known_user['used_car_valuation'].items()]
            return f"已知{already_list}，需要继续询问用户{' 和 '.join(missing_keys)}", already_known_user
        already_known_user['used_car_valuation'] = {}

        query['userId'] = 'dc14f3a28d5a4a6f'
        response = requests.post(f'http://192.168.110.147:12580/auto-ai-agent/business/usedCarValuation',json=query)
        # 处理响应
        if response.status_code == 200:
            # 请求成功
            data = response.json()  # 获取响应数据，如果是 JSON 格式
            return str(data), already_known_user
        else:
            # 请求失败
            return '查询失败，请检查', already_known_user
        # return '估值九万九',already_known_user
    return tool_