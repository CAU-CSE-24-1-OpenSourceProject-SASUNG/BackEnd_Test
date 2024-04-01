from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import openai
#from database import *

# 여기에openai 키 작성(띄어쓰기 사이에 . 추가)
openai api_key = ""


app = FastAPI()

templates = Jinja2Templates(directory="templates")

conversation_history = []

# 대화 시작
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "converstation":conversation_history})

# 사용자 입력 처리 -> ChatGPT 응답 생성
@app.post("/submit/")
async def submit_form(request: Request, user_input: str = Form(...)):
    # 사용자 입력을 대화 기록에 추가
    conversation_history.append({"speaker": "You", "message": user_input})
    
    # ChatGPT에 대화 기록을 포함하여 챗봇 응답 생성
    chat_response = generate_chat_response(conversation_history)
    
    # 챗봇 응답을 대화 기록에 추가
    conversation_history.append({"speaker": "ChatGPT", "message": chat_response})
    
    return templates.TemplateResponse("index.html", {"request": request, "conversation": conversation_history})

# 챗봇 응답을 생성하는 함수
def generate_chat_response(conversation_history):
    
    # 대화 기록을 ChatGPT의 입력으로 변환
    chat_prompt = "\n".join([f"{turn['speaker']}: {turn['message']}" for turn in conversation_history])
    
    # ChatGPT API를 사용하여 챗봇 응답 생성
    response = openai.completions.create(
        engine="davinci",  # GPT-3 엔진 사용
        prompt=chat_prompt,
        temperature=0.7,  # 응답 다양성 조절
        max_tokens=50  # 최대 토큰 수
    )
    return response.choices[0].text.strip()


#@app.get("/users/")
#async def read_users():
#    users = get_users()
#    return users
