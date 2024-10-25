from fastapi import FastAPI
from app import api

app = FastAPI()

app.include_router(api.router, prefix="/rest/api")

@app.get("/")
def read_root():
    return {"Message": "Ok"}

def run_uvicorn():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)

if __name__ == "__main__":
    from watchgod import run_process
    run_process(".", run_uvicorn)