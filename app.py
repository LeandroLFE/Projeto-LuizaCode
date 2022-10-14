from uvicorn import run as uvicorn_run

if __name__ == "__main__":
    uvicorn_run("main:app", host="0.0.0.0", port=8000, reload=True)
