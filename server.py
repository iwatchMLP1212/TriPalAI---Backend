from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import get_answer

class Message(BaseModel):
    message: str

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://192.168.1.9:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/response/")
async def generate_response(message: Message):
    return {"response": get_answer(message.message)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
