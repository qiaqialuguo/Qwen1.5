import uvicorn

if __name__ == "__main__":
    uvicorn.run("rag_main_classification:app", host="0.0.0.0", port=10019, workers=10)
