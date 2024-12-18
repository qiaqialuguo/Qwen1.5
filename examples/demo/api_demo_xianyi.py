import json
import time
from argparse import ArgumentParser
from contextlib import asynccontextmanager

import torch
import uvicorn
from fastapi import FastAPI
from threading import Thread
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from transformers import AutoTokenizer, AutoModelForCausalLM,TextIteratorStreamer

from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union, Iterable
from rag_classification.rag_tools_classification import StopWordsLogitsProcessor

from transformers import PreTrainedTokenizerFast, LogitsProcessor
from transformers.generation.logits_process import LogitsProcessorList

def _gc(args, forced: bool = False):
    if args.disable_gc and not forced:
        return

    import gc

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


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
    model: Optional[str] = 'hi'
    messages: List[ChatMessage]
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
    model.generation_config.temperature = request.temperature
    model.generation_config.top_k = request.top_k
    model.generation_config.top_p = request.top_p
    model.generation_config.do_sample = request.do_sample
    is_stream = request.stream

    stop_words = ['User:', 'Action:', 'Action Input:', 'Think:','Thought:']
    # if request.use_rag:
    stop_words_ids = [tokenizer.encode(_) for _ in stop_words]
    stop_words_logits_processor = StopWordsLogitsProcessor(
        stop_words_ids=stop_words_ids,
        eos_token_id=model.generation_config.eos_token_id,
    )
    logits_processor = LogitsProcessorList([stop_words_logits_processor])

    if is_stream:
        print(conversation)
        inputs = tokenizer.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            return_tensors='pt',
        )
        generate = predict(inputs.to('cuda'),
                           request.model,
                           logits_processor,
                           )
        s = handler(generate)
        return EventSourceResponse(s, media_type='text/event-stream')
    else:
        inputs = tokenizer.apply_chat_template(
            conversation,
            tokenize=False,
            add_generation_prompt=True
        )
        print(inputs)
        print(len(inputs.split()))
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
        print('answer: '+response)

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
        inputs,
        model_id,
logits_processor
):
    global model, tokenizer
    choice_data = ChatCompletionResponseStreamChoice(
        index=0, delta=DeltaMessage(role='assistant'), finish_reason=None)
    chunk = ChatCompletionResponse(model=model_id,
                                   choices=[choice_data],
                                   object='chat.completion.chunk')
    yield '{}'.format(_dump_json(chunk, exclude_unset=True))

    streamer = TextIteratorStreamer(tokenizer=tokenizer, skip_prompt=True, timeout=60.0, skip_special_tokens=True,logits_processor=logits_processor)
    generation_kwargs = dict(
        input_ids=inputs,
        streamer=streamer,
        max_new_tokens=1024,
    )
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    for new_text in streamer:
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

    _gc(args=args, forced=True)

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
        default='/opt/large-model/qwen/qwen1.5/Qwen2.5-14B-Instruct/',
        help='Checkpoint name or path, default to %(default)r',
    )
    parser.add_argument('--server-port',
                        type=int,
                        default=10039,
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

    tokenizer = AutoTokenizer.from_pretrained(args.checkpoint_path)

    model = AutoModelForCausalLM.from_pretrained(
        args.checkpoint_path,
        device_map='cuda'
        # ,torch_dtype=torch.float16
        , bnb_4bit_compute_dtype=torch.float16
        , load_in_4bit=True
    ).eval()

    # * 3.运行web框架
    uvicorn.run(app, host=args.server_name, port=args.server_port, workers=1)
