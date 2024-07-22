import uvicorn

from rag_classification import rag_args_classification

if __name__ == "__main__":
    uvicorn.run("api_demo_aliyun:app", host="0.0.0.0", port=10029, workers=10)
