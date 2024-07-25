import uvicorn

# from rag_classification.rag_main_classification import app

if __name__ == "__main__":
    # from multiprocessing import Manager
    # manager = Manager()
    # history_global = manager.dict()
    # already_known_user_global = manager.dict()
    # # 将共享字典注入 FastAPI 应用的依赖
    # app.state.history_global = history_global
    # app.state.already_known_user_global = already_known_user_global
    uvicorn.run("rag_main_classification:app", host="0.0.0.0", port=10019, workers=10)
