from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진을 허용하거나 필요한 도메인을 지정합니다.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 메서드를 허용하거나 필요한 메서드를 지정합니다.
    allow_headers=["*"],  # 모든 헤더를 허용하거나 필요한 헤더를 지정합니다.
)

class Character(BaseModel):
    name: str
    level: int

tempDB = [
        Character(name = "Yul", level = 280),
        Character(name = "Myung", level = 245),
        Character(name = "Yang", level = 285)
]

@app.get("/")
def printHello():
    return {"message": "Hello World"}

@app.get("/characters/{index}")
def read_character(index : int):
    if 0 <= index < len(tempDB):
        return {"name": tempDB[index].name, "level": tempDB[index].level}
    else:
        return {"message": "Index out of range"}

@app.post("/characters/")
def create_character(post : Character):
    tempDB.append(post)
    return {"message": "Character added successfully"}
