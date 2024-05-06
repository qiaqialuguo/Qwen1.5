import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from transformers import AutoTokenizer, AutoModelForCausalLM

