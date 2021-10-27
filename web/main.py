from fastapi import FastAPI
from starlette.responses import FileResponse

app = FastAPI()

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')



@app.get("/redirect")
async def read_index():
    return FileResponse('static/index.html')
