import time
from argparse import ArgumentParser
from contextlib import asynccontextmanager

import torch
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from transformers import AutoTokenizer, AutoModelForCausalLM

from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union, Iterable

from transformers import PreTrainedTokenizerFast, LogitsProcessor


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

    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role='assistant', content=response),
        finish_reason='stop',
    )
    return ChatCompletionResponse(model=request.model,
                                  choices=[choice_data],
                                  object='chat.completion')


def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-c',
        '--checkpoint-path',
        type=str,
        default='/opt/large-model/qwen/qwen1.5/Qwen1.5-14B-Chat',
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
        help=
        'Demo server name. Default: 0.0.0.0',
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
        , bnb_4bit_compute_dtype=torch.float16
        , load_in_4bit=True
    ).eval()

    # * 3.运行web框架
    uvicorn.run(app, host=args.server_name, port=args.server_port, workers=1)
